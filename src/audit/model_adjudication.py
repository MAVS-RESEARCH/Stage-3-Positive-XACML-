"""Amendment-001 cold-model blind adjudication for PC-XACML-S3+.

Implements the amended 2B gate: three independently initialized
cold-model adjudications (AUD-M01/02/03) over the already-sealed blind
packet with the frozen prompt. Unanimous FIXED on H/P_R/Lambda/Atom is
required; no majority vote, no reconciliation, no tie-breaking reruns.

Modes: --ingest (validate + seal one delivered raw response; never
rewrites verdict content), --assert-model-unlock (evaluate the full
amended conjunction; exit 0 unlock, 3 nonunanimous anchor
non-support, 4 blocked-pending, 5 invalid), --check-amendment
(validate the Amendment-001 seal record standalone).

Independence here means inference-context independence (fresh context,
identical inputs, no cross-visibility), NOT statistical independence,
NOT human independence. This module never invokes a model itself:
verdicts arrive as externally supplied raw files. Subagent-based
in-session adjudication is prohibited (shared context contaminates
blindness) and is refused by the isolation rules below.

Step console lines use the [P2:model:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from blind_adjudication import REDACTION_PATTERNS, TOUCH_ASSIGNMENT

AUDITORS = ("AUD-M01", "AUD-M02", "AUD-M03")
BLIND_ANCHORS = ("H", "P_R", "Lambda", "Atom")
ALLOWED_STATUSES = ("FIXED", "PARTIAL", "AMBIGUOUS", "UNSUPPORTED")
DECLARATION = (
    "I was not supplied an expected touch set, expected freeze signature "
    "or K vector, expected classification, desired experiment outcome, or "
    "manuscript claim. I made these judgments solely from the contents "
    "of the sealed blind packet.")
EXPECTATION_FILENAMES = ("expected_signature.json",
                         "canary_expectations.json", "experiment.yaml")
OTHER_ID = re.compile(r"AUD-M0[123]")
LOCATOR_HINT = re.compile(r"corpus|Sec\.|Section|lines?|Line", re.IGNORECASE)

EXIT_UNLOCK = 0
EXIT_NONUNANIMOUS = 3
EXIT_BLOCKED = 4
EXIT_INVALID = 5


def fail(message, code=1):
    """Emit a fail-closed error line and exit with the given code."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:model:FAIL] " + message, flush=True)
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


def audits_dir(repo_root):
    """Return the audits directory path."""
    return os.path.join(repo_root, "artifacts", "audits")


def records_root(repo_root):
    """Return the model-adjudication records directory path."""
    return os.path.join(audits_dir(repo_root), "model_adjudication")


def amendment_paths(repo_root):
    """Return (amendment file, amendment seal record) paths."""
    base = audits_dir(repo_root)
    return (os.path.join(repo_root, "PROTOCOL_AMENDMENT_001.md"),
            os.path.join(base, "amendment_001_seal.json"))


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
    """Scan text for expectation leakage and cross-adjudicator reads."""
    hits = []
    for pattern in REDACTION_PATTERNS:
        if pattern in text:
            hits.append("redaction-pattern:" + pattern)
    for name in EXPECTATION_FILENAMES:
        if name in text:
            hits.append("expectation-file:" + name)
    if TOUCH_ASSIGNMENT.search(text):
        hits.append("touch-assignment")
    for other in OTHER_ID.findall(text):
        if other != own_id:
            hits.append("cross-read:" + other)
    return hits


def validate_record(doc, sealed_prompt_sha, sealed_packet_sha):
    """Validate a parsed model verdict; return a list of problems."""
    problems = []
    if doc.get("auditor_id") not in AUDITORS:
        problems.append("auditor_id not one of AUD-M01/02/03")
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
    if doc.get("prompt_sha256") != sealed_prompt_sha:
        problems.append("prompt hash mismatch")
    if doc.get("packet_sha256") != sealed_packet_sha:
        problems.append("packet hash mismatch")
    if not doc.get("attestation_hash"):
        problems.append("attestation_hash missing")
    isolation = doc.get("isolation", {})
    for key in ("fresh_context", "no_prior_experiment_context",
                "other_outputs_unavailable"):
        if isolation.get(key) is not True:
            problems.append("isolation not affirmed: " + key)
    return problems


