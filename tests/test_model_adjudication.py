"""Amendment-001 adversarial gate controls (18 checks).

Exercises the amended cold-model unanimity gate on synthetic temporary
roots (never the real artifacts): locked/invalid/nonunanimous/unlock
outcomes, tamper detection, leakage rejection, isolation, chronology,
and real-checkout invariance (original hashes unchanged, zero target
executions, gate still locked).
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import model_adjudication as model  # noqa: E402

AUDITORS = ("AUD-M01", "AUD-M02", "AUD-M03")
FIXED4 = {"H": "FIXED", "P_R": "FIXED", "Lambda": "FIXED", "Atom": "FIXED"}


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_file(path, content, binary=False):
    """Write content, creating parents; return the path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if binary else "w"
    kwargs = {} if binary else {"encoding": "utf-8", "newline": "\n"}
    with open(path, mode, **kwargs) as handle:
        handle.write(content)
    return path


def verdict_doc(auditor, statuses, prompt_sha, packet_sha,
                declaration=None, locators=None):
    """Build one synthetic model verdict document."""
    locators = locators or ["corpus/fixture/pdp.xml Sec. 1 lines 1-2"]
    return {
        "verdict_id": auditor + "-verdict",
        "auditor_id": auditor,
        "qualification": "COLD_MODEL_INDEPENDENT",
        "verdicts": {a: {"status": s, "locators": list(locators),
                         "notes": "synthetic gate-logic probe"}
                     for a, s in statuses.items()},
        "attestation_hash": "f" * 64,
        "declaration": (model.DECLARATION if declaration is None
                        else declaration),
        "prompt_sha256": prompt_sha,
        "packet_sha256": packet_sha,
        "isolation": {"fresh_context": True,
                      "no_prior_experiment_context": True,
                      "other_outputs_unavailable": True,
                      "provider": "SYNTHETIC",
                      "model_id": "SYNTHETIC-1",
                      "sampling": "N/A",
                      "tools_web_disabled": True},
    }


def make_synth_root(base, statuses_by_auditor=(), prompt_text=None,
                    packet_text="SYNTHETIC-PACKET"):
    """Build a synthetic repo root with amendment seal + packet + prompt.

    statuses_by_auditor maps auditor id to a status map or to a raw
    string (written verbatim as the raw response). Returns the root.
    """
    os.makedirs(os.path.join(base, "artifacts", "audits",
                             "blind_anchor_packet"), exist_ok=True)
    os.makedirs(os.path.join(base, "prereg"), exist_ok=True)
    os.makedirs(os.path.join(base, "derived"), exist_ok=True)
    amendment = "SYNTHETIC AMENDMENT 001\n"
    write_file(os.path.join(base, "PROTOCOL_AMENDMENT_001.md"), amendment)
    prompt_text = ("SYNTHETIC PROMPT\n" if prompt_text is None
                   else prompt_text)
    prompt_path = write_file(
        os.path.join(base, "prereg",
                     "blind_model_adjudication_prompt.txt"), prompt_text)
    packet_path = write_file(
        os.path.join(base, "artifacts", "audits", "blind_anchor_packet",
                     "PACKET_SHA256.txt"), packet_text + "\n")
    seal = {
        "amendment_id": "SYNTHETIC",
        "amendment_sha256": sha256_file(
            os.path.join(base, "PROTOCOL_AMENDMENT_001.md")),
        "sealed_utc": "2026-01-01T00:00:00Z",
        "pre_amendment_commit": "",
        "prompt_sha256": sha256_file(prompt_path),
        "packet_sha256": open(packet_path,
                              encoding="utf-8").read().strip(),
    }
    write_file(os.path.join(base, "artifacts", "audits",
                            "amendment_001_seal.json"),
               json.dumps(seal, indent=2, sort_keys=True))
    ledger = {"anchors": {a: {"ambiguity_status": "FIXED",
                              "auditor_status": "PENDING_2B"}
                          for a in ("H", "P_R", "Lambda", "Atom")}}
    write_file(os.path.join(base, "derived", "anchor_ledger.json"),
               json.dumps(ledger, indent=2, sort_keys=True))
    for auditor, spec in statuses_by_auditor:
        dest = os.path.join(base, "artifacts", "audits",
                            "model_adjudication", auditor)
        os.makedirs(dest, exist_ok=True)
        if isinstance(spec, str):
            raw = spec
        else:
            raw = json.dumps(verdict_doc(auditor, spec,
                                         seal["prompt_sha256"],
                                         seal["packet_sha256"]),
                             indent=2, sort_keys=True)
        write_file(os.path.join(dest, "raw_response.txt"), raw)
        try:
            doc = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
        except ValueError:
            doc = None
        if doc is not None:
            write_file(os.path.join(dest, "verdict.json"),
                       json.dumps(doc, indent=2, sort_keys=True))
            verdict_sha = sha256_file(os.path.join(dest, "verdict.json"))
        else:
            verdict_sha = ""
        provenance = {"auditor_id": auditor,
                      "ingested_utc": "2026-01-02T00:00:00Z",
                      "raw_sha256": sha256_file(
                          os.path.join(dest, "raw_response.txt")),
                      "verdict_sha256": verdict_sha,
                      "sealed_prompt_sha256": seal["prompt_sha256"],
                      "sealed_packet_sha256": seal["packet_sha256"],
                      "valid": True, "problems": []}
        write_file(os.path.join(dest, "provenance.json"),
                   json.dumps(provenance, indent=2, sort_keys=True))
    return base


