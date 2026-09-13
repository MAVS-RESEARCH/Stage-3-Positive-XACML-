"""Phase-2B-H hardening machinery tests.

Covers objection-ledger operations, invariant/exec-scan units,
round-seal artifacts, freeze guard/reopen flows, and namespace
protection. Synthetic temporary roots isolate destructive cases; the
live repository is only read, except one throwaway-round integration
case that restores state.
"""
import json
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import hardening  # noqa: E402
import objection_ledger as ledger_mod  # noqa: E402

AUDIT_DIR = os.path.join(REPO_ROOT, "artifacts", "audits")
HARDENING = os.path.join(AUDIT_DIR, "semantic_hardening")


def write_json(path, doc):
    """Write a JSON document, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")


def test_ledger_verify_live():
    """Live objection ledger is structurally valid."""
    # [P2-LOG-H10] Test step: assert live ledger validity.
    print("[P2:test:hardening:010] checking live ledger", flush=True)
    with open(os.path.join(HARDENING, "objection_ledger.json"),
              encoding="utf-8") as handle:
        ledger = json.load(handle)
    assert len(ledger["objections"]) >= 61
    assert sum(1 for o in ledger["objections"]
               if o["resolution_status"] == "OPEN") == 0


def test_ledger_rejects_bad_records(tmp_path):
    """Ledger checker refuses malformed/unsafe records."""
    # [P2-LOG-H12] Test step: assert ledger refusal paths.
    print("[P2:test:hardening:012] checking ledger refusals", flush=True)
    base = {"objection_id": "X-01", "round_id": "R",
            "anchor": "H", "originating_reviewer": "t",
            "objection": "o", "locators": ["l"], "category": "A",
            "materiality": "Material", "resolution_status": "OPEN"}
    assert ledger_mod.check_record(dict(base)) == []
    bad_category = dict(base, category="Z")
    assert ledger_mod.check_record(bad_category) != []
    external_change = dict(base, external_semantics_changed=True)
    assert ledger_mod.check_record(external_change) != []
    downstream_use = dict(base, downstream_result_info_used=True)
    assert ledger_mod.check_record(downstream_use) != []
    missing_field = dict(base)
    del missing_field["locators"]
    assert ledger_mod.check_record(missing_field) != []
    unresolved_f = dict(base, category="F", resolution_status="RESOLVED")
    assert ledger_mod.check_record(unresolved_f) != []
    _ = tmp_path


def test_invariant_units(tmp_path):
    """Invariant passes on intact roots, fails on mutated ones."""
    # [P2-LOG-H14] Test step: assert invariant unit behavior.
    print("[P2:test:hardening:014] checking invariant units", flush=True)
    root = str(tmp_path / "inv")
    os.makedirs(os.path.join(root, "external", "authzforce", "fixture",
                             "policies"))
    os.makedirs(os.path.join(root, "prereg"))
    files = {
        "external/authzforce/fixture/pdp.xml": b"<pdp/>",
        "external/authzforce/fixture/request.xml": b"<request/>",
        "external/authzforce/fixture/response.xml": b"<response/>",
        "external/authzforce/fixture/policies/policy.xml": b"<policy/>",
        "external/xacml/x.html": b"spec-html",
        "IMPLEMENTATION_SPEC.md": b"spec",
        "prereg/experiment.yaml": b"expected_touch: [E]\nexpected_K: 1\n"
                                        b"unit_cost: 1\nfreeze_order: [F000]\n",
        "prereg/execution_inputs.json": b'{"worlds": 1, '
                                        b'"action_interface": 2, '
                                        b'"freeze_order": 3}',
    }
    for rel, data in files.items():
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
    import hashlib

    def sha(rel):
        with open(os.path.join(root, *rel.split("/")), "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()

    with open(os.path.join(root, "external", "MANIFEST.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump({
            "authzforce": {"fixture_files": {
                "pdp.xml": {"sha256": sha(
                    "external/authzforce/fixture/pdp.xml")},
                "request.xml": {"sha256": sha(
                    "external/authzforce/fixture/request.xml")},
                "response.xml": {"sha256": sha(
                    "external/authzforce/fixture/response.xml")},
                "policies/policy.xml": {"sha256": sha(
                    "external/authzforce/fixture/policies/"
                    "policy.xml")}}},
            "xacml": {"sha256": sha("external/xacml/x.html")},
            "implementation_spec": {
                "sha256_raw": sha("IMPLEMENTATION_SPEC.md")}}, handle)

    baseline = {
        "fixture_files": {
            "pdp.xml": sha("external/authzforce/fixture/pdp.xml"),
            "request.xml": sha(
                "external/authzforce/fixture/request.xml"),
            "response.xml": sha(
                "external/authzforce/fixture/response.xml"),
            "policies/policy.xml": sha(
                "external/authzforce/fixture/policies/policy.xml")},
        "xacml_sha256": sha("external/xacml/x.html"),
        "spec_raw": sha("IMPLEMENTATION_SPEC.md"),
        "execution_inputs": {"worlds": 1, "action_interface": 2,
                             "freeze_order": 3},
    }
    assert hardening.check_invariant_quiet(root, baseline) is True
    with open(os.path.join(
            root, "external/authzforce/fixture/pdp.xml"), "ab") as handle:
        handle.write(b"mutation")
    assert hardening.check_invariant_quiet(root, baseline) is False
    assert hardening.target_scan(root) == []
    os.makedirs(os.path.join(root, "artifacts", "raw"), exist_ok=True)
    with open(os.path.join(root, "artifacts", "raw", "target_x_actual.xml"),
              "wb") as handle:
        handle.write(b"x")
    assert hardening.target_scan(root) != []


def test_round_seal_artifacts():
    """Sealed ROUND_001 carries invariant, exec, and test evidence."""
    # [P2-LOG-H16] Test step: assert round-seal artifacts.
    print("[P2:test:hardening:016] checking round seal", flush=True)
    import pytest
    seal_path = os.path.join(
        HARDENING, "rounds", "HARDENING_ROUND_001", "round_seal.json")
    if not os.path.isfile(seal_path):
        pytest.skip("round not sealed yet")
    with open(seal_path, encoding="utf-8") as handle:
        seal = json.load(handle)
    assert seal["sealed"] is True
    assert seal["exec_count_at_seal"] == 0
    assert seal["baseline_snapshot"]["fixture_files"]
    with open(os.path.join(HARDENING, "STATE.json"),
              encoding="utf-8") as handle:
        state = json.load(handle)
    assert any(r["round_id"] == "HARDENING_ROUND_001" and r["sealed"]
               for r in state["rounds"])


def test_freeze_guard_and_reopen(tmp_path):
    """Frozen interface refuses mutation; reopen requires zero execs."""
    # [P2-LOG-H18] Test step: assert freeze guard and reopen flow.
    print("[P2:test:hardening:018] checking freeze guard", flush=True)
    root = str(tmp_path / "fz")
    hard = os.path.join(root, "artifacts", "audits",
                        "semantic_hardening")
    os.makedirs(hard)
    with open(os.path.join(hard, "STATE.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump({"phase2_state": "X", "rounds": [],
                   "freeze": {"valid": True}, "reopens": []}, handle)
    try:
        hardening.cmd_init_round(_ns(root, round="R1"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("mutation past freeze was allowed")
    os.makedirs(os.path.join(root, "artifacts", "raw"), exist_ok=True)
    with open(os.path.join(root, "artifacts", "raw",
                             "target_x.xml"), "wb") as handle:
        handle.write(b"x")
    try:
        hardening.cmd_reopen(_ns(root, reason="r", evidence="e"))
    except SystemExit:
        pass
    else:
        raise AssertionError("reopen with executions was allowed")
    os.remove(os.path.join(root, "artifacts", "raw", "target_x.xml"))
    hardening.cmd_reopen(_ns(root, reason="r", evidence="e"))
    with open(os.path.join(hard, "STATE.json"), encoding="utf-8") as handle:
        state = json.load(handle)
    assert state["freeze"]["superseded"] is True
    assert state["reopens"][0]["event"] == "SEMANTIC_FREEZE_REOPENED"


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, repo_root, **kwargs):
        self.repo_root = repo_root
        self.allow_frozen = False
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_namespace_protection(tmp_path):
    """NON_BLIND material cannot enter final-certification reads."""
    # [P2-LOG-H20] Test step: assert namespace protection.
    print("[P2:test:hardening:020] checking namespace protection",
          flush=True)
    with open(os.path.join(REPO_ROOT, "src", "audit",
                           "final_certification.py"),
              encoding="utf-8") as handle:
        final_src = handle.read()
    # NON_BLIND-adjacent literals are allowed only inside guard patterns
    # that REFUSE hardening/non-blind sources; the module must
    # never read hardening reports or blind packet candidates as verdict
    # inputs (it reads only freeze records, packet seal, prompt file,
    # and the final_certification/ chairs).
    hits = [line for line in final_src.splitlines() if "NON_BLIND" in line]
    assert len(hits) == 2, hits
    assert any("HARDENING_PATH" in line for line in hits)
    assert any('if "NON_BLIND" in text:' in line for line in hits)
    for forbidden in ("reports/non_blind", "semantic_hardening/reports",
                      "semantic_hardening/rounds", "dev_packets"):
        assert forbidden not in final_src, forbidden
    with open(os.path.join(REPO_ROOT, "src", "audit",
                           "model_adjudication.py"),
              encoding="utf-8") as handle:
        legacy_src = handle.read()
    assert "final_certification" not in legacy_src
    assert "semantic_hardening" not in legacy_src
    _ = tmp_path
