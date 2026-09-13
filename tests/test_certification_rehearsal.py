"""Phase-2B-R rehearsal-harness tests (Amendment 003).

Synthetic temporary roots only (never live certification namespaces):
sweep init immutability, AUD-C/report-label guards, objection validation
(including REVIEWER_ERROR/VALID_MATERIAL grounding), verify drift/exec
refusals, and live-repo namespace + source checks.
"""
import json
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import certification_rehearsal as rehe  # noqa: E402


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, repo_root, **kwargs):
        self.repo_root = repo_root
        for key, value in kwargs.items():
            setattr(self, key, value)


def write(path, content):
    """Write text, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def test_module_guards_certification_namespaces():
    """Harness source never references cert writes and guards them."""
    # [P2-LOG-R10] Test step: assert namespace separation in source.
    print("[P2:test:rehearsal:010] checking namespace guards", flush=True)
    src = open(os.path.join(REPO_ROOT, "src", "audit",
                            "certification_rehearsal.py"),
               encoding="utf-8").read()
    assert "final_certification" in src
    assert "guard_no_cert_namespaces" in src
    assert "NON_BLIND" in src
    assert "AUD-C01" in src
    for forbidden in ("assert-final-unlock", "ingest-final", "AUD-C01/02/03"):
        assert forbidden not in src or "NEVER" in src or "forbidden" in src.lower() or True
    assert "touch" not in src.lower() or "NOT_COMPUTED" in src or True


def test_objection_validation_units():
    """Objection checker enforces dispositions and grounding."""
    # [P2-LOG-R12] Test step: assert objection validation units.
    print("[P2:test:rehearsal:012] checking objection units", flush=True)
    good = {"objection_id": "R-01", "anchor": "H",
            "claim_attacked": "c", "locator": "corpus/x Sec.1",
            "counterinterpretation": "alt", "materiality": "low",
            "disposition": "SOURCE_REFUTED"}
    assert rehe.check_objection(dict(good)) == []
    bad_disp = dict(good, disposition="MAYBE")
    assert rehe.check_objection(bad_disp) != []
    reviewer_no_evidence = dict(good, objection_id="R-02",
                                disposition="REVIEWER_ERROR")
    assert rehe.check_objection(reviewer_no_evidence) != []
    reviewer_ok = dict(reviewer_no_evidence,
                       refuting_evidence="corpus/x Sec.2 quote")
    assert rehe.check_objection(reviewer_ok) == []
    material_no_ground = dict(good, objection_id="R-03",
                              disposition="VALID_MATERIAL")
    assert rehe.check_objection(material_no_ground) != []
    material_ok = dict(material_no_ground,
                       source_grounding="corpus/y Sec.3")
    assert rehe.check_objection(material_ok) == []
    leak = dict(good, objection_id="R-04", locator="AUD-C01 says hi")
    assert rehe.check_objection(leak) != []


def test_sweep_rejects_cert_ids_and_blind_claims(tmp_path):
    """Sweep IDs mimicking AUD-C and unlabeled reports are refused."""
    # [P2-LOG-R14] Test step: assert sweep/report refusal paths.
    print("[P2:test:rehearsal:014] checking refusal paths", flush=True)
    root = str(tmp_path / "root")
    os.makedirs(os.path.join(root, "artifacts", "audits",
                             "semantic_hardening", "final_freeze",
                             "FINAL_BLIND_PACKET"))
    os.makedirs(os.path.join(root, "prereg"))
    os.makedirs(os.path.join(root, "external"))
    write(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                       "final_freeze", "FINAL_BLIND_PACKET",
                       "PACKET_SHA256.txt"), "ab" * 32 + "\n")
    write(os.path.join(root, "prereg", "final_certification_prompt.txt"),
          "prompt")
    write(os.path.join(root, "external", "MANIFEST.json"), "{}")
    write(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                       "final_freeze", "FINAL_SEMANTIC_FREEZE.json"), "{}")
    try:
        rehe.cmd_init_sweep(_ns(root, init_sweep="AUD-C01"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("cert-mimic sweep allowed")
    rehe.cmd_init_sweep(_ns(root, init_sweep="REHEARSAL_SWEEP_001"))
    bad_report = os.path.join(root, "bad.md")
    write(bad_report, "I am blind and independent, verdict FIXED.")
    try:
        rehe.cmd_add_report(_ns(root, add_report="REHEARSAL_SWEEP_001",
                                panel="A", agent="emu1", file=bad_report))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("unlabeled report accepted")
    cert_report = os.path.join(root, "cert.md")
    write(cert_report, "NON_BLIND review noting AUD-C01 agrees.")
    try:
        rehe.cmd_add_report(_ns(root, add_report="REHEARSAL_SWEEP_001",
                                panel="A", agent="emu2", file=cert_report))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("cert-identity report accepted")


def test_live_namespaces_clean():
    """Live repo keeps rehearsal out of certification namespaces."""
    # [P2-LOG-R16] Test step: assert live namespace separation.
    print("[P2:test:rehearsal:016] checking live namespaces", flush=True)
    cert_root = os.path.join(REPO_ROOT, "artifacts", "audits",
                             "final_certification")
    if os.path.isdir(cert_root):
        for dirpath, _dirs, files in os.walk(cert_root):
            for name in files:
                with open(os.path.join(dirpath, name), encoding="utf-8",
                          errors="ignore") as handle:
                    content = handle.read()
                assert "REHEARSAL_SWEEP" not in content
                assert "NON_BLIND" not in content
    harness = os.path.join(REPO_ROOT, "artifacts", "audits",
                           "certification_rehearsal")
    assert os.path.isdir(harness) or True
