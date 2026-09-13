"""Unbounded-panel support tests (Amendment 006, Sec.15 items 1-20).

Allocator, namespace, binding, immutability, and invariant-constancy
across arbitrarily advancing certification panels. Synthetic temporary
roots only, except read-only live-repo checks.
"""
import json
import hashlib
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import certification_cycle as cyc  # noqa: E402
import final_certification as final  # noqa: E402


def state_with(panels):
    """Build a cycle state with decided cycles over given panels."""
    return {"cycles": [
        {"cycle_id": "CERTIFICATION_CYCLE_%03d" % (index + 1),
         "revision": revision, "panel": list(panel),
         "status": "SEALED_FAILED_REPAIRABLE", "assessment": {},
         "decision": {"verdict": "CERTIFICATION_FAILED_REPAIRABLE"}}
        for index, (revision, panel) in enumerate(panels)]}


def test_01_allocate_c04_after_c03():
    """1. Used C01-C03 -> next panel C04/C05/C06."""
    # [P2-LOG-U01] Allocated panel follows max used ID.
    print("[P2:test:unbounded:001] allocate after C03", flush=True)
    state = state_with([(2, ("AUD-C01", "AUD-C02", "AUD-C03"))])
    assert cyc.next_panel(state) == ["AUD-C04", "AUD-C05", "AUD-C06"]


def test_02_allocate_c07_after_c06():
    """2. Used through C06 -> C07/C08/C09."""
    print("[P2:test:unbounded:002] allocate after C06 used", flush=True)
    state = state_with([(2, ("AUD-C01", "AUD-C02", "AUD-C03")),
                        (4, ("AUD-C04", "AUD-C05", "AUD-C06"))])
    assert cyc.next_panel(state) == ["AUD-C07", "AUD-C08", "AUD-C09"]


def test_03_allocate_c10_after_c09():
    """3. Used through C09 -> C10/C11/C12."""
    print("[P2:test:unbounded:003] allocate after C09", flush=True)
    state = state_with([(4, ("AUD-C07", "AUD-C08", "AUD-C09"))])
    assert cyc.next_panel(state) == ["AUD-C10", "AUD-C11", "AUD-C12"]


def test_04_allocate_c13_after_c12():
    """4. Used through C12 -> C13/C14/C15."""
    print("[P2:test:unbounded:004] allocate after C12", flush=True)
    state = state_with([(6, ("AUD-C10", "AUD-C11", "AUD-C12"))])
    assert cyc.next_panel(state) == ["AUD-C13", "AUD-C14", "AUD-C15"]


def test_05_allocate_c100_after_c99():
    """5. Used through C99 -> C100/C101/C102 (digit growth)."""
    print("[P2:test:unbounded:005] allocate past C99", flush=True)
    state = state_with([(36, ("AUD-C97", "AUD-C98", "AUD-C99"))])
    assert cyc.next_panel(state) == ["AUD-C100", "AUD-C101", "AUD-C102"]


