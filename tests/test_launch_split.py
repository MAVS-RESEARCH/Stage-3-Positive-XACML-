"""Split-gate launch + conformance tests (Amendment 007).

Covers battery items: registry shape, launch ingest/unlock matrix,
judge outcomes, quarantine capsule, parser gate, execution lock,
stdout redaction, ledger/outcome bans, seals/specimen stability,
tool-copy currency, launch freeze validity. Synthetic roots except
explicit live-repo checks. No PDP execution.
"""
import hashlib
import json
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import conformance_verify_a as va  # noqa: E402
import conformance_verify_b as vb  # noqa: E402
import launch_certification as launch  # noqa: E402
import launch_freeze as freeze  # noqa: E402

OBLIGATIONS = ["RC-CLASSPATH-ACTUAL", "RC-DEPLOYMENT-ACTUAL",
               "RC-REQUEST-ACTUAL", "RC-LAMBDA-POST", "RC-ATOM-ORDER",
               "RC-DEPS-CONSISTENT"]


def post_execution_authorized():
    """True once authorized Phase-2F execution sealed (Amend.007).

    Pre-execution gate tests (lock absence, pre-pass quarantine) are
    superseded in this state by design; they still assert in
    pre-execution checkouts.
    """
    lock = os.path.join(REPO_ROOT, "artifacts", "seal",
                        "TARGET_EXECUTION_LOCK.json")
    gate = os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                        "RUN_CONFORMANCE_PASS.json")
    if not (os.path.isfile(lock) and os.path.isfile(gate)):
        return False
    try:
        with open(gate, encoding="utf-8") as handle:
            return json.load(handle).get("verdict") == \
                "RUN_CONFORMANCE_PASSED"
    except (OSError, ValueError):
        return False


