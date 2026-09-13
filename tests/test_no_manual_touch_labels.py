"""Phase-3 no-manual-label tests (presence-vs-use + mutation).

Asserts the static audit passes on the clean tree, allows sealed
predictions and derived outputs in their homes, rejects planted
action-specific preassignments, rejects expectation reads into
computation, and rejects touch-accepting contract schemas.
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import check_no_manual_labels as scanner  # noqa: E402


def test_scanner_clean_on_live_tree():
    """Static audit passes on the unmutated repository."""
    # [P3-LOG-T40] Test step: assert clean-tree audit pass.
    print("[P3:test:nolabel:040] clean audit", flush=True)
    assert scanner.scan_root(REPO_ROOT) == []


def test_sealed_predictions_allowed_presence():
    """Sealed predictions may contain the expected mapping."""
    # [P3-LOG-T42] Test step: assert allowed prediction presence.
    print("[P3:test:nolabel:042] prediction presence", flush=True)
    with open(os.path.join(REPO_ROOT, "prereg",
                           "expected_signature.json"),
              encoding="utf-8") as handle:
        doc = json.load(handle)
    assert doc["expected_touch"]["q_supply_missing_attribute"] == ["E"]
    # The scanner allowlists these homes, so presence alone is clean.
    assert "prereg/expected_signature.json" in scanner.ALLOWED_PRESENCE
    assert "prereg/experiment.yaml" in scanner.ALLOWED_PRESENCE


def test_derived_output_allowed_with_provenance():
    """Derived touch output is allowed only with seal provenance."""
    # [P3-LOG-T44] Test step: assert output provenance link.
    print("[P3:test:nolabel:044] output provenance", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "contracts",
                           "touch.json"),
              encoding="utf-8") as handle:
        assert json.load(handle)["q_supply_missing_attribute"] == ["E"]
    with open(os.path.join(REPO_ROOT, "artifacts", "seal",
                           "phase3_manifest.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    with open(os.path.join(REPO_ROOT, "artifacts", "contracts",
                           "touch.json"), "rb") as handle:
        import hashlib
        actual = hashlib.sha256(handle.read()).hexdigest()
    assert manifest["touch_sha256"] == actual
    assert "derive_touch" in json.dumps(manifest.get("derivation", {}))


def test_mutation_action_map_rejected(tmp_path):
    """Planted action-specific map fails the audit (control 5.11)."""
    # [P3-LOG-T46] Test step: assert mutation detection.
    print("[P3:test:nolabel:046] mutation map", flush=True)
    evil = os.path.join(str(tmp_path), "evil_labels.py")
    with open(evil, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("MAP = {\"q_supply_missing_attribute\": [\"E\"]}\n")
    problems = scanner._check_src_file(evil, "src/pc/evil_labels.py")
    assert any("evil_labels" in item for item in problems), problems
    # End-to-end: the same payload planted in the live tree layout is
    # caught by the full scan (written then removed fail-closed).
    live_evil = os.path.join(REPO_ROOT, "src", "pc", "evil_labels_tmp.py")
    try:
        with open(live_evil, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(
                "MAP = {\"q_supply_missing_attribute\": [\"E\"]}\n")
        full = scanner.scan_root(REPO_ROOT)
        assert any("evil_labels_tmp" in item for item in full), full
    finally:
        if os.path.isfile(live_evil):
            os.remove(live_evil)


def test_mutation_touch_input_field_rejected(tmp_path):
    """Planted touch input field fails the audit."""
    # [P3-LOG-T48] Test step: assert input-field detection.
    print("[P3:test:nolabel:048] mutation field", flush=True)
    evil = os.path.join(str(tmp_path), "evil_field.py")
    with open(evil, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("CFG = {\"touch\": [\"E\"]}\n")
    problems = scanner._check_src_file(evil, "src/pc/evil_field.py")
    assert any("evil_field" in item for item in problems), problems


def test_mutation_expectation_read_rejected(tmp_path):
    """Planted expectation open fails the audit."""
    # [P3-LOG-T50] Test step: assert expectation-read detection.
    print("[P3:test:nolabel:050] mutation read", flush=True)
    evil = os.path.join(str(tmp_path), "evil_read.py")
    with open(evil, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("import json\n"
                     "open(\"prereg/expected_signature.json\")\n")
    problems = scanner._check_src_file(evil, "src/pc/evil_read.py")
    assert any("evil_read" in item for item in problems), problems


def test_contract_schema_rejects_touch_inputs():
    """Contract input schema rejects touch/resource payloads."""
    # [P3-LOG-T52] Test step: assert schema rejection.
    print("[P3:test:nolabel:052] schema rejection", flush=True)
    with open(os.path.join(REPO_ROOT, "schemas",
                           "contract.schema.json"),
              encoding="utf-8") as handle:
        schema = json.load(handle)
    assert schema.get("additionalProperties") is False
    assert "touch" not in schema.get("properties", {})
    assert "resource" not in schema.get("properties", {})
    # Structural rejection proof without a validator dependency.
    try:
        import jsonschema
    except ImportError:
        return
    for bad in ({"touch": ["E"]}, {"resource": ["E"]},
                {"touches": ["E"]}, {"resources": ["E"]}):
        base = {
            "contract_id": "x",
            "experiment_id": "y",
            "worlds": ["x_permit"],
            "initial_checkpoint": "S0",
            "checkpoints": {},
            "target": {},
            "H": {},
            "PR": {},
            "Lambda": {},
            "omega": {},
            "actions": {},
            "successors": {},
            "costs": {},
            "atomicity": {},
            "provenance": {},
        }
        trial = dict(base)
        trial.update(bad)
        try:
            jsonschema.validate(trial, schema)
        except jsonschema.ValidationError:
            pass
        else:
            raise AssertionError("schema accepted %r" % (bad,))


def test_phase5_label_injection_artifact():
    """C08 extension: Phase-5 label-injection artifact proves detection."""
    # [P5-LOG-T72] Test step: assert Phase-5 injection seal.
    print("[P5:test:nolabel:072] Phase-5 injection artifact", flush=True)
    path = os.path.join(REPO_ROOT, "artifacts", "audits",
                        "label_injection.json")
    if not os.path.isfile(path):
        import pytest
        pytest.skip("Phase-5 label artifact absent (pre-Phase-5)")
    with open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert doc["detected"] is True
    assert doc["pass"] is True


def test_contract_input_has_no_touch():
    """Compiled contract input carries no touch field."""
    # [P3-LOG-T54] Test step: assert contract input purity.
    print("[P3:test:nolabel:054] contract purity", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "contracts",
                           "pc_xacml_primary.contract.json"),
              encoding="utf-8") as handle:
        doc = json.load(handle)

    def _walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key != "touch", "touch in contract input"
                assert key != "resource", "resource in contract input"
                _walk(value)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(doc)
