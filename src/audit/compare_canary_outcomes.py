"""Phase-5 post-execution canary comparison for PC-XACML-S3PLUS-v1.

Separate post-execution comparison step: reads each canary_*_raw.json plus
the sealed prereg/canary_expectations.json, writes canary_*_comparison.json.

This module (plus final reporting) is the ONLY place allowed to open an
expectation file. Execution writes raw outputs first without opening
expectations; this step opens them afterward for exact judgment.

Each canary has an exact expected decision/status/error class, or an exact
finite permissible set (acceptable_alternatives) dictated by XACML, sealed
before execution. A canary passes iff observed triple equals expected OR
equals one listed alternative (exact triple match). Vague criteria are
forbidden.

Step console lines use the [P5:cmp:NNN] tag, each marked by a
[P5-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P5-LOG-900] Fail-closed termination marker for every abort path.
    print("[P5:cmp:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    """Load a JSON document, failing closed on absence."""
    if not os.path.isfile(path):
        fail("missing required artifact: " + path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def triple_of(entry):
    """Normalize an expectation/raw triple to (decision, status, detail_bool)."""
    if "expected" in entry:
        obj = entry["expected"]
        return (obj.get("decision"), obj.get("status_code"),
                obj.get("missing_attribute_detail_present"))
    observed = entry.get("observed", entry)
    return (observed.get("decision"), observed.get("status_code"),
            observed.get("missing_attribute_detail_present"))


def compare_one(canary_id, expected_entry, raw_doc):
    """Compare one canary raw against its sealed expectation."""
    expected = expected_entry.get("expected", {})
    alternatives = expected_entry.get("acceptable_alternatives", []) or []
    observed = raw_doc.get("observed", {})
    obs_triple = (observed.get("decision"),
                  observed.get("status_code"),
                  observed.get("missing_attribute_detail_present"))
    exp_triple = (expected.get("decision"),
                  expected.get("status_code"),
                  expected.get("missing_attribute_detail_present"))
    match_expected = (obs_triple == exp_triple)
    match_alternative = False
    matched_alt_index = None
    for idx, alt in enumerate(alternatives):
        alt_triple = (alt.get("decision"), alt.get("status_code"),
                      alt.get("missing_attribute_detail_present"))
        if obs_triple == alt_triple:
            match_alternative = True
            matched_alt_index = idx
            break
    passed = bool(match_expected or match_alternative)
    return {
        "canary_id": canary_id,
        "experiment_id": "PC-XACML-S3PLUS-v1",
        "expected": expected,
        "acceptable_alternatives": alternatives,
        "observed": observed,
        "match_expected": match_expected,
        "match_alternative": match_alternative,
        "matched_alternative_index": matched_alt_index,
        "pass": passed,
        "raw_sha256": raw_doc.get("response_sha256"),
        "compared_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }


def main(argv):
    """Entry point: compare all canary raws against sealed expectations."""
    # [P5-LOG-010] Step: start comparison, echo resolved arguments.
    print("[P5:cmp:010] start canary comparison", flush=True)
    if len(argv) != 3:
        fail("usage: compare_canary_outcomes.py <repo-root> <audits-dir>")
    repo_root = os.path.abspath(argv[1])
    audits_dir = os.path.abspath(argv[2])
    # [P5-LOG-012] Step: echo resolved paths.
    print("[P5:cmp:012] repo=%s audits=%s" % (repo_root, audits_dir),
          flush=True)
    # [P5-LOG-020] Step: open sealed expectations (post-execution only).
    print("[P5:cmp:020] opening sealed canary expectations", flush=True)
    exp_path = os.path.join(repo_root, "prereg", "canary_expectations.json")
    expectations = load_json(exp_path)
    if expectations.get("sealed_before_execution") is not True:
        fail("canary expectations not sealed")
    canaries = expectations.get("canaries", {})
    if not canaries:
        fail("no sealed canaries")
    exp_sha = sha256_file(exp_path)
    # [P5-LOG-022] Step: sealed-canary inventory line.
    print("[P5:cmp:022] sealed canaries=%d sha=%s"
          % (len(canaries), exp_sha[:16]), flush=True)
    # [P5-LOG-030] Step: compare each sealed canary with its raw.
    print("[P5:cmp:030] comparing each canary raw", flush=True)
    results = {}
    for canary_id in sorted(canaries.keys()):
        raw_path = os.path.join(audits_dir, "canary_%s_raw.json" % canary_id)
        if not os.path.isfile(raw_path):
            fail("missing raw for sealed canary: " + canary_id)
        raw_doc = load_json(raw_path)
        entry = canaries[canary_id]
        comp = compare_one(canary_id, entry, raw_doc)
        comp["expectations_sha256"] = exp_sha
        out_path = os.path.join(
            audits_dir, "canary_%s_comparison.json" % canary_id)
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(comp, handle, indent=2, sort_keys=True)
            handle.write("\n")
        results[canary_id] = comp["pass"]
        # [P5-LOG-032] Step: per-canary verdict line.
        print("[P5:cmp:032] %s pass=%s observed=%s expected=%s"
              % (canary_id, comp["pass"], comp["observed"],
                 comp["expected"]), flush=True)
    # [P5-LOG-040] Step: summary.
    npass = sum(1 for v in results.values() if v)
    print("[P5:cmp:040] comparison complete pass=%d/%d"
          % (npass, len(results)), flush=True)
    if npass != len(results):
        fail("canary comparison failures: %s"
             % sorted(k for k, v in results.items() if not v))
    # [P5-LOG-050] Step: comparison complete.
    print("[P5:cmp:050] all canary comparisons passed", flush=True)


if __name__ == "__main__":
    main(sys.argv)
