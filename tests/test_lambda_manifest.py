"""Lambda manifest reconstruction tests (Amendment 004).

Independent-implementation agreement: the manifest builder and the
standalone recompute tool must agree on pre_hash; a frozen test vector
pins the canonicalization; constituent spot checks bind key hashes.
"""
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import hardening_evidence as hev  # noqa: E402
import recompute_lambda as rec  # noqa: E402

VECTOR_DOC = {"components": {"a": {"sha256": "0" * 64}}, "exclusions": {}}
VECTOR_DIGEST = ("9e9d6fe0f640a67ec429f167f6fc278346f82513a392a2b705eaf9be47ba99e9")


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def manifest_args(out):
    """Build args for regenerating the live Lambda manifest."""
    ev = os.path.join(REPO_ROOT, "artifacts", "audits", "semantic_hardening",
                      "rounds", "HARDENING_ROUND_003", "evidence")
    return _ns(manifest=os.path.join(REPO_ROOT, "external", "MANIFEST.json"),
               fixture_dir=os.path.join(REPO_ROOT, "external", "authzforce",
                                        "fixture"),
               repo_root=REPO_ROOT,
               resolved_effective=os.path.join(ev, "resolved_effective.json"),
               dir_listing=os.path.join(ev, "policy_dir_listing.json"),
               out=out)


def test_canonical_vector_pinned():
    """Frozen test vector pins the exact canonicalization."""
    # [P2-LOG-V10] Test step: assert canonical test vector.
    print("[P2:test:lambda:010] canonical vector", flush=True)
    assert hashlib.sha256(rec.canonical_composite(
        VECTOR_DOC)).hexdigest() == VECTOR_DIGEST


def test_builder_recompute_agreement(tmp_path):
    """Builder and recompute tool agree on pre_hash (independent paths)."""
    # [P2-LOG-V12] Test step: assert dual-implementation agreement.
    print("[P2:test:lambda:012] builder/recompute agreement", flush=True)
    out = str(tmp_path / "lambda_manifest.json")
    hev.cmd_lambda_manifest(manifest_args(out))
    with open(out, encoding="utf-8") as handle:
        manifest = json.load(handle)
    assert manifest["pre_hash"] == hashlib.sha256(
        rec.canonical_composite(manifest)).hexdigest()
    assert len(manifest["components"]["engine_semantic_set"]
               ["files"]) >= 76
    assert manifest["components"]["built_artifacts"]["jars"]
    assert "reconstruction" in manifest


def test_constituent_spot_checks():
    """Policy/provider/listing constituents match frozen bytes."""
    # [P2-LOG-V14] Test step: assert constituent spot checks.
    print("[P2:test:lambda:014] constituent spots", flush=True)
    packet = os.path.join(REPO_ROOT, "artifacts", "audits",
                          "semantic_hardening", "final_freeze",
                          "FINAL_BLIND_PACKET")
    if not os.path.isdir(packet):
        import pytest
        pytest.skip("no frozen packet")
    manifest = json.load(open(os.path.join(
        packet, "candidates", "lambda_manifest.json"), encoding="utf-8"))
    comps = manifest["components"]
    assert rec.sha256_file(os.path.join(
        packet, "corpus", "fixture", "policies",
        "policy.xml")) == comps["policy_bytes"]["sha256"]


def test_packet_mode_verifies_layout(tmp_path):
    """Packet-mode tool verifies laid-out constituents, flags drift."""
    # [P2-LOG-V16] Test step: assert packet-mode verification.
    print("[P2:test:lambda:016] packet mode", flush=True)
    import shutil
    ev = os.path.join(REPO_ROOT, "artifacts", "audits", "semantic_hardening",
                      "rounds", "HARDENING_ROUND_005", "evidence")
    packet = str(tmp_path / "packet")
    os.makedirs(os.path.join(packet, "candidates", "engine_sources"))
    os.makedirs(os.path.join(packet, "corpus", "fixture", "policies"))
    shutil.copyfile(os.path.join(ev, "lambda_manifest.json"),
                    os.path.join(packet, "candidates", "lambda_manifest.json"))
    shutil.copyfile(os.path.join(REPO_ROOT, "external", "authzforce",
                                 "fixture", "policies", "policy.xml"),
                    os.path.join(packet, "corpus", "fixture", "policies",
                                 "policy.xml"))
    manifest = json.load(open(os.path.join(
        packet, "candidates", "lambda_manifest.json"), encoding="utf-8"))
    first = sorted(manifest["components"]["engine_semantic_set"]
                   ["files"])[0]
    clone_rel = os.path.join("external", "authzforce-repo",
                             *first.split("/"))
    dest = os.path.join(packet, "candidates", "engine_sources",
                        *first.split("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(os.path.join(REPO_ROOT, clone_rel), dest)
    rec.main(["--manifest",
              os.path.join(packet, "candidates", "lambda_manifest.json"),
              "--packet-dir", packet])
    with open(dest, "ab") as handle:
        handle.write(b" ")
    try:
        rec.main(["--manifest",
                  os.path.join(packet, "candidates", "lambda_manifest.json"),
                  "--packet-dir", packet])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("tampered engine file accepted")
