"""Run-conformance verifier A (Amendment 007).

Evaluates frozen registry predicates over a conformance-evidence
directory. Reads only hashes/counts/order/names — never outcome content.
Per-obligation: SATISFIED / FAILED / UNVERIFIABLE. Independent
implementation of verifier B (no shared helpers).

Usage: conformance_verify_a.py <registry.json> <evidence-dir> <out.json>

Step console lines use the [P2:cva:NNN] tag, each marked by a
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
    print("[P2:cva:FAIL] " + message, flush=True)
    sys.exit(code)


def load_json(path):
    """Load JSON or return None."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def check_lambda_post(evidence):
    """SATISFIED iff pre and post composite hashes are equal non-empty."""
    # [P2-LOG-010] Step: check Lambda post equality.
    if not isinstance(evidence, dict):
        return "UNVERIFIABLE"
    pre = evidence.get("pre_hash")
    post = evidence.get("post_hash")
    if not isinstance(pre, str) or not isinstance(post, str):
        return "UNVERIFIABLE"
    if not HEX64.match(pre) or not HEX64.match(post):
        return "UNVERIFIABLE"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    return "SATISFIED" if pre == post else "FAILED"


def check_map_equal(evidence):
    """SATISFIED iff expected and live string maps are equal non-empty."""
    # [P2-LOG-012] Step: check manifest-vs-live map equality.
    if not isinstance(evidence, dict):
        return "UNVERIFIABLE"
    expected = evidence.get("expected")
    live = evidence.get("live")
    if not isinstance(expected, dict) or not isinstance(live, dict):
        return "UNVERIFIABLE"
    if not expected:
        return "UNVERIFIABLE"
    if set(expected) != set(live):
        return "FAILED"
    for key in expected:
        if not isinstance(expected[key], str) \
                or not isinstance(live[key], str):
            return "UNVERIFIABLE"
        if not HEX64.match(expected[key]) or not HEX64.match(live[key]):
            return "UNVERIFIABLE"
        if expected[key] != live[key]:
            return "FAILED"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    return "SATISFIED"


def check_worlds_equal(evidence):
    """SATISFIED iff both worlds carry identical maps."""
    # [P2-LOG-014] Step: check cross-world consistency.
    if not isinstance(evidence, dict):
        return "UNVERIFIABLE"
    worlds = evidence.get("worlds")
    if not isinstance(worlds, dict) or sorted(worlds) != [
            "x_nonpermit", "x_permit"]:
        return "UNVERIFIABLE"
    left = worlds["x_permit"]
    right = worlds["x_nonpermit"]
    if not isinstance(left, dict) or not isinstance(right, dict):
        return "UNVERIFIABLE"
    if not left:
        return "UNVERIFIABLE"
    for mapping in (left, right):
        for value in mapping.values():
            if not isinstance(value, str) or not HEX64.match(value):
                return "UNVERIFIABLE"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    return "SATISFIED" if left == right else "FAILED"


def check_order(evidence):
    """SATISFIED iff events follow the frozen order exactly."""
    # [P2-LOG-016] Step: check event ordering.
    if not isinstance(evidence, dict):
        return "UNVERIFIABLE"
    events = evidence.get("events")
    expected = ["build_done", "stage_done", "verify_done", "invoke_start",
                "invoke_end", "response_sealed"]
    if not isinstance(events, list) or not all(
            isinstance(item, str) for item in events):
        return "UNVERIFIABLE"
    if any(ban in json.dumps(evidence) for ban in BANNED_SUBSTRINGS):
        return "UNVERIFIABLE"
    return "SATISFIED" if events == expected else "FAILED"


CHECKS = {
    "RC-LAMBDA-POST": check_lambda_post,
    "RC-CLASSPATH-ACTUAL": check_map_equal,
    "RC-DEPLOYMENT-ACTUAL": check_map_equal,
    "RC-REQUEST-ACTUAL": check_map_equal,
    "RC-ATOM-ORDER": check_order,
    "RC-DEPS-CONSISTENT": check_worlds_equal,
}


def main(argv):
    """Entry point: verify one evidence directory."""
    # [P2-LOG-020] Step: run verifier A.
    print("[P2:cva:020] verifier A invoked", flush=True)
    if len(argv) != 4:
        fail("usage: conformance_verify_a.py <registry> <evidence> <out>")
    registry = load_json(argv[1])
    if registry is None:
        fail("registry unreadable")
    verdicts = {}
    for entry in registry.get("obligations", []):
        obligation = entry.get("obligation_id", "?")
        check = CHECKS.get(obligation)
        if check is None:
            verdicts[obligation] = "UNVERIFIABLE"
            continue
        evidence = load_json(os.path.join(
            argv[2], obligation + ".json"))
        if evidence is None:
            verdicts[obligation] = "UNVERIFIABLE"
        else:
            verdicts[obligation] = check(evidence)
    overall = "SATISFIED"
    for verdict in verdicts.values():
        if verdict == "FAILED":
            overall = "FAILED"
            break
        if verdict == "UNVERIFIABLE":
            overall = "UNVERIFIABLE"
    with open(argv[3], "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"verifier": "A", "verdicts": verdicts,
                   "overall": overall}, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:cva:022] verifier A overall=%s" % overall, flush=True)


if __name__ == "__main__":
    main(sys.argv)