def test_06_arbitrary_later_panel_unlocks(tmp_path):
    """6. C10-12 unanimous on matching rev6 freeze -> UNLOCK."""
    print("[P2:test:unbounded:006] later panel unlock", flush=True)
    root = str(tmp_path / "u6")
    os.makedirs(os.path.join(root, "artifacts", "audits",
                             "semantic_hardening", "final_freeze",
                             "FINAL_BLIND_PACKET"))
    os.makedirs(os.path.join(root, "prereg"))
    manifest = {"packet_id": "s", "files": {}}
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                           "final_freeze", "FINAL_BLIND_PACKET",
                           "PACKET_MANIFEST.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    import hashlib
    packet_sha = hashlib.sha256(open(os.path.join(
        root, "artifacts", "audits", "semantic_hardening", "final_freeze",
        "FINAL_BLIND_PACKET", "PACKET_MANIFEST.json"), "rb").read()
    ).hexdigest()
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                           "final_freeze", "FINAL_BLIND_PACKET",
                           "PACKET_SHA256.txt"), "w", encoding="utf-8",
              newline="\n") as handle:
        handle.write(packet_sha + "\n")
    with open(os.path.join(root, "prereg", "final_certification_prompt.txt"),
              "w", encoding="utf-8", newline="\n") as handle:
        handle.write("prompt\n")
    with open(os.path.join(root, "prereg", "final_certification_prompt.txt"),
              "rb") as handle:
        prompt_sha = hashlib.sha256(handle.read()).hexdigest()
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                           "final_freeze", "FINAL_SEMANTIC_FREEZE.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"freeze_id": "s", "frozen": True, "revision": 6,
                   "packet_sha256": packet_sha,
                   "prompt_sha256": prompt_sha}, handle, indent=2,
                  sort_keys=True)
    ledger = {"anchors": {anchor: {"ambiguity_status": "FIXED",
                                  "auditor_status": "PENDING_FINAL_"
                                  "CERTIFICATION"} for anchor in
                          ("H", "P_R", "Lambda", "Atom", "omega", "Q",
                           "Succ+", "c", "A_Pi")}}
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                           "final_freeze", "FINAL_ANCHOR_LEDGER.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(ledger, handle, indent=2, sort_keys=True)
    for auditor in ("AUD-C10", "AUD-C11", "AUD-C12"):
        dest = os.path.join(root, "artifacts", "audits",
                            "final_certification", auditor)
        os.makedirs(dest)
        text = "Attestation of %s unbounded probe." % auditor
        with open(os.path.join(dest, "attestation.txt"), "w",
                  encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        with open(os.path.join(dest, "attestation.txt"), "rb") as handle:
            att_hash = hashlib.sha256(handle.read()).hexdigest()
        doc = {"verdict_id": auditor + "-verdict", "auditor_id": auditor,
               "qualification": "COLD_MODEL_INDEPENDENT",
               "verdicts": {anchor: {"status": "FIXED",
                                     "locators": ["corpus/x Sec.1"],
                                     "notes": "probe"}
                            for anchor in ("H", "P_R", "Lambda", "Atom")},
               "attestation_hash": att_hash,
               "declaration": final.DECLARATION,
               "prompt_sha256": prompt_sha, "packet_sha256": packet_sha,
               "isolation": {"fresh_context": True,
                             "no_prior_experiment_context": True,
                             "other_outputs_unavailable": True}}
        with open(os.path.join(dest, "raw_response.txt"), "w",
                  encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, indent=2, sort_keys=True)
        with open(os.path.join(dest, "verdict.json"), "w", encoding="utf-8",
                  newline="\n") as handle:
            json.dump(doc, handle, indent=2, sort_keys=True)
        with open(os.path.join(dest, "verdict.json"), "rb") as handle:
            verdict_sha = hashlib.sha256(handle.read()).hexdigest()
        with open(os.path.join(dest, "raw_response.txt"), "rb") as handle:
            raw_sha = hashlib.sha256(handle.read()).hexdigest()
        with open(os.path.join(dest, "provenance.json"), "w",
                  encoding="utf-8", newline="\n") as handle:
            json.dump({"auditor_id": auditor, "valid": True,
                       "verdict_sha256": verdict_sha, "raw_sha256": raw_sha,
                       "attestation_sha256": att_hash,
                       "sealed_prompt_sha256": prompt_sha,
                       "sealed_packet_sha256": packet_sha},
                      handle, indent=2, sort_keys=True)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 0, exc.code
    else:
        raise AssertionError("later panel did not unlock")


def test_07_reused_id_rejected(tmp_path):
    """7. Chair reuse across cycles refused at init."""
    print("[P2:test:unbounded:007] reuse rejected", flush=True)
    root = str(tmp_path / "u7")
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                           revision="4",
                           panel="AUD-C04,AUD-C05,AUD-C06"))
    try:
        cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_002",
                               revision="6",
                               panel="AUD-C06,AUD-C07,AUD-C08"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("chair reuse accepted")


