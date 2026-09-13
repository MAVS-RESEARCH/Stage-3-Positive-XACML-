"""Phase-4 all-freeze tests (F000-F111 + dual-solver agreement).

Builds minimal spec-conformant fixture contracts in tmp dirs (never
depending on the parallel Phase-3 outputs), proves the primary solver
yields the preregistered structural geometry, proves the independent
solver agrees on every coordinate, checks identifier-only removal
(INV-12/13), freeze-order fidelity, hash embedding, nontriviality, and
sealed-output isolation. Integrates against the real artifacts when
present as a reported comparison only (never as solver input).
"""
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "pc"))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import solve_freezes as primary  # noqa: E402
import independent_solver as independent  # noqa: E402

ACTION = "q_supply_missing_attribute"
SEALED_ORDER = ["F000", "F100", "F010", "F001",
                "F110", "F101", "F011", "F111"]
SEALED_K = [1, "INF", 1, 1, "INF", "INF", 1, "INF"]


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fixture_contract(action=ACTION, cost=1):
    """Build a minimal spec-conformant single-action contract."""
    return {
        "contract_id": "pc-xacml-s3plus-primary",
        "worlds": ["x_permit", "x_nonpermit"],
        "initial_checkpoint": "S0",
        "target": {"x_permit": "Permit",
                   "x_nonpermit": "NotApplicable"},
        "H": {"S0": "H_initial", "S_permit": "H_permit",
              "S_nonpermit": "H_nonpermit"},
        "PR": {"relation_id": "PC-XACML-S3PLUS-v1-PR"},
        "Lambda": {"lambda_id": "PC-XACML-S3PLUS-v1-Lambda"},
        "omega": {"classes": ["Decision", "StatusCode",
                              "StatusDetail"]},
        "actions": {action: {"boundary": "xacml-request-transaction"}},
        "successors": {action: {"x_permit": "S_permit",
                                "x_nonpermit": "S_nonpermit"}},
        "costs": {action: cost},
        "atomicity": {action: {
            "atom_id": "xacml-request-transaction",
            "decomposable_in_primary_interface": False}},
        "provenance": {"execution_inputs":
                       "prereg/execution_inputs.json"},
        "checkpoints": {"S0": {"open": True},
                        "S_permit": {"open": False},
                        "S_nonpermit": {"open": False}},
    }


