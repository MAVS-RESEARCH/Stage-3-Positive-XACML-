"""Phase-2C final-certification gate tests (Amendment 002).

All gate-logic cases run on synthetic temporary roots (never the real
artifacts): locked/invalid/nonunanimous/unlock outcomes, ingest-final
strictness (§15), namespace protection, and overwrite rules. Real-repo
checks assert the gate stays locked pre-certification and the freeze
record is well-formed post-freeze (skipped until frozen).
"""
import hashlib
import json
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import final_certification as final  # noqa: E402

AUDITORS = ("AUD-C01", "AUD-C02", "AUD-C03")
FIXED4 = {"H": "FIXED", "P_R": "FIXED", "Lambda": "FIXED", "Atom": "FIXED"}


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_file(path, content, binary=False):
    """Write content, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if binary:
        with open(path, "wb") as handle:
            handle.write(content)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)


def verdict_doc(auditor, statuses, prompt_sha, packet_sha,
                declaration=None, attestation=None):
    """Build one synthetic final verdict document."""
    return {
        "verdict_id": auditor + "-verdict",
        "auditor_id": auditor,
        "qualification": "COLD_MODEL_INDEPENDENT",
        "verdicts": {a: {"status": s,
                         "locators": ["corpus/fixture/pdp.xml Sec. X"],
                         "notes": "synthetic gate-logic probe"}
                     for a, s in statuses.items()},
        "attestation_hash": attestation or "e" * 64,
        "declaration": (final.DECLARATION if declaration is None
                        else declaration),
        "prompt_sha256": prompt_sha,
        "packet_sha256": packet_sha,
        "isolation": {"fresh_context": True,
                      "no_prior_experiment_context": True,
                      "other_outputs_unavailable": True},
    }


def make_freeze_root(base, statuses_by_auditor=(), attestation_text=None):
    """Build a synthetic frozen root with optional C records."""
    os.makedirs(os.path.join(base, "artifacts", "audits",
                             "final_freeze", "FINAL_BLIND_PACKET"),
                exist_ok=True)
    os.makedirs(os.path.join(base, "prereg"), exist_ok=True)
    prompt = "SYNTHETIC FINAL PROMPT\n"
    write_file(os.path.join(base, "prereg",
                            "final_certification_prompt.txt"), prompt)
    packet_manifest = {"packet_id": "synthetic", "files": {}}
    write_file(os.path.join(base, "artifacts", "audits", "semantic_hardening", "final_freeze",
                            "FINAL_BLIND_PACKET", "PACKET_MANIFEST.json"),
               json.dumps(packet_manifest, indent=2, sort_keys=True))
    packet_sha = sha256_file(os.path.join(
        base, "artifacts", "audits", "semantic_hardening", "final_freeze", "FINAL_BLIND_PACKET",
        "PACKET_MANIFEST.json"))
    write_file(os.path.join(base, "artifacts", "audits", "semantic_hardening", "final_freeze",
                            "FINAL_BLIND_PACKET", "PACKET_SHA256.txt"),
               packet_sha + "\n")
    prompt_sha = sha256_file(os.path.join(
        base, "prereg", "final_certification_prompt.txt"))
    freeze = {"freeze_id": "synthetic", "frozen": True, "revision": 1,
              "round": "R", "packet_sha256": packet_sha,
              "prompt_sha256": prompt_sha, "frozen_files": {},
              "completed_executions": 0, "superseded": False}
    write_file(os.path.join(base, "artifacts", "audits", "semantic_hardening", "final_freeze",
                            "FINAL_SEMANTIC_FREEZE.json"),
               json.dumps(freeze, indent=2, sort_keys=True))
    ledger = {"anchors": {a: {"ambiguity_status": "FIXED",
                              "auditor_status": "PENDING_FINAL_"
                              "CERTIFICATION"} for a in
                          ("H", "P_R", "Lambda", "Atom", "omega", "Q",
                           "Succ+", "c", "A_Pi")}}
    write_file(os.path.join(base, "artifacts", "audits", "semantic_hardening", "final_freeze",
                            "FINAL_ANCHOR_LEDGER.json"),
               json.dumps(ledger, indent=2, sort_keys=True))
    for auditor, spec in statuses_by_auditor:
        dest = os.path.join(base, "artifacts", "audits",
                            "final_certification", auditor)
        os.makedirs(dest, exist_ok=True)
        text = ("Attestation of %s, synthetic gate probe %s." % (
            auditor, attestation_text or "alpha"))
        write_file(os.path.join(dest, "attestation.txt"), text)
        attestation_sha = sha256_file(os.path.join(dest, "attestation.txt"))
        if isinstance(spec, str):
            raw = spec
        else:
            doc = verdict_doc(auditor, spec, prompt_sha, packet_sha)
            if isinstance(spec, dict) and spec.get("__attestation__"):
                doc["attestation_hash"] = spec.pop("__attestation__")
            else:
                doc["attestation_hash"] = attestation_sha
            raw = json.dumps(doc, indent=2, sort_keys=True)
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
                      "attestation_sha256": attestation_sha,
                      "sealed_prompt_sha256": prompt_sha,
                      "sealed_packet_sha256": packet_sha,
                      "valid": True, "problems": []}
        write_file(os.path.join(dest, "provenance.json"),
                   json.dumps(provenance, indent=2, sort_keys=True))
    return base


def expect_exit(label, func, code):
    """Assert func raises SystemExit with the expected code."""
    # [P2-LOG-F10] Test step: assert one gate exit-code expectation.
    print("[P2:test:final:010] gate case %s" % label, flush=True)
    try:
        func()
    except SystemExit as exc:
        assert exc.code == code, (label, exc.code)
    else:
        raise AssertionError("gate granted unexpectedly: " + label)


def test_final_no_records_locked(tmp_path):
    """0 records -> BLOCKED (exit 4)."""
    root = make_freeze_root(str(tmp_path / "f0"))
    expect_exit("0-records", lambda: final.assert_final_unlock(root), 4)


def test_final_two_records_locked(tmp_path):
    """2 records -> BLOCKED (exit 4)."""
    root = make_freeze_root(str(tmp_path / "f2"),
                            [("AUD-C01", FIXED4), ("AUD-C02", FIXED4)])
    expect_exit("2-records", lambda: final.assert_final_unlock(root), 4)


def test_final_unanimous_unlock(tmp_path):
    """3 unanimous FIXED -> UNLOCK (exit 0) with ledger flip."""
    # [P2-LOG-F12] Test step: assert the unanimous unlock path.
    print("[P2:test:final:012] unanimous unlock case", flush=True)
    root = make_freeze_root(str(tmp_path / "f3"),
                            [(a, FIXED4) for a in AUDITORS])
    expect_exit("3-unanimous", lambda: final.assert_final_unlock(root), 0)
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening", "final_freeze",
                           "final_unlock.json"),
              encoding="utf-8") as handle:
        assert json.load(handle)["unlocked"] is True
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening", "final_freeze",
                           "FINAL_ANCHOR_LEDGER.json"),
              encoding="utf-8") as handle:
        ledger = json.load(handle)
    for anchor in ("H", "P_R", "Lambda", "Atom"):
        assert ledger["anchors"][anchor][
            "auditor_status"] == "FINAL_CERTIFIED"


def test_final_nonunanimous_locked(tmp_path):
    """PARTIAL verdict -> exit 3 (failure-seal route)."""
    root = make_freeze_root(
        str(tmp_path / "f4"),
        [("AUD-C01", FIXED4), ("AUD-C02", FIXED4),
         ("AUD-C03", dict(FIXED4, P_R="PARTIAL"))])
    expect_exit("partial", lambda: final.assert_final_unlock(root), 3)


def test_final_tampered_packet_locked(tmp_path):
    """Tampered packet content -> exit 4."""
    root = make_freeze_root(str(tmp_path / "f5"),
                            [(a, FIXED4) for a in AUDITORS])
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening", "final_freeze",
                           "FINAL_BLIND_PACKET", "PACKET_SHA256.txt"),
              "w", encoding="utf-8", newline="\n") as handle:
        handle.write("0" * 64 + "\n")
    expect_exit("packet-tamper", lambda: final.assert_final_unlock(root),
                4)


def ingested_root(tmp_path, name):
    """Build a minimal root with freeze files for ingest tests."""
    root = make_freeze_root(str(tmp_path / name))
    return root


def ingest_case(tmp_path, name, auditor, raw_text, attestation_text,
                want_code):
    """Run one ingest-final case and assert its exit code."""
    root = ingested_root(tmp_path, name)
    raw_path = os.path.join(str(tmp_path), name + "-raw.txt")
    att_path = os.path.join(str(tmp_path), name + "-att.txt")
    write_file(raw_path, raw_text)
    write_file(att_path, attestation_text)
    try:
        final.ingest_final(root, auditor, raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == want_code, (name, exc.code)
    else:
        assert want_code == 0, name


def test_ingest_auditor_mismatch(tmp_path):
    """auditor_id != CLI chair -> INVALID (exit 5)."""
    # [P2-LOG-F14] Test step: assert ingest-final strictness matrix.
    print("[P2:test:final:014] ingest strictness matrix", flush=True)
    root = ingested_root(tmp_path, "g1")
    prompt_sha, packet_sha = freeze_hashes(root)
    doc = verdict_doc("AUD-C02", FIXED4, prompt_sha, packet_sha)
    doc["attestation_hash"] = "d" * 64
    raw_path = os.path.join(str(tmp_path), "g1-raw.txt")
    att_path = os.path.join(str(tmp_path), "g1-att.txt")
    write_file(raw_path, json.dumps(doc, indent=2, sort_keys=True))
    write_file(att_path, "Attestation of AUD-C01 synthetic mismatch.")
    try:
        final.ingest_final(root, "AUD-C01", raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("mismatched auditor ingested")


def freeze_hashes(root):
    """Read sealed prompt/packet hashes from a synthetic freeze."""
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening", "final_freeze",
                           "FINAL_SEMANTIC_FREEZE.json"),
              encoding="utf-8") as handle:
        freeze = json.load(handle)
    return freeze["prompt_sha256"], freeze["packet_sha256"]


def ingested_valid(root, tmp_path, tag, auditor, statuses, att_text):
    """Ingest a fully valid record; assert exit 0; return paths."""
    prompt_sha, packet_sha = freeze_hashes(root)
    att_path = os.path.join(str(tmp_path), tag + "-att.txt")
    write_file(att_path, att_text)
    with open(att_path, "rb") as handle:
        att_hash = hashlib.sha256(handle.read()).hexdigest()
    doc = verdict_doc(auditor, statuses, prompt_sha, packet_sha)
    doc["attestation_hash"] = att_hash
    raw_path = os.path.join(str(tmp_path), tag + "-raw.txt")
    write_file(raw_path, json.dumps(doc, indent=2, sort_keys=True))
    try:
        final.ingest_final(root, auditor, raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 0, (tag, exc.code)
    return raw_path, att_path


def test_ingest_duplicate_attestation(tmp_path):
    """Duplicate attestation text/hash across chairs -> INVALID (5)."""
    root = make_freeze_root(str(tmp_path / "g2"))
    ingested_valid(root, tmp_path, "g2-C01", "AUD-C01", FIXED4,
                   "Attestation of AUD-C01. Shared generic text.")
    ingested_valid(root, tmp_path, "g2-C02", "AUD-C02", FIXED4,
                   "Attestation of AUD-C02. Shared generic text.")
    prompt_sha, packet_sha = freeze_hashes(root)
    first = open(os.path.join(str(tmp_path), "g2-C01-att.txt"),
                 encoding="utf-8").read()
    doc = verdict_doc("AUD-C03", FIXED4, prompt_sha, packet_sha)
    with open(os.path.join(str(tmp_path), "g2-C01-att.txt"), "rb") as h:
        doc["attestation_hash"] = hashlib.sha256(h.read()).hexdigest()
    raw_path = os.path.join(str(tmp_path), "g2-C03-raw.txt")
    att_path = os.path.join(str(tmp_path), "g2-C03-att.txt")
    write_file(raw_path, json.dumps(doc, indent=2, sort_keys=True))
    write_file(att_path, first)
    try:
        final.ingest_final(root, "AUD-C03", raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("duplicate attestation ingested")


def test_ingest_recompute_and_crossread(tmp_path):
    """Attestation recompute mismatch and cross-reads -> INVALID (5)."""
    # [P2-LOG-F16] Test step: assert hash/cross-read refusal.
    print("[P2:test:final:016] recompute and cross-read cases", flush=True)
    root = ingested_root(tmp_path, "g3")
    with open(os.path.join(root, "artifacts", "audits", "semantic_hardening", "final_freeze",
                           "FINAL_SEMANTIC_FREEZE.json"),
              encoding="utf-8") as handle:
        freeze = json.load(handle)
    doc = verdict_doc("AUD-C01", FIXED4, freeze["prompt_sha256"],
                      freeze["packet_sha256"])
    doc["attestation_hash"] = "0" * 64
    raw_path = os.path.join(str(tmp_path), "g3-raw.txt")
    att_path = os.path.join(str(tmp_path), "g3-att.txt")
    write_file(raw_path, json.dumps(doc, indent=2, sort_keys=True))
    write_file(att_path, "Attestation of AUD-C01 synthetic recompute.")
    try:
        final.ingest_final(root, "AUD-C01", raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("recompute mismatch ingested")
    doc["attestation_hash"] = sha256_file(att_path)
    doc["verdicts"]["H"]["notes"] = "seen AUD-C02 draft"
    raw_path2 = os.path.join(str(tmp_path), "g3-raw2.txt")
    write_file(raw_path2, json.dumps(doc, indent=2, sort_keys=True))
    try:
        final.ingest_final(root, "AUD-C01", raw_path2, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("cross-reading raw ingested")


def test_ingest_hardening_path_and_overwrite(tmp_path):
    """Hardening-dir raws refused; VALID chairs refuse overwrite."""
    # [P2-LOG-F18] Test step: assert path and overwrite rules.
    print("[P2:test:final:018] path and overwrite rules", flush=True)
    root = make_freeze_root(str(tmp_path / "g4"))
    prompt_sha, packet_sha = freeze_hashes(root)
    evil = os.path.join(root, "artifacts", "audits",
                        "semantic_hardening", "evil-raw.txt")
    os.makedirs(os.path.dirname(evil), exist_ok=True)
    doc = verdict_doc("AUD-C01", FIXED4, prompt_sha, packet_sha)
    doc["attestation_hash"] = "a" * 64
    write_file(evil, json.dumps(doc, indent=2, sort_keys=True))
    write_file(os.path.join(str(tmp_path), "g4-att.txt"),
               "Attestation of AUD-C01 synthetic path.")
    try:
        final.ingest_final(root, "AUD-C01", evil,
                           os.path.join(str(tmp_path), "g4-att.txt"))
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("hardening-dir raw ingested")
    ingested_valid(root, tmp_path, "g4ok", "AUD-C01", FIXED4,
                   "Attestation of AUD-C01 synthetic overwrite.")
    raw_path = os.path.join(str(tmp_path), "g4ok-raw.txt")
    att_path = os.path.join(str(tmp_path), "g4ok-att.txt")
    try:
        final.ingest_final(root, "AUD-C01", raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("overwrite of VALID chair allowed")


def test_ingest_malformed_and_mids(tmp_path):
    """Malformed raw and wrong-namespace IDs -> INVALID (5)."""
    # [P2-LOG-F20] Test step: assert malformed/namespace refusal.
    print("[P2:test:final:020] malformed and namespace cases", flush=True)
    root = ingested_root(tmp_path, "g5")
    raw_path = os.path.join(str(tmp_path), "g5-raw.txt")
    att_path = os.path.join(str(tmp_path), "g5-att.txt")
    write_file(raw_path, "not json {{{")
    write_file(att_path, "Attestation of AUD-C01 synthetic malformed.")
    try:
        final.ingest_final(root, "AUD-C01", raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("malformed raw ingested")
    try:
        final.ingest_final(root, "AUD-M01", raw_path, att_path)
    except SystemExit as exc:
        assert exc.code == 5, exc.code
    else:
        raise AssertionError("historical ID ingested as final")


def test_real_repo_still_locked():
    """Real repo: gate never unlocks without unanimous FIXED (exit 3/4)."""
    # [P2-LOG-F22] Test step: assert real-repo locked state.
    # Sealed 2026-09-12: three valid chairs, Lambda PARTIAL x3 + Atom
    # PARTIAL x1 -> exit 3 failure-seal route (was exit 4 pre-certification).
    print("[P2:test:final:022] real-repo locked state", flush=True)
    try:
        final.assert_final_unlock(REPO_ROOT)
    except SystemExit as exc:
        assert exc.code == 3, exc.code
    else:
        raise AssertionError("real-repo final gate granted")
