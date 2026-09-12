"""Amendment-002 final blind certification for PC-XACML-S3+.

Implements Phase 2C: ingest-final (strict validation for AUD-C01/02/03
into final_certification/, never into historical namespaces) and
assert-final-unlock (unanimous FIXED over the FROZEN final packet).
Strictness beyond the ROUND_000 path: CLI auditor must equal the JSON
auditor; attestation text is supplied alongside, must name its auditor,
must recompute to the verdict hash, and must be distinct (text and
hash) across chairs; raw bytes preserved verbatim; no hand edits;
cross-chair reads forbidden; occupied VALID chairs refuse overwrite
(INVALID records may be superseded once). In-session subagent output
can never satisfy these checks (wrong namespace/IDs/declarations).

Step console lines use the [P2:final:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

from blind_adjudication import REDACTION_PATTERNS, TOUCH_ASSIGNMENT

AUDITORS = ("AUD-C01", "AUD-C02", "AUD-C03")
PANEL_1 = AUDITORS
PANEL_2 = ("AUD-C04", "AUD-C05", "AUD-C06")
PANEL_3 = ("AUD-C07", "AUD-C08", "AUD-C09")
PANEL_4 = ("AUD-C10", "AUD-C11", "AUD-C12")
PANELS = (PANEL_1, PANEL_2, PANEL_3, PANEL_4)
PANEL_IDS = PANEL_1 + PANEL_2 + PANEL_3 + PANEL_4
FINAL_NAMESPACE = re.compile(r"^AUD-C(0[1-9]|1[0-2])$")
# Revision-to-panel binding (Amendment 005): only the listed panel may
# certify a freeze revision. Revisions without a panel were never
# externally certified (rehearsal-only). Future revisions map to the
# next unused panel by index rev-3.
REVISION_PANELS = {1: None, 2: 0, 3: None, 4: 1}
BLIND_ANCHORS = ("H", "P_R", "Lambda", "Atom")
ALLOWED_STATUSES = ("FIXED", "PARTIAL", "AMBIGUOUS", "UNSUPPORTED")
DECLARATION = (
    "I was not supplied an expected touch set, expected freeze signature "
    "or K vector, expected classification, desired experiment outcome, or "
    "manuscript claim. I made these judgments solely from the contents "
    "of the sealed blind packet.")
EXPECTATION_FILENAMES = ("expected_signature.json",
                         "canary_expectations.json", "experiment.yaml")
OTHER_ID = re.compile(r"AUD-[A-Z][0-9A-Z-]*")
LOCATOR_HINT = re.compile(r"corpus|Sec\.|Section|lines?|Line", re.IGNORECASE)
HARDENING_PATH = re.compile(r"semantic_hardening|non_blind|NON_BLIND",
                            re.IGNORECASE)

EXIT_UNLOCK = 0
EXIT_NONUNANIMOUS = 3
EXIT_BLOCKED = 4
EXIT_INVALID = 5


def fail(message, code=1):
    """Emit a fail-closed error line and exit with the given code."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:final:FAIL] " + message, flush=True)
    sys.exit(code)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utcnow():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def freeze_dir(repo_root):
    """Return the final-freeze directory path."""
    # Operative freeze lives under semantic_hardening (written by
    # hardening.py --freeze). Developmental sweep inputs stay off-limits
    # to certification reads; the frozen output itself is the input.
    return os.path.join(repo_root, "artifacts", "audits",
                         "semantic_hardening", "final_freeze")


def records_root(repo_root):
    """Return the final-certification records directory path."""
    return os.path.join(repo_root, "artifacts", "audits",
                        "final_certification")


