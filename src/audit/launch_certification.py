"""Phase-2E pre-execution launch certification (Amendment 007).

Fresh AUD-LNN chairs judge a launch packet: four anchors
FIXED/PARTIAL/AMBIGUOUS/UNSUPPORTED plus per-obligation deferral status
LEGITIMATELY_DEFERRED/IMPROPER_DEFERRAL/UNSUPPORTED. Launch requires one
complete fresh triple, unanimous FIXED anchors AND unanimous
LEGITIMATELY_DEFERRED obligations. Writes into
artifacts/audits/launch_certification/ (never final_certification/).

Step console lines use the [P2:launch:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

ANCHORS = ("H", "P_R", "Lambda", "Atom")
ANCHOR_STATUSES = ("FIXED", "PARTIAL", "AMBIGUOUS", "UNSUPPORTED")
DEFER_STATUSES = ("LEGITIMATELY_DEFERRED", "IMPROPER_DEFERRAL",
                  "UNSUPPORTED")
LAUNCH_RE = re.compile(r"^AUD-L(0*[1-9][0-9]*)$")
OTHER_ID = re.compile(r"AUD-[A-Z][0-9A-Z-]*")
LOCATOR_HINT = re.compile(r"corpus|Sec\.|Section|lines?|Line", re.IGNORECASE)
HARDENING_PATH = re.compile(r"semantic_hardening|non_blind|NON_BLIND",
                            re.IGNORECASE)
DECLARATION = (
    "I was not supplied an expected touch set, expected freeze signature "
    "or K vector, expected classification, desired experiment outcome, or "
    "manuscript claim. I made these judgments solely from the contents "
    "of the sealed launch packet.")

EXIT_UNLOCK = 0
EXIT_NONUNANIMOUS = 3
EXIT_BLOCKED = 4
EXIT_INVALID = 5


def fail(message, code=1):
    """Emit a fail-closed error line and exit with the given code."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:launch:FAIL] " + message, flush=True)
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


def chair_number(chair):
    """Return the integer N of AUD-LN, or None if malformed."""
    if not isinstance(chair, str):
        return None
    match = LAUNCH_RE.match(chair)
    if not match:
        return None
    try:
        number = int(match.group(1))
    except (TypeError, ValueError):
        return None
    return number if number >= 1 else None


def chair_id(number):
    """Return the canonical display ID (zero-padded below 100)."""
    if not isinstance(number, int) or isinstance(number, bool) \
            or number < 1:
        return None
    return "AUD-L%02d" % number if number < 100 else "AUD-L%d" % number


def panel_of(chair):
    """Return the launch panel triple containing a chair, or None."""
    number = chair_number(chair)
    if number is None:
        return None
    base = (number - 1) // 3 * 3 + 1
    return tuple(chair_id(base + offset) for offset in (0, 1, 2))


def launch_dir(repo_root):
    """Return the launch freeze directory path."""
    return os.path.join(repo_root, "artifacts", "audits", "launch")


def records_root(repo_root):
    """Return the launch-certification records directory path."""
    return os.path.join(repo_root, "artifacts", "audits",
                        "launch_certification")


