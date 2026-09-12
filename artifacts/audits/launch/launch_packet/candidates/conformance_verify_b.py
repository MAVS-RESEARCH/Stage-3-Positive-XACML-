"""Run-conformance verifier B (Amendment 007).

Independent reimplementation of verifier A over the same evidence
format: own loaders, own predicate structure, own writers. Reads only
hashes/counts/order/names — never outcome content. Agreement between A
and B is required; disagreement is itself terminal.

Usage: conformance_verify_b.py <registry.json> <evidence-dir> <out.json>

Step console lines use the [P2:cvb:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")
BANNED_SUBSTRINGS = ("Permit", "NotApplicable", "Decision", "touch",
                     "classification", "expected_")


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:cvb:FAIL] " + message, flush=True)
    sys.exit(code)


def read_json(path):
    """Read JSON or return a missing marker."""
    try:
        with open(path, encoding="utf-8") as handle:
            return (True, json.load(handle))
    except (OSError, ValueError):
        return (False, None)


def is_text(value):
    """Check for a non-empty string."""
    return isinstance(value, str) and len(value) > 0


def judge_lambda_post(evidence):
    """Judge post equality of composite hashes."""
    # [P2-LOG-010] Step: judge Lambda post equality.
    if type(evidence) is not dict:
        return "UNVERIFIABLE"
    pre_hash = evidence.get("pre_hash")
    post_hash = evidence.get("post_hash")
    if not is_text(pre_hash) or not is_text(post_hash):
        return "UNVERIFIABLE"
    if not HEX64.match(pre_hash) or not HEX64.match(post_hash):
        return "UNVERIFIABLE"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    if pre_hash == post_hash:
        return "SATISFIED"
    return "FAILED"


def judge_string_maps(evidence):
    """Judge equality of two non-empty string maps."""
    # [P2-LOG-012] Step: judge manifest-vs-live maps.
    if type(evidence) is not dict:
        return "UNVERIFIABLE"
    expected = evidence.get("expected")
    live = evidence.get("live")
    if type(expected) is not dict or type(live) is not dict:
        return "UNVERIFIABLE"
    if len(expected) == 0:
        return "UNVERIFIABLE"
    expected_keys = sorted(expected.keys())
    live_keys = sorted(live.keys())
    if expected_keys != live_keys:
        return "FAILED"
    for key in expected_keys:
        if not is_text(expected[key]) or not is_text(live[key]):
            return "UNVERIFIABLE"
        if not HEX64.match(expected[key]) or not HEX64.match(live[key]):
            return "UNVERIFIABLE"
        if expected[key] != live[key]:
            return "FAILED"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    return "SATISFIED"


def judge_world_pair(evidence):
    """Judge cross-world map identity."""
    # [P2-LOG-014] Step: judge world-pair consistency.
    if type(evidence) is not dict:
        return "UNVERIFIABLE"
    worlds = evidence.get("worlds")
    if type(worlds) is not dict:
        return "UNVERIFIABLE"
    permit = worlds.get("x_permit")
    nonpermit = worlds.get("x_nonpermit")
    if type(permit) is not dict or type(nonpermit) is not dict:
        return "UNVERIFIABLE"
    if len(permit) == 0:
        return "UNVERIFIABLE"
    for mapping in (permit, nonpermit):
        for value in mapping.values():
            if not is_text(value) or not HEX64.match(value):
                return "UNVERIFIABLE"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    permit_items = sorted(permit.items())
    nonpermit_items = sorted(nonpermit.items())
    if permit_items == nonpermit_items:
        return "SATISFIED"
    return "FAILED"


def judge_sequence(evidence):
    """Judge exact frozen event order."""
    # [P2-LOG-016] Step: judge event sequence.
    if type(evidence) is not dict:
        return "UNVERIFIABLE"
    events = evidence.get("events")
    frozen = ["build_done", "stage_done", "verify_done", "invoke_start",
              "invoke_end", "response_sealed"]
    if type(events) is not list:
        return "UNVERIFIABLE"
    for item in events:
        if type(item) is not str:
            return "UNVERIFIABLE"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    if events == frozen:
        return "SATISFIED"
    return "FAILED"


def verdict_for(obligation, evidence):
    """Dispatch one obligation to its predicate."""
    table = {"RC-LAMBDA-POST": judge_lambda_post,
             "RC-CLASSPATH-ACTUAL": judge_string_maps,
             "RC-DEPLOYMENT-ACTUAL": judge_string_maps,
             "RC-REQUEST-ACTUAL": judge_string_maps,
             "RC-ATOM-ORDER": judge_sequence,
             "RC-DEPS-CONSISTENT": judge_world_pair}
    predicate = table.get(obligation)
    if predicate is None:
        return "UNVERIFIABLE"
    return predicate(evidence)


def main(argv):
    """Entry point: verify one evidence directory."""
    # [P2-LOG-020] Step: run verifier B.
    print("[P2:cvb:020] verifier B invoked", flush=True)
    if len(argv) != 4:
        fail("usage: conformance_verify_b.py <registry> <evidence> <out>")
    present, registry = read_json(argv[1])
    if not present:
        fail("registry unreadable")
    verdicts = {}
    obligations = registry.get("obligations", [])
    if type(obligations) is not list:
        fail("registry malformed")
    for entry in obligations:
        obligation = entry.get("obligation_id", "?") \
            if type(entry) is dict else "?"
        present, evidence = read_json(
            os.path.join(argv[2], obligation + ".json"))
        if not present:
            verdicts[obligation] = "UNVERIFIABLE"
        else:
            verdicts[obligation] = verdict_for(obligation, evidence)
    overall = "SATISFIED"
    for obligation in sorted(verdicts):
        if verdicts[obligation] == "FAILED":
            overall = "FAILED"
            break
    if overall == "SATISFIED":
        for obligation in sorted(verdicts):
            if verdicts[obligation] == "UNVERIFIABLE":
                overall = "UNVERIFIABLE"
                break
    with open(argv[3], "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps({"verifier": "B", "verdicts": verdicts,
                                 "overall": overall}, indent=2,
                                sort_keys=True))
        handle.write("\n")
    print("[P2:cvb:022] verifier B overall=%s" % overall, flush=True)


if __name__ == "__main__":
    main(sys.argv)
