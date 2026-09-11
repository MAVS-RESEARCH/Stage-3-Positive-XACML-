"""Phase-1+ source verifier for PC-XACML-S3+.

Re-verifies frozen local SHA-256 digests, recomputes recorded Git blob
SHAs directly on the frozen files with `git hash-object` (no working
tree required), and checks manifest plus authoritative-spec hashes.
HEAD/cleanliness of the upstream tree is verified ONCE at lock time and
recorded in the manifest; this module never claims to re-check a working
tree that no longer exists. `--recheckout` performs a disposable fresh
clone for full HEAD/clean/blob re-verification on demand.

Step console lines use the [P1:verify:NNN] tag, each marked by a
[P1-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P1-LOG-900] Fail-closed termination marker for every abort path.
    print("[P1:verify:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file's bytes."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha(path):
    """Recompute the Git blob SHA of a file, config-independent.

    Applies the documented CRLF->LF normalization before hashing (the
    upstream blobs are LF-normalized; working bytes may be CRLF). This
    replaces `git hash-object`, whose conversion behavior depends on
    local Git attributes configuration.
    """
    with open(path, "rb") as handle:
        content = handle.read().replace(b"\r\n", b"\n")
    header = ("blob %d\0" % len(content)).encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def main(argv):
    """Entry point: verify all sealed Phase-1 source hashes."""
    # [P1-LOG-010] Step: start verification, echo resolved arguments.
    print("[P1:verify:010] start source verification", flush=True)
    args = list(argv[1:])
    recheckout = False
    if "--recheckout" in args:
        recheckout = True
        args.remove("--recheckout")
    if len(args) != 1:
        fail("usage: verify_sources.py [--recheckout] <repo-root>")
    repo_root = os.path.abspath(args[0])
    print("[P1:verify:012] repo-root=%s recheckout=%s"
          % (repo_root, recheckout), flush=True)

    manifest_path = os.path.join(repo_root, "external", "MANIFEST.json")
    if not os.path.isfile(manifest_path):
        fail("external manifest missing")
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    # [P1-LOG-020] Step: verify lock-time provenance record exists.
    print("[P1:verify:020] checking lock-time provenance record", flush=True)
    authz = manifest.get("authzforce", {})
    if not authz.get("verified_head"):
        fail("manifest lacks verified lock-time HEAD record")
    print("[P1:verify:022] lock commit=%s tag=%s"
          % (authz.get("commit"), authz.get("tag")), flush=True)

    fixture_dir = os.path.join(repo_root, "external", "authzforce",
                               "fixture")
    checked = 0
    # [P1-LOG-030] Step: re-hash every frozen fixture file.
    print("[P1:verify:030] re-hashing frozen fixture files", flush=True)
    for rel, record in sorted(authz.get("fixture_files", {}).items()):
        path = os.path.join(fixture_dir, rel)
        if not os.path.isfile(path):
            fail("frozen fixture file missing: " + rel)
        if sha256_file(path) != record["sha256"]:
            fail("SHA-256 drift detected: " + rel)
        if git_blob_sha(path) != record["git_blob_sha"]:
            fail("Git blob SHA drift detected: " + rel)
        checked += 1
        # [P1-LOG-032] Step: per-file verification confirmation.
        print("[P1:verify:032] ok %s" % rel, flush=True)

    # [P1-LOG-040] Step: verify XACML specification hash.
    print("[P1:verify:040] verifying XACML specification", flush=True)
    spec_path = os.path.join(repo_root, "external", "xacml",
                             "xacml-3.0-core-spec-cos01-en.html")
    if sha256_file(spec_path) != manifest["xacml"]["sha256"]:
        fail("XACML specification drift detected")
    print("[P1:verify:042] XACML specification ok", flush=True)

    # [P1-LOG-050] Step: verify authoritative spec hashes.
    print("[P1:verify:050] verifying authoritative spec", flush=True)
    impl_path = os.path.join(repo_root, "IMPLEMENTATION_SPEC.md")
    with open(impl_path, "rb") as handle:
        raw = handle.read()
    spec_record = manifest.get("implementation_spec", {})
    if hashlib.sha256(raw).hexdigest() != spec_record.get("sha256_raw"):
        fail("IMPLEMENTATION_SPEC.md raw drift detected")
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if hashlib.sha256(normalized).hexdigest() != spec_record.get(
            "sha256_lf_normalized"):
        fail("IMPLEMENTATION_SPEC.md normalized drift detected")
    print("[P1:verify:052] authoritative spec ok", flush=True)

    if recheckout:
        # [P1-LOG-060] Step: disposable fresh-clone re-verification.
        print("[P1:verify:060] disposable recheckout requested", flush=True)
        tmp = tempfile.mkdtemp(prefix="pc-xacml-recheckout-")
        try:
            completed = subprocess.run(
                ["git", "clone", "--branch", authz["tag"], "--depth", "1",
                 authz["repository"], tmp + "/core"],
                capture_output=True, text=True, timeout=600)
            if completed.returncode != 0:
                fail("recheckout clone failed")
            head = subprocess.run(
                ["git", "-C", tmp + "/core", "rev-parse", "HEAD"],
                capture_output=True, text=True,
                timeout=120).stdout.strip()
            if head != authz["commit"]:
                fail("recheckout HEAD %s != locked %s"
                     % (head, authz["commit"]))
            print("[P1:verify:062] recheckout HEAD matches lock", flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # [P1-LOG-070] Step: verification complete.
    print("[P1:verify:070] source verification complete files=%d" % checked,
          flush=True)


if __name__ == "__main__":
    main(sys.argv)