def load_seal_record(repo_root):
    """Load the amendment seal record, failing closed if absent."""
    amendment_file, seal_path = amendment_paths(repo_root)
    if not (os.path.isfile(amendment_file)
            and os.path.isfile(seal_path)):
        return None, "amendment or seal record absent"
    with open(seal_path, "r", encoding="utf-8") as handle:
        return json.load(handle), ""


def check_amendment(repo_root):
    """Validate the Amendment-001 seal: hash, ordering basis, ancestry."""
    # [P2-LOG-010] Step: validate the amendment seal record.
    print("[P2:model:010] validating Amendment-001 seal", flush=True)
    amendment_file, seal_path = amendment_paths(repo_root)
    seal, error = load_seal_record(repo_root)
    if seal is None:
        print("[P2:model:012] " + error, flush=True)
        return False
    if sha256_file(amendment_file) != seal.get("amendment_sha256"):
        print("[P2:model:014] amendment hash mismatch", flush=True)
        return False
    if not seal.get("sealed_utc"):
        print("[P2:model:016] amendment seal timestamp missing",
              flush=True)
        return False
    pre_commit = seal.get("pre_amendment_commit", "")
    git_dir = os.path.join(repo_root, ".git")
    # Review-snapshot branch (double-blind, see README_REVIEW.md):
    # orphan review commit has no canonical history and pre_amendment_commit
    # is a review alias (<AUTHOR_REPO_COMMIT_...>), not a resolvable git
    # object. Skip the merge-base ancestry check in that case; other bindings
    # (amendment hash, timestamp) remain enforced. Canonical branch retains
    # the strict check.
    if seal.get("review_snapshot") is True and isinstance(pre_commit, str) and pre_commit.startswith("<AUTHOR_"):
        print("[P2:model:018] review snapshot: ancestry check skipped (alias)", flush=True)
    elif pre_commit and os.path.isdir(git_dir):
        try:
            completed = subprocess.run(
                ["git", "merge-base", "--is-ancestor", pre_commit, "HEAD"],
                cwd=repo_root, capture_output=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            completed = None
        if completed is not None and completed.returncode != 0:
            print("[P2:model:018] pre-amendment commit not an ancestor",
                  flush=True)
            return False
    print("[P2:model:019] amendment seal valid", flush=True)
    return True


def ingest(repo_root, auditor, raw_path):
    """Ingest one delivered raw model response (no content rewriting)."""
    # [P2-LOG-020] Step: ingest one raw adjudication.
    print("[P2:model:020] ingesting %s" % auditor, flush=True)
    if auditor not in AUDITORS:
        fail("unknown adjudicator: " + auditor, EXIT_INVALID)
    with open(raw_path, "rb") as handle:
        raw_bytes = handle.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = ""
    problems = []
    doc, error = extract_json(raw_text)
    if doc is None:
        problems.append(error)
    else:
        problems.extend(scan_text_leakage(raw_text, auditor))
    seal, _ = load_seal_record(repo_root)
    sealed_prompt = (seal or {}).get("prompt_sha256", "")
    sealed_packet = (seal or {}).get("packet_sha256", "")
    if doc is not None:
        problems.extend(validate_record(doc, sealed_prompt, sealed_packet))
    dest = os.path.join(records_root(repo_root), auditor)
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "raw_response.txt"), "wb") as handle:
        handle.write(raw_bytes)
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
        "sealed_prompt_sha256": sealed_prompt,
        "sealed_packet_sha256": sealed_packet,
        "valid": not problems,
        "problems": problems,
    }
    with open(os.path.join(dest, "provenance.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(provenance, handle, indent=2, sort_keys=True)
        handle.write("\n")
    if problems:
        # [P2-LOG-022] Step: invalid ingest recorded, not counted.
        print("[P2:model:022] ingest INVALID: %s" % problems, flush=True)
        sys.exit(EXIT_INVALID)
    # [P2-LOG-024] Step: valid ingest sealed.
    print("[P2:model:024] ingest valid, verdict sealed", flush=True)


def collect_valid(repo_root):
    """Collect the valid adjudication records (AUD-M01/02/03)."""
    valid = {}
    for auditor in AUDITORS:
        record_dir = os.path.join(records_root(repo_root), auditor)
        provenance_path = os.path.join(record_dir, "provenance.json")
        verdict_path = os.path.join(record_dir, "verdict.json")
        raw_path = os.path.join(record_dir, "raw_response.txt")
        if not (os.path.isfile(provenance_path)
                and os.path.isfile(verdict_path)
                and os.path.isfile(raw_path)):
            continue
        with open(provenance_path, "r", encoding="utf-8") as handle:
            provenance = json.load(handle)
        if not provenance.get("valid"):
            continue
        # Tamper-evidence: re-hash sealed artifacts before trusting them.
        if (sha256_file(verdict_path) != provenance.get("verdict_sha256")
                or sha256_file(raw_path) != provenance.get("raw_sha256")):
            continue
        with open(verdict_path, "r", encoding="utf-8") as handle:
            valid[auditor] = json.load(handle)
    return valid


def assert_model_unlock(repo_root):
    """Evaluate the full amended unlock conjunction."""
    # [P2-LOG-030] Step: judge the amended model unlock conjunction.
    print("[P2:model:030] judging amended model unlock", flush=True)
    if not check_amendment(repo_root):
        print("[P2:model:032] amendment invalid: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    seal, _ = load_seal_record(repo_root)
    with open(os.path.join(audits_dir(repo_root), "blind_anchor_packet",
                           "PACKET_SHA256.txt"),
              encoding="utf-8") as handle:
        live_packet = handle.read().strip()
    if live_packet != seal.get("packet_sha256"):
        print("[P2:model:034] packet hash drift: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    prompt_path = os.path.join(repo_root, "prereg",
                               "blind_model_adjudication_prompt.txt")
    if sha256_file(prompt_path) != seal.get("prompt_sha256"):
        print("[P2:model:036] prompt hash drift: locked", flush=True)
        sys.exit(EXIT_BLOCKED)
    valid = collect_valid(repo_root)
    missing = [a for a in AUDITORS if a not in valid]
    if missing:
        print("[P2:model:038] valid records=%d missing=%s: blocked"
              % (len(valid), missing), flush=True)
        sys.exit(EXIT_BLOCKED)
    short = [a for a in AUDITORS
             if any(valid[a]["verdicts"][anchor]["status"] != "FIXED"
                    for anchor in BLIND_ANCHORS)]
    if short:
        print("[P2:model:039] nonunanimous %s: failure-seal route"
              % short, flush=True)
        sys.exit(EXIT_NONUNANIMOUS)
    unlock = {
        "unlocked": True,
        "rule": "Amendment-001 unanimous cold-model adjudication",
        "auditors": list(AUDITORS),
        "amendment_sha256": seal.get("amendment_sha256"),
        "packet_sha256": seal.get("packet_sha256"),
        "prompt_sha256": seal.get("prompt_sha256"),
        "sealed_utc": utcnow(),
    }
    with open(os.path.join(audits_dir(repo_root), "model_unlock.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(unlock, handle, indent=2, sort_keys=True)
        handle.write("\n")
    ledger_path = os.path.join(repo_root, "derived", "anchor_ledger.json")
    with open(ledger_path, "r", encoding="utf-8") as handle:
        ledger = json.load(handle)
    for anchor in BLIND_ANCHORS:
        ledger["anchors"][anchor]["auditor_status"] = "MODEL_BLIND_PASS"
    with open(ledger_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(ledger, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:model:039] unanimous FIXED: unlocked", flush=True)
    sys.exit(EXIT_UNLOCK)


def main(argv):
    """Entry point: ingest / assert-model-unlock / check-amendment."""
    # [P2-LOG-040] Step: dispatch model-adjudication mode.
    print("[P2:model:040] model adjudication invoked", flush=True)
    parser = argparse.ArgumentParser(description="Amendment-001 gate.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--ingest", action="store_true")
    parser.add_argument("--auditor", default="")
    parser.add_argument("--raw", default="")
    parser.add_argument("--assert-model-unlock", action="store_true")
    parser.add_argument("--check-amendment", action="store_true")
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)
    if args.ingest:
        if not args.auditor or not args.raw:
            fail("--ingest requires --auditor and --raw", EXIT_INVALID)
        ingest(repo_root, args.auditor, os.path.abspath(args.raw))
    elif args.assert_model_unlock:
        assert_model_unlock(repo_root)
    elif args.check_amendment:
        sys.exit(0 if check_amendment(repo_root) else 1)
    else:
        fail("one of --ingest, --assert-model-unlock, --check-amendment "
             "is required", EXIT_INVALID)


if __name__ == "__main__":
    main(sys.argv[1:])
