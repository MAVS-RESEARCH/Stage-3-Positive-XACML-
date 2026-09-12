"""Generic recursive certification cycles (Amendment 005).

Each CERTIFICATION_CYCLE_NNN binds one frozen semantic revision to one
fresh three-chair panel and resolves to exactly one of
CERTIFICATION_PASSED, CERTIFICATION_FAILED_REPAIRABLE, or
CERTIFICATION_FAILED_IRREDUCIBLE. Sealed cycles are immutable.

Commands (all --repo-root required):
--init-cycle ID --revision N --panel AUD-C0X,AUD-C0Y,AUD-C0Z
--assess-cycle ID (tally panel records vs operative freeze)
--decide-cycle ID --verdict V --reason R [--material-objections M]
--handoff (write NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md)
--status

Step console lines use the [P2:cyc:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

BASE_SUBDIR = os.path.join("artifacts", "audits", "certification_cycles")
PANEL_RE = re.compile(r"^AUD-C(0[1-9]|1[0-2])$")
CYCLE_RE = re.compile(r"^CERTIFICATION_CYCLE_[0-9]{3}$")
DECISIONS = ("CERTIFICATION_PASSED", "CERTIFICATION_FAILED_REPAIRABLE",
             "CERTIFICATION_FAILED_IRREDUCIBLE")
FORBIDDEN_HANDOFF = ("expected_touch", "expected_K", "expected_classification",
                     "hardening history", "rehearsal", "manuscript",
                     "desired outcome", "AUD-C01-verdict", "AUD-C02-verdict",
                     "AUD-C03-verdict")


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:cyc:FAIL] " + message, flush=True)
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
    """Return the cycles base directory."""
    return os.path.join(repo_root, *BASE_SUBDIR.split("/"))


def state_path(repo_root):
    """Return the cycles state file path."""
    return os.path.join(base_dir(repo_root), "CYCLES.json")


def load_state(repo_root):
    """Load cycle state, or a pristine default."""
    path = state_path(repo_root)
    if not os.path.isfile(path):
        return {"cycles": []}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(repo_root, state):
    """Write cycle state deterministically."""
    state["updated_utc"] = utcnow()
    os.makedirs(base_dir(repo_root), exist_ok=True)
    with open(state_path(repo_root), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")


def find_cycle(state, cycle_id):
    """Return the cycle record or None."""
    for record in state.get("cycles", []):
        if record.get("cycle_id") == cycle_id:
            return record
    return None


def cmd_init_cycle(args):
    """Create an immutable cycle binding revision to panel."""
    # [P2-LOG-010] Step: initialize a certification cycle.
    print("[P2:cyc:010] initializing %s" % args.init_cycle, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    if not CYCLE_RE.match(args.init_cycle):
        fail("bad cycle id (want CERTIFICATION_CYCLE_NNN)")
    try:
        revision = int(args.revision)
    except (TypeError, ValueError):
        fail("revision must be an integer")
    if isinstance(args.revision, bool) or revision < 1:
        fail("revision must be a positive integer")
    panel = [item.strip() for item in args.panel.split(",")]
    if len(panel) != 3 or any(not PANEL_RE.match(item) for item in panel):
        fail("panel must be three AUD-CNN chairs")
    if len(set(panel)) != 3:
        fail("panel chairs must be distinct")
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.abspath(__file__))))
    import final_certification
    numbers = sorted(int(item.rsplit("-C", 1)[1]) for item in panel)
    if numbers[2] - numbers[0] != 2 or (numbers[0] - 1) % 3 != 0:
        fail("panel must be one fixed triple (01-03, 04-06, 07-09, 10-12)")
    expected = final_certification.REVISION_PANELS.get(revision, None)
    if expected is None:
        if revision < 5:
            fail("revision %d takes no external panel" % revision)
        expected = revision - 3
    if tuple(panel) != final_certification.PANELS[expected]:
        fail("panel does not match revision binding (want %s)" % ",".join(
            final_certification.PANELS[expected]))
    state = load_state(repo_root)
    if find_cycle(state, args.init_cycle) is not None:
        fail("cycle exists and is immutable: " + args.init_cycle)
    for record in state.get("cycles", []):
        if record.get("revision") == revision:
            fail("revision already bound to " + record["cycle_id"])
        if set(record.get("panel", [])) & set(panel):
            fail("chair reuse across cycles is forbidden")
    state["cycles"].append({"cycle_id": args.init_cycle,
                            "revision": revision, "panel": panel,
                            "status": "OPEN_PENDING", "assessment": None,
                            "decision": None})
    save_state(repo_root, state)
    print("[P2:cyc:012] cycle initialized", flush=True)


def read_panel_records(repo_root, panel):
    """Load sealed final-certification records for a panel."""
    records = {}
    for auditor in panel:
        base = os.path.join(repo_root, "artifacts", "audits",
                            "final_certification", auditor)
        paths = {name: os.path.join(base, name) for name in
                 ("verdict.json", "provenance.json", "raw_response.txt",
                  "attestation.txt")}
        if not all(os.path.isfile(path) for path in paths.values()):
            continue
        with open(paths["verdict.json"], encoding="utf-8") as handle:
            verdict = json.load(handle)
        with open(paths["provenance.json"], encoding="utf-8") as handle:
            provenance = json.load(handle)
        records[auditor] = {"verdict": verdict, "provenance": provenance,
                            "shas": {name: sha256_file(paths[name])
                                     for name in paths}}
    return records


def cmd_assess_cycle(args):
    """Tally a cycle's panel against the operative freeze; no judgment."""
    # [P2-LOG-020] Step: assess a certification cycle.
    print("[P2:cyc:020] assessing %s" % args.assess_cycle, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    record = find_cycle(state, args.assess_cycle)
    if record is None:
        fail("unknown cycle")
    if record.get("decision") is not None:
        fail("cycle already decided; assessment is immutable")
    freeze_path = os.path.join(repo_root, "artifacts", "audits",
                               "semantic_hardening", "final_freeze",
                               "FINAL_SEMANTIC_FREEZE.json")
    if not os.path.isfile(freeze_path):
        fail("no operative freeze present")
    with open(freeze_path, encoding="utf-8") as handle:
        freeze = json.load(handle)
    if freeze.get("revision") != record["revision"]:
        snap = os.path.join(
            repo_root, "artifacts", "audits", "semantic_hardening",
            "final_freeze_REVISION_%03d" % record["revision"],
            "FINAL_SEMANTIC_FREEZE.json")
        if not os.path.isfile(snap):
            fail("operative freeze revision %s != cycle revision %s "
                 "and no snapshot" % (freeze.get("revision"),
                                      record["revision"]))
        with open(snap, encoding="utf-8") as handle:
            freeze = json.load(handle)
        if freeze.get("revision") != record["revision"]:
            fail("snapshot revision %s != cycle revision %s" % (
                freeze.get("revision"), record["revision"]))
        print("[P2:cyc:021] assessing against preserved revision %s" % (
            record["revision"]), flush=True)
    panel_records = read_panel_records(repo_root, record["panel"])
    tally = {}
    for auditor in record["panel"]:
        entry = panel_records.get(auditor)
        if entry is None or not entry["provenance"].get("valid"):
            tally[auditor] = "MISSING_OR_INVALID"
            continue
        verdict = entry["verdict"]
        if (entry["provenance"].get("sealed_packet_sha256")
                != freeze.get("packet_sha256")
                or entry["provenance"].get("sealed_prompt_sha256")
                != freeze.get("prompt_sha256")):
            tally[auditor] = "STALE_FREEZE"
            continue
        verdicts = verdict.get("verdicts", {})
        bad = [anchor for anchor in ("H", "P_R", "Lambda", "Atom")
               if verdicts.get(anchor, {}).get("status") != "FIXED"]
        tally[auditor] = "FIXED" if not bad else "NON_FIXED:" + ",".join(bad)
    assessment = {"assessed_utc": utcnow(),
                  "freeze_packet_sha256": freeze.get("packet_sha256"),
                  "freeze_prompt_sha256": freeze.get("prompt_sha256"),
                  "tally": tally,
                  "unanimous": all(value == "FIXED"
                                   for value in tally.values())
                  and len(tally) == 3}
    record["assessment"] = assessment
    save_state(repo_root, state)
    with open(os.path.join(base_dir(repo_root),
                           args.assess_cycle + ".assessment.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(assessment, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:cyc:022] unanimous=%s" % assessment["unanimous"], flush=True)


def cmd_decide_cycle(args):
    """Seal a cycle decision, consistency-checked against assessment."""
    # [P2-LOG-030] Step: decide a certification cycle.
    print("[P2:cyc:030] deciding %s" % args.decide_cycle, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    if args.verdict not in DECISIONS:
        fail("bad verdict (want %s)" % "/".join(DECISIONS))
    state = load_state(repo_root)
    record = find_cycle(state, args.decide_cycle)
    if record is None:
        fail("unknown cycle: " + args.decide_cycle)
    if record.get("decision") is not None:
        fail("cycle already decided and immutable")
    assessment = record.get("assessment")
    if assessment is None:
        fail("assess the cycle before deciding")
    material = [item.strip() for item in (args.material_objections or "")
                .split(";") if item.strip()]
    if not args.reason.strip():
        fail("every decision requires a non-empty reason")
    if args.verdict == "CERTIFICATION_PASSED":
        if not assessment.get("unanimous"):
            fail("PASSED requires a unanimous FIXED tally")
        if material:
            fail("PASSED admits no material objections")
    elif args.verdict == "CERTIFICATION_FAILED_REPAIRABLE":
        if assessment.get("unanimous"):
            fail("unanimous tally cannot be repairable-failed")
        if not material:
            fail("REPAIRABLE requires >=1 material objection id")
    elif args.verdict == "CERTIFICATION_FAILED_IRREDUCIBLE":
        if assessment.get("unanimous"):
            fail("unanimous tally cannot be irreducible-failed")
        if not args.reason.strip():
            fail("IRREDUCIBLE requires a naturalness proof pointer")
    record["decision"] = {"verdict": args.verdict, "reason": args.reason,
                          "material_objections": material,
                          "decided_utc": utcnow()}
    record["status"] = {"CERTIFICATION_PASSED": "SEALED_PASSED",
                        "CERTIFICATION_FAILED_REPAIRABLE":
                        "SEALED_FAILED_REPAIRABLE",
                        "CERTIFICATION_FAILED_IRREDUCIBLE":
                        "SEALED_FAILED_IRREDUCIBLE"}[args.verdict]
    save_state(repo_root, state)
    print("[P2:cyc:032] decision sealed: %s" % args.verdict, flush=True)


def next_panel(state):
    """Return the panel needing external sessions: oldest open cycle first."""
    import re as re_module
    for record in state.get("cycles", []):
        panel = record.get("panel", [])
        if record.get("decision") is None and len(panel) == 3 and all(
                PANEL_RE.match(item) for item in panel) and len(
                set(panel)) == 3:
            return list(panel)
    highest = 0
    for record in state.get("cycles", []):
        try:
            numbers = sorted(int(re_module.search(r"\d+", chair).group(0))
                             for chair in record.get("panel", []))
        except (TypeError, ValueError, AttributeError):
            continue
        if (len(numbers) == 3 and numbers[2] - numbers[0] == 2
                and (numbers[0] - 1) % 3 == 0):
            highest = max(highest, (numbers[0] - 1) // 3 + 1)
    base = highest * 3 + 1
    if base + 2 > 12:
        return None
    return ["AUD-C%02d" % number
            for number in (base, base + 1, base + 2)]


def cmd_handoff(args):
    """Write the next-panel handoff file from live operative hashes."""
    # [P2-LOG-040] Step: generate the external handoff.
    print("[P2:cyc:040] generating handoff", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    freeze_path = os.path.join(repo_root, "artifacts", "audits",
                               "semantic_hardening", "final_freeze",
                               "FINAL_SEMANTIC_FREEZE.json")
    with open(freeze_path, encoding="utf-8") as handle:
        freeze = json.load(handle)
    panel = None
    for record in state.get("cycles", []):
        if (record.get("decision") is None
                and record.get("revision") == freeze.get("revision")):
            panel = list(record["panel"])
            break
    if panel is None:
        panel = next_panel(state)
    if panel is None:
        fail("no fresh panel available")
    packet = "artifacts/audits/semantic_hardening/final_freeze/" \
        "FINAL_BLIND_PACKET"
    prompt = "prereg/final_certification_prompt.txt"
    ingest_lines = [
        "python src/audit/final_certification.py --repo-root . "
        "--ingest-final --auditor %s "
        "--raw <chair-%s-raw-file> --attestation <chair-%s-attestation>"
        % (chair, chair, chair) for chair in panel]
    doc = "\n".join([
        "# NEXT EXTERNAL CERTIFICATION HANDOFF (frozen inputs only)",
        "",
        "Auditor IDs (fresh chairs, one isolated session each): %s."
        % ", ".join(panel),
        ("Operative packet path: "
         "artifacts/audits/semantic_hardening/final_freeze/"
         "FINAL_BLIND_PACKET/"),
        "Operative packet SHA-256: %s" % freeze.get("packet_sha256"),
        "Operative prompt path: prereg/final_certification_prompt.txt",
        "Operative prompt SHA-256: %s" % freeze.get("prompt_sha256"),
        ("Final schema: embedded in the prompt (verdict JSON shape lines "
         "39-52: verdict_id, auditor_id, qualification "
         "COLD_MODEL_INDEPENDENT, per-anchor verdicts with locators, "
         "attestation_hash, verbatim declaration, prompt/packet hashes, "
         "isolation flags) plus a separate attestation text file."),
        "",
        "## Cold-session instructions",
        "",
        ("1. Open a brand-new empty session per chair; never reuse a "
         "session across chairs."),
        ("2. Give the chair ONLY: the packet folder, the prompt file "
         "bytes, and the schema above. Nothing else."),
        ("3. Tell the chair its auditor ID and demand exactly two "
         "artifacts: the verdict JSON and the separate attestation text, "
         "with attestation_hash = sha256 of the attestation exact bytes."),
        ("4. Never mention other chairs, prior results, or any expectation "
         "about the outcome."),
        "",
        "## Ingestion commands (operator runs after collecting outputs)",
        "",
        *ingest_lines,
        ("python src/audit/final_certification.py --repo-root . "
         "--assert-final-unlock"),
        "",
        "## Attestation and isolation requirements",
        "",
        ("Attestation names its auditor, is written in its own words, "
         "and is byte-distinct across chairs; verdict carries the "
         "verbatim non-exposure declaration and affirms fresh_context, "
         "no_prior_experiment_context, other_outputs_unavailable."),
    ]) + "\n"
    for forbidden in FORBIDDEN_HANDOFF:
        if forbidden in doc:
            fail("handoff leaks forbidden content: " + forbidden)
    dest = os.path.join(repo_root, "NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md")
    with open(dest, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(doc)
    print("[P2:cyc:042] handoff written for %s" % ",".join(panel),
          flush=True)


def cmd_status(args):
    """Print cycle state summary."""
    # [P2-LOG-050] Step: report cycle status.
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    for record in state.get("cycles", []):
        print("[P2:cyc:052] %s rev=%s panel=%s status=%s" % (
            record.get("cycle_id"), record.get("revision"),
            ",".join(record.get("panel", [])),
            record.get("status")), flush=True)


def main(argv=None):
    """Entry point: dispatch cycle operations."""
    # [P2-LOG-060] Step: dispatch cycle mode.
    print("[P2:cyc:060] certification cycle invoked", flush=True)
    parser = argparse.ArgumentParser(description="Certification cycles.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--init-cycle", default="")
    parser.add_argument("--revision", default="")
    parser.add_argument("--panel", default="")
    parser.add_argument("--assess-cycle", default="")
    parser.add_argument("--decide-cycle", default="")
    parser.add_argument("--verdict", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--material-objections", default="")
    parser.add_argument("--handoff", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    if args.init_cycle:
        cmd_init_cycle(args)
    elif args.assess_cycle:
        cmd_assess_cycle(args)
    elif args.decide_cycle:
        cmd_decide_cycle(args)
    elif args.handoff:
        cmd_handoff(args)
    elif args.status:
        cmd_status(args)
    else:
        fail("no cycle operation given")
    # [P2-LOG-062] Step: cycle operation complete.
    print("[P2:cyc:062] cycle operation complete", flush=True)


if __name__ == "__main__":
    main()
