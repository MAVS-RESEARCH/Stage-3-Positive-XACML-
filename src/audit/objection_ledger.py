"""Objection-ledger operations for PC-XACML-S3+ Phase 2B-H.

The ledger is append-mostly: objections are added, resolved with
source-grounded evidence, or marked IRREDUCIBLE; nothing is deleted and
no reviewer disagreement is ever merely marked "wrong" (category F
requires exact frozen-source counter-evidence). Modes: --render-md,
--add, --resolve, --verify, --list-open. Any record with
external_semantics_changed true or downstream_result_info_used true
fails verification (fail-closed).

Step console lines use the [P2:obj:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import json
import os
import sys

ANCHORS = ("H", "P_R", "Lambda", "Atom", "GLOBAL")
CATEGORIES = ("A", "B", "C", "D", "E", "F", "G")
STATUSES = ("OPEN", "RESOLVED", "IRREDUCIBLE")
REQUIRED = ("objection_id", "round_id", "anchor", "originating_reviewer",
            "objection", "locators", "category", "materiality",
            "resolution_status")


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:obj:FAIL] " + message, flush=True)
    sys.exit(1)


def load_ledger(path):
    """Load and minimally shape-check the ledger."""
    with open(path, "r", encoding="utf-8") as handle:
        ledger = json.load(handle)
    if not isinstance(ledger.get("objections"), list):
        fail("ledger lacks objections list: " + path)
    return ledger


def save_ledger(path, ledger):
    """Write the ledger back deterministically."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(ledger, handle, indent=2, sort_keys=True)
        handle.write("\n")


def check_record(record):
    """Return a list of structural problems for one objection."""
    problems = []
    for key in REQUIRED:
        if key not in record:
            problems.append("missing " + key)
    if record.get("anchor") not in ANCHORS:
        problems.append("bad anchor")
    if record.get("category") not in CATEGORIES:
        problems.append("bad category")
    if record.get("resolution_status") not in STATUSES:
        problems.append("bad status")
    if record.get("category") == "F" and record.get(
            "resolution_status") == "RESOLVED" and not record.get(
                "source_grounding_evidence"):
        problems.append("category F resolution needs frozen evidence")
    if record.get("external_semantics_changed") is True:
        problems.append("external semantics must never change")
    if record.get("downstream_result_info_used", False) is True:
        problems.append("downstream result information forbidden")
    return problems


def cmd_verify(args):
    """Verify ledger structure and fail-closed invariants."""
    # [P2-LOG-010] Step: verify the objection ledger.
    print("[P2:obj:010] verifying objection ledger", flush=True)
    ledger = load_ledger(args.ledger)
    seen = set()
    bad = []
    for record in ledger["objections"]:
        if record.get("objection_id") in seen:
            bad.append("duplicate id " + str(record.get("objection_id")))
        seen.add(record.get("objection_id"))
        bad.extend(record.get("objection_id", "?") + ": " + problem
                   for problem in check_record(record))
    if bad:
        fail("ledger invalid: %s" % bad)
    print("[P2:obj:012] ledger valid objections=%d" % len(seen), flush=True)


def cmd_render_md(args):
    """Render the human-readable ledger table."""
    # [P2-LOG-020] Step: render the ledger markdown.
    print("[P2:obj:020] rendering ledger markdown", flush=True)
    ledger = load_ledger(args.ledger)
    lines = ["# Objection ledger (%s)" % ledger.get("ledger_id", ""),
             "",
             "| id | round | anchor | cat | status | objection |",
             "|---|---|---|---|---|---|"]
    for record in ledger["objections"]:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            record.get("objection_id"), record.get("round_id"),
            record.get("anchor"), record.get("category"),
            record.get("resolution_status"),
            record.get("objection", "")[:160].replace("|", "/")))
    lines += ["",
              "Full records (evidence, dispositions) live in the JSON "
              "ledger; this table is a finding aid only."]
    out = args.out or os.path.splitext(args.ledger)[0] + ".md"
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print("[P2:obj:022] rendered %s" % out, flush=True)


def cmd_add(args):
    """Append one objection from a JSON file."""
    # [P2-LOG-030] Step: add one objection.
    print("[P2:obj:030] adding objection", flush=True)
    ledger = load_ledger(args.ledger)
    with open(args.objection, "r", encoding="utf-8") as handle:
        record = json.load(handle)
    ids = set(r.get("objection_id") for r in ledger["objections"])
    if record.get("objection_id") in ids:
        fail("duplicate objection id")
    problems = check_record(record)
    if problems:
        fail("invalid objection: %s" % problems)
    ledger["objections"].append(record)
    save_ledger(args.ledger, ledger)
    print("[P2:obj:032] added %s" % record.get("objection_id"), flush=True)


def cmd_resolve(args):
    """Mark one objection resolved/irreducible with evidence."""
    # [P2-LOG-040] Step: resolve one objection.
    print("[P2:obj:040] resolving %s" % args.objection_id, flush=True)
    ledger = load_ledger(args.ledger)
    found = [r for r in ledger["objections"]
             if r.get("objection_id") == args.objection_id]
    if len(found) != 1:
        fail("objection id not unique/found")
    record = found[0]
    record["resolution_status"] = args.status
    record["final_disposition"] = args.disposition
    record["files_changed"] = args.files.split(",") if args.files else []
    record["source_grounding_evidence"] = args.evidence
    record["independent_recheck"] = args.recheck
    problems = check_record(record)
    if problems:
        fail("resolution invalid: %s" % problems)
    save_ledger(args.ledger, ledger)
    print("[P2:obj:042] resolved %s as %s"
          % (args.objection_id, args.status), flush=True)


def cmd_list_open(args):
    """List unresolved material objections."""
    # [P2-LOG-050] Step: list open objections.
    print("[P2:obj:050] open material objections:", flush=True)
    ledger = load_ledger(args.ledger)
    count = 0
    for record in ledger["objections"]:
        if record.get("resolution_status") == "OPEN":
            print("[P2:obj:052] %s [%s/%s] %s" % (
                record.get("objection_id"), record.get("anchor"),
                record.get("category"),
                record.get("objection", "")[:120]), flush=True)
            count += 1
    print("[P2:obj:054] open count=%d" % count, flush=True)


def main(argv):
    """Entry point: dispatch ledger operations."""
    # [P2-LOG-060] Step: dispatch ledger mode.
    print("[P2:obj:060] objection ledger invoked", flush=True)
    parser = argparse.ArgumentParser(description="Objection ledger ops.")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--render-md", action="store_true")
    parser.add_argument("--out", default="")
    parser.add_argument("--add", action="store_true")
    parser.add_argument("--objection", default="")
    parser.add_argument("--resolve", action="store_true")
    parser.add_argument("--objection-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--disposition", default="")
    parser.add_argument("--files", default="")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--recheck", default="")
    parser.add_argument("--list-open", action="store_true")
    args = parser.parse_args(argv)
    if args.verify:
        cmd_verify(args)
    elif args.render_md:
        cmd_render_md(args)
    elif args.add:
        cmd_add(args)
    elif args.resolve:
        cmd_resolve(args)
    elif args.list_open:
        cmd_list_open(args)
    else:
        fail("one mode is required")


if __name__ == "__main__":
    main(sys.argv[1:])
