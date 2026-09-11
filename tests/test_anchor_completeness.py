"""Phase-2 anchor-completeness tests (A01-A04 + gate semantics).

Asserts the ledger carries all nine anchors with the required states
(four critical FIXED + PENDING_2B, envelope FIXED), the H objects are
non-empty, and the checker exit semantics hold: exit 4 while the blind
verdict is absent (blocked, current state), non-zero on anchor ablation
in an isolated copy.
"""
import json
import os
import shutil
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "pc"))

import check_anchor_completeness as checker  # noqa: E402


def load_ledger():
    """Load the assembled anchor ledger."""
    # [P2-LOG-T30] Test step: load the ledger once per check.
    print("[P2:test:completeness:030] loading anchor ledger", flush=True)
    with open(os.path.join(REPO_ROOT, "derived", "anchor_ledger.json"),
              encoding="utf-8") as handle:
        return json.load(handle)


def test_ledger_states():
    """A01-A04: critical anchors FIXED/PENDING_2B, envelope FIXED."""
    # [P2-LOG-T32] Test step: assert ledger anchor states.
    print("[P2:test:completeness:032] checking ledger states", flush=True)
    anchors = load_ledger()["anchors"]
    for name in ("H", "P_R", "Lambda", "Atom", "omega", "Q", "Succ+",
                 "c", "A_Pi"):
        assert name in anchors, name
        assert anchors[name]["ambiguity_status"] == "FIXED", name
        assert anchors[name]["manual_semantic_choice_required"] is False
    for name in ("H", "P_R", "Lambda", "Atom"):
        assert anchors[name]["auditor_status"] == "PENDING_2B", name
        assert set(anchors[name]["source_class"]) & {"N1", "N2", "N3"}, name
    for checkpoint in ("H_initial", "H_permit", "H_nonpermit"):
        with open(os.path.join(REPO_ROOT, "derived",
                               "%s.json" % checkpoint),
                  encoding="utf-8") as handle:
            assert json.load(handle)["attributes"]


def test_checker_blocked_without_verdict():
    """Checker exits 4 (blocked) while the blind verdict is absent."""
    # [P2-LOG-T34] Test step: assert blocked exit semantics.
    print("[P2:test:completeness:034] checking blocked exit code",
          flush=True)
    verdict = os.path.join(REPO_ROOT, "artifacts", "audits",
                           "blind_anchor_verdict.json")
    if os.path.isfile(verdict):
        print("[P2:test:completeness:035] verdict present, expecting 0",
              flush=True)
        want = 0
    else:
        want = 4
    try:
        checker.main(["check_anchor_completeness.py", REPO_ROOT,
                      os.path.join(REPO_ROOT, "derived")])
    except SystemExit as exc:
        assert exc.code == want, exc.code
    else:
        raise AssertionError("checker did not exit")


def test_checker_refuses_ablation(tmp_path):
    """Checker refuses a ledger with one anchor record removed."""
    # [P2-LOG-T36] Test step: assert ablation refusal in isolation.
    print("[P2:test:completeness:036] checking ablation refusal",
          flush=True)
    fake_root = tmp_path / "root"
    fake_derived = fake_root / "derived"
    shutil.copytree(os.path.join(REPO_ROOT, "derived"), str(fake_derived))
    os.remove(str(fake_derived / "lambda_record.json"))
    (fake_root / "external").mkdir(parents=True)
    shutil.copyfile(os.path.join(REPO_ROOT, "external", "MANIFEST.json"),
                    str(fake_root / "external" / "MANIFEST.json"))
    (fake_root / "prereg").mkdir()
    shutil.copyfile(os.path.join(REPO_ROOT, "prereg",
                                 "execution_inputs.json"),
                    str(fake_root / "prereg" / "execution_inputs.json"))
    raw_dir = fake_root / "artifacts" / "raw"
    raw_dir.mkdir(parents=True)
    shutil.copyfile(os.path.join(REPO_ROOT, "artifacts", "raw",
                                 "original_response_actual.xml"),
                    str(raw_dir / "original_response_actual.xml"))
    try:
        checker.main(["check_anchor_completeness.py", str(fake_root),
                      str(fake_derived)])
    except SystemExit as exc:
        assert exc.code != 0, exc.code
    else:
        raise AssertionError("ablated ledger was accepted")