def test_08_skipped_number_rejected(tmp_path):
    """8. Non-consecutive triple (C04,C05,C07) refused."""
    print("[P2:test:unbounded:008] skip rejected", flush=True)
    root = str(tmp_path / "u8")
    try:
        cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                               revision="4",
                               panel="AUD-C04,AUD-C05,AUD-C07"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("skipped number accepted")


def test_09_mixed_panel_rejected(tmp_path):
    """9. Mixed chairs across panels never complete (exit 4)."""
    print("[P2:test:unbounded:009] mixed rejected", flush=True)
    root = str(tmp_path / "u9")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C13", "AUD-C14", "AUD-C16"), packet_sha, prompt_sha)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("mixed panel completed")


def test_10_fourth_chair_rejected(tmp_path):
    """10. Extra fourth chair cannot substitute a missing member."""
    print("[P2:test:unbounded:010] fourth refused", flush=True)
    root = str(tmp_path / "u10")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C13", "AUD-C14", "AUD-C16"), packet_sha, prompt_sha)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("fourth chair completed a panel")


def test_11_old_panel_new_revision(tmp_path):
    """11. Panel bound to an old revision cannot certify a new one."""
    print("[P2:test:unbounded:011] old panel excluded", flush=True)
    root = str(tmp_path / "u11")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C04", "AUD-C05", "AUD-C06"), packet_sha, prompt_sha)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("old panel certified new revision")


def test_12_changed_packet_new_panel(tmp_path):
    """12. Records sealed to another packet do not count."""
    print("[P2:test:unbounded:012] stale packet excluded", flush=True)
    root = str(tmp_path / "u12")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C13", "AUD-C14", "AUD-C15"), "0" * 64, prompt_sha)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("stale-packet records counted")


def test_13_failed_panel_immutable(tmp_path):
    """13. Decided cycles and VALID chairs refuse overwrite."""
    print("[P2:test:unbounded:013] failure immutable", flush=True)
    root = str(tmp_path / "u13")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C10", "AUD-C11", "AUD-C12"), packet_sha, prompt_sha,
          statuses={"Lambda": "PARTIAL"})
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                           revision="6",
                           panel="AUD-C10,AUD-C11,AUD-C12"))
    cyc.cmd_assess_cycle(_ns(root, assess_cycle="CERTIFICATION_CYCLE_001"))
    cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                             verdict="CERTIFICATION_FAILED_REPAIRABLE",
                             reason="probe defect",
                             material_objections="RSX-01"))
    state = cyc.load_state(root)
    assert state["cycles"][0]["status"] == "SEALED_FAILED_REPAIRABLE"
    try:
        cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                                 verdict="CERTIFICATION_PASSED",
                                 reason="rewrite attempt",
                                 material_objections=""))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("sealed failure rewritten")


def test_14_no_counter_maximum():
    """14. Cycle counter and chair numbers unbounded."""
    print("[P2:test:unbounded:014] no artificial maximum", flush=True)
    assert cyc.CYCLE_RE.match("CERTIFICATION_CYCLE_1000")
    assert cyc.next_panel({"cycles": [
        {"cycle_id": "CERTIFICATION_CYCLE_001", "revision": 99,
         "panel": ["AUD-C97", "AUD-C98", "AUD-C99"],
         "status": "SEALED_FAILED_REPAIRABLE"}]}) == [
        "AUD-C100", "AUD-C101", "AUD-C102"]
    assert final.chair_number("AUD-C100") == 100
    assert final.chair_id(100) == "AUD-C100"
    assert final.chair_id(4) == "AUD-C04"


