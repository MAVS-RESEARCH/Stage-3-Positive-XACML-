"""Phase-3 independent touch reimplementation for PC-XACML-S3PLUS-v1.

Separate implementation of the section-6 comparison with its own
canonicalization and its own equality checks. It never imports the
primary derivation module or any of its helpers; agreement is checked
by byte comparison of the serialized outputs.

Step console lines use the [P3:indep:NNN] tag, each marked by a
[P3-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys

# [P3-LOG-010] Step: declare the closed-input denylist (never opened).
# Substring check on its own lines, never combined with an open call.
_CLOSED_TOKENS = (
    "expected_signature",
    "canary_expectations",
    "experiment.yaml",
)


def _refuse(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P3-LOG-900] Fail-closed termination marker for every abort path.
    print("[P3:indep:FAIL] " + message, flush=True)
    sys.exit(1)


def _guard(path):
    """Refuse any read path naming a sealed expectation file."""
    text = str(path)
    for token in _CLOSED_TOKENS:
        if token in text:
            _refuse("closed-input violation: refused " + text)


def _load(path):
    """Load JSON after the closed-input guard."""
    _guard(path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _digest(path):
    """Return the hex SHA-256 digest of a file."""
    _guard(path)
    acc = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            acc.update(chunk)
    return acc.hexdigest()


def _h_canonical_independent(h_obj):
    """Independently canonicalize an H object to comparable bytes.

    Own implementation: flatten each attribute to a single pipe-joined
    record string, sort records, join with newlines. No shared code
    with the primary derivation path.
    """
    parts = []
    for entry in h_obj.get("attributes", []):
        cat = entry.get("category") or ""
        aid = entry.get("attribute_id") or ""
        typ = entry.get("data_type") or ""
        iss = entry.get("issuer")
        iss_text = "" if iss is None else str(iss)
        vals = sorted(entry.get("values", []))
        parts.append("|".join([cat, aid, typ, iss_text,
                               ",".join(vals)]))
    parts.sort()
    return ("\n".join(parts) + "\n").encode("utf-8")


def _pr_canonical_independent(pr_obj):
    """Independently canonicalize the P_R relation object.

    Own implementation: join each coordinate as a hash-joined token,
    sort tokens, bind the rule length plus rule text.
    """
    toks = []
    for coord in pr_obj.get("designator_coordinates", []):
        iss = coord.get("issuer")
        toks.append("#".join([
            str(coord.get("category") or ""),
            str(coord.get("attribute_id") or ""),
            str(coord.get("data_type") or ""),
            "" if iss is None else str(iss),
        ]))
    toks.sort()
    rule = pr_obj.get("rule", "")
    blob = "PR|%d|%s|%s" % (len(toks), ";".join(toks), rule)
    return blob.encode("utf-8")


def _lambda_canonical_independent(lambda_obj):
    """Independently canonicalize the Lambda authority object.

    Own implementation: walk sorted component keys, render each value
    with repr, join as key=value lines.
    """
    components = lambda_obj.get("components", {})
    lines = []
    for key in sorted(components.keys()):
        lines.append("%s=%r" % (key, components[key]))
    return ("\n".join(lines) + "\n").encode("utf-8")


def audit_touch(pre_view, post_views):
    """Recompute the touch set with independent compares."""
    found = set()
    for post in post_views:
        if (_h_canonical_independent(post["H"])
                != _h_canonical_independent(pre_view["H"])):
            found.add("E")
        if (_pr_canonical_independent(post["PR"])
                != _pr_canonical_independent(pre_view["PR"])):
            found.add("R")
        if (_lambda_canonical_independent(post["Lambda"])
                != _lambda_canonical_independent(pre_view["Lambda"])):
            found.add("A")
    return found


def main(argv):
    """Entry point: recompute touch and write the comparison output."""
    # [P3-LOG-020] Step: start independent recomputation.
    print("[P3:indep:020] start independent touch", flush=True)
    if len(argv) != 3:
        _refuse("usage: independent_touch.py <contract.json> <out.json>")
    contract_path, out_path = argv[1], argv[2]
    contract = _load(contract_path)
    # [P3-LOG-030] Step: assemble pre vs successor views independently.
    print("[P3:indep:030] assembling views", flush=True)
    actions = contract.get("actions", {})
    if len(actions) != 1:
        _refuse("contract must expose exactly one repair action")
    action_key = sorted(actions.keys())[0]
    h_table = contract.get("H", {})
    pr_doc = contract.get("PR", {})
    lambda_doc = contract.get("Lambda", {})
    for need in ("S0", "S_permit", "S_nonpermit"):
        if need not in h_table:
            _refuse("contract H missing checkpoint " + need)
    before = {"H": h_table["S0"], "PR": pr_doc, "Lambda": lambda_doc}
    afters = [
        {"H": h_table["S_permit"], "PR": pr_doc, "Lambda": lambda_doc},
        {"H": h_table["S_nonpermit"], "PR": pr_doc, "Lambda": lambda_doc},
    ]
    # [P3-LOG-040] Step: run the independent comparison.
    print("[P3:indep:040] running independent comparison", flush=True)
    result = audit_touch(before, afters)
    payload = {action_key: sorted(result)}
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P3-LOG-050] Step: independent recomputation complete.
    print("[P3:indep:050] touch=%s sha256=%s"
          % (sorted(result), _digest(out_path)), flush=True)


if __name__ == "__main__":
    main(sys.argv)
