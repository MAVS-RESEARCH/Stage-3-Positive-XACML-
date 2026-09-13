"""Phase-5 parser/corruption tests (C01-C03/C09 + canary seal conformance).

Judges each control against its sealed exact expectation (never against
the primary result). Execution wrote raw outputs first; comparison opened
expectations afterward; these tests verify the sealed verdicts.
"""
import hashlib
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDITS = os.path.join(REPO_ROOT, "artifacts", "audits")


def load_json(path):
    """Load JSON relative to repo or absolute."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_corruption_detected_5_of_5():
    """C09: 1-byte flips in 4 fixtures + spec HTML all trip verifier."""
    # [P5-LOG-T10] Test step: assert corruption detection.
    print("[P5:test:corrupt:010] checking 5/5 corruptions", flush=True)
    for name in ("pdp", "request", "response", "policy", "spec"):
        path = os.path.join(AUDITS, "corruption_%s.json" % name)
        assert os.path.isfile(path), name
        doc = load_json(path)
        assert doc["control"] == "5.1", name
        assert doc["detected"] is True, name
        assert doc["verifier_exit_nonzero"] is True, name
        assert doc["frozen_external_untouched"] is True, name
        assert doc["mutated_sha256"] != doc["sealed_sha256"], name
    # Frozen externals themselves still match the seal (never mutated).
    with open(os.path.join(REPO_ROOT, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = load_json(os.path.join(
            REPO_ROOT, "external", "MANIFEST.json"))
    for rel in ("pdp.xml", "request.xml", "response.xml",
                "policies/policy.xml"):
        fpath = os.path.join(REPO_ROOT, "external", "authzforce",
                             "fixture", *rel.split("/"))
        assert os.path.isfile(fpath), rel
        digest = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
        assert digest == manifest["authzforce"]["fixture_files"][rel][
            "sha256"], rel


def test_canary_comparisons_pass_sealed():
    """C01-C03 + 5.2/5.9: every sealed canary comparison passes."""
    # [P5-LOG-T12] Test step: assert sealed canary verdicts.
    print("[P5:test:corrupt:012] checking canary comparisons", flush=True)
    exp = load_json(os.path.join(REPO_ROOT, "prereg",
                                 "canary_expectations.json"))
    assert exp["sealed_before_execution"] is True
    for canary_id in sorted(exp["canaries"].keys()):
        raw_path = os.path.join(AUDITS, "canary_%s_raw.json" % canary_id)
        comp_path = os.path.join(
            AUDITS, "canary_%s_comparison.json" % canary_id)
        assert os.path.isfile(raw_path), canary_id
        assert os.path.isfile(comp_path), canary_id
        raw = load_json(raw_path)
        comp = load_json(comp_path)
        assert comp["canary_id"] == canary_id
        assert comp["pass"] is True, (canary_id, comp)
        # Re-verify triple match generically (expected or alternative).
        obs = (raw["observed"]["decision"],
               raw["observed"]["status_code"],
               raw["observed"]["missing_attribute_detail_present"])
        entry = exp["canaries"][canary_id]
        exp_triple = (entry["expected"]["decision"],
                      entry["expected"]["status_code"],
                      entry["expected"][
                          "missing_attribute_detail_present"])
        alts = [(a["decision"], a["status_code"],
                 a["missing_attribute_detail_present"])
                for a in entry.get("acceptable_alternatives", []) or []]
        assert obs == exp_triple or obs in alts, (canary_id, obs)
        assert raw["frozen_external_untouched"] is True


def test_wrong_category_is_non_satisfying():
    """C01: wrong-category canary is a non-satisfying class."""
    # [P5-LOG-T14] Test step: assert Category-aware distinction.
    print("[P5:test:corrupt:014] wrong-category class", flush=True)
    comp = load_json(os.path.join(
        AUDITS, "canary_wrong_category_comparison.json"))
    assert comp["pass"] is True
    assert comp["observed"]["decision"] != "Permit", comp["observed"]


def test_wrong_datatype_never_coerced():
    """C02: wrong-datatype never silently coerced into expected bag."""
    # [P5-LOG-T16] Test step: assert datatype semantics.
    print("[P5:test:corrupt:016] wrong-datatype class", flush=True)
    comp = load_json(os.path.join(
        AUDITS, "canary_wrong_datatype_comparison.json"))
    assert comp["pass"] is True
    assert comp["observed"]["decision"] == "Indeterminate", comp["observed"]
    raw = load_json(os.path.join(
        AUDITS, "canary_wrong_datatype_raw.json"))
    # Must not equal the permit-world Permit bag.
    assert raw["observed"]["decision"] != "Permit"


def test_projection_respects_h_vs_pr():
    """C03: irrelevant extra attribute respects H vs P_R distinction."""
    # [P5-LOG-T18] Test step: assert projection distinction.
    print("[P5:test:corrupt:018] projection H vs P_R", flush=True)
    comp = load_json(os.path.join(
        AUDITS, "canary_irrelevant_extra_attribute_comparison.json"))
    assert comp["pass"] is True
    # Raw was built on the original (missing) request + extra, so the
    # PDP decision must equal the original missing-attribute class,
    # proving the fixed P_R did not expand.
    assert comp["observed"]["decision"] == "Indeterminate", comp["observed"]


def test_raw_written_before_comparison():
    """Ordering: raw outputs predate comparisons (no circularity)."""
    # [P5-LOG-T20] Test step: assert raw-first ordering.
    print("[P5:test:corrupt:020] raw-first ordering", flush=True)
    for canary_id in ("mustbepresent_removed", "wrong_category",
                      "wrong_datatype", "irrelevant_extra_attribute",
                      "wrong_answer_1", "wrong_answer_2"):
        raw_path = os.path.join(AUDITS, "canary_%s_raw.json" % canary_id)
        comp_path = os.path.join(
            AUDITS, "canary_%s_comparison.json" % canary_id)
        assert os.path.getmtime(raw_path) <= os.path.getmtime(
            comp_path) + 1, canary_id