def load_freeze(repo_root):
    """Load the final freeze record, or None."""
    path = os.path.join(freeze_dir(repo_root), "FINAL_SEMANTIC_FREEZE.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_json(raw_text):
    """Deterministically extract the single JSON object from raw text."""
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None, "no JSON object found in raw response"
    try:
        return json.loads(raw_text[start:end + 1]), ""
    except ValueError as exc:
        return None, "raw JSON unparseable: %s" % exc


def scan_text_leakage(text, own_id):
    """Scan text for expectation leakage and cross-chair reads."""
    hits = []
    for pattern in REDACTION_PATTERNS:
        if pattern in text:
            hits.append("redaction-pattern:" + pattern)
    for name in EXPECTATION_FILENAMES:
        if name in text:
            hits.append("expectation-file:" + name)
    if TOUCH_ASSIGNMENT.search(text):
        hits.append("touch-assignment")
    for other in set(OTHER_ID.findall(text)):
        if other != own_id and other in PANEL_IDS + (
                "AUD-M01", "AUD-M02", "AUD-M03"):
            hits.append("cross-read:" + other)
    return hits


def validate_final(doc, freeze, auditor):
    """Validate a parsed final verdict; return a list of problems."""
    problems = []
    if doc.get("auditor_id") != auditor:
        problems.append("auditor_id must equal the ingested chair")
    if not FINAL_NAMESPACE.match(doc.get("auditor_id", "")):
        problems.append("auditor_id not in final namespace AUD-C01..C12")
    if doc.get("qualification") != "COLD_MODEL_INDEPENDENT":
        problems.append("qualification must be COLD_MODEL_INDEPENDENT")
    verdicts = doc.get("verdicts", {})
    for anchor in BLIND_ANCHORS:
        record = verdicts.get(anchor, {})
        if record.get("status") not in ALLOWED_STATUSES:
            problems.append("bad status for " + anchor)
            continue
        locators = record.get("locators")
        if not isinstance(locators, list) or not locators or not all(
                isinstance(item, str) and item.strip()
                for item in locators):
            problems.append("missing locators for " + anchor)
        elif not any(LOCATOR_HINT.search(item) for item in locators):
            problems.append("locators lack packet/corpus reference: "
                            + anchor)
    if doc.get("declaration") != DECLARATION:
        problems.append("declaration missing or not verbatim")
    if doc.get("prompt_sha256") != freeze.get("prompt_sha256"):
        problems.append("prompt hash mismatch vs freeze")
    if doc.get("packet_sha256") != freeze.get("packet_sha256"):
        problems.append("packet hash mismatch vs freeze")
    if not doc.get("attestation_hash"):
        problems.append("attestation_hash missing")
    isolation = doc.get("isolation", {})
    for key in ("fresh_context", "no_prior_experiment_context",
                "other_outputs_unavailable"):
        if isolation.get(key) is not True:
            problems.append("isolation not affirmed: " + key)
    return problems


def existing_texts_and_hashes(repo_root, exclude=""):
    """Collect attestation texts/hashes of the other valid chairs."""
    texts, hashes = set(), set()
    for auditor in PANEL_IDS:
        if auditor == exclude:
            continue
        provenance_path = os.path.join(records_root(repo_root), auditor,
                                       "provenance.json")
        if not os.path.isfile(provenance_path):
            continue
        with open(provenance_path, "r", encoding="utf-8") as handle:
            provenance = json.load(handle)
        if not provenance.get("valid"):
            continue
        attestation_path = os.path.join(records_root(repo_root), auditor,
                                        "attestation.txt")
        if os.path.isfile(attestation_path):
            with open(attestation_path, "rb") as handle:
                texts.add(handle.read())
        if provenance.get("attestation_sha256"):
            hashes.add(provenance["attestation_sha256"])
    return texts, hashes


def ingest_final(repo_root, auditor, raw_path, attestation_path):
    """Ingest one final raw response with strict Amendment-002 rules."""
    # [P2-LOG-010] Step: ingest one final raw adjudication.
    print("[P2:final:010] ingesting final %s" % auditor, flush=True)
    if auditor not in PANEL_IDS:
        fail("unknown final chair (want AUD-C01..C06): " + auditor,
             EXIT_INVALID)
    if HARDENING_PATH.search(os.path.abspath(raw_path)):
        fail("raw source lives under hardening/non-blind paths",
             EXIT_INVALID)
    freeze = load_freeze(repo_root)
    if freeze is None or not freeze.get("frozen"):
        fail("no valid final freeze; certification not open", EXIT_BLOCKED)
    dest = os.path.join(records_root(repo_root), auditor)
    existing = os.path.join(dest, "provenance.json")
    if os.path.isfile(existing):
        with open(existing, "r", encoding="utf-8") as handle:
            if json.load(handle).get("valid"):
                fail("chair holds a VALID record; overwrite refused",
                     EXIT_INVALID)
    try:
        with open(raw_path, "rb") as handle:
            raw_bytes = handle.read()
        with open(attestation_path, "rb") as handle:
            attestation_bytes = handle.read()
    except OSError:
        fail("raw or attestation file unreadable", EXIT_INVALID)
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = ""
    try:
        attestation_text = attestation_bytes.decode("utf-8")
    except UnicodeDecodeError:
        attestation_text = ""
    problems = []
    doc, error = extract_json(raw_text)
    if doc is None:
        problems.append(error)
    else:
        problems.extend(scan_text_leakage(raw_text, auditor))
        problems.extend(scan_text_leakage(attestation_text, auditor))
    if auditor not in attestation_text:
        problems.append("attestation text does not bind auditor id")
    recomputed = hashlib.sha256(attestation_bytes).hexdigest()
    if doc is not None and doc.get("attestation_hash") != recomputed:
        problems.append("attestation hash does not recompute from "
                        "retained text")
    if doc is not None:
        problems.extend(validate_final(doc, freeze, auditor))
    other_texts, other_hashes = existing_texts_and_hashes(
        repo_root, exclude=auditor)
    if attestation_bytes in other_texts:
        problems.append("duplicate attestation text across chairs")
    if doc is not None and doc.get("attestation_hash") in other_hashes:
        problems.append("duplicate attestation hash across chairs")
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "raw_response.txt"), "wb") as handle:
        handle.write(raw_bytes)
    with open(os.path.join(dest, "attestation.txt"), "wb") as handle:
        handle.write(attestation_bytes)
    raw_sha = sha256_file(os.path.join(dest, "raw_response.txt"))
    if doc is not None:
        with open(os.path.join(dest, "verdict.json"), "w",
                  encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, indent=2, sort_keys=True)
            handle.write("\n")
        verdict_sha = sha256_file(os.path.join(dest, "verdict.json"))
    else:
        verdict_sha = ""
    provenance = {
        "auditor_id": auditor,
        "ingested_utc": utcnow(),
        "raw_sha256": raw_sha,
        "verdict_sha256": verdict_sha,
        "attestation_sha256": recomputed,
        "sealed_prompt_sha256": freeze.get("prompt_sha256", ""),
        "sealed_packet_sha256": freeze.get("packet_sha256", ""),
        "valid": not problems,
        "problems": problems,
    }
    with open(os.path.join(dest, "provenance.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(provenance, handle, indent=2, sort_keys=True)
        handle.write("\n")
    if problems:
        # [P2-LOG-012] Step: invalid final ingest recorded, not counted.
        print("[P2:final:012] final ingest INVALID: %s" % problems,
              flush=True)
        sys.exit(EXIT_INVALID)
    # [P2-LOG-014] Step: valid final ingest sealed.
    print("[P2:final:014] final ingest valid, record sealed", flush=True)


def collect_valid(repo_root):
    """Collect the valid final certification records."""
    valid = {}
    for auditor in PANEL_IDS:
        record_dir = os.path.join(records_root(repo_root), auditor)
        provenance_path = os.path.join(record_dir, "provenance.json")
        verdict_path = os.path.join(record_dir, "verdict.json")
        raw_path = os.path.join(record_dir, "raw_response.txt")
        attestation_path = os.path.join(record_dir, "attestation.txt")
        if not all(os.path.isfile(p) for p in (provenance_path,
                                               verdict_path, raw_path,
                                               attestation_path)):
            continue
        with open(provenance_path, "r", encoding="utf-8") as handle:
            provenance = json.load(handle)
        if not provenance.get("valid"):
            continue
        if (sha256_file(verdict_path) != provenance.get("verdict_sha256")
                or sha256_file(raw_path) != provenance.get("raw_sha256")
                or hashlib.sha256(open(attestation_path, "rb").read(
                    )).hexdigest() != provenance.get(
                        "attestation_sha256")):
            continue
        with open(verdict_path, "r", encoding="utf-8") as handle:
            valid[auditor] = json.load(handle)
    return valid


def eligible_panel(freeze):
    """Return the single panel bound to the freeze revision, or None.

    Revision 2 belongs to PANEL_1; revisions 1 and 3 were never
    externally certified; revision 4 requires the fresh PANEL_2. Later
    revisions take the next unused panel by index rev-3. A panel never
    certifies another revision's freeze: chairs are not reusable across
    revisions, and no fourth chair ever completes a panel.
    """
    raw = (freeze or {}).get("revision", 1)
    if isinstance(raw, bool) or not isinstance(raw, int):
        return None
    revision = raw
    if revision in REVISION_PANELS:
        index = REVISION_PANELS[revision]
        return PANELS[index] if index is not None else None
    if revision >= 5:
        index = revision - 3
        if 0 <= index < len(PANELS):
            return PANELS[index]
    return None
def matching_freeze_records(repo_root, freeze, valid):
    """Keep only records sealed against the operative freeze."""
    # [P2-LOG-016] Step: bind records to the operative freeze.
    kept = {}
    for auditor, verdict in valid.items():
        provenance_path = os.path.join(records_root(repo_root), auditor,
                                       "provenance.json")
        try:
            with open(provenance_path, "r", encoding="utf-8") as handle:
                provenance = json.load(handle)
        except (OSError, ValueError):
            continue
        if (provenance.get("sealed_packet_sha256")
                == freeze.get("packet_sha256")
                and provenance.get("sealed_prompt_sha256")
                == freeze.get("prompt_sha256")):
            kept[auditor] = verdict
    return kept


def assert_final_unlock(repo_root):
    """Evaluate the final-certification unlock conjunction."""
    # [P2-LOG-020] Step: judge final unlock.
    print("[P2:final:020] judging final certification unlock", flush=True)
    freeze = load_freeze(repo_root)
    if freeze is None or not freeze.get("frozen"):
        print("[P2:final:022] no valid freeze: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    packet_seal = os.path.join(freeze_dir(repo_root), "FINAL_BLIND_PACKET",
                               "PACKET_SHA256.txt")
    prompt_path = os.path.join(repo_root, "prereg",
                               "final_certification_prompt.txt")
    if (not os.path.isfile(packet_seal)
            or open(packet_seal, encoding="utf-8").read().strip()
            != freeze.get("packet_sha256")
            or sha256_file(prompt_path) != freeze.get("prompt_sha256")):
        print("[P2:final:024] freeze/packet/prompt drift: locked",
              flush=True)
        sys.exit(EXIT_BLOCKED)
    valid = matching_freeze_records(repo_root, freeze,
                                      collect_valid(repo_root))
    panel = eligible_panel(freeze)
    if panel is None:
        print("[P2:final:027] freeze revision has no eligible panel: "
              "blocked", flush=True)
        sys.exit(EXIT_BLOCKED)
    if all(auditor in valid for auditor in panel):
        short = [auditor for auditor in panel
                 if any(valid[auditor]["verdicts"][anchor]["status"]
                        != "FIXED" for anchor in BLIND_ANCHORS)]
        if short:
            print("[P2:final:028] nonunanimous %s: failure-seal route"
                  % short, flush=True)
            sys.exit(EXIT_NONUNANIMOUS)
        unlock = {
            "unlocked": True,
            "rule": ("Amendment-004 unanimous fresh-panel final "
                     "certification"),
            "auditors": list(panel),
            "packet_sha256": freeze.get("packet_sha256"),
            "prompt_sha256": freeze.get("prompt_sha256"),
            "sealed_utc": utcnow(),
        }
        with open(os.path.join(freeze_dir(repo_root), "final_unlock.json"),
                  "w", encoding="utf-8", newline="\n") as handle:
            json.dump(unlock, handle, indent=2, sort_keys=True)
            handle.write("\n")
        ledger_path = os.path.join(freeze_dir(repo_root),
                                   "FINAL_ANCHOR_LEDGER.json")
        with open(ledger_path, "r", encoding="utf-8") as handle:
            ledger = json.load(handle)
        for anchor in BLIND_ANCHORS:
            ledger["anchors"][anchor]["auditor_status"] = "FINAL_CERTIFIED"
        with open(ledger_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(ledger, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print("[P2:final:029] unanimous FIXED: unlocked", flush=True)
        sys.exit(EXIT_UNLOCK)
    missing = [auditor for auditor in panel if auditor not in valid]
    print("[P2:final:026] panel=%s valid matching records=%d missing=%s: "
          "blocked" % (list(panel), len(valid), missing), flush=True)
    sys.exit(EXIT_BLOCKED)


def main(argv):
    """Entry point: ingest-final / assert-final-unlock modes."""
    # [P2-LOG-030] Step: dispatch final-certification mode.
    print("[P2:final:030] final certification invoked", flush=True)
    parser = argparse.ArgumentParser(description="Final certification.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--ingest-final", action="store_true")
    parser.add_argument("--auditor", default="")
    parser.add_argument("--raw", default="")
    parser.add_argument("--attestation", default="")
    parser.add_argument("--assert-final-unlock", action="store_true")
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)
    if args.ingest_final:
        if not args.auditor or not args.raw or not args.attestation:
            fail("--ingest-final requires --auditor, --raw and "
                 "--attestation", EXIT_INVALID)
        ingest_final(repo_root, args.auditor,
                     os.path.abspath(args.raw),
                     os.path.abspath(args.attestation))
    elif args.assert_final_unlock:
        assert_final_unlock(repo_root)
    else:
        fail("one of --ingest-final, --assert-final-unlock is required",
             EXIT_INVALID)


if __name__ == "__main__":
    main(sys.argv[1:])
