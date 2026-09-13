"""Phase-2 frozen-policy parser for PC-XACML-S3+.

Walks the frozen policy.xml and extracts every reachable
AttributeDesignator with full coordinates (RuleId/path, Category,
AttributeId, DataType, Issuer, MustBePresent, enclosing Match function),
plus a complete construct inventory (selectors, XPath usage, functions,
datatypes, combining algorithm, references, obligations). No handwritten
allowlist: every designator present in the file is recorded. Output:
derived/policy_projection.json.

Step console lines use the [P2:proj:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from lxml import etree

CANARY_TRIPLE = (
    "urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute",
    "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
    "http://www.w3.org/2001/XMLSchema#string",
)


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:proj:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def element_path(element):
    """Return the ancestor local-name path of an element."""
    names = []
    node = element
    while node is not None:
        names.append(localname(node))
        node = node.getparent()
    return "/" + "/".join(reversed(names))


def enclosing_match_function(element):
    """Return the MatchId of the enclosing Match element, if any."""
    node = element.getparent()
    while node is not None:
        if localname(node) == "Match":
            return node.get("MatchId")
        node = node.getparent()
    return None


def enclosing_rule(element):
    """Return the RuleId of the enclosing Rule element, if any."""
    node = element.getparent()
    while node is not None:
        if localname(node) == "Rule":
            return node.get("RuleId")
        node = node.getparent()
    return None


def main(argv):
    """Entry point: parse the frozen policy into a projection record."""
    # [P2-LOG-010] Step: start projection, echo resolved arguments.
    print("[P2:proj:010] start policy projection", flush=True)
    if len(argv) != 4:
        fail("usage: parse_policy.py <policy.xml> <manifest.json> <out>")
    policy_path, manifest_path, out_path = argv[1], argv[2], argv[3]
    print("[P2:proj:012] policy=%s" % os.path.abspath(policy_path),
          flush=True)

    # [P2-LOG-020] Step: parse policy and extract designators.
    print("[P2:proj:020] extracting AttributeDesignators", flush=True)
    try:
        root = etree.parse(policy_path).getroot()
    except etree.XMLSyntaxError as exc:
        fail("policy XML syntax error: %s" % exc)
    designators = []
    for node in root.iter():
        if localname(node) != "AttributeDesignator":
            continue
        designators.append({
            "path": element_path(node),
            "rule_id": enclosing_rule(node),
            "category": node.get("Category"),
            "attribute_id": node.get("AttributeId"),
            "data_type": node.get("DataType"),
            "issuer": node.get("Issuer"),
            "must_be_present": node.get("MustBePresent"),
            "match_function": enclosing_match_function(node),
        })
    print("[P2:proj:022] designators=%d" % len(designators), flush=True)

    # [P2-LOG-030] Step: inventory all request-sensitive constructs.
    print("[P2:proj:030] inventorying policy constructs", flush=True)
    inventory = {
        "attribute_selectors": sum(
            1 for e in root.iter() if localname(e) == "AttributeSelector"),
        "xpath_expressions": sum(
            1 for e in root.iter()
            if (e.get("XPathVersion") is not None
                or localname(e) == "XPath")),
        "match_functions": sorted(set(
            e.get("MatchId") for e in root.iter()
            if localname(e) == "Match" and e.get("MatchId"))),
        "data_types": sorted(set(
            t for e in root.iter()
            for t in (e.get("DataType"),)
            if t)),
        "rule_combining": root.get("RuleCombiningAlgId"),
        "policy_id_references": sum(
            1 for e in root.iter()
            if localname(e) in ("PolicyIdReference",
                                "PolicySetIdReference")),
        "obligations_advice": sum(
            1 for e in root.iter()
            if localname(e) in ("Obligations", "AssociatedAdvice",
                                "ObligationExpressions",
                                "AdviceExpressions")),
    }
    print("[P2:proj:032] selectors=%d xpath=%d references=%d" % (
        inventory["attribute_selectors"], inventory["xpath_expressions"],
        inventory["policy_id_references"]), flush=True)

    # [P2-LOG-040] Step: canary assert on the missing-attribute designator.
    print("[P2:proj:040] checking missing-attribute canary", flush=True)
    canary = [d for d in designators
              if (d["attribute_id"], d["category"], d["data_type"])
              == CANARY_TRIPLE and d["must_be_present"] == "true"]
    if len(canary) != 1:
        fail("canary designator count=%d, want exactly 1" % len(canary))
    print("[P2:proj:042] canary designator confirmed", flush=True)

    with open(policy_path, "rb") as handle:
        policy_sha = hashlib.sha256(handle.read()).hexdigest()
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    record = {
        "projection_id": "PC-XACML-S3PLUS-v1-projection",
        "policy_sha256": policy_sha,
        "manifest_policy_sha256": manifest["authzforce"][
            "fixture_files"]["policies/policy.xml"]["sha256"],
        "designators": designators,
        "construct_inventory": inventory,
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    if record["policy_sha256"] != record["manifest_policy_sha256"]:
        fail("policy bytes differ from sealed manifest")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-050] Step: projection complete.
    print("[P2:proj:050] projection complete out=%s"
          % os.path.abspath(out_path), flush=True)


if __name__ == "__main__":
    main(sys.argv)
