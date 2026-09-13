"""Phase-5 cost-robustness tests (R03-R05, control 5.8).

Finite entries rescale, E-freezes stay INF, structural class invariant.
Judged against the sealed structural expectation (never vs primary K
as a fitted target; primary K is the rescaled reference only).
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "pc"))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

AUDITS = os.path.join(REPO_ROOT, "artifacts", "audits")


def load_json(path):
    """Load a JSON document."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_cost_sweep_rescale_and_invariance():
    """R03-R05: 0.5/2/10 rescale finite, INF stable, class invariant."""
    # [P5-LOG-T30] Test step: assert cost-sweep invariance.
    print("[P5:test:cost:030] cost sweep", flush=True)
    doc = load_json(os.path.join(AUDITS, "cost_sweep.json"))
    assert doc["control"] == "5.8"
    assert doc["pass"] is True
    with open(os.path.join(REPO_ROOT, "prereg", "execution_inputs.json"),
              encoding="utf-8") as handle:
        order = json.load(handle)["freeze_order"]
    assert order == ["F000", "F100", "F010", "F001",
                     "F110", "F101", "F011", "F111"]
    for cost_str in ("0.5", "2", "10"):
        entry = doc["costs"][cost_str]
        assert entry["pass"] is True, cost_str
        assert entry["dual_agreement"] is True, cost_str
        assert entry["class"] == "STRUCTURAL_E_TOUCH_DEPENDENCE", cost_str
        kappa = entry["kappa"]
        assert len(kappa) == 8, cost_str
        for name, val in zip(order, kappa):
            if name[1] == "1":  # E frozen
                assert val == "INF", (cost_str, name, val)
            else:
                assert float(val) == float(cost_str), (cost_str, name, val)


def test_cost_sweep_dual_agreement_independent():
    """Dual solvers agree at every swept cost (computational check)."""
    # [P5-LOG-T32] Test step: assert swept dual agreement.
    print("[P5:test:cost:032] swept dual agreement", flush=True)
    import solve_freezes as primary
    import independent_solver as independent
    import tempfile
    import shutil
    contract = load_json(os.path.join(
        REPO_ROOT, "artifacts", "contracts",
        "pc_xacml_primary.contract.json"))
    touch_map = load_json(os.path.join(
        REPO_ROOT, "artifacts", "contracts", "touch.json"))
    inputs = load_json(os.path.join(
        REPO_ROOT, "prereg", "execution_inputs.json"))
    action_id = sorted(contract["actions"].keys())[0]
    for cost in (0.5, 2, 10):
        tmp = tempfile.mkdtemp(prefix="pc-cost-test-")
        try:
            import copy
            mod = copy.deepcopy(contract)
            mod["costs"] = {action_id: cost}
            mod["actions"][action_id]["cost"] = cost
            c_path = os.path.join(tmp, "c.json")
            t_path = os.path.join(tmp, "t.json")
            i_path = os.path.join(tmp, "i.json")
            for p, d in ((c_path, mod), (t_path, touch_map),
                         (i_path, inputs)):
                with open(p, "w", encoding="utf-8", newline="\n") as h:
                    json.dump(d, h, indent=2, sort_keys=True)
                    h.write("\n")
            p_out = os.path.join(tmp, "p")
            i_out = os.path.join(tmp, "i")
            primary.main(["solve_freezes.py", c_path, t_path, i_path,
                          p_out])
            independent.main(["independent_solver.py", c_path, t_path,
                              i_path, i_out])
            with open(os.path.join(p_out, "K_table.json"),
                      encoding="utf-8") as h:
                pk = json.load(h)["kappa"]
            with open(os.path.join(i_out, "K_table.json"),
                      encoding="utf-8") as h:
                ik = json.load(h)["kappa"]
            assert pk == ik, (cost, pk, ik)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
