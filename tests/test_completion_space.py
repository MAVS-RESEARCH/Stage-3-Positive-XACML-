"""Phase-4 completion-space certificate tests.

Verifies the machine-checked closure certificate over the thirteen
K-relevant fields with per-row constraint source plus artifact-hash
evidence and a zero-free gate for cardinality 1. Fixture ledgers and
tables prove the checker logic in isolation; the live repo certificate
is integrated when present. The checker never opens sealed outputs;
only these tests compare the observed signature against the sealed
value as a reported comparison.
"""
import hashlib
import json
import os
import shutil
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "pc"))

import check_completion_space as checker  # noqa: E402

FIELDS = ["X", "U_H", "S", "H", "P_R", "Lambda", "omega", "Q",
          "Succ+", "c", "A_Pi", "Atom", "Y"]


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, doc):
    """Write deterministic JSON with LF newlines."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")


def fixture_contract_touch(tmp_path):
    """Write a minimal fixture contract+touch; return their paths."""
    action = "q_supply_missing_attribute"
    contract = {
        "contract_id": "pc-xacml-s3plus-primary",
        "worlds": ["x_permit", "x_nonpermit"],
        "initial_checkpoint": "S0",
        "target": {"x_permit": "Permit",
                   "x_nonpermit": "NotApplicable"},
        "H": {"S0": "H_initial"},
        "PR": {"relation_id": "PC-XACML-S3PLUS-v1-PR"},
        "Lambda": {"lambda_id": "PC-XACML-S3PLUS-v1-Lambda"},
        "omega": {"classes": ["Decision"]},
        "actions": {action: {"boundary": "native"}},
        "successors": {action: {"x_permit": "S_permit",
                                "x_nonpermit": "S_nonpermit"}},
        "costs": {action: 1},
        "atomicity": {action: {}},
        "provenance": {},
        "checkpoints": {"S0": {"open": True},
                        "S_permit": {"open": False},
                        "S_nonpermit": {"open": False}},
    }
    c_path = os.path.join(str(tmp_path), "contract.json")
    write_json(c_path, contract)
    return c_path


def make_overlay_repo(tmp_path, ledger_mutator=None):
    """Build a tmp repo overlay reusing sealed derived evidence.

    Copies the minimum live evidence tree (execution inputs, H set,
    proofs, requests, manifest, raw response) so the checker runs in
    isolation; the ledger may be mutated to simulate ablation.
    """
    # [P4-LOG-T50] Test helper: overlay repo for isolation.
    root = os.path.join(str(tmp_path), "overlay")
    for rel in ("prereg/execution_inputs.json",
                "derived/H_initial.json",
                "derived/H_permit.json",
                "derived/H_nonpermit.json",
                "derived/h_equivalence_proof.json",
                "derived/policy_adequacy_certificate.json",
                "derived/policy_projection.json",
                "derived/pr_relation.json",
                "derived/lambda_record.json",
                "derived/atom_record.json",
                "derived/requests/request_x_permit.xml",
                "derived/requests/request_x_nonpermit.xml",
                "external/MANIFEST.json",
                "artifacts/raw/original_response_actual.xml"):
        src = os.path.join(REPO_ROOT, *rel.split("/"))
        dst = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    with open(os.path.join(REPO_ROOT, "derived", "anchor_ledger.json"),
              encoding="utf-8") as handle:
        ledger = json.load(handle)
    if ledger_mutator is not None:
        ledger_mutator(ledger)
    write_json(os.path.join(root, "derived", "anchor_ledger.json"),
               ledger)
    return root


def write_ktable(path, contract_path, kappa):
    """Write a K_table matching the sealed freeze order."""
    with open(os.path.join(REPO_ROOT, "prereg",
                           "execution_inputs.json"),
              encoding="utf-8") as handle:
        order = json.load(handle)["freeze_order"]
    with open(contract_path, encoding="utf-8") as handle:
        contract = json.load(handle)
    write_json(path, {
        "experiment_id": "PC-XACML-S3PLUS-v1",
        "contract_id": contract.get("contract_id", ""),
        "contract_sha256": sha256_file(contract_path),
        "freeze_order": order,
        "kappa": list(kappa),
        "nontrivial": any(v != kappa[0] for v in kappa[1:]),
        "solver": "primary",
        "produced_utc": "2026-01-01T00:00:00Z",
    })


def run_checker(repo_root, contract_path, ktable_path, tmp_path,
                name="cert"):
    """Invoke the checker; return (exit_code, cert, ident_path)."""
    cert = os.path.join(str(tmp_path), "%s.json" % name)
    ident = os.path.join(str(tmp_path), "%s_ident.json" % name)
    try:
        checker.main(["check_completion_space.py", repo_root,
                      contract_path, ktable_path, cert, ident])
    except SystemExit as exc:
        code = exc.code
    else:
        raise AssertionError("checker did not exit")
    doc = None
    if os.path.isfile(cert):
        with open(cert, encoding="utf-8") as handle:
            doc = json.load(handle)
    return code, doc, ident


def test_certificate_passes_on_complete_overlay(tmp_path):
    """Zero-free certificate authorizes cardinality 1 from observed K."""
    # [P4-LOG-T52] Test step: assert complete-overlay pass.
    print("[P4:test:complete:052] complete overlay", flush=True)
    root = make_overlay_repo(tmp_path)
    c_path = fixture_contract_touch(tmp_path)
    # Trim to the canonical single-action geometry for agreement with
    # the sealed K shape used below.
    with open(c_path, encoding="utf-8") as handle:
        contract = json.load(handle)
    keep = sorted(contract["actions"].keys())[0]
    for field in ("actions", "successors", "costs", "atomicity"):
        contract[field] = {keep: contract[field][keep]}
    write_json(c_path, contract)
    kappa = [1, "INF", 1, 1, "INF", "INF", 1, "INF"]
    k_path = os.path.join(str(tmp_path), "K_table.json")
    write_ktable(k_path, c_path, kappa)
    code, doc, ident_path = run_checker(root, c_path, k_path,
                                        tmp_path)
    assert code == 0, doc
    assert doc["free_k_relevant_fields"] == 0
    assert doc["verdict"] == "COMPLETE"
    assert [r["pc_field"] for r in doc["rows"]] == FIELDS
    for row in doc["rows"]:
        assert row["source_constraint"].strip() != ""
        assert isinstance(row["evidence"], dict)
        assert len(row["evidence"]) >= 1
        assert row["free_after_audit"] is False
        for _artifact, digest in row["evidence"].items():
            if digest != "MISSING":
                assert len(digest) == 64
    assert doc["nontrivial"] is True
    assert os.path.isfile(ident_path)
    with open(ident_path, encoding="utf-8") as handle:
        ident = json.load(handle)
    assert ident["identified_set_cardinality"] == 1
    assert ident["signature"] == kappa
    assert ident["contract_sha256"] == sha256_file(c_path)


def test_certificate_refuses_on_ablated_anchor(tmp_path):
    """Any non-constrained row blocks cardinality 1."""
    # [P4-LOG-T54] Test step: assert ablation refusal.
    print("[P4:test:complete:054] ablation refusal", flush=True)
    def ablate(ledger):
        ledger["anchors"]["H"]["ambiguity_status"] = "AMBIGUOUS"
    root = make_overlay_repo(tmp_path, ledger_mutator=ablate)
    c_path = fixture_contract_touch(tmp_path)
    with open(c_path, encoding="utf-8") as handle:
        contract = json.load(handle)
    keep = sorted(contract["actions"].keys())[0]
    for field in ("actions", "successors", "costs", "atomicity"):
        contract[field] = {keep: contract[field][keep]}
    write_json(c_path, contract)
    k_path = os.path.join(str(tmp_path), "K_table.json")
    write_ktable(k_path, c_path,
                 [1, "INF", 1, 1, "INF", "INF", 1, "INF"])
    code, doc, ident_path = run_checker(root, c_path, k_path,
                                        tmp_path, name="abl")
    assert code == 2, code
    assert doc["free_k_relevant_fields"] >= 1
    assert doc["verdict"] == "INCOMPLETE"
    assert not os.path.isfile(ident_path)


def test_checker_isolation_from_sealed_outputs():
    """Checker never opens sealed output files."""
    # [P4-LOG-T56] Test step: assert checker isolation.
    print("[P4:test:complete:056] checker isolation", flush=True)
    with open(os.path.join(REPO_ROOT, "src", "pc",
                           "check_completion_space.py"),
              encoding="utf-8") as handle:
        content = handle.read()
    code = "\n".join(ln.split("#", 1)[0] for ln in
                     content.splitlines())
    for token in ("expected_signature", "canary_expectations",
                  "expected_K", "expected_touch"):
        assert token not in code, token
    import re
    assert not re.search(r"open\s*\([^)]*expected_signature",
                         code)


def test_live_certificate_schema_if_present():
    """Live certificate (if present) validates and gates correctly."""
    # [P4-LOG-T58] Test step: live-certificate integration if present.
    print("[P4:test:complete:058] live certificate if present",
          flush=True)
    c_path = os.path.join(REPO_ROOT, "artifacts", "seal",
                          "completion_space_certificate.json")
    if not os.path.isfile(c_path):
        print("[P4:test:complete:059] no live certificate yet",
              flush=True)
        return
    with open(os.path.join(REPO_ROOT, "schemas",
                           "completion_space.schema.json"),
              encoding="utf-8") as handle:
        schema = json.load(handle)
    with open(c_path, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert doc["certificate_id"] == schema["properties"][
        "certificate_id"]["const"]
    assert [r["pc_field"] for r in doc["rows"]] == FIELDS
    assert doc["free_k_relevant_fields"] == sum(
        1 for r in doc["rows"] if r["free_after_audit"])
    if doc["verdict"] == "COMPLETE":
        assert doc["free_k_relevant_fields"] == 0
        i_path = os.path.join(REPO_ROOT, "artifacts", "freezes",
                              "identified_set.json")
        assert os.path.isfile(i_path)
        with open(i_path, encoding="utf-8") as handle:
            ident = json.load(handle)
        assert ident["identified_set_cardinality"] == 1
        k_path = os.path.join(REPO_ROOT, "artifacts", "freezes",
                              "K_table.json")
        with open(k_path, encoding="utf-8") as handle:
            ktable = json.load(handle)
        assert ident["signature"] == ktable["kappa"]
        with open(os.path.join(REPO_ROOT, "prereg",
                               "expected_signature.json"),
                  encoding="utf-8") as handle:
            sealed = json.load(handle)["expected_K"]
        print("[P4:test:complete:060] live K=%s sealed=%s"
              % (ktable["kappa"], sealed), flush=True)
        assert ktable["kappa"] == sealed
    else:
        assert doc["free_k_relevant_fields"] > 0
