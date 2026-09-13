"""Phase-5 interface tests (R01-R02, controls 5.6-5.7).

R01: whitespace/order/rename preserve H/P_R/Lambda/T/K.
R02: split interface refuses T3 invariance (INTERFACE_CHANGED).
"""
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDITS = os.path.join(REPO_ROOT, "artifacts", "audits")


def load_json(path):
    """Load a JSON document."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_preserving_perturbations_hold():
    """R01: all preserving variants keep H/P_R/Lambda/T/K."""
    # [P5-LOG-T40] Test step: assert preservation.
    print("[P5:test:iface:040] preserving perturbations", flush=True)
    for variant in ("whitespace", "order", "rename"):
        path = os.path.join(AUDITS, "perturbation_%s.json" % variant)
        assert os.path.isfile(path), variant
        doc = load_json(path)
        assert doc["control"] == "5.6", variant
        assert doc["h_equal"] is True, variant
        assert doc["pr_equal"] is True, variant
        assert doc["lambda_equal"] is True, variant
        assert doc["pdp_decision_equal"] is True, variant
        assert doc["touch_equal"] is True, variant
        assert doc["k_equal"] is True, variant
        assert doc["frozen_external_untouched"] is True
    # Rename additionally proves path relocation with ref update.
    rename = load_json(os.path.join(AUDITS, "perturbation_rename.json"))
    assert rename.get("relocated_equal", True) is True


def test_interface_change_refuses_t3():
    """R02: split interface is OUT_OF_SCOPE, never a T3 claim."""
    # [P5-LOG-T42] Test step: assert interface-change refusal.
    print("[P5:test:iface:042] interface-change control", flush=True)
    for name in ("perturbation_interface_change.json",
                 "interface_change.json"):
        path = os.path.join(AUDITS, name)
        assert os.path.isfile(path), name
        doc = load_json(path)
        assert doc["control"] == "5.7", name
        assert doc["variant"] == "OUT_OF_SCOPE_INTERFACE_CHANGE"
        assert doc["audit_verdict"] == "INTERFACE_CHANGED"
        assert doc["theorem3"] == "THEOREM3_INVARIANCE_NOT_APPLICABLE"
        assert doc["is_t3_claim"] is False
