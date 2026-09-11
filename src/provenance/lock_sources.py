"""Phase-1 external source lock for PC-XACML-S3+.

Clones AuthzForce at the pinned release tag, verifies HEAD and tree
cleanliness, copies only the four frozen fixture files, checks their
upstream Git blob SHAs, freezes the OASIS XACML 3.0 core specification,
and writes the external manifest. Any mismatch fails closed (exit 1).

Step console lines use the [P1:lock:NNN] tag; each is marked in code by
a [P1-LOG-NNN] comment so Path.md can cite exact file:line locations.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

EXPERIMENT_ID = "PC-XACML-S3PLUS-v1"
AUTHZFORCE_REPO_URL = "https://github.com/authzforce/core"
AUTHZFORCE_TAG = "release-21.2.0"
AUTHZFORCE_PINNED_COMMIT = "3cc0e988e1639da48184434cd5c918102ff5b499"
FIXTURE_SUBPATH = (
    "pdp-testutils/src/test/resources/conformance/others/"
    "StatusDetail.MissingAttributeDetail"
)
FIXTURE_FILES = [
    "pdp.xml",
    "request.xml",
    "response.xml",
    "policies/policy.xml",
]
# Upstream Git blob SHAs recorded in the controlling specification.
EXPECTED_BLOB_SHAS = {
    "pdp.xml": "01a0adc080253afc2c523a0b8e58e8578e8275eb",
    "request.xml": "ff6582db3d9c2bd00ae87e69279c23057b14a47a",
    "response.xml": "835d483564a1c3ab052e0dbbd24c2258e5a5c295",
    "policies/policy.xml": "698af364ba2db79534cc654765baaed4d1c8f867",
}
XACML_SPEC_URL = (
    "https://docs.oasis-open.org/xacml/3.0/"
    "xacml-3.0-core-spec-cos01-en.html"
)
XACML_TITLE_MARKER = b"xacml-3.0-core-spec"


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P1-LOG-900] Fail-closed termination marker for every abort path.
    print("[P1:lock:FAIL] " + message, flush=True)
    sys.exit(1)


def run_git(args, cwd):
    """Run a git subprocess and return stripped stdout, failing closed."""
    try:
        completed = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        fail("git invocation failed: %s (%s)" % (" ".join(args), exc))
    if completed.returncode != 0:
        fail("git %s failed: %s" % (" ".join(args), completed.stderr.strip()))
    return completed.stdout.strip()


def sha256_file(path):
    """Return the hex SHA-256 digest of a file's bytes."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clone_or_reuse(repo_url, tag, clone_dir):
    """Clone the tag shallowly, or reuse a verified existing clone."""
    # [P1-LOG-020] Step: obtain the pinned AuthzForce source tree.
    print("[P1:lock:020] cloning %s tag %s" % (repo_url, tag), flush=True)
    if os.path.isdir(os.path.join(clone_dir, ".git")):
        print("[P1:lock:022] existing clone found, reusing after verification",
              flush=True)
        return
    if os.path.exists(clone_dir):
        fail("clone path exists but is not a git tree: " + clone_dir)
    parent = os.path.dirname(os.path.abspath(clone_dir))
    os.makedirs(parent, exist_ok=True)
    run_git(["clone", "--branch", tag, "--depth", "1", repo_url, clone_dir],
            cwd=parent)
    print("[P1:lock:024] clone complete", flush=True)