def write(path, content):
    """Write text, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def good_evidence():
    """Return a fully passing synthetic evidence set."""
    blobs = {"a": "0" * 64, "b": "1" * 64}
    return {
        "RC-LAMBDA-POST": {"pre_hash": "ab" * 32, "post_hash": "ab" * 32},
        "RC-CLASSPATH-ACTUAL": {"expected": blobs, "live": dict(blobs)},
        "RC-DEPLOYMENT-ACTUAL": {"expected": blobs, "live": dict(blobs)},
        "RC-REQUEST-ACTUAL": {"expected": blobs, "live": dict(blobs)},
        "RC-ATOM-ORDER": {"events": ["build_done", "stage_done",
                                     "verify_done", "invoke_start",
                                     "invoke_end", "response_sealed"]},
        "RC-DEPS-CONSISTENT": {"worlds": {"x_permit": blobs,
                                          "x_nonpermit": dict(blobs)}},
    }


def run_verifiers(root, evidence):
    """Run both verifiers over synthetic evidence; return verdict paths."""
    registry = {"obligations": [{"obligation_id": obligation}
                                for obligation in OBLIGATIONS]}
    reg_path = os.path.join(root, "registry.json")
    write(reg_path, json.dumps(registry, indent=2, sort_keys=True))
    ev_dir = os.path.join(root, "evidence")
    for obligation, doc in evidence.items():
        write(os.path.join(ev_dir, obligation + ".json"),
              json.dumps(doc, indent=2, sort_keys=True))
    out_a = os.path.join(root, "a.json")
    out_b = os.path.join(root, "b.json")
    va.main(["conformance_verify_a.py", reg_path, ev_dir, out_a])
    vb.main(["conformance_verify_b.py", reg_path, ev_dir, out_b])
    with open(out_a, encoding="utf-8") as handle:
        result_a = json.load(handle)
    with open(out_b, encoding="utf-8") as handle:
        result_b = json.load(handle)
    assert result_a["verdicts"] == result_b["verdicts"]
    return out_a, out_b, result_a["overall"]


def test_verifiers_agree_pass(tmp_path):
    """Dual verifiers agree SATISFIED on conforming evidence."""
    # [P2-LOG-V20] Test step: assert verifier agreement (pass).
    print("[P2:test:launch:020] verifiers agree pass", flush=True)
    _a, _b, overall = run_verifiers(str(tmp_path / "vpass"),
                                    good_evidence())
    assert overall == "SATISFIED"


def test_verifiers_each_failure_mode(tmp_path):
    """Each failure mode trips both verifiers identically."""
    # [P2-LOG-V22] Test step: assert failure-mode agreement.
    print("[P2:test:launch:022] failure modes", flush=True)
    base = good_evidence()
    mutated = dict(base)
    mutated["RC-LAMBDA-POST"] = {"pre_hash": "ab" * 32,
                                 "post_hash": "cd" * 32}
    _a, _b, overall = run_verifiers(str(tmp_path / "vfail"), mutated)
    assert overall == "FAILED"
    mutated = dict(base)
    mutated["RC-ATOM-ORDER"] = {"events": ["build_done", "invoke_start"]}
    _a, _b, overall = run_verifiers(str(tmp_path / "vorder"), mutated)
    assert overall == "FAILED"
    mutated = dict(base)
    mutated["RC-DEPLOYMENT-ACTUAL"] = {"expected": {"a": "0" * 64}}
    _a, _b, overall = run_verifiers(str(tmp_path / "vunver"), mutated)
    assert overall == "UNVERIFIABLE"


def test_judge_outcomes(tmp_path):
    """Judge seals exactly one outcome record per agreement class."""
    # [P2-LOG-V24] Test step: assert judge outcomes.
    print("[P2:test:launch:024] judge outcomes", flush=True)
    out_a, out_b, _overall = run_verifiers(str(tmp_path / "jpass"),
                                           good_evidence())
    for launch_dir in ("launch", "launch2", "launch3"):
        write(os.path.join(str(tmp_path / launch_dir),
                           "run_conformance_obligations.json"),
              json.dumps({"obligations": [{"obligation_id": oid}
                                          for oid in OBLIGATIONS]},
                         indent=2, sort_keys=True))
    outcome = freeze.judge_conformance(out_a, out_b,
                                       str(tmp_path / "launch"))
    assert outcome == "RUN_CONFORMANCE_PASSED"
    with open(os.path.join(str(tmp_path / "launch"),
                           "RUN_CONFORMANCE_PASS.json"),
              encoding="utf-8") as handle:
        assert json.load(handle)["verdict"] == "RUN_CONFORMANCE_PASSED"
    mutated = dict(good_evidence())
    mutated["RC-REQUEST-ACTUAL"] = {"expected": {"a": "0" * 64},
                                    "live": {"a": "1" * 64}}
    out_a, out_b, _overall = run_verifiers(str(tmp_path / "jfail"), mutated)
    outcome = freeze.judge_conformance(out_a, out_b,
                                      str(tmp_path / "launch2"))
    assert outcome == "EXECUTION_CONFORMANCE_FAIL"
    with open(out_a, encoding="utf-8") as handle:
        tampered = json.load(handle)
    tampered["overall"] = "SATISFIED"
    tampered_path = os.path.join(str(tmp_path), "tampered.json")
    write(tampered_path, json.dumps(tampered, indent=2, sort_keys=True))
    outcome = freeze.judge_conformance(out_a, tampered_path,
                                      str(tmp_path / "launch3"))
    assert outcome == "EXECUTION_CONFORMANCE_VERIFIER_MISMATCH"


def test_registry_schema_live():
    """Live registry validates: 6 obligations, binary predicates, no leaks."""
    # [P2-LOG-V26] Test step: assert registry shape.
    print("[P2:test:launch:026] registry shape", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                           "run_conformance_obligations.json"),
              encoding="utf-8") as handle:
        doc = json.load(handle)
    assert [entry["obligation_id"] for entry in doc["obligations"]] == \
        OBLIGATIONS
    text = json.dumps({key: value for key, value in doc.items()
                       if key != "registry_id"})
    # Content ban scopes to semantic fields only: the prohibited_fields
    # allowlists legitimately name banned strings (D03 fix). Scan every
    # obligation field EXCEPT its own prohibited_fields list.
    for entry in doc["obligations"]:
        scoped = {key: value for key, value in entry.items()
                  if key != "prohibited_fields"}
        scoped_text = json.dumps(scoped)
        for forbidden in ("Permit", "NotApplicable", "expected_touch",
                          "expected_K", "expected_signature", "touch",
                          "classification"):
            assert forbidden not in scoped_text, (entry["obligation_id"],
                                                  forbidden)
        # The ban list itself must declare the outcome quarantine.
        for required in ("Decision", "Permit", "NotApplicable", "touch",
                         "K", "classification", "expected_*"):
            assert required in entry["prohibited_fields"], \
                (entry["obligation_id"], required)
    for entry in doc["obligations"]:
        assert entry["needs_decision_content"] is False
        assert entry["pass_criterion"].strip() != ""
        assert "TERMINAL" in entry["failure_outcome"]


def test_parser_gate_closed_without_pass(tmp_path):
    """Parser refuses quarantined target files before conformance pass."""
    # [P2-LOG-V28] Test step: assert parser quarantine gate.
    print("[P2:test:launch:028] parser gate closed", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))
    import parse_response
    target = os.path.join(str(tmp_path), "target_x_permit_actual.xml")
    write(target, "<Result xmlns=\"urn:oasis:names:tc:xacml:3.0:core:schema"
                  ":wd-17\"><Decision>Permit</Decision></Result>\n")
    try:
        parse_response.main(["parse_response.py", target,
                             os.path.join(REPO_ROOT, "external",
                                          "authzforce", "fixture",
                                          "response.xml"),
                             os.path.join(str(tmp_path), "out.json")])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("parser opened quarantined target")


def test_parser_gate_original_still_works(tmp_path):
    """Parser still compares the frozen original fixture freely."""
    # [P2-LOG-V30] Test step: assert original-fixture path open.
    print("[P2:test:launch:030] original path open", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))
    import parse_response
    parse_response.main([
        "parse_response.py",
        os.path.join(REPO_ROOT, "artifacts", "raw",
                     "original_response_actual.xml"),
        os.path.join(REPO_ROOT, "external", "authzforce", "fixture",
                     "response.xml"),
        os.path.join(str(tmp_path), "out.json")])
    with open(os.path.join(str(tmp_path), "out.json"),
              encoding="utf-8") as handle:
        assert json.load(handle)["semantic_match"] is True


def test_execution_lock_unit(tmp_path):
    """Lock records worlds cumulatively without executing anything."""
    # [P2-LOG-V32] Test step: assert execution lock unit.
    print("[P2:test:launch:032] execution lock", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))
    import run_authzforce
    run_authzforce.write_execution_lock(str(tmp_path), "x_permit")
    run_authzforce.write_execution_lock(str(tmp_path), "x_nonpermit")
    with open(os.path.join(str(tmp_path), "artifacts", "seal",
                           "TARGET_EXECUTION_LOCK.json"),
              encoding="utf-8") as handle:
        record = json.load(handle)
    assert record["worlds"] == ["x_nonpermit", "x_permit"]


def test_no_lock_live():
    """No execution lock exists in the live repo (pre-target)."""
    # [P2-LOG-V34] Test step: assert pre-target lock absence.
    print("[P2:test:launch:034] no live lock", flush=True)
    if post_execution_authorized():
        pytest.skip("authorized Phase-2F execution sealed the lock "
                    "by design; pre-target assert N/A")
    assert not os.path.isfile(os.path.join(
        REPO_ROOT, "artifacts", "seal", "TARGET_EXECUTION_LOCK.json"))


def test_stdout_redacted():
    """Runner logs carry codes/counts, never driver output content."""
    # [P2-LOG-V36] Test step: assert stdout redaction.
    print("[P2:test:launch:036] stdout redaction", flush=True)
    with open(os.path.join(REPO_ROOT, "src", "xacml", "run_authzforce.py"),
              encoding="utf-8") as handle:
        source = handle.read()
    assert "stderr.strip()[-2000:]" not in source
    assert 'splitlines()[-1]' not in source
    assert "stdout_bytes=" in source


def test_ledger_evidence_ban():
    """No ledger evidence embeds Decision/touch/K content."""
    # [P2-LOG-V38] Test step: assert ledger content ban.
    print("[P2:test:launch:038] ledger ban", flush=True)
    for rel in ("derived/anchor_ledger.json",
                "artifacts/audits/semantic_hardening/final_freeze/"
                "FINAL_ANCHOR_LEDGER.json"):
        with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as handle:
            doc = json.load(handle)
        for anchor, record in doc.get("anchors", {}).items():
            text = json.dumps(record.get("evidence", {}))
            for forbidden in ('"Decision"', '"Permit"', '"NotApplicable"',
                              "expected_touch", "expected_K"):
                assert forbidden not in text, (rel, anchor, forbidden)


def test_expected_values_unreachable():
    """Computation sources never open sealed expectation files."""
    # [P2-LOG-V40] Test step: assert expectation isolation.
    print("[P2:test:launch:040] expectation isolation", flush=True)
    import re
    hits = []
    for dirpath, _dirs, files in os.walk(os.path.join(REPO_ROOT, "src")):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            for lineno, line in enumerate(text.splitlines(), 1):
                stripped = line.split("#", 1)[0]
                if re.search(r"open\s*\([^)]*expected_signature",
                             stripped):
                    hits.append("%s:%d" % (
                        os.path.relpath(path, REPO_ROOT), lineno))
    whole = []
    for dirpath, _dirs, files in os.walk(os.path.join(REPO_ROOT, "src")):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8", errors="replace") as handle:
                content = handle.read()
            for token in ("expected_signature", "canary_expectations"):
                if token in content:
                    # Allowlist: denylist literals and comparison-only
                    # readers. Flag Path.read_text / pathlib / getattr-open
                    # exfiltration shapes that the line-grep misses.
                    for lineno, line in enumerate(content.splitlines(), 1):
                        code = line.split("#", 1)[0]
                        if token in code and (
                                "read_text" in code or "pathlib" in code
                                or "Path(" in code):
                            whole.append("%s:%d:%s" % (
                                os.path.relpath(path, REPO_ROOT), lineno,
                                token))
    assert hits == [], hits
    assert whole == [], whole


def test_tool_copy_currency():
    """Packet-bound tool copies equal live sources."""
    # [P2-LOG-V42] Test step: assert tool-copy currency.
    print("[P2:test:launch:042] tool currency", flush=True)
    pairs = [("src/audit/recompute_lambda.py",
              "artifacts/audits/semantic_hardening/rounds/"
              "HARDENING_ROUND_007/evidence/recompute_lambda.py"),
             ("src/audit/verify_deployment_set.py",
              "artifacts/audits/semantic_hardening/rounds/"
              "HARDENING_ROUND_007/evidence/verify_deployment_set.py"),
             ("src/xacml/build_repaired_requests.py",
              "artifacts/audits/semantic_hardening/rounds/"
              "HARDENING_ROUND_007/evidence/wrapper_source/"
              "build_repaired_requests.py")]
    for live_rel, frozen_rel in pairs:
        with open(os.path.join(REPO_ROOT, live_rel), "rb") as handle:
            live = hashlib.sha256(handle.read()).hexdigest()
        with open(os.path.join(REPO_ROOT, frozen_rel), "rb") as handle:
            frozen = hashlib.sha256(handle.read()).hexdigest()
        assert live == frozen, live_rel


def test_historical_seals_stable():
    """CYCLE_001/002 seals and cycle decisions unchanged."""
    # [P2-LOG-V44] Test step: assert historical seal stability.
    print("[P2:test:launch:044] historical seals", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "seal",
                           "FINAL_RESULT.json"),
              encoding="utf-8") as handle:
        assert json.load(handle)["outcome"] == "NATIVE_ANCHOR_INSUFFICIENT"
    with open(os.path.join(REPO_ROOT, "artifacts", "seal",
                           "FINAL_RESULT_CYCLE_002.json"),
              encoding="utf-8") as handle:
        assert json.load(handle)["outcome"] == "NATIVE_ANCHOR_INSUFFICIENT"
    with open(os.path.join(REPO_ROOT, "artifacts", "audits",
                           "certification_cycles", "CYCLES.json"),
              encoding="utf-8") as handle:
        cycles = {record["cycle_id"]: record["status"]
                  for record in json.load(handle)["cycles"]}
    assert cycles["CERTIFICATION_CYCLE_001"] == "SEALED_FAILED_REPAIRABLE"
    assert cycles["CERTIFICATION_CYCLE_002"] == \
        "SEALED_FAILED_IRREDUCIBLE"


def test_launch_ingest_unlock_matrix(tmp_path):
    """Launch ingest/unlock matrix on synthetic roots."""
    # [P2-LOG-V46] Test step: assert launch gate matrix.
    print("[P2:test:launch:046] launch matrix", flush=True)
    root = str(tmp_path / "launch")
    packet = os.path.join(root, "artifacts", "audits", "launch",
                          "launch_packet")
    os.makedirs(packet)
    manifest = {"packet_id": "launch", "files": {}}
    with open(os.path.join(packet, "PACKET_MANIFEST.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    with open(os.path.join(packet, "PACKET_MANIFEST.json"), "rb") as handle:
        packet_sha = hashlib.sha256(handle.read()).hexdigest()
    with open(os.path.join(packet, "PACKET_SHA256.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(packet_sha + "\n")
    prompt = os.path.join(root, "artifacts", "audits", "launch",
                          "launch_certification_prompt.txt")
    with open(prompt, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("launch prompt\n")
    with open(prompt, "rb") as handle:
        prompt_sha = hashlib.sha256(handle.read()).hexdigest()
    registry = {"obligations": [
        {"obligation_id": "RC-LAMBDA-POST"},
        {"obligation_id": "RC-ATOM-ORDER"}]}
    with open(os.path.join(root, "artifacts", "audits", "launch",
                           "run_conformance_obligations.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(registry, handle, indent=2, sort_keys=True)
    with open(os.path.join(root, "artifacts", "audits", "launch",
                           "LAUNCH_FREEZE.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump({"launch_id": "s", "frozen": True,
                   "packet_sha256": packet_sha,
                   "prompt_sha256": prompt_sha,
                   "panel": ["AUD-L01", "AUD-L02", "AUD-L03"]},
                  handle, indent=2, sort_keys=True)
    for auditor in ("AUD-L01", "AUD-L02", "AUD-L03"):
        dest = os.path.join(root, "artifacts", "audits",
                            "launch_certification", auditor)
        os.makedirs(dest)
        text = ("Attestation of %s launch probe. packet %s prompt %s." %
                (auditor, packet_sha, prompt_sha))
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
               "deferrals": {"RC-LAMBDA-POST": "LEGITIMATELY_DEFERRED",
                             "RC-ATOM-ORDER": "LEGITIMATELY_DEFERRED"},
               "attestation_hash": att_hash,
               "declaration": launch.DECLARATION,
               "prompt_sha256": prompt_sha, "packet_sha256": packet_sha,
               "isolation": {"fresh_context": True,
                             "no_prior_experiment_context": True,
                             "other_outputs_unavailable": True}}
        with open(os.path.join(dest, "raw_response.txt"), "w",
                  encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, indent=2, sort_keys=True)
        with open(os.path.join(dest, "raw_response.txt"),
                  encoding="utf-8") as handle:
            stored = handle.read()
        assert json.loads(stored)["deferrals"]["RC-LAMBDA-POST"] == \
            "LEGITIMATELY_DEFERRED"
    assert launch.chair_number("AUD-L100") == 100
    assert launch.chair_id(100) == "AUD-L100"
    assert launch.panel_of("AUD-L02") == ("AUD-L01", "AUD-L02", "AUD-L03")
    assert launch.panel_of("AUD-C04") is None
    try:
        launch.ingest_launch(
            root, "AUD-L01",
            os.path.join(root, "artifacts", "audits",
                         "launch_certification", "AUD-L01",
                         "raw_response.txt"),
            os.path.join(root, "artifacts", "audits",
                         "launch_certification", "AUD-L01",
                         "attestation.txt"))
    except SystemExit as exc:
        assert exc.code == 0, exc.code
    try:
        launch.assert_launch_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("partial launch panel unlocked")


def test_verifiers_reject_decision_plaintext(tmp_path):
    """Evidence carrying Decision/Permit text is UNVERIFIABLE, never pass."""
    # [P2-LOG-V48] Test step: assert outcome-content rejection.
    print("[P2:test:launch:048] evidence content rejection", flush=True)
    registry = {"obligations": [{"obligation_id": "RC-CLASSPATH-ACTUAL"}]}
    reg_path = os.path.join(str(tmp_path), "registry.json")
    write(reg_path, json.dumps(registry, indent=2, sort_keys=True))
    ev_dir = os.path.join(str(tmp_path), "evidence")
    write(os.path.join(ev_dir, "RC-CLASSPATH-ACTUAL.json"), json.dumps(
        {"expected": {"a": "Permit"}, "live": {"a": "Permit"}},
        indent=2, sort_keys=True))
    out_a = os.path.join(str(tmp_path), "a.json")
    out_b = os.path.join(str(tmp_path), "b.json")
    va.main(["conformance_verify_a.py", reg_path, ev_dir, out_a])
    vb.main(["conformance_verify_b.py", reg_path, ev_dir, out_b])
    with open(out_a, encoding="utf-8") as handle:
        assert json.load(handle)["verdicts"]["RC-CLASSPATH-ACTUAL"] == \
            "UNVERIFIABLE"
    with open(out_b, encoding="utf-8") as handle:
        assert json.load(handle)["verdicts"]["RC-CLASSPATH-ACTUAL"] == \
            "UNVERIFIABLE"


def test_judge_missing_registry_unverifiable(tmp_path):
    """Judge with unreadable registry cannot mint a PASS."""
    # [P2-LOG-V50] Test step: assert missing-registry fail-closed.
    print("[P2:test:launch:050] missing registry", flush=True)
    registry = {"obligations": [{"obligation_id": "RC-LAMBDA-POST"}]}
    reg_path = os.path.join(str(tmp_path), "registry.json")
    write(reg_path, json.dumps(registry, indent=2, sort_keys=True))
    ev_dir = os.path.join(str(tmp_path), "evidence")
    write(os.path.join(ev_dir, "RC-LAMBDA-POST.json"), json.dumps(
        {"pre_hash": "ab" * 32, "post_hash": "ab" * 32},
        indent=2, sort_keys=True))
    out_a = os.path.join(str(tmp_path), "a.json")
    out_b = os.path.join(str(tmp_path), "b.json")
    va.main(["conformance_verify_a.py", reg_path, ev_dir, out_a])
    vb.main(["conformance_verify_b.py", reg_path, ev_dir, out_b])
    empty_launch = os.path.join(str(tmp_path), "launch_empty")
    os.makedirs(empty_launch)
    outcome = freeze.judge_conformance(out_a, out_b, empty_launch)
    assert outcome == "EXECUTION_CONFORMANCE_UNVERIFIABLE"
    assert not os.path.isfile(os.path.join(
        empty_launch, "RUN_CONFORMANCE_PASS.json"))


def test_parser_rename_evasion_blocked(tmp_path):
    """Renamed target bytes are still quarantined via content allowlist."""
    # [P2-LOG-V52] Test step: assert rename-evasion block.
    print("[P2:test:launch:052] rename evasion", flush=True)
    if post_execution_authorized():
        pytest.skip("quarantine lifted by RUN_CONFORMANCE_PASSED by "
                    "design; pre-pass block N/A")
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))
    import parse_response
    import shutil
    src = os.path.join(REPO_ROOT, "artifacts", "raw",
                       "original_response_actual.xml")
    evade = os.path.join(str(tmp_path), "evade_copy.xml")
    shutil.copyfile(src, evade)
    with open(evade, "r+b") as handle:
        handle.seek(0, os.SEEK_END)
        handle.write(b"<!-- x -->")
    try:
        parse_response.main(["parse_response.py", evade,
                             os.path.join(REPO_ROOT, "external",
                                          "authzforce", "fixture",
                                          "response.xml"),
                             os.path.join(str(tmp_path), "out.json")])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("renamed bytes bypassed quarantine")


def test_launch_locked_after_execution(tmp_path):
    """Ingest and unlock refuse once the execution lock exists."""
    # [P2-LOG-V54] Test step: assert post-invocation lock closure.
    print("[P2:test:launch:054] post-invocation lock", flush=True)
    root = str(tmp_path / "locked")
    os.makedirs(os.path.join(root, "artifacts", "seal"))
    with open(os.path.join(root, "artifacts", "seal",
                           "TARGET_EXECUTION_LOCK.json"), "w",
               encoding="utf-8", newline="\n") as handle:
        json.dump({"lock_id": "t", "worlds": ["x_permit"]}, handle)
    raw = os.path.join(str(tmp_path), "raw.txt")
    att = os.path.join(str(tmp_path), "att.txt")
    write(raw, "{}")
    write(att, "AUD-L01")
    try:
        launch.ingest_launch(root, "AUD-L01", raw, att)
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("ingest passed post-lock")
    try:
        launch.assert_launch_unlock(root)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("unlock passed post-lock")


def test_launch_packet_poms_distinct():
    """Both poms staged under distinct names with manifest-matching bytes."""
    # [P2-LOG-V56] Test step: assert pom-collision regression (L01-03).
    print("[P2:test:launch:056] pom staging", flush=True)
    packet = os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                          "launch_packet")
    with open(os.path.join(packet, "PACKET_MANIFEST.json"),
              encoding="utf-8") as handle:
        files = json.load(handle)["files"]
    for key in ("candidates/built/poms/root-pom.xml",
                "candidates/built/poms/pdp-engine-pom.xml"):
        assert key in files, key
    with open(os.path.join(packet, "candidates", "lambda_manifest.json"),
              encoding="utf-8") as handle:
        poms = json.load(handle)["components"]["built_artifacts"]["poms"]
    want = {entry["path"]: entry["sha256"] for entry in poms}
    assert set(want) == {"pom.xml", "pdp-engine/pom.xml"}
    pairs = {"pom.xml": "candidates/built/poms/root-pom.xml",
             "pdp-engine/pom.xml":
             "candidates/built/poms/pdp-engine-pom.xml"}
    for manifest_path, packet_key in pairs.items():
        with open(os.path.join(packet, *packet_key.split("/")), "rb") \
                as handle:
            assert hashlib.sha256(handle.read()).hexdigest() == \
                want[manifest_path], packet_key


def test_launch_packet_manifest_driver_currency():
    """Staged manifest drivers equal staged invocation bytes; composite ok."""
    # [P2-LOG-V58] Test step: assert driver-currency regression (L01-03).
    print("[P2:test:launch:058] driver currency", flush=True)
    packet = os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                          "launch_packet")
    with open(os.path.join(packet, "candidates", "lambda_manifest.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    composite = json.dumps(
        {"components": manifest["components"],
         "exclusions": manifest["exclusions"]},
        sort_keys=True, ensure_ascii=True,
        separators=(", ", ": ")).encode("utf-8")
    assert hashlib.sha256(composite).hexdigest() == manifest["pre_hash"]
    inv_map = {"src/xacml/PdpRunner.java":
               "candidates/invocation/PdpRunner.java",
               "src/xacml/run_authzforce.py":
               "candidates/invocation/run_authzforce.py"}
    for entry in manifest["components"]["built_artifacts"]["drivers"]:
        staged = os.path.join(packet, *inv_map[entry["path"]].split("/"))
        with open(staged, "rb") as handle:
            assert hashlib.sha256(handle.read()).hexdigest() == \
                entry["sha256"], entry["path"]
        assert os.path.getsize(staged) == entry["bytes"], entry["path"]
    with open(os.path.join(packet, "candidates", "pre_hash_lineage.json"),
              encoding="utf-8") as handle:
        lineage = json.load(handle)
    assert lineage["current"]["pre_hash"] == manifest["pre_hash"]
    with open(os.path.join(packet, "candidates",
                           "dependency_hashes.json"),
              encoding="utf-8") as handle:
        deps = json.load(handle)
    assert deps["count"] == len(deps["entries"]) >= 100
    assert manifest["components"]["dependency_content"]["count"] == \
        deps["count"]


def test_launch_packet_dependency_file_hash():
    """Manifest dependency_content binds staged file bytes (R7-12)."""
    # [P2-LOG-V60] Test step: assert file-hash binding.
    print("[P2:test:launch:060] dependency binding", flush=True)
    packet = os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                          "launch_packet")
    with open(os.path.join(packet, "candidates", "lambda_manifest.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    dep_path = os.path.join(packet, "candidates", "dependency_hashes.json")
    with open(dep_path, "rb") as handle:
        assert hashlib.sha256(handle.read()).hexdigest() == \
            manifest["components"]["dependency_content"]["sha256"]
    with open(dep_path, encoding="utf-8") as handle:
        deps = json.load(handle)
    assert deps["count"] == len(deps["entries"]) >= 100


def test_launch_packet_path_remap():
    """Every manifest built path resolves to an existing packet file."""
    # [P2-LOG-V62] Test step: assert remap completeness (R7-13).
    print("[P2:test:launch:062] path remap", flush=True)
    packet = os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                          "launch_packet")
    with open(os.path.join(packet, "candidates", "path_remap.json"),
              encoding="utf-8") as handle:
        remap = json.load(handle)["mappings"]
    with open(os.path.join(packet, "candidates", "lambda_manifest.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    with open(os.path.join(packet, "PACKET_MANIFEST.json"),
              encoding="utf-8") as handle:
        files = set(json.load(handle)["files"])
    for group in ("drivers", "jars", "poms"):
        for entry in manifest["components"]["built_artifacts"][group]:
            target = remap.get(entry["path"], "")
            assert target, entry["path"]
            assert target in files, target
            assert os.path.isfile(os.path.join(
                packet, *target.split("/"))), target


def test_recompute_extended_live_packet():
    """Extended recompute passes on the live launch packet."""
    # [P2-LOG-V64] Test step: assert extended recompute (R7-14).
    print("[P2:test:launch:064] extended recompute", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))
    import recompute_lambda as rec
    packet = os.path.join(REPO_ROOT, "artifacts", "audits", "launch",
                          "launch_packet")
    assert rec.main(["--manifest", os.path.join(
        packet, "candidates", "lambda_manifest.json"),
        "--packet-dir", packet]) is None


def test_chronology_writer_unit(tmp_path):
    """Chronology emits the frozen six events with no outcome content."""
    # [P2-LOG-V66] Test step: assert chronology producer (R7-15).
    print("[P2:test:launch:066] chronology unit", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))
    import run_authzforce
    for event in ("build_done", "stage_done", "verify_done",
                  "invoke_start", "invoke_end", "response_sealed"):
        run_authzforce.write_chronology(
            str(tmp_path), "x_permit", event,
            {"request_sha256": "ab" * 32} if event == "build_done"
            else None)
    with open(os.path.join(str(tmp_path), "chronology_x_permit.jsonl"),
              encoding="utf-8") as handle:
        events = [json.loads(line)["event"] for line in handle]
    assert events == ["build_done", "stage_done", "verify_done",
                      "invoke_start", "invoke_end", "response_sealed"]
    with open(os.path.join(str(tmp_path), "chronology_x_permit.jsonl"),
              encoding="utf-8") as handle:
        text = handle.read()
    for banned in ("Decision", "Permit", "NotApplicable"):
        assert banned not in text


def test_hash_cp_unit(tmp_path):
    """--hash-cp freezes every listed jar (R7-16)."""
    # [P2-LOG-V68] Test step: assert cp-hasher producer.
    print("[P2:test:launch:068] hash-cp unit", flush=True)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))
    import verify_deployment_set as gate
    jars = os.path.join(str(tmp_path), "jars")
    os.makedirs(jars)
    with open(os.path.join(jars, "a.jar"), "w", encoding="utf-8",
              newline="\n") as handle:
        handle.write("A")
    with open(os.path.join(jars, "b.jar"), "w", encoding="utf-8",
              newline="\n") as handle:
        handle.write("BB")
    cp_file = os.path.join(str(tmp_path), "cp.txt")
    with open(cp_file, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(os.path.join(jars, "a.jar") + ";" +
                     os.path.join(jars, "b.jar"))
    out = os.path.join(str(tmp_path), "cp_manifest.json")
    gate.main(["--repo-root", REPO_ROOT, "--hash-cp", "--cp-file",
               cp_file, "--out", out, "--world", "x_permit"])
    with open(out, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert doc["count"] == 2 and doc["world"] == "x_permit"
    assert sorted(entry["bytes"] for entry in doc["entries"]) == [1, 2]