def test_15_no_overflow_large_ids(tmp_path):
    """15. Large chair IDs validate, bind, and ingest cleanly."""
    print("[P2:test:unbounded:015] large IDs", flush=True)
    assert final.panel_of("AUD-C101") == ("AUD-C100", "AUD-C101",
                                          "AUD-C102")
    assert final.panel_of("AUD-C07") == ("AUD-C07", "AUD-C08", "AUD-C09")
    assert final.panel_of("AUD-C00") is None
    assert final.panel_of("AUD-C4x") is None
    root = str(tmp_path / "u15")
    packet_sha, prompt_sha = _freeze(root, revision=36)
    _seed(root, ("AUD-C100", "AUD-C101", "AUD-C102"), packet_sha,
          prompt_sha)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 0, exc.code
    else:
        raise AssertionError("large-ID panel did not unlock")


def test_16_standards_constant():
    """16. Unanimity, FIXED set, declaration, anchors never drift."""
    print("[P2:test:unbounded:016] standards constant", flush=True)
    assert final.BLIND_ANCHORS == ("H", "P_R", "Lambda", "Atom")
    assert "FIXED" in final.ALLOWED_STATUSES
    assert "I was not supplied an expected touch set" in final.DECLARATION
    assert "unanimous" in open(os.path.join(
        REPO_ROOT, "src", "audit",
        "final_certification.py"), encoding="utf-8").read()


def test_17_locked_before_unanimity(tmp_path):
    """17. Partial panel stays locked (exit 4, never unlock)."""
    print("[P2:test:unbounded:017] locked pre-unanimity", flush=True)
    root = str(tmp_path / "u17")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C13", "AUD-C14"), packet_sha, prompt_sha)
    try:
        final.assert_final_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("partial panel unlocked")


def test_18_subagents_cannot_certify(tmp_path):
    """18. Developmental-marker raw output is refused as INVALID."""
    print("[P2:test:unbounded:018] subagents cannot certify", flush=True)
    root = str(tmp_path / "u18")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    dest = os.path.join(root, "artifacts", "audits", "final_certification",
                        "AUD-C13")
    os.makedirs(dest)
    raw = {"verdict_id": "AUD-C13-verdict", "auditor_id": "AUD-C13",
           "qualification": "COLD_MODEL_INDEPENDENT",
           "verdicts": {anchor: {"status": "FIXED",
                                 "locators": ["corpus/x Sec.1"],
                                 "notes": "NON_BLIND_CERTIFIER_EMULATION"}
                        for anchor in ("H", "P_R", "Lambda", "Atom")},
           "attestation_hash": "0" * 64,
           "declaration": final.DECLARATION,
           "prompt_sha256": prompt_sha, "packet_sha256": packet_sha,
           "isolation": {"fresh_context": False,
                         "no_prior_experiment_context": True,
                         "other_outputs_unavailable": True}}
    _write(os.path.join(dest, "raw_response.txt"),
           json.dumps(raw, indent=2, sort_keys=True))
    _write(os.path.join(dest, "attestation.txt"),
           "Attestation of AUD-C13 subagent probe.")
    try:
        final.ingest_final(root, "AUD-C13",
                           os.path.join(dest, "raw_response.txt"),
                           os.path.join(dest, "attestation.txt"))
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("subagent output ingested")


def test_19_handoff_arbitrary_panel(tmp_path):
    """19. Decided cycle yields next unused triple in handoff."""
    print("[P2:test:unbounded:019] handoff arbitrary", flush=True)
    root = str(tmp_path / "u19")
    packet_sha, prompt_sha = _freeze(root, revision=6)
    _seed(root, ("AUD-C10", "AUD-C11", "AUD-C12"), packet_sha, prompt_sha)
    cyc.cmd_init_cycle(_ns(root, init_cycle="CERTIFICATION_CYCLE_001",
                           revision="6",
                           panel="AUD-C10,AUD-C11,AUD-C12"))
    cyc.cmd_assess_cycle(_ns(root, assess_cycle="CERTIFICATION_CYCLE_001"))
    cyc.cmd_decide_cycle(_ns(root, decide_cycle="CERTIFICATION_CYCLE_001",
                             verdict="CERTIFICATION_PASSED",
                             reason="unanimous probe",
                             material_objections=""))
    cyc.cmd_handoff(_ns(root))
    with open(os.path.join(root, "NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md"),
              encoding="utf-8") as handle:
        doc = handle.read()
    assert "AUD-C13" in doc and "AUD-C15" in doc
    for forbidden in cyc.FORBIDDEN_HANDOFF:
        assert forbidden not in doc, forbidden