def expect_exit(label, func, code):
    """Assert func raises SystemExit with the expected code."""
    # [P2-LOG-T60] Test step: assert one gate exit-code expectation.
    print("[P2:test:model:060] gate case %s" % label, flush=True)
    try:
        func()
    except SystemExit as exc:
        assert exc.code == code, (label, exc.code)
    else:
        raise AssertionError("gate granted unexpectedly: " + label)


def test_1_no_records_locked(tmp_path):
    """Control 1: 0 adjudicators -> LOCKED (exit 4)."""
    root = make_synth_root(str(tmp_path / "c1"))
    expect_exit("0-records", lambda: model.assert_model_unlock(root), 4)


def test_2_one_fixed_locked(tmp_path):
    """Control 2: 1 FIXED adjudicator -> LOCKED (exit 4)."""
    root = make_synth_root(str(tmp_path / "c2"), [("AUD-M01", FIXED4)])
    expect_exit("1-record", lambda: model.assert_model_unlock(root), 4)


def test_3_two_fixed_locked(tmp_path):
    """Control 3: 2 FIXED adjudicators -> LOCKED (exit 4)."""
    root = make_synth_root(str(tmp_path / "c3"),
                           [("AUD-M01", FIXED4), ("AUD-M02", FIXED4)])
    expect_exit("2-records", lambda: model.assert_model_unlock(root), 4)


def test_4_three_unanimous_unlock(tmp_path):
    """Control 4: 3 unanimously FIXED -> UNLOCK (exit 0)."""
    # [P2-LOG-T62] Test step: assert the unanimous unlock path.
    print("[P2:test:model:062] unanimous unlock case", flush=True)
    root = make_synth_root(str(tmp_path / "c4"),
                           [(a, FIXED4) for a in AUDITORS])
    expect_exit("3-unanimous", lambda: model.assert_model_unlock(root), 0)
    with open(os.path.join(root, "artifacts", "audits",
                           "model_unlock.json"),
              encoding="utf-8") as handle:
        unlock = json.load(handle)
    assert unlock["unlocked"] is True
    with open(os.path.join(root, "derived", "anchor_ledger.json"),
              encoding="utf-8") as handle:
        ledger = json.load(handle)
    for anchor in ("H", "P_R", "Lambda", "Atom"):
        assert ledger["anchors"][anchor][
            "auditor_status"] == "MODEL_BLIND_PASS"


def modified(statuses, anchor, value):
    """Return a status map with one anchor set to value."""
    updated = dict(statuses)
    updated[anchor] = value
    return updated


def test_5_partial_locked(tmp_path):
    """Control 5: 2 FIXED + 1 PARTIAL -> LOCKED (exit 3)."""
    root = make_synth_root(
        str(tmp_path / "c5"),
        [("AUD-M01", FIXED4), ("AUD-M02", FIXED4),
         ("AUD-M03", modified(FIXED4, "P_R", "PARTIAL"))])
    expect_exit("partial", lambda: model.assert_model_unlock(root), 3)


def test_6_ambiguous_locked(tmp_path):
    """Control 6: 2 FIXED + 1 AMBIGUOUS -> LOCKED (exit 3)."""
    root = make_synth_root(
        str(tmp_path / "c6"),
        [("AUD-M01", FIXED4), ("AUD-M02", FIXED4),
         ("AUD-M03", modified(FIXED4, "Atom", "AMBIGUOUS"))])
    expect_exit("ambiguous", lambda: model.assert_model_unlock(root), 3)


def test_7_unsupported_locked(tmp_path):
    """Control 7: any UNSUPPORTED -> LOCKED (exit 3)."""
    root = make_synth_root(
        str(tmp_path / "c7"),
        [("AUD-M01", FIXED4), ("AUD-M02", FIXED4),
         ("AUD-M03", modified(FIXED4, "H", "UNSUPPORTED"))])
    expect_exit("unsupported", lambda: model.assert_model_unlock(root), 3)


