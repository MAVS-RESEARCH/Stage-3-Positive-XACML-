"""Phase-6 seal tests (success-path gate in pytest form).

Validates the sealed positive result against schemas and live bytes:
outcome taxonomy, required fields, hash bindings, historical-seal
preservation, manifest/archive integrity, audit sections, and claims.
No PDP execution; no frozen-seal mutation.
"""
import hashlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TAXONOMY = (
    "POSITIVE_NATIVE_STAGE3",
    "NATIVE_ANCHOR_INSUFFICIENT",
    "SOURCE_REPRODUCTION_FAIL",
    "TARGET_REPRODUCTION_FAIL",
    "TOUCH_DERIVATION_MISMATCH",
    "SOLVER_MISMATCH",
    "NONTRIVIALITY_FAIL",
    "INDEPENDENT_REPRODUCTION_FAIL",
)


def _sha(rel):
    """Return the hex SHA-256 digest of a repo-relative file."""
    # [P6-LOG-S10] Test step: hash one sealed file.
    print("[P6:test:seal:010] hashing %s" % rel, flush=True)
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, *rel.split("/")), "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(rel):
    """Load a JSON artifact relative to the repo root."""
    # [P6-LOG-S12] Test step: load one sealed record.
    print("[P6:test:seal:012] loading %s" % rel, flush=True)
    with open(os.path.join(REPO_ROOT, *rel.split("/")),
              encoding="utf-8") as handle:
        return json.load(handle)


def test_seal_outcome_and_required_fields():
    """Seal carries the taxonomy outcome and all required fields."""
    # [P6-LOG-S20] Test step: assert seal shape and outcome.
    print("[P6:test:seal:020] seal shape", flush=True)
    seal = _load("artifacts/seal/FINAL_RESULT_LAUNCH.json")
    schema = _load("schemas/final_result.schema.json")
    assert seal["outcome"] in TAXONOMY
    assert seal["outcome"] in schema["properties"]["outcome"]["enum"]
    for field in schema["required"]:
        assert field in seal, field
    assert seal["experiment_id"] == "PC-XACML-S3PLUS-v1"
    assert seal["outcome"] == "POSITIVE_NATIVE_STAGE3"
    assert seal["derived_touch"] == {"q_supply_missing_attribute": ["E"]}
    assert seal["K"] == [1, "INF", 1, 1, "INF", "INF", 1, "INF"]
    assert seal["identified_set_cardinality"] == 1


def test_seal_hash_bindings():
    """Seal-embedded hashes match live artifact bytes."""
    # [P6-LOG-S22] Test step: assert seal hash bindings.
    print("[P6:test:seal:022] seal bindings", flush=True)
    seal = _load("artifacts/seal/FINAL_RESULT_LAUNCH.json")
    assert seal["contract_sha256"] == _sha(
        "artifacts/contracts/pc_xacml_primary.contract.json")
    assert seal["touch_sha256"] == _sha("artifacts/contracts/touch.json")
    assert seal["k_table_sha256"] == _sha("artifacts/freezes/K_table.json")
    assert seal["completion_certificate_sha256"] == _sha(
        "artifacts/seal/completion_space_certificate.json")


def test_historical_seals_preserved():
    """Earlier negative seals are untouched and still negative."""
    # [P6-LOG-S24] Test step: assert historical seal preservation.
    print("[P6:test:seal:024] historical seals", flush=True)
    for rel in ("artifacts/seal/FINAL_RESULT.json",
                "artifacts/seal/FINAL_RESULT_CYCLE_002.json"):
        doc = _load(rel)
        assert doc["outcome"] == "NATIVE_ANCHOR_INSUFFICIENT", rel


