"""Phase-1 prereg-seal test (gate box [10]).

Asserts prereg_sha256.txt matches recomputed file hashes (plus sealed
spec hashes), execution_inputs.json conforms to its schema and contains
no expected outputs of any kind, and canary_expectations.json conforms
to its schema with sealed_before_execution true.
"""
import hashlib
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(rel):
    """Load a JSON document relative to the repo root."""
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as handle:
        return json.load(handle)


def test_prereg_hashes_match():
    """prereg_sha256.txt entries match recomputed hashes."""
    # [P1-LOG-T40] Test step: assert prereg seal integrity.
    print("[P1:test:prereg:040] checking prereg seal hashes", flush=True)
    prereg_dir = os.path.join(REPO_ROOT, "prereg")
    with open(os.path.join(prereg_dir, "prereg_sha256.txt"),
              encoding="utf-8") as handle:
        lines = [line.rstrip("\n") for line in handle if line.strip()]
    recorded = {}
    for line in lines:
        digest, sep, name = line.partition("  ")
        if not sep:
            name, _, digest = line.partition("=")
            recorded[name] = digest
        else:
            recorded[name] = digest
    for name in sorted(os.listdir(prereg_dir)):
        if name in ("prereg_sha256.txt",
                    "blind_model_adjudication_prompt.txt"):
            # The frozen prompt is sealed by Amendment 001, not by the
            # Phase-1 prereg seal (which stays byte-immutable); its
            # coverage is asserted in test_prompt_covered_by_amendment.
            continue
        path = os.path.join(prereg_dir, name)
        if os.path.isfile(path):
            assert recorded.get(name) == sha256_file(path), name
    manifest = load_json("external/MANIFEST.json")
    spec = manifest["implementation_spec"]
    assert recorded.get("spec:sha256_raw") == spec["sha256_raw"]
    assert recorded.get("spec:sha256_lf_normalized") == spec[
        "sha256_lf_normalized"]


def test_prompt_covered_by_amendment():
    """Frozen prompt hash matches the Amendment-001 seal record."""
    # [P1-LOG-T46] Test step: assert prompt seal coverage.
    print("[P1:test:prereg:046] checking prompt amendment seal",
          flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "audits",
                           "amendment_001_seal.json"),
              encoding="utf-8") as handle:
        seal = json.load(handle)
    assert sha256_file(os.path.join(
        REPO_ROOT, "prereg",
        "blind_model_adjudication_prompt.txt")) == seal["prompt_sha256"]


def test_execution_inputs_valid():
    """execution_inputs.json is schema-shaped and outcome-free."""
    # [P1-LOG-T42] Test step: assert execution-inputs validity.
    print("[P1:test:prereg:042] checking execution inputs", flush=True)
    doc = load_json("prereg/execution_inputs.json")
    assert doc["action_interface"]["unit_cost"] > 0
    assert doc["action_interface"]["authorization_logic_performed"] is False
    assert len(doc["freeze_order"]) == 8
    assert doc["worlds"]["x_permit"]["missing_attribute_value"]
    assert doc["worlds"]["x_nonpermit"]["missing_attribute_value"]
    text = json.dumps(doc)
    for forbidden in ("expected_touch", "expected_K", "expected_decision",
                      "expected_classification", "Permit", "NotApplicable"):
        assert forbidden not in text, forbidden
    assert "canonical XACML Decision" in doc["target_semantics"]["rule"]


def test_canary_expectations_valid():
    """canary_expectations.json is schema-shaped and presealed."""
    # [P1-LOG-T44] Test step: assert canary-expectation seal.
    print("[P1:test:prereg:044] checking canary expectations", flush=True)
    doc = load_json("prereg/canary_expectations.json")
    assert doc["sealed_before_execution"] is True
    required = {"mustbepresent_removed", "wrong_category",
                "wrong_datatype", "irrelevant_extra_attribute",
                "wrong_answer_1", "wrong_answer_2"}
    assert required.issubset(set(doc["canaries"].keys())), \
        set(doc["canaries"].keys())
    for name, entry in doc["canaries"].items():
        assert entry["expected"]["decision"] in (
            "Permit", "Deny", "NotApplicable", "Indeterminate"), name
        assert entry["rationale"].strip() != "", name
