"""Phase-5 clean-reproduction + leakage tests (R06, 5.12-5.13, 5.2/5.9).

R06: fresh temp rerun byte-matches primary (excluding timestamps/paths).
5.12: expected payload reachable only from final comparison; 2A/2B never
opened it; Amendment-001 chain intact.
5.2/5.9: MustBePresent + negative-world sealed verdicts + fiber/E checks.
"""
import hashlib
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDITS = os.path.join(REPO_ROOT, "artifacts", "audits")


def load_json(path):
    """Load a JSON document."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_mustbepresent_canary_sealed():
    """5.2: MustBePresent-removed behavior equals sealed expectation."""
    # [P5-LOG-T60] Test step: assert MustBePresent canary.
    print("[P5:test:clean:060] mustbepresent canary", flush=True)
    comp = load_json(os.path.join(
        AUDITS, "canary_mustbepresent_removed_comparison.json"))
    assert comp["pass"] is True, comp
    raw = load_json(os.path.join(
        AUDITS, "canary_mustbepresent_removed_raw.json"))
    assert raw["frozen_external_untouched"] is True


def test_negative_world_sweep():
    """5.9: wrong answers stay NotApplicable, fiber open, E preserved."""
    # [P5-LOG-T62] Test step: assert negative-world sweep.
    print("[P5:test:clean:062] negative-world sweep", flush=True)
    doc = load_json(os.path.join(AUDITS, "negative_world_sweep.json"))
    assert doc["control"] == "5.9"
    assert doc["fiber_open"] is True, doc
    assert doc["e_class_preserved"] is True, doc
    assert doc["primary_never_replaced"] is True, doc
    for key in ("wrong_answer_1", "wrong_answer_2"):
        comp = load_json(os.path.join(
            AUDITS, "canary_%s_comparison.json" % key))
        assert comp["pass"] is True, (key, comp)
        assert comp["observed"]["decision"] == "NotApplicable", (
            key, comp["observed"])
    # Primary x_nonpermit bytes still carry the preregistered literal.
    with open(os.path.join(REPO_ROOT, "prereg", "execution_inputs.json"),
              encoding="utf-8") as h:
        nonpermit_val = json.load(h)["worlds"]["x_nonpermit"][
            "missing_attribute_value"]
    with open(os.path.join(REPO_ROOT, "derived", "requests",
                           "request_x_nonpermit.xml"), "rb") as h:
        assert nonpermit_val.encode("utf-8") in h.read()


def test_leakage_graph_passes():
    """5.12: leakage graph proves comparison-only reachability + chain."""
    # [P5-LOG-T64] Test step: assert leakage audit.
    print("[P5:test:clean:064] leakage graph", flush=True)
    doc = load_json(os.path.join(AUDITS, "leakage_graph.json"))
    assert doc["control"] == "5.12"
    assert doc["pass"] is True, doc
    assert doc["offenders"] == [], doc["offenders"]
    assert doc["twoAB_edges"] == [], doc["twoAB_edges"]
    assert doc["reachable_only_from_comparison"] is True
    assert doc["amendment_001"]["prompt_match"] is True


def test_clean_repro_matches():
    """R06: clean rerun matches primary (canonical, excl. timestamps)."""
    # [P5-LOG-T66] Test step: assert clean reproduction.
    print("[P5:test:clean:066] clean reproduction", flush=True)
    doc = load_json(os.path.join(AUDITS, "clean_repro.json"))
    assert doc["control"] == "5.13"
    assert doc["pass"] is True, doc
    assert doc["hashes_verified"] is True
    assert doc["touch_match"] is True
    assert doc["k_match"] is True
    # Primary K still the sealed structural vector.
    with open(os.path.join(REPO_ROOT, "artifacts", "freezes",
                           "K_table.json"), encoding="utf-8") as h:
        kappa = json.load(h)["kappa"]
    assert kappa == [1, "INF", 1, 1, "INF", "INF", 1, "INF"], kappa


def test_frozen_externals_untouched():
    """Global: frozen external/ bytes still match the seal."""
    # [P5-LOG-T68] Test step: assert no frozen mutation.
    print("[P5:test:clean:068] frozen untouched", flush=True)
    manifest = load_json(os.path.join(REPO_ROOT, "external",
                                      "MANIFEST.json"))

    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    for rel, rec in sorted(manifest["authzforce"][
            "fixture_files"].items()):
        p = os.path.join(REPO_ROOT, "external", "authzforce",
                         "fixture", *rel.split("/"))
        assert sha(p) == rec["sha256"], rel
    spec = os.path.join(REPO_ROOT, "external", "xacml",
                        "xacml-3.0-core-spec-cos01-en.html")
    assert sha(spec) == manifest["xacml"]["sha256"]
