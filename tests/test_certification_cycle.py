"""Certification-cycle state machine tests (Amendment 005).

Synthetic temporary roots only: init validation (IDs, triples, reuse,
revision double-bind), assess tallies (unanimous/partial/missing/stale),
decide consistency (PASSED/REPAIRABLE/IRREDUCIBLE guards + immutability),
handoff content rules, and live-repo cycle inventory.
"""
import json
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import certification_cycle as cyc  # noqa: E402
import final_certification as final  # noqa: E402


def write(path, content):
    """Write text, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def freeze_root(base, revision=4):
    """Minimal operative freeze: packet seal + prompt + hashes."""
    packet = os.path.join(base, "artifacts", "audits", "semantic_hardening",
                          "final_freeze", "FINAL_BLIND_PACKET")
    os.makedirs(packet)
    os.makedirs(os.path.join(base, "prereg"))
    write(os.path.join(packet, "PACKET_MANIFEST.json"), '{"files": {}}')
    with open(os.path.join(packet, "PACKET_MANIFEST.json"),
              "rb") as handle:
        import hashlib
        packet_sha = hashlib.sha256(handle.read()).hexdigest()
    write(os.path.join(packet, "PACKET_SHA256.txt"), packet_sha + "\n")
    write(os.path.join(base, "prereg", "final_certification_prompt.txt"),
          "prompt\n")
    with open(os.path.join(base, "prereg", "final_certification_prompt.txt"),
              "rb") as handle:
        prompt_sha = hashlib.sha256(handle.read()).hexdigest()
    write(os.path.join(base, "artifacts", "audits", "semantic_hardening",
                       "final_freeze", "FINAL_SEMANTIC_FREEZE.json"),
          json.dumps({"freeze_id": "s", "frozen": True, "revision": revision,
                      "packet_sha256": packet_sha,
                      "prompt_sha256": prompt_sha}, indent=2,
                     sort_keys=True))
    return packet_sha, prompt_sha


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, repo_root, **kwargs):
        self.repo_root = repo_root
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_init_validation(tmp_path):
    """Init refuses bad IDs, non-triples, reuse, double-bound revision."""
    # [P2-LOG-Y10] Test step: assert cycle init guards.
    print("[P2:test:cycle:010] init guards", flush=True)
    root = str(tmp_path / "c0")
    try:
        cyc.cmd_init_cycle(_ns(root, init_cycle="BAD",
                               revision="4", panel="AUD-C04,AUD-C05,AUD-C06"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("bad cycle id accepted")
    try:
        cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_009",
                               revision="4", panel="AUD-C04,AUD-C05"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("non-triple panel accepted")
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_009",
                           revision="4",
                           panel="AUD-C04,AUD-C05,AUD-C06"))
    try:
        cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_010",
                               revision="4",
                               panel="AUD-C07,AUD-C08,AUD-C09"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("double-bound revision accepted")
    try:
        cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_010",
                               revision="5",
                               panel="AUD-C06,AUD-C07,AUD-C08"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("chair reuse accepted")


def seed_records(root, panel, statuses, packet_sha, prompt_sha):
    """Write valid sealed records bound to the given freeze hashes."""
    for auditor in panel:
        dest = os.path.join(root, "artifacts", "audits",
                            "final_certification", auditor)
        os.makedirs(dest, exist_ok=True)
        text = "Attestation of %s cycle probe text." % auditor
        write(os.path.join(dest, "attestation.txt"), text)
        with open(os.path.join(dest, "attestation.txt"), "rb") as handle:
            import hashlib
            att_hash = hashlib.sha256(handle.read()).hexdigest()
        doc = {"verdict_id": auditor + "-verdict", "auditor_id": auditor,
               "qualification": "COLD_MODEL_INDEPENDENT",
               "verdicts": {anchor: {"status": statuses.get(anchor, "FIXED"),
                                     "locators": ["corpus/x Sec.1"],
                                     "notes": "probe"}
                            for anchor in ("H", "P_R", "Lambda", "Atom")},
               "attestation_hash": att_hash,
               "declaration": final.DECLARATION,
               "prompt_sha256": prompt_sha, "packet_sha256": packet_sha,
               "isolation": {"fresh_context": True,
                             "no_prior_experiment_context": True,
                             "other_outputs_unavailable": True}}
        write(os.path.join(dest, "raw_response.txt"),
              json.dumps(doc, indent=2, sort_keys=True))
        write(os.path.join(dest, "verdict.json"),
              json.dumps(doc, indent=2, sort_keys=True))
        import hashlib
        with open(os.path.join(dest, "verdict.json"), "rb") as handle:
            verdict_sha = hashlib.sha256(handle.read()).hexdigest()
        with open(os.path.join(dest, "raw_response.txt"), "rb") as handle:
            raw_sha = hashlib.sha256(handle.read()).hexdigest()
        write(os.path.join(dest, "provenance.json"), json.dumps(
            {"auditor_id": auditor, "valid": True,
             "verdict_sha256": verdict_sha, "raw_sha256": raw_sha,
             "attestation_sha256": att_hash,
             "sealed_prompt_sha256": prompt_sha,
             "sealed_packet_sha256": packet_sha}, indent=2, sort_keys=True))


def test_assess_and_decide_matrix(tmp_path):
    """Assess tallies; decide enforces outcome consistency + sealing."""
    # [P2-LOG-Y12] Test step: assert assess/decide matrix.
    print("[P2:test:cycle:012] assess/decide matrix", flush=True)
    root = str(tmp_path / "c1")
    packet_sha, prompt_sha = freeze_root(root)
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                           revision="4",
                           panel="AUD-C04,AUD-C05,AUD-C06"))
    seed_records(root, ("AUD-C04", "AUD-C05", "AUD-C06"),
                 {"H": "FIXED", "P_R": "FIXED", "Lambda": "PARTIAL",
                  "Atom": "FIXED"}, packet_sha, prompt_sha)
    cyc.cmd_assess_cycle(_ns(root, assess_cycle="CERTIFICATION_CYCLE_001"))
    state = cyc.load_state(root)
    assessment = state["cycles"][0]["assessment"]
    assert assessment["unanimous"] is False
    assert assessment["tally"]["AUD-C04"] == "NON_FIXED:Lambda"
    assert assessment["tally"]["AUD-C06"].startswith("NON_FIXED")
    try:
        cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                                 verdict="CERTIFICATION_PASSED",
                                 reason="x", material_objections=""))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("PASSED allowed on split tally")
    try:
        cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                                 verdict="CERTIFICATION_FAILED_REPAIRABLE",
                                 reason="x", material_objections=""))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("REPAIRABLE allowed without material ids")
    cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                             verdict="CERTIFICATION_FAILED_REPAIRABLE",
                             reason="Lambda engine closure",
                             material_objections="RSX-01; RSX-02"))
    try:
        cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                                 verdict="CERTIFICATION_FAILED_IRREDUCIBLE",
                                 reason="y", material_objections=""))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("decided cycle reopened")


def test_handoff_rules(tmp_path):
    """Handoff names next panel, binds hashes, leaks nothing forbidden."""
    # [P2-LOG-Y14] Test step: assert handoff generation rules.
    print("[P2:test:cycle:014] handoff rules", flush=True)
    root = str(tmp_path / "c2")
    freeze_root(root)
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                           revision="4",
                           panel="AUD-C04,AUD-C05,AUD-C06"))
    cyc.cmd_handoff(_ns(root))
    with open(os.path.join(root, "NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md"),
              encoding="utf-8") as handle:
        doc = handle.read()
    assert "AUD-C04" in doc and "AUD-C06" in doc
    assert "AUD-C01" not in doc
    for forbidden in cyc.FORBIDDEN_HANDOFF:
        assert forbidden not in doc, forbidden


def test_live_cycles_schema():
    """Live cycle records validate against the cycle schema."""
    # [P2-LOG-Y16] Test step: assert live cycle schema conformance.
    print("[P2:test:cycle:016] live schema", flush=True)
    with open(os.path.join(REPO_ROOT, "schemas",
                           "certification_cycle.schema.json"),
              encoding="utf-8") as handle:
        schema = json.load(handle)
    state = cyc.load_state(REPO_ROOT)
    assert state["cycles"], "no live cycles"
    for record in state["cycles"]:
        assert re_match(schema["properties"]["cycle_id"]["pattern"],
                        record["cycle_id"])
        assert record["panel"] and len(record["panel"]) == 3
        assert record["status"] in schema["properties"]["status"]["enum"]


def re_match(pattern, value):
    """Match a value against a regex pattern."""
    import re
    return re.match(pattern, value)


def test_handoff_advances_past_decided(tmp_path):
    """Decided cycles yield the next unused triple in handoff."""
    # [P2-LOG-Y18] Test step: assert handoff panel advancement.
    print("[P2:test:cycle:018] handoff advancement", flush=True)
    root = str(tmp_path / "c3")
    packet_sha, prompt_sha = freeze_root(root)
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                           revision="4",
                           panel="AUD-C04,AUD-C05,AUD-C06"))
    seed_records(root, ("AUD-C04", "AUD-C05", "AUD-C06"),
                 {"H": "FIXED", "P_R": "FIXED", "Lambda": "FIXED",
                  "Atom": "FIXED"}, packet_sha, prompt_sha)
    cyc.cmd_assess_cycle(_ns(root, assess_cycle="CERTIFICATION_CYCLE_001"))
    cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                             verdict="CERTIFICATION_PASSED",
                             reason="unanimous", material_objections=""))
    cyc.cmd_handoff(_ns(root))
    with open(os.path.join(root, "NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md"),
              encoding="utf-8") as handle:
        doc = handle.read()
    assert "AUD-C07" in doc and "AUD-C09" in doc
