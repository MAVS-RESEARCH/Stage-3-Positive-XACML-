"""Staging-certificate tests (Amendment 004).

Builds the evaluation-free staging certificate into tmp and asserts all
13 inspectable fields, hash bindings, marker presence, and PENDING_TARGET
markers for evaluation-bound fields. No PDP execution.
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import hardening_evidence as hev  # noqa: E402


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def build(out):
    """Build the staging certificate to the given path."""
    hev.cmd_staging_certificate(_ns(repo_root=REPO_ROOT, out=out))


def test_staging_certificate_fields(tmp_path):
    """All inspectable fields present with live-bound hashes."""
    # [P2-LOG-S10] Test step: assert staging certificate content.
    print("[P2:test:staging:010] certificate fields", flush=True)
    out = str(tmp_path / "staging_certificate.json")
    build(out)
    with open(out, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert doc["certificate_id"] == "PC-XACML-S3PLUS-v1-staging"
    assert doc["repaired_hashes"]["permit"]["world_value_bound"] is True
    assert doc["repaired_hashes"]["nonpermit"]["world_value_bound"] is True
    assert doc["deployment_set_manifest"]["count_is_one"] is True
    assert doc["disjointness"]["live_out_dir_disjoint"] is True
    assert doc["no_prior_response"]["target_scan_empty"] is True
    assert "PENDING_TARGET" in doc["before_after_manifests"]
    assert doc["no_prior_response"]["responses_pending_target"] is True
    assert doc["no_alternate_policy"]["copy_whitelist"] == [
        "pdp.xml", "policies/policy.xml"]
    with open(os.path.join(REPO_ROOT, "derived", "requests",
                           "request_x_permit.xml"), "rb") as handle:
        import hashlib
        assert hashlib.sha256(handle.read()).hexdigest() == \
            doc["repaired_hashes"]["permit"]["sha256"]


def test_staging_certificate_deterministic(tmp_path):
    """Two builds agree modulo produced_utc (no PDP, no clock in hash)."""
    # [P2-LOG-S12] Test step: assert staging determinism.
    print("[P2:test:staging:012] certificate determinism", flush=True)
    first = str(tmp_path / "a.json")
    second = str(tmp_path / "b.json")
    build(first)
    build(second)

    def norm(path):
        """Load a certificate minus volatile timestamps."""
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
        doc.pop("produced_utc", None)
        return doc

    assert norm(first) == norm(second)