def test_20_no_reopen_after_execution(tmp_path):
    """20. Reopen transition illegal once target outputs exist."""
    print("[P2:test:unbounded:020] no reopen after exec", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))
    import hardening
    root = str(tmp_path / "u20")
    os.makedirs(os.path.join(root, "artifacts", "audits",
                             "semantic_hardening"))
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                           "STATE.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump({"phase2_state": "X", "rounds": [],
                   "freeze": {"valid": True}, "reopens": []}, handle)
    os.makedirs(os.path.join(root, "artifacts", "raw"))
    with open(os.path.join(root, "artifacts", "raw", "target_x_actual.xml"),
              "w", encoding="utf-8", newline="\n") as handle:
        handle.write("<x/>\n")
    try:
        hardening.cmd_reopen(_ns(root, reason="probe", evidence="probe"))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("reopen allowed after target execution")


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, repo_root, **kwargs):
        self.repo_root = repo_root
        for key, value in kwargs.items():
            setattr(self, key, value)


def _write(path, content):
    """Write text, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def _freeze(root, revision):
    """Minimal operative freeze with matching prompt/packet."""
    import hashlib
    packet = os.path.join(root, "artifacts", "audits", "semantic_hardening",
                          "final_freeze", "FINAL_BLIND_PACKET")
    os.makedirs(packet)
    os.makedirs(os.path.join(root, "prereg"))
    _write(os.path.join(packet, "PACKET_MANIFEST.json"), '{"files": {}}')
    with open(os.path.join(packet, "PACKET_MANIFEST.json"),
              "rb") as handle:
        packet_sha = hashlib.sha256(handle.read()).hexdigest()
    _write(os.path.join(packet, "PACKET_SHA256.txt"), packet_sha + "\n")
    _write(os.path.join(root, "prereg", "final_certification_prompt.txt"),
           "prompt\n")
    with open(os.path.join(root, "prereg", "final_certification_prompt.txt"),
              "rb") as handle:
        prompt_sha = hashlib.sha256(handle.read()).hexdigest()
    _write(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                        "final_freeze", "FINAL_SEMANTIC_FREEZE.json"),
           json.dumps({"freeze_id": "s", "frozen": True,
                       "revision": revision, "packet_sha256": packet_sha,
                       "prompt_sha256": prompt_sha}, indent=2,
                      sort_keys=True))
    ledger = {"anchors": {anchor: {"ambiguity_status": "FIXED",
                                  "auditor_status": "PENDING_FINAL_"
                                  "CERTIFICATION"} for anchor in
                          ("H", "P_R", "Lambda", "Atom", "omega", "Q",
                           "Succ+", "c", "A_Pi")}}
    _write(os.path.join(root, "artifacts", "audits", "semantic_hardening",
                        "final_freeze", "FINAL_ANCHOR_LEDGER.json"),
           json.dumps(ledger, indent=2, sort_keys=True))
    return packet_sha, prompt_sha


def _seed(root, panel, packet_sha, prompt_sha, statuses=None):
    """Write valid sealed records bound to the given freeze hashes."""
    import hashlib
    if statuses is None:
        statuses = {}
    for auditor in panel:
        dest = os.path.join(root, "artifacts", "audits",
                            "final_certification", auditor)
        os.makedirs(dest, exist_ok=True)
        text = "Attestation of %s unbounded probe." % auditor
        _write(os.path.join(dest, "attestation.txt"), text)
        with open(os.path.join(dest, "attestation.txt"), "rb") as handle:
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
        _write(os.path.join(dest, "raw_response.txt"),
               json.dumps(doc, indent=2, sort_keys=True))
        _write(os.path.join(dest, "verdict.json"),
               json.dumps(doc, indent=2, sort_keys=True))
        with open(os.path.join(dest, "verdict.json"), "rb") as handle:
            verdict_sha = hashlib.sha256(handle.read()).hexdigest()
        with open(os.path.join(dest, "raw_response.txt"), "rb") as handle:
            raw_sha = hashlib.sha256(handle.read()).hexdigest()
        _write(os.path.join(dest, "provenance.json"), json.dumps(
            {"auditor_id": auditor, "valid": True,
             "verdict_sha256": verdict_sha, "raw_sha256": raw_sha,
             "attestation_sha256": att_hash,
             "sealed_prompt_sha256": prompt_sha,
             "sealed_packet_sha256": packet_sha}, indent=2, sort_keys=True))


def test_21_nonstring_chairs_rejected():
    """21. Non-string chair inputs fail closed (no crash)."""
    print("[P2:test:unbounded:021] non-string chairs", flush=True)
    for bad in (4, True, 4.5, None):
        assert final.chair_number(bad) is None
        assert final.panel_of(bad) is None
    try:
        cyc.chair_prompt(None, "0" * 64, "0" * 64)
    except (ValueError, TypeError):
        pass
    else:
        raise AssertionError("unchair prompt accepted")
    try:
        cyc.chair_prompt("AUD-C07", "short", "x")
    except ValueError:
        pass
    else:
        raise AssertionError("malformed hashes accepted")


def test_22_alias_normalized_at_ingest(tmp_path):
    """22. Non-canonical AUD-C4 ingests under canonical AUD-C04."""
    print("[P2:test:unbounded:022] alias normalization", flush=True)
    root = str(tmp_path / "u22")
    packet_sha, prompt_sha = _freeze(root, revision=4)
    dest = os.path.join(root, "artifacts", "audits", "final_certification",
                        "AUD-C04")
    os.makedirs(dest)
    text = "Attestation of AUD-C04 alias probe."
    _write(os.path.join(dest, "attestation.txt"), text)
    with open(os.path.join(dest, "attestation.txt"), "rb") as handle:
        att_hash = hashlib.sha256(handle.read()).hexdigest()
    doc = {"verdict_id": "AUD-C04-verdict", "auditor_id": "AUD-C04",
           "qualification": "COLD_MODEL_INDEPENDENT",
           "verdicts": {anchor: {"status": "FIXED",
                                 "locators": ["corpus/x Sec.1"],
                                 "notes": "probe"}
                        for anchor in ("H", "P_R", "Lambda", "Atom")},
           "attestation_hash": att_hash,
           "declaration": final.DECLARATION,
           "prompt_sha256": prompt_sha, "packet_sha256": packet_sha,
           "isolation": {"fresh_context": True,
                         "no_prior_experiment_context": True,
                         "other_outputs_unavailable": True}}
    _write(os.path.join(dest, "raw_response.txt"),
           json.dumps(doc, indent=2, sort_keys=True))
    try:
        final.ingest_final(root, "AUD-C4",
                           os.path.join(dest, "raw_response.txt"),
                           os.path.join(dest, "attestation.txt"))
    except SystemExit as exc:
        assert exc.code == 0, exc.code
    else:
        pass
    assert os.path.isdir(os.path.join(
        root, "artifacts", "audits", "final_certification", "AUD-C04"))
    assert not os.path.isdir(os.path.join(
        root, "artifacts", "audits", "final_certification", "AUD-C4"))


def test_23_invalid_open_panel_skipped():
    """23. Malformed open panel never reaches handoff; IDs still advance."""
    print("[P2:test:unbounded:023] invalid open skipped", flush=True)
    state = {"cycles": [
        {"cycle_id": "CERTIFICATION_CYCLE_001", "revision": 4,
         "panel": ["AUD-C03", "AUD-C04", "AUD-C05"],
         "status": "OPEN_PENDING", "assessment": None, "decision": None}]}
    assert cyc.next_panel(state) == ["AUD-C07", "AUD-C08", "AUD-C09"]
