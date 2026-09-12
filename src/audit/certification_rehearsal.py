"""Phase-2B-R autonomous adversarial certification rehearsal (Amendment 003).

Developmental-only harness. Attacks a candidate final freeze with
context-contaminated subagents BEFORE any genuine AUD-C01/02/03 runs.

Layout: artifacts/audits/certification_rehearsal/REHEARSAL_SWEEP_NNN/.
NEVER writes into artifacts/audits/final_certification/ or any AUD-C
namespace (fail-closed + tests). Every output is labeled NON_BLIND.

Commands (all --repo-root required):
--init-sweep SWEEP  (bind freeze REVISION_001 hashes, invariant, exec 0)
--add-report SWEEP --panel PANEL --agent AGENT --file PATH
--normalize SWEEP   (validate + summarize objections ledger)
--verify SWEEP      (invariant + exec 0 + namespace + ledger valid)
--status

Step console lines use the [P2:rehe:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

BASE_SUBDIR = os.path.join("artifacts", "audits", "certification_rehearsal")
FORBIDDEN_WRITE = ("final_certification",)
AUDC_ID = re.compile(r"AUD-C\d")
REHEARSAL_LABEL = re.compile(r"NON_BLIND_(CERTIFICATION_REHEARSAL|ADVERSARIAL_REVIEW|CERTIFIER_EMULATION)")
ALLOWED_DISPOSITIONS = ("VALID_MATERIAL", "VALID_NONMATERIAL", "DUPLICATE",
                        "SOURCE_REFUTED", "OUT_OF_SCOPE", "REVIEWER_ERROR",
                        "IRREDUCIBLE", "UNRESOLVED")
ALLOWED_STATUSES = ("FIXED", "PARTIAL", "AMBIGUOUS", "UNSUPPORTED")
ALLOWED_ANCHORS = ("H", "P_R", "Lambda", "Atom", "PACKET", "PROVENANCE",
                   "LOCATOR", "INVARIANT", "JOINT")
REHEARSAL_HEADER = ("THIS IS A NON_BLIND DEVELOPMENTAL REHEARSAL. "
                    "THIS OUTPUT CANNOT CERTIFY OR UNLOCK THE EXPERIMENT.")


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:rehe:FAIL] " + message, flush=True)
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


def base_dir(repo_root):
    """Return the rehearsal base directory."""
    return os.path.join(repo_root, *BASE_SUBDIR.split("/"))


def sweep_dir(repo_root, sweep):
    """Return one immutable sweep directory."""
    return os.path.join(base_dir(repo_root), sweep)


def guard_no_cert_namespaces(repo_root, sweep=None):
    """Refuse any rehearsal path touching certification namespaces."""
    # [P2-LOG-005] Step: enforce certification-namespace separation.
    targets = [base_dir(repo_root)]
    if sweep:
        targets.append(sweep_dir(repo_root, sweep))
    for target in targets:
        lowered = target.replace(os.sep, "/")
        for forbidden in FORBIDDEN_WRITE:
            if forbidden in lowered:
                fail("rehearsal must never touch %s" % forbidden)
        if AUDC_ID.search(target):
            fail("rehearsal must never touch a certifier namespace")


def target_scan(repo_root):
    """Return completed-world execution artifacts (must stay empty)."""
    # [P2-LOG-008] Step: prove zero completed-world executions.
    hits = []
    for dirpath, _dirs, files in os.walk(repo_root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for name in files:
            lowered = name.lower()
            if lowered.startswith("target_") or lowered.startswith("response_x_"):
                if "blind_anchor_packet" not in dirpath and "final_freeze" not in dirpath:
                    hits.append(os.path.join(dirpath, name))
    return hits


def freeze_hashes(repo_root):
    """Bind operative freeze revision packet/prompt/manifest hashes."""
    # [P2-LOG-010] Step: bind candidate-freeze hashes.
    packet_sha_path = os.path.join(repo_root, "artifacts", "audits",
                                   "semantic_hardening", "final_freeze",
                                   "FINAL_BLIND_PACKET", "PACKET_SHA256.txt")
    with open(packet_sha_path, encoding="utf-8") as handle:
        packet_sha = handle.read().strip()
    prompt_sha = sha256_file(os.path.join(repo_root, "prereg",
                                          "final_certification_prompt.txt"))
    manifest_sha = sha256_file(os.path.join(repo_root, "external",
                                            "MANIFEST.json"))
    freeze_sha = sha256_file(os.path.join(
        repo_root, "artifacts", "audits", "semantic_hardening",
        "final_freeze", "FINAL_SEMANTIC_FREEZE.json"))
    revision = "SEMANTIC_FREEZE_REVISION_001"
    record_path = os.path.join(
        repo_root, "artifacts", "audits", "semantic_hardening",
        "final_freeze", "FINAL_SEMANTIC_FREEZE.json")
    try:
        with open(record_path, encoding="utf-8") as handle:
            revision = "SEMANTIC_FREEZE_REVISION_%03d" % int(
                json.load(handle).get("revision", 1))
    except (OSError, ValueError, TypeError):
        pass
    return {"packet_sha256": packet_sha, "prompt_sha256": prompt_sha,
            "manifest_sha256": manifest_sha, "freeze_sha256": freeze_sha,
            "freeze_revision": revision}


def cmd_init_sweep(args):
    """Create an immutable rehearsal sweep bound to REVISION_001."""
    # [P2-LOG-020] Step: initialize a rehearsal sweep.
    print("[P2:rehe:020] initializing %s" % args.init_sweep, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    guard_no_cert_namespaces(repo_root, args.init_sweep)
    if AUDC_ID.search(args.init_sweep):
        fail("sweep ID must never mimic AUD-C chairs")
    dest = sweep_dir(repo_root, args.init_sweep)
    if os.path.exists(dest):
        fail("sweep exists and is immutable: " + args.init_sweep)
    os.makedirs(os.path.join(dest, "raw_reports"))
    hashes = freeze_hashes(repo_root)
    if target_scan(repo_root):
        fail("completed-world executions exist; rehearsal refused")
    try:
        commit = __import__("subprocess").run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True,
            text=True, timeout=60).stdout.strip()
    except OSError:
        commit = "unknown"
    sweep = {"sweep_id": args.init_sweep,
             "label": "NON_BLIND_CERTIFICATION_REHEARSAL",
             "header": REHEARSAL_HEADER,
             "created_utc": utcnow(), "repo_commit": commit,
             "phase": "2B-R", **hashes,
             "exec_count_at_init": 0, "panels_required": ["A", "B", "C", "D", "E"],
             "mutation_required": None, "preservation": None}
    with open(os.path.join(dest, "SWEEP.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(sweep, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(dest, "objections.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump({"sweep_id": args.init_sweep, "objections": []}, handle,
                  indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:rehe:022] sweep initialized revision=%s packet=%s" % (
        hashes["freeze_revision"], hashes["packet_sha256"][:16]), flush=True)


def check_objection(record):
    """Validate one normalized objection; return problem list."""
    problems = []
    for field in ("objection_id", "anchor", "claim_attacked", "locator",
                  "counterinterpretation", "materiality", "disposition"):
        if not record.get(field):
            problems.append("missing:" + field)
    if record.get("anchor") not in ALLOWED_ANCHORS:
        problems.append("bad-anchor")
    if record.get("disposition") not in ALLOWED_DISPOSITIONS:
        problems.append("bad-disposition")
    if AUDC_ID.search(json.dumps(record)):
        problems.append("cert-namespace-leak")
    if record.get("disposition") == "REVIEWER_ERROR" and not record.get(
            "refuting_evidence"):
        problems.append("reviewer-error-needs-evidence")
    if record.get("disposition") == "VALID_MATERIAL" and not record.get(
            "source_grounding"):
        problems.append("material-needs-grounding")
    return problems


def cmd_add_report(args):
    """Ingest one subagent raw report file into a sweep (copy, never move)."""
    # [P2-LOG-030] Step: ingest a contaminated subagent report.
    print("[P2:rehe:030] ingesting %s/%s" % (args.panel, args.agent), flush=True)
    repo_root = os.path.abspath(args.repo_root)
    guard_no_cert_namespaces(repo_root, args.add_report)
    dest = sweep_dir(repo_root, args.add_report)
    if not os.path.isdir(dest):
        fail("unknown sweep: " + args.add_report)
    with open(args.file, "r", encoding="utf-8", errors="strict") as handle:
        content = handle.read()
    if AUDC_ID.search(content):
        fail("report claims AUD-C identity; refused")
    if "blind" in content.lower() and "NON_BLIND" not in content:
        fail("report missing NON_BLIND label; refused")
    out = os.path.join(dest, "raw_reports", "%s_%s.md" % (args.panel, args.agent))
    if os.path.exists(out):
        fail("report slot occupied (immutable)")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    print("[P2:rehe:032] report stored", flush=True)


def cmd_normalize(args):
    """Validate the sweep objection ledger and write the summary."""
    # [P2-LOG-040] Step: normalize objections (no auto-patching).
    print("[P2:rehe:040] normalizing %s" % args.normalize, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    dest = sweep_dir(repo_root, args.normalize)
    path = os.path.join(dest, "objections.json")
    with open(path, encoding="utf-8") as handle:
        ledger = json.load(handle)
    problems = []
    for record in ledger.get("objections", []):
        bad = check_objection(record)
        if bad:
            problems.append("%s:%s" % (record.get("objection_id", "?"), ",".join(bad)))
    if problems:
        fail("objection ledger invalid: %s" % problems)
    surviving = [o for o in ledger["objections"]
                 if o["disposition"] in ("VALID_MATERIAL", "UNRESOLVED")]
    material = [o for o in surviving if o["disposition"] == "VALID_MATERIAL"]
    summary = {"sweep_id": args.normalize, "normalized_utc": utcnow(),
               "total": len(ledger["objections"]),
               "surviving": len(surviving),
               "valid_material": len(material),
               "mutation_required": bool(material),
               "surviving_ids": [o["objection_id"] for o in surviving]}
    with open(os.path.join(dest, "NORMALIZATION.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(dest, "SWEEP.json"), "r", encoding="utf-8") as handle:
        sweep = json.load(handle)
    sweep["mutation_required"] = bool(material)
    with open(os.path.join(dest, "SWEEP.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(sweep, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:rehe:042] total=%d surviving=%d material=%d" % (
        summary["total"], summary["surviving"], summary["valid_material"]),
        flush=True)
    if material:
        print("[P2:rehe:044] MUTATION_REQUIRED", flush=True)
    else:
        print("[P2:rehe:046] NO_SURVIVING_MATERIAL", flush=True)


def cmd_verify(args):
    """Fail-closed sweep verification: hashes, exec 0, namespaces, ledger."""
    # [P2-LOG-050] Step: verify a rehearsal sweep.
    print("[P2:rehe:050] verifying %s" % args.verify, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    dest = sweep_dir(repo_root, args.verify)
    with open(os.path.join(dest, "SWEEP.json"), encoding="utf-8") as handle:
        sweep = json.load(handle)
    live = freeze_hashes(repo_root)
    for key in ("packet_sha256", "prompt_sha256", "manifest_sha256"):
        if sweep.get(key) != live[key]:
            fail("freeze drift under rehearsal: " + key)
    if target_scan(repo_root):
        fail("executions appeared during rehearsal")
    if os.path.isdir(os.path.join(repo_root, "artifacts", "audits",
                                  "final_certification")):
        for dirpath, _dirs, files in os.walk(os.path.join(
                repo_root, "artifacts", "audits", "final_certification")):
            for name in files:
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8", errors="ignore") as handle:
                    if "REHEARSAL" in handle.read():
                        fail("rehearsal material entered certification")
    with open(os.path.join(dest, "objections.json"), encoding="utf-8") as handle:
        ledger = json.load(handle)
    for record in ledger.get("objections", []):
        if check_objection(record):
            fail("invalid objection: %s" % record.get("objection_id"))
        if record.get("disposition") == "UNRESOLVED":
            fail("UNRESOLVED objection blocks preservation")
    print("[P2:rehe:052] sweep verified", flush=True)


def cmd_status(args):
    """Print rehearsal base status."""
    # [P2-LOG-060] Step: report rehearsal status.
    repo_root = os.path.abspath(args.repo_root)
    base = base_dir(repo_root)
    sweeps = sorted(os.listdir(base)) if os.path.isdir(base) else []
    print("[P2:rehe:060] sweeps=%s" % ",".join(sweeps), flush=True)


def main(argv=None):
    """Entry point: dispatch rehearsal operations."""
    # [P2-LOG-070] Step: dispatch rehearsal mode.
    print("[P2:rehe:070] certification rehearsal invoked", flush=True)
    parser = argparse.ArgumentParser(description="Certification rehearsal.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--init-sweep", default="")
    parser.add_argument("--add-report", default="")
    parser.add_argument("--panel", default="")
    parser.add_argument("--agent", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--normalize", default="")
    parser.add_argument("--verify", default="")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    if args.init_sweep:
        cmd_init_sweep(args)
    elif args.add_report:
        if not (args.panel and args.agent and args.file):
            fail("--add-report needs --panel --agent --file")
        cmd_add_report(args)
    elif args.normalize:
        cmd_normalize(args)
    elif args.verify:
        cmd_verify(args)
    elif args.status:
        cmd_status(args)
    else:
        fail("no rehearsal operation given")
    # [P2-LOG-072] Step: rehearsal operation complete.
    print("[P2:rehe:072] rehearsal operation complete", flush=True)


if __name__ == "__main__":
    main()
