"""Phase-3 touch-derivation tests (T01/T02 + contract mechanics).

Asserts the mechanical touch for the sole repair action is the
single-element evidence set, that the independent reimplementation
byte-agrees, that the contract target map comes from parsed PDP
responses, that S0 is open for the preregistered heterogeneity reason
with both successors non-open singletons, and that computation never
opens sealed expectation files.
"""
import builtins
import hashlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "pc"))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import compile_contract as compiler  # noqa: E402
import derive_touch as primary  # noqa: E402

CONTRACT_REL = os.path.join("artifacts", "contracts",
                            "pc_xacml_primary.contract.json")
TOUCH_REL = os.path.join("artifacts", "contracts", "touch.json")


def _load(rel):
    """Load a JSON artifact relative to the repo root."""
    # [P3-LOG-T10] Test step: load one sealed artifact.
    print("[P3:test:touch:010] loading %s" % rel, flush=True)
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decision_of(path):
    """Independently extract the Decision string from a response."""
    from lxml import etree
    root = etree.parse(path).getroot()
    for element in root.iter():
        tag = element.tag
        name = tag.split("}", 1)[1] if tag.startswith("{") else tag
        if name == "Decision" and element.text:
            return element.text.strip()
    raise AssertionError("no Decision in " + path)


def test_contract_exists_and_deterministic():
    """Contract compiles to deterministic sorted-key JSON."""
    # [P3-LOG-T12] Test step: assert contract presence and order.
    print("[P3:test:touch:012] contract determinism", flush=True)
    path = os.path.join(REPO_ROOT, CONTRACT_REL)
    assert os.path.isfile(path), CONTRACT_REL
    with open(path, "rb") as handle:
        raw = handle.read()
    doc = json.loads(raw.decode("utf-8"))
    reser = (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode(
        "utf-8")
    assert raw == reser, "contract JSON is not canonical"
    assert doc["contract_id"] == "pc-xacml-s3plus-primary"
    assert doc["experiment_id"] == "PC-XACML-S3PLUS-v1"


def test_target_map_from_parsed_responses():
    """Target map equals independently parsed PDP decisions."""
    # [P3-LOG-T14] Test step: assert parsed-response target map.
    print("[P3:test:touch:014] target map provenance", flush=True)
    contract = _load(CONTRACT_REL)
    permit = _decision_of(os.path.join(
        REPO_ROOT, "artifacts", "audits", "launch", "quarantine",
        "response_x_permit.xml"))
    nonpermit = _decision_of(os.path.join(
        REPO_ROOT, "artifacts", "audits", "launch", "quarantine",
        "response_x_nonpermit.xml"))
    assert contract["target"]["x_permit"] == permit
    assert contract["target"]["x_nonpermit"] == nonpermit
    assert permit != nonpermit


def test_open_computed_from_fiber_homogeneity():
    """S0 open by heterogeneity; successors non-open singletons."""
    # [P3-LOG-T16] Test step: assert computed openness.
    print("[P3:test:touch:016] openness computation", flush=True)
    contract = _load(CONTRACT_REL)
    checkpoints = contract["checkpoints"]
    assert checkpoints["S0"]["open"] is True
    assert set(checkpoints["S0"]["fiber"]) == {"x_permit", "x_nonpermit"}
    assert checkpoints["S_permit"]["open"] is False
    assert checkpoints["S_nonpermit"]["open"] is False
    assert checkpoints["S_permit"]["fiber"] == ["x_permit"]
    assert checkpoints["S_nonpermit"]["fiber"] == ["x_nonpermit"]
    # Preregistered reason is visible in the S0 rationale.
    reason = checkpoints["S0"]["reason"]
    assert contract["target"]["x_permit"] in reason
    assert contract["target"]["x_nonpermit"] in reason


def test_no_copied_closed_literal():
    """Compiler computes openness; it never copies a closed literal."""
    # [P3-LOG-T18] Test step: assert no copied closed literal.
    print("[P3:test:touch:018] no copied closed literal", flush=True)
    path = os.path.join(REPO_ROOT, "src", "pc", "compile_contract.py")
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    lowered = source.lower()
    assert '"closed": true' not in lowered
    assert "'closed': true" not in lowered
    assert '"closed":true' not in lowered
    # Openness is assigned from computed booleans.
    assert "s0_open" in source or "s0-open" in source.lower()


def test_primary_touch_is_singleton_evidence():
    """T01: primary mechanical touch is the singleton evidence set."""
    # [P3-LOG-T20] Test step: assert primary touch value.
    print("[P3:test:touch:020] primary touch value", flush=True)
    touch = _load(TOUCH_REL)
    keys = sorted(touch.keys())
    assert len(keys) == 1
    action = keys[0]
    assert touch[action] == ["E"]


def test_independent_byte_agreement(tmp_path):
    """T02: independent reimplementation byte-agrees with primary."""
    # [P3-LOG-T22] Test step: assert dual-implementation agreement.
    print("[P3:test:touch:022] dual agreement", flush=True)
    import independent_touch as checker
    contract_path = os.path.join(REPO_ROOT, CONTRACT_REL)
    first = os.path.join(str(tmp_path), "a.json")
    second = os.path.join(str(tmp_path), "b.json")
    primary.main(["derive_touch.py", contract_path, first])
    checker.main(["independent_touch.py", contract_path, second])
    with open(first, "rb") as handle:
        left = handle.read()
    with open(second, "rb") as handle:
        right = handle.read()
    assert left == right, "primary/independent touch bytes differ"
    # Both equal the sealed artifact bytes.
    with open(os.path.join(REPO_ROOT, TOUCH_REL), "rb") as handle:
        sealed = handle.read()
    assert left == sealed


def test_independent_has_no_primary_import():
    """Independent module shares no code with the primary path."""
    # [P3-LOG-T24] Test step: assert implementation independence.
    print("[P3:test:touch:024] independence", flush=True)
    path = os.path.join(REPO_ROOT, "src", "audit",
                        "independent_touch.py")
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    assert "derive_touch" not in source
    assert "from pc" not in source and "from src" not in source
    assert "canonical_H" not in source or "_h_canonical_independent" in source


def test_pseudocode_literal():
    """Primary module implements the section-6 pseudocode literally."""
    # [P3-LOG-T26] Test step: assert literal pseudocode lines.
    print("[P3:test:touch:026] pseudocode literal", flush=True)
    path = os.path.join(REPO_ROOT, "src", "pc", "derive_touch.py")
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    assert "def derive_touch(pre, successors):" in source
    assert "touch = set()" in source
    assert "for post in successors:" in source
    assert 'touch.add("E")' in source
    assert 'touch.add("R")' in source
    assert 'touch.add("A")' in source
    assert "return touch" in source


def test_closed_inputs_file_open_trace(tmp_path):
    """Computation opens no sealed expectation file (open trace)."""
    # [P3-LOG-T28] Test step: assert closed inputs via open trace.
    print("[P3:test:touch:028] closed-input trace", flush=True)
    forbidden = ("expected_signature", "canary_expectations",
                 "experiment.yaml")
    seen = []
    real_open = builtins.open

    def _tracing(path, *args, **kwargs):
        seen.append(str(path))
        return real_open(path, *args, **kwargs)

    contract_tmp = os.path.join(str(tmp_path), "contract.json")
    touch_tmp = os.path.join(str(tmp_path), "touch.json")
    indep_tmp = os.path.join(str(tmp_path), "indep.json")
    builtins.open = _tracing
    try:
        compiler.build_contract(REPO_ROOT)
        primary.main(["derive_touch.py",
                      os.path.join(REPO_ROOT, CONTRACT_REL), touch_tmp])
        import independent_touch as checker
        checker.main(["independent_touch.py",
                      os.path.join(REPO_ROOT, CONTRACT_REL), indep_tmp])
        with real_open(contract_tmp, "w", encoding="utf-8") as handle:
            handle.write("{}")
    finally:
        builtins.open = real_open
    hits = [p for p in seen if any(tok in p for tok in forbidden)]
    assert hits == [], hits


def test_closed_inputs_import_guards():
    """Computation modules carry closed-input guards, no direct opens."""
    # [P3-LOG-T30] Test step: assert import-time guards.
    print("[P3:test:touch:030] import guards", flush=True)
    import re
    for rel in ("src/pc/compile_contract.py", "src/pc/derive_touch.py",
                "src/audit/independent_touch.py"):
        with open(os.path.join(REPO_ROOT, rel),
                  encoding="utf-8") as handle:
            text = handle.read()
        assert "expected_signature" in text, rel
        assert "canary_expectations" in text, rel
        for lineno, line in enumerate(text.splitlines(), 1):
            code = line.split("#", 1)[0]
            if re.search(r"open\s*\([^)]*expected_signature", code):
                raise AssertionError("%s:%d" % (rel, lineno))
            if re.search(r"open\s*\([^)]*canary_expectations", code):
                raise AssertionError("%s:%d" % (rel, lineno))


def test_models_have_no_touch_fields():
    """Input models expose no touch/resource fields."""
    # [P3-LOG-T32] Test step: assert model purity.
    print("[P3:test:touch:032] model purity", flush=True)
    import models as models
    contract = models.Contract(
        contract_id="x", experiment_id="y", worlds=("a",),
        initial_checkpoint="S0")
    doc = contract.to_dict()
    assert "touch" not in doc
    assert "resource" not in doc
    for name in ("canonical_json_bytes", "sha256_bytes",
                 "sha256_canonical", "sha256_file"):
        assert callable(getattr(models, name)), name


def test_models_self_check_entry():
    """models.py --self-check exits 0 with the P3:models tag line."""
    # [P3-LOG-T34] Test step: assert models self-check entry point.
    print("[P3:test:touch:034] models self-check", flush=True)
    import subprocess
    completed = subprocess.run(
        [sys.executable,
         os.path.join(REPO_ROOT, "src", "pc", "models.py"),
         "--self-check"],
        capture_output=True, text=True, timeout=120)
    assert completed.returncode == 0, completed.stderr
    assert "[P3:models:110] self-check ok" in completed.stdout