def load_launch(repo_root):
    """Load the launch freeze record, or None."""
    path = os.path.join(launch_dir(repo_root), "LAUNCH_FREEZE.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_obligations(repo_root):
    """Return the ordered registry obligation IDs."""
    path = os.path.join(launch_dir(repo_root),
                        "run_conformance_obligations.json")
    with open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    return [entry["obligation_id"] for entry in doc.get("obligations", [])]


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
    for name in ("expected_signature.json", "canary_expectations.json",
                 "experiment.yaml"):
        if name in text:
            hits.append("expectation-file:" + name)
    if "NON_BLIND" in text:
        hits.append("developmental-marker: in-session subagent output "
                    "cannot certify")
    for other in set(OTHER_ID.findall(text)):
        if other != own_id and (chair_number(other) is not None
                                or re.match(r"^AUD-C(0*[1-9][0-9]*)$",
                                            other)
                                or other in ("AUD-M01", "AUD-M02",
                                             "AUD-M03")):
            hits.append("cross-read:" + other)
    return hits


def validate_launch(doc, launch, auditor, obligation_ids):
    """Validate a parsed launch verdict; return a list of problems."""
    problems = []
    if doc.get("auditor_id") != auditor:
        problems.append("auditor_id must equal the ingested chair")
    if chair_number(doc.get("auditor_id")) is None:
        problems.append("auditor_id not in launch namespace AUD-L<N>")
    if doc.get("qualification") != "COLD_MODEL_INDEPENDENT":
        problems.append("qualification must be COLD_MODEL_INDEPENDENT")
    verdicts = doc.get("verdicts", {})
    for anchor in ANCHORS:
        record = verdicts.get(anchor, {})
        if record.get("status") not in ANCHOR_STATUSES:
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
    deferrals = doc.get("deferrals", {})
    for obligation in obligation_ids:
        status = deferrals.get(obligation)
        if status not in DEFER_STATUSES:
            problems.append("bad deferral status for " + obligation)
    if doc.get("declaration") != DECLARATION:
        problems.append("declaration missing or not verbatim")
    if doc.get("prompt_sha256") != launch.get("prompt_sha256"):
        problems.append("prompt hash mismatch vs launch freeze")
    if doc.get("packet_sha256") != launch.get("packet_sha256"):
        problems.append("packet hash mismatch vs launch freeze")
    if not doc.get("attestation_hash"):
        problems.append("attestation_hash missing")
    isolation = doc.get("isolation", {})
    for key in ("fresh_context", "no_prior_experiment_context",
                "other_outputs_unavailable"):
        if isolation.get(key) is not True:
            problems.append("isolation not affirmed: " + key)
    return problems


def ingest_launch(repo_root, auditor, raw_path, attestation_path):
    """Ingest one launch raw response with strict rules."""
    # [P2-LOG-010] Step: ingest one launch adjudication.
    print("[P2:launch:010] ingesting launch %s" % auditor, flush=True)
    if os.path.isfile(os.path.join(repo_root, "artifacts", "seal",
                                   "TARGET_EXECUTION_LOCK.json")):
        fail("execution lock sealed; launch ingest forbidden "
             "post-invocation", EXIT_INVALID)
    if chair_number(auditor) is None:
        fail("unknown launch chair (want AUD-L<N>, N>=1): " + str(auditor),
             EXIT_INVALID)
    auditor = chair_id(chair_number(auditor))
    if HARDENING_PATH.search(os.path.abspath(raw_path)):
        fail("raw source lives under hardening/non-blind paths",
             EXIT_INVALID)
    launch = load_launch(repo_root)
    if launch is None or not launch.get("frozen"):
        fail("no valid launch freeze; certification not open", EXIT_BLOCKED)
    try:
        expected = launch["panel"]
        if auditor not in expected:
            fail("chair not on the launch panel: " + auditor, EXIT_INVALID)
    except (KeyError, TypeError):
        fail("launch freeze has no panel", EXIT_BLOCKED)
    try:
        obligation_ids = expected_obligations(repo_root)
    except (OSError, ValueError, KeyError):
        fail("run-conformance registry unreadable", EXIT_BLOCKED)
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
    if launch.get("packet_sha256", "") not in attestation_text:
        problems.append("attestation does not bind launch packet hash")
    if launch.get("prompt_sha256", "") not in attestation_text:
        problems.append("attestation does not bind launch prompt hash")
    recomputed = hashlib.sha256(attestation_bytes).hexdigest()
    if doc is not None and doc.get("attestation_hash") != recomputed:
        problems.append("attestation hash does not recompute from "
                        "retained text")
    if doc is not None:
        problems.extend(validate_launch(doc, launch, auditor,
                                        obligation_ids))
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
        "sealed_prompt_sha256": launch.get("prompt_sha256", ""),
        "sealed_packet_sha256": launch.get("packet_sha256", ""),
        "valid": not problems,
        "problems": problems,
    }
    with open(os.path.join(dest, "provenance.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(provenance, handle, indent=2, sort_keys=True)
        handle.write("\n")
    if problems:
        # [P2-LOG-012] Step: invalid launch ingest recorded, not counted.
        print("[P2:launch:012] launch ingest INVALID: %s" % problems,
              flush=True)
        sys.exit(EXIT_INVALID)
    # [P2-LOG-014] Step: valid launch ingest sealed.
    print("[P2:launch:014] launch ingest valid, record sealed", flush=True)


def collect_valid(repo_root, launch, obligation_ids):
    """Collect valid launch records sealed against the launch freeze."""
    valid = {}
    for auditor in launch.get("panel", []):
        record_dir = os.path.join(records_root(repo_root), auditor)
        paths = {name: os.path.join(record_dir, name) for name in
                 ("provenance.json", "verdict.json", "raw_response.txt",
                  "attestation.txt")}
        if not all(os.path.isfile(path) for path in paths.values()):
            continue
        with open(paths["provenance.json"], "r",
                  encoding="utf-8") as handle:
            provenance = json.load(handle)
        if not provenance.get("valid"):
            continue
        if (sha256_file(paths["verdict.json"])
                != provenance.get("verdict_sha256")
                or sha256_file(paths["raw_response.txt"])
                != provenance.get("raw_sha256")
                or hashlib.sha256(open(paths["attestation.txt"], "rb").read(
                    )).hexdigest() != provenance.get(
                    "attestation_sha256")):
            continue
        if (provenance.get("sealed_packet_sha256")
                != launch.get("packet_sha256")
                or provenance.get("sealed_prompt_sha256")
                != launch.get("prompt_sha256")):
            continue
        with open(paths["verdict.json"], "r", encoding="utf-8") as handle:
            valid[auditor] = json.load(handle)
    return valid


def assert_launch_unlock(repo_root):
    """Evaluate the launch conjunction: unanimous anchors + deferrals."""
    # [P2-LOG-020] Step: judge launch unlock.
    print("[P2:launch:020] judging launch certification", flush=True)
    if os.path.isfile(os.path.join(repo_root, "artifacts", "seal",
                                   "TARGET_EXECUTION_LOCK.json")):
        print("[P2:launch:022] execution lock sealed: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    launch = load_launch(repo_root)
    if launch is None or not launch.get("frozen"):
        print("[P2:launch:022] no valid launch freeze: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    try:
        obligation_ids = expected_obligations(repo_root)
    except (OSError, ValueError, KeyError):
        print("[P2:launch:024] registry unreadable: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    valid = collect_valid(repo_root, launch, obligation_ids)
    panel = launch.get("panel", [])
    if not all(auditor in valid for auditor in panel):
        missing = [auditor for auditor in panel if auditor not in valid]
        print("[P2:launch:026] panel=%s valid=%d missing=%s: blocked"
              % (panel, len(valid), missing), flush=True)
        sys.exit(EXIT_BLOCKED)
    short = [auditor for auditor in panel
             if any(valid[auditor]["verdicts"][anchor]["status"] != "FIXED"
                    for anchor in ANCHORS)]
    improper = [(auditor, obligation)
                for auditor in panel for obligation in obligation_ids
                if valid[auditor].get("deferrals", {}).get(obligation)
                != "LEGITIMATELY_DEFERRED"]
    if short or improper:
        print("[P2:launch:028] nonunanimous/improper %s %s: "
              "failure-seal route" % (short, improper), flush=True)
        sys.exit(EXIT_NONUNANIMOUS)
    authorization = {
        "authorized": True,
        "rule": "Amendment-007 unanimous launch certification",
        "auditors": list(panel),
        "packet_sha256": launch.get("packet_sha256"),
        "prompt_sha256": launch.get("prompt_sha256"),
        "sealed_utc": utcnow(),
    }
    with open(os.path.join(launch_dir(repo_root),
                           "TARGET_EXECUTION_AUTHORIZED.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(authorization, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:launch:029] launch authorized", flush=True)
    sys.exit(EXIT_UNLOCK)


def main(argv=None):
    """Entry point: ingest-launch / assert-launch-unlock modes."""
    # [P2-LOG-030] Step: dispatch launch-certification mode.
    print("[P2:launch:030] launch certification invoked", flush=True)
    parser = argparse.ArgumentParser(description="Launch certification.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--ingest-launch", action="store_true")
    parser.add_argument("--auditor", default="")
    parser.add_argument("--raw", default="")
    parser.add_argument("--attestation", default="")
    parser.add_argument("--assert-launch-unlock", action="store_true")
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)
    if args.ingest_launch:
        if not args.auditor or not args.raw or not args.attestation:
            fail("--ingest-launch requires --auditor, --raw and "
                 "--attestation", EXIT_INVALID)
        ingest_launch(repo_root, args.auditor,
                      os.path.abspath(args.raw),
                      os.path.abspath(args.attestation))
    elif args.assert_launch_unlock:
        assert_launch_unlock(repo_root)
    else:
        fail("no launch-certification operation given", EXIT_INVALID)


if __name__ == "__main__":
    main()
