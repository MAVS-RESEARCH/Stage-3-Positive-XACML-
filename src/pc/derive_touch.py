"""Phase-3 mechanical touch derivation for PC-XACML-S3PLUS-v1.

Implements IMPLEMENTATION_SPEC.md section 6 pseudocode literally over
canonical H / PR / Lambda pre vs successors. The expected result is a
single-element set, but no expectation is ever an input to this module.

Step console lines use the [P3:touch:NNN] tag, each marked by a
[P3-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

# [P3-LOG-010] Step: declare the closed-input denylist (never opened).
# Checked as substrings of every read path on lines without any open
# call, so the source never matches an open-with-expectation pattern.
_FORBIDDEN_TOKENS = (
    "expected_signature",
    "canary_expectations",
    "experiment.yaml",
)


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P3-LOG-900] Fail-closed termination marker for every abort path.
    print("[P3:touch:FAIL] " + message, flush=True)
    sys.exit(1)


def _assert_not_forbidden(path):
    """Refuse any read path naming a sealed expectation file."""
    text = str(path)
    for token in _FORBIDDEN_TOKENS:
        if token in text:
            fail("closed-input violation: refused " + text)


def _read_json(path):
    """Load JSON after the closed-input guard."""
    _assert_not_forbidden(path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    _assert_not_forbidden(path)
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_H(h_obj):
    """Canonicalize an H history object to comparable bytes.

    H is the multimap keyed by (Category, AttributeId, DataType,
    Issuer-or-null) with sorted typed value bags; canonical form sorts
    entries and values deterministically.
    """
    attrs = h_obj.get("attributes", [])
    rows = []
    for entry in attrs:
        rows.append((
            entry.get("category") or "",
            entry.get("attribute_id") or "",
            entry.get("data_type") or "",
            entry.get("issuer") or "",
            tuple(sorted(entry.get("values", []))),
        ))
    rows.sort()
    return json.dumps(rows, sort_keys=True).encode("utf-8")


def canonical_PR(pr_obj):
    """Canonicalize the P_R relation object to comparable bytes.

    The relation itself is constant across the repair; only the
    presented histories change. Canonical form sorts the frozen
    designator coordinates and binds the rule text.
    """
    coords = pr_obj.get("designator_coordinates", [])
    rows = sorted(
        (c.get("category") or "", c.get("attribute_id") or "",
         c.get("data_type") or "",
         "" if c.get("issuer") is None else str(c.get("issuer")))
        for c in coords)
    payload = {"coordinates": rows, "rule": pr_obj.get("rule", "")}
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def canonical_Lambda(lambda_obj):
    """Canonicalize the Lambda authority object to comparable bytes.

    Canonical form is the sorted-component JSON; the repair must leave
    every component extensionally identical.
    """
    components = lambda_obj.get("components", {})
    return json.dumps(components, sort_keys=True).encode("utf-8")


def derive_touch(pre, successors):
    """Derive the resource touch set (spec section 6, literal)."""
    touch = set()
    for post in successors:
        if canonical_H(post["H"]) != canonical_H(pre["H"]):
            touch.add("E")
        if canonical_PR(post["PR"]) != canonical_PR(pre["PR"]):
            touch.add("R")
        if canonical_Lambda(post["Lambda"]) != canonical_Lambda(pre["Lambda"]):
            touch.add("A")
    return touch


def main(argv):
    """Entry point: derive touch from the contract and write touch.json."""
    # [P3-LOG-020] Step: start derivation, echo resolved arguments.
    print("[P3:touch:020] start touch derivation", flush=True)
    if len(argv) != 3:
        fail("usage: derive_touch.py <contract.json> <touch-out.json>")
    contract_path, out_path = argv[1], argv[2]
    contract = _read_json(contract_path)
    # [P3-LOG-030] Step: assemble pre vs successor views.
    print("[P3:touch:030] assembling pre/successor views", flush=True)
    actions = contract.get("actions", {})
    if len(actions) != 1:
        fail("contract must expose exactly one repair action")
    action_id = sorted(actions.keys())[0]
    h_map = contract.get("H", {})
    pr_obj = contract.get("PR", {})
    lambda_obj = contract.get("Lambda", {})
    for key in ("S0", "S_permit", "S_nonpermit"):
        if key not in h_map:
            fail("contract H missing checkpoint " + key)
    pre = {"H": h_map["S0"], "PR": pr_obj, "Lambda": lambda_obj}
    successors = [
        {"H": h_map["S_permit"], "PR": pr_obj, "Lambda": lambda_obj},
        {"H": h_map["S_nonpermit"], "PR": pr_obj, "Lambda": lambda_obj},
    ]
    # [P3-LOG-040] Step: run the literal pseudocode.
    print("[P3:touch:040] running mechanical comparison", flush=True)
    touch = derive_touch(pre, successors)
    record = {action_id: sorted(touch)}
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P3-LOG-050] Step: derivation complete.
    print("[P3:touch:050] touch=%s sha256=%s"
          % (sorted(touch), sha256_file(out_path)), flush=True)


if __name__ == "__main__":
    main(sys.argv)