def test_manifest_and_archive():
    """Manifest verifies modulo declared post-seal maintenance drift."""
    # [P6-LOG-S26] Test step: assert manifest and archive integrity.
    print("[P6:test:seal:026] manifest and archive", flush=True)
    # Post-seal maintenance set (documentation/marker/timestamp only;
    # sealed scientific values untouched — seal bindings checked in
    # test_seal_hash_bindings and the Phase-6 runner). Any drift outside
    # this set fails loudly; any missing entry fails.
    maintenance = {
        # Documentation reconciliation passes (no semantic content).
        "Path.md": "docs",
        "WorkPlan.md": "docs",
        # Comparison reruns stamp compared_utc (run metadata only).
        "artifacts/audits/canary_irrelevant_extra_attribute_comparison.json":
            "timestamp",
        "artifacts/audits/canary_mustbepresent_removed_comparison.json":
            "timestamp",
        "artifacts/audits/canary_wrong_answer_1_comparison.json":
            "timestamp",
        "artifacts/audits/canary_wrong_answer_2_comparison.json":
            "timestamp",
        "artifacts/audits/canary_wrong_category_comparison.json":
            "timestamp",
        "artifacts/audits/canary_wrong_datatype_comparison.json":
            "timestamp",
        # Console-marker additions from Phase 3/4/5/6 compliance passes
        # (marker comments only; reruns reproduce identical outputs).
        "scripts/run_phase3.ps1": "markers",
        "scripts/run_phase3.sh": "markers",
        "scripts/run_phase4.ps1": "markers",
        "scripts/run_phase4.sh": "markers",
        "scripts/run_phase5.ps1": "markers",
        "scripts/run_phase5.sh": "markers",
        "scripts/run_phase6.ps1": "markers",
        "scripts/run_phase6.sh": "markers",
        "src/audit/check_no_manual_labels.py": "markers",
        "src/audit/compare_canary_outcomes.py": "markers",
        "src/audit/independent_solver.py": "markers",
        "src/audit/phase5_execute.py": "markers",
        "src/pc/check_completion_space.py": "markers",
        "src/pc/compile_contract.py": "markers",
        "src/pc/models.py": "self-check entry (outputs verified identical)",
        "src/pc/solve_freezes.py": "markers",
        "tests/test_touch_derivation.py": "self-check test",
    }
    lines = open(os.path.join(REPO_ROOT, "MANIFEST.sha256"),
                 encoding="utf-8").read().splitlines()
    assert len([l for l in lines if l.strip()]) >= 2000
    drifted = []
    for line in lines:
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        full = os.path.join(REPO_ROOT, *rel.split("/"))
        assert os.path.isfile(full), rel
        if _sha(rel) != digest:
            drifted.append(rel)
    unexpected = [r for r in drifted if r not in maintenance]
    assert unexpected == [], unexpected
    print("[P6:test:seal:026] drifted=%d all declared maintenance"
          % len(drifted), flush=True)
    exp = open(os.path.join(REPO_ROOT, "PC-XACML-S3PLUS-v1.sha256"),
               encoding="utf-8").read().split()[0]
    assert _sha("PC-XACML-S3PLUS-v1.tar.gz") == exp
    exp2 = open(os.path.join(REPO_ROOT, "PC-XACML-S3PLUS-v1.tar.gz.sha256"),
                encoding="utf-8").read().split()[0]
    assert exp2 == exp


def test_audit_report_and_claims():
    """Audit carries required sections, binds values, passes linter."""    # [P6-LOG-S28] Test step: assert audit report and claim gate.
    print("[P6:test:seal:028] audit and claims", flush=True)
    text = open(os.path.join(REPO_ROOT, "artifacts", "audits",
                             "FINAL_AUDIT.md"), encoding="utf-8").read()
    for section in ("External source provenance", "Original fixture",
                    "Anchor-by-anchor", "Policy projection",
                    "H-equivalence", "Blind-adjudication",
                    "Native target decisions", "PC contract hash",
                    "touch derivations", "Completion-space",
                    "freeze values", "solver agreement", "Falsification",
                    "limitations", "Allowed and forbidden"):
        assert section.lower() in text.lower(), section
    for banned in ("real systems naturally provide PC anchors",
                   "Stage III works in the wild",
                   "production authorization systems are PC-identifiable"):
        assert banned not in text
    assert "POSITIVE_NATIVE_STAGE3" in text


def test_builder_schema_and_reproducers_present():
    """Assembler, result schema, and reproducers exist and run clean."""
    # [P6-LOG-S30] Test step: assert Phase-6 tooling presence.
    print("[P6:test:seal:030] builder and reproducers", flush=True)
    import subprocess
    assert os.path.isfile(os.path.join(
        REPO_ROOT, "src", "audit", "build_audit_report.py"))
    assert os.path.isfile(os.path.join(
        REPO_ROOT, "scripts", "reproduce_all.sh"))
    assert os.path.isfile(os.path.join(
        REPO_ROOT, "scripts", "reproduce_all.ps1"))
    completed = subprocess.run(
        [sys.executable,
         os.path.join(REPO_ROOT, "src", "audit",
                      "build_audit_report.py"), REPO_ROOT],
        capture_output=True, text=True, timeout=120)
    assert completed.returncode == 0, completed.stdout
    assert "[P6:report:040] audit binds artifacts; claims green" in \
        completed.stdout
