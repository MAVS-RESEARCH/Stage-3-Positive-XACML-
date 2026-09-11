"""Phase-1 source-hash tests (S01-S03 + authoritative-spec hashes).

Verifies the pinned AuthzForce commit, the frozen fixture blob SHAs, the
local SHA-256 digests, the XACML specification freeze, and the
authoritative IMPLEMENTATION_SPEC.md raw + LF-normalized hashes.
"""
import hashlib
import json
import os
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PINNED_COMMIT = "3cc0e988e1639da48184434cd5c918102ff5b499"
EXPECTED_BLOBS = {
    "pdp.xml": "01a0adc080253afc2c523a0b8e58e8578e8275eb",
    "request.xml": "ff6582db3d9c2bd00ae87e69279c23057b14a47a",
    "response.xml": "835d483564a1c3ab052e0dbbd24c2258e5a5c295",
    "policies/policy.xml": "698af364ba2db79534cc654765baaed4d1c8f867",
}


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest():
    """Load the external manifest."""
    # [P1-LOG-T10] Test step: load the sealed manifest once per test module.
    print("[P1:test:hashes:010] loading external manifest", flush=True)
    with open(os.path.join(REPO_ROOT, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        return json.load(handle)


def test_pinned_commit_and_tag():
    """S01: release tag and exact commit are pinned and verified."""
    # [P1-LOG-T11] Test step: assert S01 commit/tag provenance.
    print("[P1:test:hashes:011] checking S01 commit pin", flush=True)
    manifest = load_manifest()
    assert manifest["authzforce"]["commit"] == PINNED_COMMIT
    assert manifest["authzforce"]["tag"] == "release-21.2.0"
    with open(os.path.join(REPO_ROOT, "external", "authzforce",
                           "COMMIT.txt"), encoding="utf-8") as handle:
        assert handle.read().strip() == PINNED_COMMIT


def test_fixture_blobs_and_content():
    """S02/S03: upstream blob SHAs match and local bytes are intact."""
    # [P1-LOG-T12] Test step: assert S02/S03 fixture hashes.
    print("[P1:test:hashes:012] checking S02/S03 fixture hashes",
          flush=True)
    manifest = load_manifest()
    fixture_dir = os.path.join(REPO_ROOT, "external", "authzforce",
                               "fixture")
    for rel, expected_blob in EXPECTED_BLOBS.items():
        path = os.path.join(fixture_dir, rel)
        assert os.path.isfile(path), rel
        assert manifest["authzforce"]["fixture_files"][rel][
            "git_blob_sha"] == expected_blob
        blob = subprocess.run(["git", "hash-object", path],
                              capture_output=True, text=True,
                              timeout=120).stdout.strip()
        assert blob == expected_blob, rel
        digest = sha256_file(path)
        assert digest == manifest["authzforce"]["fixture_files"][rel][
            "sha256"], rel


def test_xacml_spec_frozen():
    """XACML specification local copy matches the sealed hash."""
    # [P1-LOG-T13] Test step: assert XACML freeze integrity.
    print("[P1:test:hashes:013] checking XACML freeze", flush=True)
    manifest = load_manifest()
    spec_path = os.path.join(REPO_ROOT, "external", "xacml",
                             "xacml-3.0-core-spec-cos01-en.html")
    assert os.path.getsize(spec_path) > 1000000
    assert sha256_file(spec_path) == manifest["xacml"]["sha256"]


def test_authoritative_spec_hashes():
    """Authoritative spec raw + LF-normalized hashes match the seal."""
    # [P1-LOG-T14] Test step: assert authoritative-spec identity hashes.
    print("[P1:test:hashes:014] checking authoritative spec hashes",
          flush=True)
    manifest = load_manifest()
    with open(os.path.join(REPO_ROOT, "IMPLEMENTATION_SPEC.md"),
              "rb") as handle:
        raw = handle.read()
    record = manifest["implementation_spec"]
    assert hashlib.sha256(raw).hexdigest() == record["sha256_raw"]
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    assert hashlib.sha256(normalized).hexdigest() == record[
        "sha256_lf_normalized"]
    assert record["size_bytes"] == len(raw)