def main(argv):
    """Entry point: lock all Phase-1 external sources."""
    # [P1-LOG-010] Step: start lock, echo resolved arguments.
    print("[P1:lock:010] start external source lock", flush=True)
    if len(argv) != 3:
        fail("usage: lock_sources.py <repo-root> <clone-dir>")
    repo_root = os.path.abspath(argv[1])
    clone_dir = os.path.abspath(argv[2])
    print("[P1:lock:012] repo-root=%s clone-dir=%s" % (repo_root, clone_dir),
          flush=True)

    clone_or_reuse(AUTHZFORCE_REPO_URL, AUTHZFORCE_TAG, clone_dir)

    # [P1-LOG-030] Step: verify pinned commit.
    print("[P1:lock:030] verifying HEAD == pinned commit", flush=True)
    head = run_git(["rev-parse", "HEAD"], cwd=clone_dir)
    print("[P1:lock:032] HEAD=%s" % head, flush=True)
    if head != AUTHZFORCE_PINNED_COMMIT:
        fail("HEAD %s != pinned %s" % (head, AUTHZFORCE_PINNED_COMMIT))

    # [P1-LOG-040] Step: verify clean working tree.
    print("[P1:lock:040] verifying clean working tree", flush=True)
    porcelain = run_git(["status", "--porcelain"], cwd=clone_dir)
    if porcelain != "":
        fail("working tree not clean: " + porcelain)
    print("[P1:lock:042] working tree clean", flush=True)

    fixture_src = os.path.join(clone_dir, FIXTURE_SUBPATH)
    fixture_dst = os.path.join(repo_root, "external", "authzforce", "fixture")
    os.makedirs(os.path.join(fixture_dst, "policies"), exist_ok=True)

    manifest_files = {}
    sums_lines = []
    # [P1-LOG-050] Step: copy fixture files, check blob + content hashes.
    print("[P1:lock:050] copying %d fixture files" % len(FIXTURE_FILES),
          flush=True)
    for rel in FIXTURE_FILES:
        src = os.path.join(fixture_src, rel)
        dst = os.path.join(fixture_dst, rel)
        if not os.path.isfile(src):
            fail("fixture file missing upstream: " + rel)
        shutil.copyfile(src, dst)
        blob_sha = run_git(["hash-object", os.path.join(FIXTURE_SUBPATH, rel)],
                           cwd=clone_dir)
        if blob_sha != EXPECTED_BLOB_SHAS[rel]:
            fail("blob SHA mismatch for %s: got %s want %s"
                 % (rel, blob_sha, EXPECTED_BLOB_SHAS[rel]))
        content_sha = sha256_file(dst)
        manifest_files[rel] = {"git_blob_sha": blob_sha,
                               "sha256": content_sha}
        sums_lines.append("%s  fixture/%s\n" % (content_sha, rel))
        # [P1-LOG-052] Step: per-file hash confirmation.
        print("[P1:lock:052] %s blob=%s sha256=%s"
              % (rel, blob_sha, content_sha), flush=True)

    with open(os.path.join(repo_root, "external", "authzforce",
                           "SHA256SUMS"), "w", newline="\n") as handle:
        handle.writelines(sums_lines)
    with open(os.path.join(repo_root, "external", "authzforce",
                           "RELEASE.json"), "w", newline="\n") as handle:
        json.dump({"repository": AUTHZFORCE_REPO_URL,
                   "tag": AUTHZFORCE_TAG,
                   "commit": head,
                   "verified_head": True,
                   "working_tree_clean": True,
                   "cloned_at_utc": datetime.now(timezone.utc).strftime(
                       "%Y-%m-%dT%H:%M:%SZ")}, handle, indent=2,
                  sort_keys=True)
        handle.write("\n")
    with open(os.path.join(repo_root, "external", "authzforce",
                           "COMMIT.txt"), "w", newline="\n") as handle:
        handle.write(head + "\n")

    # [P1-LOG-070] Step: freeze the OASIS XACML 3.0 core specification.
    print("[P1:lock:070] freezing XACML specification", flush=True)
    xacml_dir = os.path.join(repo_root, "external", "xacml")
    os.makedirs(xacml_dir, exist_ok=True)
    spec_path = os.path.join(xacml_dir, "xacml-3.0-core-spec-cos01-en.html")
    manifest_path = os.path.join(repo_root, "external", "MANIFEST.json")
    if os.path.isfile(spec_path) and os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as handle:
                prior = json.load(handle)
            if sha256_file(spec_path) == prior["xacml"]["sha256"]:
                retrieved = prior["xacml"]["retrieved_utc"]
                spec_bytes = open(spec_path, "rb").read()
                spec_sha = prior["xacml"]["sha256"]
                print("[P1:lock:071] reusing frozen spec sha256=%s" % spec_sha,
                      flush=True)
        except (KeyError, ValueError, OSError):
            pass
    if "spec_bytes" not in dir():
        retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with urllib.request.urlopen(XACML_SPEC_URL, timeout=300) as resp:
                spec_bytes = resp.read()
        except OSError as exc:
            fail("spec download failed: %s" % exc)
        if XACML_TITLE_MARKER not in spec_bytes:
            fail("downloaded spec missing title marker; refusing to freeze")
        with open(spec_path, "wb") as handle:
            handle.write(spec_bytes)
        spec_sha = sha256_file(spec_path)
    with open(os.path.join(xacml_dir, "SHA256SUMS"), "w",
              newline="\n") as handle:
        handle.write("%s  xacml-3.0-core-spec-cos01-en.html\n" % spec_sha)
    # [P1-LOG-072] Step: spec freeze confirmation.
    print("[P1:lock:072] spec bytes=%d sha256=%s retrieved=%s"
          % (len(spec_bytes), spec_sha, retrieved), flush=True)

    # [P1-LOG-080] Step: write the external manifest.
    print("[P1:lock:080] writing external manifest", flush=True)
    os.makedirs(os.path.join(repo_root, "derived"), exist_ok=True)
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "created_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "authzforce": {"repository": AUTHZFORCE_REPO_URL,
                       "tag": AUTHZFORCE_TAG,
                       "commit": head,
                       "verified_head": True,
                       "working_tree_clean": True,
                       "fixture_subpath": FIXTURE_SUBPATH,
                       "fixture_files": manifest_files},
        "xacml": {"source_url": XACML_SPEC_URL,
                  "retrieved_utc": retrieved,
                  "local_path": "external/xacml/"
                                "xacml-3.0-core-spec-cos01-en.html",
                  "sha256": spec_sha,
                  "size_bytes": len(spec_bytes)},
    }
    with open(os.path.join(repo_root, "external", "MANIFEST.json"), "w",
              newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(repo_root, "derived",
                           "canonical_external_manifest.json"), "w",
              newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P1-LOG-090] Step: lock complete.
    print("[P1:lock:090] source lock complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
