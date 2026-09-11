"""Phase-2 blind-adjudication machinery tests.

Verifies the sealed auditor packet (redaction clean, corpus
byte-identical to sealed sources, manifest hash matches) and the
unlock-gate logic on synthetic verdicts confined to temporary
directories (never the real artifacts): missing verdict refuses,
tampered seal refuses, PARTIAL verdict routes to failure-seal (exit 3),
all-FIXED qualifying verdict unlocks (exit 0). No human judgment is
fabricated for the real experiment path.
"""
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import blind_adjudication as blind  # noqa: E402

PACKET = os.path.join(REPO_ROOT, "artifacts", "audits",
                      "blind_anchor_packet")


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_packet_redaction_and_corpus():
    """Packet redaction passes; corpus matches sealed sources."""
    # [P2-LOG-T40] Test step: assert packet integrity.
    print("[P2:test:blind:040] checking packet integrity", flush=True)
    assert os.path.isdir(PACKET)
    assert blind.scan_redaction(PACKET) == []
    pairs = (
        ("corpus/xacml-3.0-core-spec-cos01-en.html",
         "external/xacml/xacml-3.0-core-spec-cos01-en.html"),
        ("corpus/fixture/pdp.xml",
         "external/authzforce/fixture/pdp.xml"),
        ("corpus/fixture/request.xml",
         "external/authzforce/fixture/request.xml"),
        ("corpus/fixture/response.xml",
         "external/authzforce/fixture/response.xml"),
        ("corpus/fixture/policies/policy.xml",
         "external/authzforce/fixture/policies/policy.xml"),
    )
    for packet_rel, repo_rel in pairs:
        assert (sha256_file(os.path.join(PACKET, packet_rel))
                == sha256_file(os.path.join(REPO_ROOT, repo_rel))), \
            packet_rel
    with open(os.path.join(PACKET, "PACKET_SHA256.txt"),
              encoding="utf-8") as handle:
        sealed = handle.read().strip()
    with open(os.path.join(PACKET, "PACKET_MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest_json = handle.read()
    assert hashlib.sha256(
        manifest_json.encode("utf-8")).hexdigest() == sealed
    # [P2-LOG-T42] Test step: assert packet contents.
    print("[P2:test:blind:042] checking packet contents", flush=True)
    for name in ("rubric.md", "locator_index.md",
                 "candidates/anchor_ledger.json",
                 "candidates/policy_adequacy_certificate.json",
                 "candidates/h_equivalence_proof.json",
                 "candidates/atom_record.json",
                 "candidates/execution_inputs.json"):
        assert os.path.isfile(os.path.join(PACKET, name)), name


def write_synthetic_root(tmp_path, statuses, tamper_seal=False):
    """Build a synthetic repo root with a verdict + seal (temp only)."""
    audits = tmp_path / "artifacts" / "audits"
    audits.mkdir(parents=True)
    verdict = {
        "verdict_id": "SYNTHETIC-LOGIC-PROBE",
        "auditor_id": "AUD-SYNTH",
        "qualification": "QUALIFIED_INDEPENDENT",
        "verdicts": {a: {"status": s, "locators": ["loc"]}
                     for a, s in statuses.items()},
        "attestation_hash": "0" * 64,
    }
    (audits / "blind_anchor_verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
    digest = sha256_file(str(audits / "blind_anchor_verdict.json"))
    (audits / "blind_verdict_seal.json").write_text(
        json.dumps({"verdict_sha256": ("x" * 64 if tamper_seal else digest),
                    "sealed_utc": "2026-01-01T00:00:00Z",
                    "auditor_id": "AUD-SYNTH"}, indent=2, sort_keys=True),
        encoding="utf-8")
    return str(tmp_path)


def test_unlock_logic_matrix(tmp_path):
    """Unlock gate logic: missing/tampered/partial/fixed verdicts."""
    # [P2-LOG-T44] Test step: assert unlock-gate logic matrix.
    print("[P2:test:blind:044] checking unlock-gate logic", flush=True)
    try:
        blind.assert_unlock(REPO_ROOT)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("unlock without verdict was granted")
    partial = write_synthetic_root(
        tmp_path / "p1",
        {"H": "FIXED", "P_R": "PARTIAL", "Lambda": "FIXED",
         "Atom": "FIXED"})
    try:
        blind.assert_unlock(partial)
    except SystemExit as exc:
        assert exc.code == 3, exc.code
    else:
        raise AssertionError("partial verdict unlocked")
    fixed = write_synthetic_root(
        tmp_path / "p2",
        {"H": "FIXED", "P_R": "FIXED", "Lambda": "FIXED",
         "Atom": "FIXED"})
    try:
        blind.assert_unlock(fixed)
    except SystemExit as exc:
        assert exc.code == 0, exc.code
    else:
        raise AssertionError("fixed verdict did not unlock")
    tampered = write_synthetic_root(
        tmp_path / "p3",
        {"H": "FIXED", "P_R": "FIXED", "Lambda": "FIXED",
         "Atom": "FIXED"},
        tamper_seal=True)
    try:
        blind.assert_unlock(tampered)
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    else:
        raise AssertionError("tampered seal unlocked")