def test_8_malformed_invalid(tmp_path):
    """Control 8: malformed raw response -> INVALID (exit 5)."""
    # [P2-LOG-T64] Test step: assert ingest-time invalid paths.
    print("[P2:test:model:064] malformed ingest case", flush=True)
    root = make_synth_root(str(tmp_path / "c8"))
    try:
        model.ingest(root, "AUD-M01",
                     write_file(str(tmp_path / "c8raw.txt"),
                                "not json at all {{{"))
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("malformed raw was ingested")


def test_9_missing_declaration_invalid(tmp_path):
    """Control 9: missing declaration -> INVALID (exit 5)."""
    root = make_synth_root(str(tmp_path / "c9"))
    doc = verdict_doc("AUD-M01", FIXED4, "x", "y", declaration="wrong")
    raw_path = write_file(str(tmp_path / "c9raw.txt"),
                          json.dumps(doc, indent=2, sort_keys=True))
    try:
        model.ingest(root, "AUD-M01", raw_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("declaration-less verdict was ingested")


def test_10_altered_prompt_locked(tmp_path):
    """Control 10: altered prompt hash -> LOCKED (exit 4)."""
    root = make_synth_root(
        str(tmp_path / "c10"), [(a, FIXED4) for a in AUDITORS])
    with open(os.path.join(root, "prereg",
                           "blind_model_adjudication_prompt.txt"),
              "a", encoding="utf-8") as handle:
        handle.write("tampered\n")
    expect_exit("prompt-tamper", lambda: model.assert_model_unlock(root),
                4)


def test_11_altered_packet_locked(tmp_path):
    """Control 11: altered packet hash -> LOCKED (exit 4)."""
    root = make_synth_root(
        str(tmp_path / "c11"), [(a, FIXED4) for a in AUDITORS])
    with open(os.path.join(root, "artifacts", "audits",
                           "blind_anchor_packet", "PACKET_SHA256.txt"),
              "w", encoding="utf-8", newline="\n") as handle:
        handle.write("0" * 64 + "\n")
    expect_exit("packet-tamper", lambda: model.assert_model_unlock(root),
                4)


def test_12_expectation_leakage_rejected(tmp_path):
    """Control 12: expectation-file content in raw -> ingest FAIL (5)."""
    # [P2-LOG-T66] Test step: assert leakage rejection.
    print("[P2:test:model:066] leakage rejection case", flush=True)
    root = make_synth_root(str(tmp_path / "c12"))
    raw_path = write_file(
        str(tmp_path / "c12raw.txt"),
        "verdict aligns with expected_signature.json "
        '{"a": 1}')
    try:
        model.ingest(root, "AUD-M01", raw_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("leaking raw was ingested")


def test_13_cross_read_rejected(tmp_path):
    """Control 13: raw mentioning another adjudicator -> FAIL (5)."""
    root = make_synth_root(str(tmp_path / "c13"))
    raw_path = write_file(str(tmp_path / "c13raw.txt"),
                          '{"note": "agreeing with AUD-M02 here"}')
    try:
        model.ingest(root, "AUD-M01", raw_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("cross-reading raw was ingested")


def test_14_manual_modification_detected(tmp_path):
    """Control 14: post-seal verdict edit breaks the hash (LOCKED/4)."""
    # [P2-LOG-T68] Test step: assert post-seal tamper evidence.
    print("[P2:test:model:068] post-seal modification case", flush=True)
    root = make_synth_root(str(tmp_path / "c14"),
                           [(a, FIXED4) for a in AUDITORS])
    victim = os.path.join(root, "artifacts", "audits",
                          "model_adjudication", "AUD-M03", "verdict.json")
    with open(victim, encoding="utf-8") as handle:
        doc = json.load(handle)
    doc["verdicts"]["H"]["notes"] = "hand-edited after seal"
    with open(victim, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
    expect_exit("post-seal-edit", lambda: model.assert_model_unlock(root),
                4)


def repo_target_scan():
    """Return completed/target output paths in the real checkout."""
    hits = []
    for base in (os.path.join(REPO_ROOT, "artifacts"),
                 os.path.join(REPO_ROOT, "derived")):
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                lowered = name.lower()
                if (("target_" in lowered or "x_permit" in lowered
                     or "x_nonpermit" in lowered)
                        and "request_x_" not in lowered
                        and "blind_anchor_packet" not in dirpath):
                    hits.append(os.path.join(dirpath, name))
    return hits


def post_execution_authorized():
    """True once authorized Phase-2F execution sealed (Amend.007).

    The scan-based pre-execution asserts below are superseded in that
    state (AUTHORIZED/LOCK/quarantine/conformance evidence exist by
    design); they still assert in pre-execution checkouts.
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


def test_15_no_execution_before_unlock():
    """Control 15: gate refuses everywhere short of unanimous unlock."""
    # [P2-LOG-T70] Test step: assert pre-unlock execution ban.
    print("[P2:test:model:070] pre-unlock execution ban", flush=True)
    try:
        model.assert_model_unlock(REPO_ROOT)
    except SystemExit as exc:
        # Current true state: three valid but nonunanimous records
        # exist, so the gate exits 3 (failure-seal route). Any
        # non-zero exit proves no execution path opened; exit 0 here
        # would be the failure.
        assert exc.code == 3, exc.code
    else:
        raise AssertionError("real-repo gate granted without unanimity")
    if post_execution_authorized():
        print("[P2:test:model:070] authorized Phase-2F state: "
              "pre-execution scan N/A", flush=True)
    else:
        assert repo_target_scan() == []


def test_16_zero_executions_during_amendment():
    """Control 16: three valid records exist yet execution stays zero."""
    # [P2-LOG-T72] Test step: assert zero-execution window.
    print("[P2:test:model:072] zero-execution window", flush=True)
    if post_execution_authorized():
        pytest.skip("authorized Phase-2F execution exists by design; "
                    "amendment-window scan N/A")
    for auditor in ("AUD-M01", "AUD-M02", "AUD-M03"):
        provenance_path = os.path.join(
            REPO_ROOT, "artifacts", "audits", "model_adjudication",
            auditor, "provenance.json")
        assert os.path.isfile(provenance_path), auditor
        with open(provenance_path, encoding="utf-8") as handle:
            assert json.load(handle)["valid"] is True, auditor
    assert os.path.isfile(os.path.join(
        REPO_ROOT, "artifacts", "audits", "amendment_001_seal.json"))


def git_blob(path):
    """Return the HEAD blob hash of a repo-relative path."""
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD:" + path.replace(os.sep, "/")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, path
    return completed.stdout.strip()


def git_hash(path):
    """Return the working-tree hash of a repo-relative path."""
    completed = subprocess.run(
        ["git", "hash-object",
         os.path.join(REPO_ROOT, path.replace("/", os.sep))],
        capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, path
    return completed.stdout.strip()


def test_17_original_hashes_unchanged():
    """Control 17: sealed spec/prereg hashes unchanged by amendment."""
    # [P2-LOG-T74] Test step: assert sealed-history invariance.
    print("[P2:test:model:074] sealed-history invariance", flush=True)
    assert git_hash("IMPLEMENTATION_SPEC.md") == git_blob(
        "IMPLEMENTATION_SPEC.md")
    assert git_hash("prereg/prereg_sha256.txt") == git_blob(
        "prereg/prereg_sha256.txt")
    with open(os.path.join(REPO_ROOT, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    assert manifest["implementation_spec"]["sha256_raw"] == (
        "92c55d425531e578ad6ea266e7c6f1bd0418990bd973cd0033fcf6a20dc83963")


def test_18_amendment_chronology():
    """Control 18: amendment hashed, prior to verdicts and execution."""
    # [P2-LOG-T76] Test step: assert amendment chronology.
    print("[P2:test:model:076] amendment chronology", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "audits",
                           "amendment_001_seal.json"),
              encoding="utf-8") as handle:
        seal = json.load(handle)
    amendment = os.path.join(REPO_ROOT, "PROTOCOL_AMENDMENT_001.md")
    with open(amendment, "rb") as handle:
        assert hashlib.sha256(handle.read()).hexdigest() == seal[
            "amendment_sha256"]
    sealed_time = datetime.strptime(seal["sealed_utc"], "%Y-%m-%dT%H:%M:%SZ"
                                    ).replace(tzinfo=timezone.utc)
    assert sealed_time <= datetime.now(timezone.utc)
    # Review-snapshot branch (double-blind, see README_REVIEW.md):
    # orphan review commit has no canonical history and pre_amendment_commit
    # is a review alias (<AUTHOR_REPO_COMMIT_...>), not a resolvable git
    # object. Skip the merge-base ancestry check in that case; amendment hash
    # binding above remains enforced. Canonical branch retains strict check.
    _pre = seal.get("pre_amendment_commit", "")
    if seal.get("review_snapshot") is True and isinstance(_pre, str) and _pre.startswith("<AUTHOR_"):
        print("[P2:test:model:076] review snapshot: ancestry check skipped (alias)", flush=True)
    else:
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor",
             seal["pre_amendment_commit"], "HEAD"],
            cwd=REPO_ROOT, capture_output=True, timeout=60)
        assert completed.returncode == 0
    if post_execution_authorized():
        print("[P2:test:model:076] authorized Phase-2F state: "
              "pre-execution scan N/A", flush=True)
    else:
        assert repo_target_scan() == []