def write_json(path, doc):
    """Write deterministic JSON with LF newlines."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_both(tmp_path, touch_map, contract=None):
    """Run both solvers on a fixture; return primary/independent dirs."""
    # [P4-LOG-T10] Test helper: fixture run for both solvers.
    contract = contract if contract is not None else fixture_contract()
    c_path = os.path.join(str(tmp_path), "contract.json")
    t_path = os.path.join(str(tmp_path), "touch.json")
    write_json(c_path, contract)
    write_json(t_path, touch_map)
    inputs = os.path.join(REPO_ROOT, "prereg", "execution_inputs.json")
    p_out = os.path.join(str(tmp_path), "primary")
    i_out = os.path.join(str(tmp_path), "independent")
    primary.main(["solve_freezes.py", c_path, t_path, inputs, p_out])
    independent.main(["independent_solver.py", c_path, t_path,
                      inputs, i_out])
    return p_out, i_out, c_path


def load_rows(out_dir):
    """Load the eight rows plus table in freeze order."""
    with open(os.path.join(REPO_ROOT, "prereg",
                           "execution_inputs.json"),
              encoding="utf-8") as handle:
        order = json.load(handle)["freeze_order"]
    rows = []
    for name in order:
        with open(os.path.join(out_dir, "%s.json" % name),
                  encoding="utf-8") as handle:
            rows.append(json.load(handle))
    with open(os.path.join(out_dir, "K_table.json"),
              encoding="utf-8") as handle:
        table = json.load(handle)
    return rows, table, order


def test_fixture_yields_preregistered_geometry(tmp_path):
    """Primary solver yields the structural E-dependence signature."""
    # [P4-LOG-T20] Test step: assert fixture K geometry.
    print("[P4:test:freezes:020] fixture geometry", flush=True)
    p_out, _i_out, c_path = run_both(
        tmp_path, {ACTION: ["E"]})
    rows, table, order = load_rows(p_out)
    assert order == SEALED_ORDER
    assert table["freeze_order"] == SEALED_ORDER
    assert table["kappa"] == SEALED_K, table["kappa"]
    assert [r["kappa"] for r in rows] == SEALED_K
    for row, name in zip(rows, order):
        assert row["freeze"] == name
        assert row["solver"] == "primary"
        assert row["contract_sha256"] == sha256_file(c_path)
        assert row["kappa"] in (1, "INF") or (
            isinstance(row["kappa"], float) and row["kappa"] > 0)
        assert isinstance(row["proper_closer_exists"], bool)
        assert (row["proper_closer_exists"]
                == (row["kappa"] != "INF"))
        assert sorted(row["removed_actions"]
                      + row["surviving_actions"]) == [ACTION]
    # E-freezes remove the sole action; others keep it.
    by_name = {r["freeze"]: r for r in rows}
    for name in ("F100", "F110", "F101", "F111"):
        assert by_name[name]["removed_actions"] == [ACTION]
        assert by_name[name]["surviving_actions"] == []
        assert by_name[name]["kappa"] == "INF"
    for name in ("F000", "F010", "F001", "F011"):
        assert by_name[name]["removed_actions"] == []
        assert by_name[name]["surviving_actions"] == [ACTION]
        assert by_name[name]["kappa"] == 1


def test_independent_agrees_on_fixture(tmp_path):
    """Dual solvers agree on set, closer, cost, all coordinates."""
    # [P4-LOG-T22] Test step: assert dual-solver agreement.
    print("[P4:test:freezes:022] dual agreement", flush=True)
    p_out, i_out, _c = run_both(tmp_path, {ACTION: ["E"]})
    p_rows, p_table, order = load_rows(p_out)
    i_rows, i_table, _o2 = load_rows(i_out)
    assert p_table["kappa"] == i_table["kappa"] == SEALED_K
    assert p_table["freeze_order"] == i_table["freeze_order"]
    assert p_table["contract_sha256"] == i_table["contract_sha256"]
    for prow, irow in zip(p_rows, i_rows):
        assert prow["freeze"] == irow["freeze"]
        assert prow["frozen_resources"] == irow["frozen_resources"]
        assert prow["removed_actions"] == irow["removed_actions"]
        assert prow["surviving_actions"] == irow["surviving_actions"]
        assert (prow["proper_closer_exists"]
                == irow["proper_closer_exists"])
        assert prow["kappa"] == irow["kappa"]
        assert prow["worst_branch_cost"] == irow["worst_branch_cost"]


def test_variant_touch_still_agrees(tmp_path):
    """Generic enumeration: agreement holds beyond the E-only case."""
    # [P4-LOG-T24] Test step: assert generic (non-hardcoded) search.
    print("[P4:test:freezes:024] variant touch agreement", flush=True)
    p_out, i_out, _c = run_both(tmp_path, {ACTION: ["R"]})
    _p_rows, p_table, _o = load_rows(p_out)
    _i_rows, i_table, _o2 = load_rows(i_out)
    want = [1, 1, "INF", 1, "INF", 1, "INF", "INF"]
    assert p_table["kappa"] == want, p_table["kappa"]
    assert i_table["kappa"] == want, i_table["kappa"]


def test_no_partial_fabrication_and_exhaustive(tmp_path):
    """INV-12/13: identifier-only ops; itertools, no sampling."""
    # [P4-LOG-T26] Test step: assert no fabrication + enumeration.
    print("[P4:test:freezes:026] fabrication/enumeration", flush=True)
    p_out, _i, _c = run_both(tmp_path, {ACTION: ["E"]})
    rows, _t, _o = load_rows(p_out)
    for row in rows:
        universe = sorted(row["removed_actions"]
                          + row["surviving_actions"])
        assert universe == [ACTION] or universe == []
        for ident in row["removed_actions"] + row["surviving_actions"]:
            assert "/" not in ident and "+" not in ident
    for rel in ("src/pc/solve_freezes.py",
                "src/audit/independent_solver.py"):
        with open(os.path.join(REPO_ROOT, rel),
                  encoding="utf-8") as handle:
            src = handle.read()
        assert "itertools" in src, rel
        assert "import random" not in src, rel
        assert "random.sample" not in src, rel


def test_solver_isolation_from_sealed_outputs():
    """Solvers never open sealed output files; no hardcoded mapping."""
    # [P4-LOG-T28] Test step: assert sealed-output isolation.
    print("[P4:test:freezes:028] solver isolation", flush=True)
    for rel in ("src/pc/solve_freezes.py",
                "src/audit/independent_solver.py"):
        with open(os.path.join(REPO_ROOT, rel),
                  encoding="utf-8") as handle:
            content = handle.read()
        code_lines = [ln.split("#", 1)[0] for ln in
                      content.splitlines()]
        code = "\n".join(code_lines)
        for token in ("expected_signature", "canary_expectations",
                      "expected_K", "expected_touch"):
            assert token not in code, (rel, token)
        import re
        assert not re.search(
            r"open\s*\([^)]*expected_signature", code), rel
        # No hardcoded action-specific touch preassignment.
        assert "q_supply" not in code, rel


def test_independent_has_separate_search_code():
    """Independent solver shares no search code with the primary."""
    # [P4-LOG-T30] Test step: assert search-code separation.
    print("[P4:test:freezes:030] search separation", flush=True)
    with open(os.path.join(REPO_ROOT, "src", "audit",
                           "independent_solver.py"),
              encoding="utf-8") as handle:
        indep = handle.read()
    assert "solve_freezes" not in indep
    assert "from pc" not in indep and "import solve_freezes" not in indep
    with open(os.path.join(REPO_ROOT, "src", "pc",
                           "solve_freezes.py"),
              encoding="utf-8") as handle:
        prim = handle.read()
    # Distinct enumeration shapes: combinations vs product.
    assert "combinations" in prim
    assert "product" in indep


def test_freeze_order_hash_and_nontriviality(tmp_path):
    """Order fidelity, hash embedding, nontrivial signature."""
    # [P4-LOG-T32] Test step: assert order/hash/nontriviality.
    print("[P4:test:freezes:032] order/hash/nontrivial", flush=True)
    p_out, _i, c_path = run_both(tmp_path, {ACTION: ["E"]})
    rows, table, order = load_rows(p_out)
    with open(os.path.join(REPO_ROOT, "prereg",
                           "execution_inputs.json"),
              encoding="utf-8") as handle:
        sealed_order = json.load(handle)["freeze_order"]
    assert order == sealed_order == SEALED_ORDER
    want_hash = sha256_file(c_path)
    for row in rows:
        assert row["contract_sha256"] == want_hash
    assert table["contract_sha256"] == want_hash
    assert table["nontrivial"] is True
    assert any(k != table["kappa"][0]
               for k in table["kappa"][1:])


def test_k_reported_vs_sealed_as_comparison(tmp_path):
    """Observed K reported against the sealed value (never an input)."""
    # [P4-LOG-T34] Test step: reported comparison only.
    print("[P4:test:freezes:034] sealed comparison", flush=True)
    p_out, _i, _c = run_both(tmp_path, {ACTION: ["E"]})
    _rows, table, _o = load_rows(p_out)
    with open(os.path.join(REPO_ROOT, "prereg",
                           "expected_signature.json"),
              encoding="utf-8") as handle:
        sealed = json.load(handle)["expected_K"]
    # Honest report: mismatch would fail here openly, never overwrite.
    assert table["kappa"] == sealed, (table["kappa"], sealed)


def test_real_artifacts_comparison_if_present():
    """Integrate against real artifacts when present (comparison)."""
    # [P4-LOG-T36] Test step: real-artifact integration if present.
    print("[P4:test:freezes:036] real artifacts if present", flush=True)
    k_path = os.path.join(REPO_ROOT, "artifacts", "freezes",
                          "K_table.json")
    if not os.path.isfile(k_path):
        print("[P4:test:freezes:037] no real K_table, fixture-covered",
              flush=True)
        return
    with open(k_path, encoding="utf-8") as handle:
        real = json.load(handle)
    assert real["freeze_order"] == SEALED_ORDER
    assert len(real["kappa"]) == 8
    with open(os.path.join(REPO_ROOT, "prereg",
                           "expected_signature.json"),
              encoding="utf-8") as handle:
        sealed = json.load(handle)["expected_K"]
    print("[P4:test:freezes:038] real K=%s sealed=%s"
          % (real["kappa"], sealed), flush=True)
    assert real["kappa"] == sealed, (real["kappa"], sealed)
    for name in SEALED_ORDER:
        with open(os.path.join(REPO_ROOT, "artifacts", "freezes",
                               "%s.json" % name),
                  encoding="utf-8") as handle:
            row = json.load(handle)
        assert row["freeze"] == name
        assert row["contract_sha256"] == real["contract_sha256"]
    c_path = os.path.join(REPO_ROOT, "artifacts", "contracts",
                          "pc_xacml_primary.contract.json")
    if os.path.isfile(c_path):
        assert real["contract_sha256"] == sha256_file(c_path)
