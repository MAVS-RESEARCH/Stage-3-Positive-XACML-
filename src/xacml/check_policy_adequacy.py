"""Phase-2 policy-projection adequacy certificate for PC-XACML-S3+.

Proves the frozen designator projection captures every request-sensitive
input channel of this fixture: rejects unsupported AttributeSelectors,
XPath usage, policy references, custom datatypes, and hidden
provider-sensitive channels (verified against the frozen pdp.xml, which
must expose no attribute-provider or preprocessor configuration).
Separately records why equality of designator results instantiates PC's
certificate relation, with exact N1 locators. Output:
derived/policy_adequacy_certificate.json with verdict PASS/FAIL.

Step console lines use the [P2:adeq:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from lxml import etree

STANDARD_DATATYPES = {
    "http://www.w3.org/2001/XMLSchema#string",
    "http://www.w3.org/2001/XMLSchema#anyURI",
}
# N1 locators in the frozen XACML HTML (stripped-text lines + sections).
N1_RETRIEVAL = ("Sec. 7.3.5 Attribute Retrieval (frozen stripped-text "
                "lines 8405-8424): the PDP SHALL request attribute values "
                "in the request context from the context handler; "
                "Category/AttributeId/DataType/Issuer matching; missing "
                "attribute with MustBePresent=false yields an empty bag, "
                "with MustBePresent=true yields Indeterminate.")
N1_DESIGNATOR = ("Sec. 5.29 Element AttributeDesignator (frozen "
                 "stripped-text lines 406-407); MustBePresent governs "
                 "empty-bag vs Indeterminate (frozen stripped-text lines "
                 "6292-6294, see Sec. 7.3.5).")
N1_MATCH = ("Sec. 7.6 Match evaluation (frozen stripped-text lines "
            "8577-8594): MatchId function compares the literal "
            "AttributeValue with the designator-selected context bag; "
            "designator DataType SHALL match the function argument type.")


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:adeq:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def main(argv):
    """Entry point: certify projection adequacy."""
    # [P2-LOG-010] Step: start adequacy check, echo arguments.
    print("[P2:adeq:010] start adequacy certification", flush=True)
    if len(argv) != 5:
        fail("usage: check_policy_adequacy.py <projection.json> "
             "<pdp.xml> <manifest.json> <out>")
    projection_path, pdp_path, manifest_path, out_path = (
        argv[1], argv[2], argv[3], argv[4])
    with open(projection_path, "r", encoding="utf-8") as handle:
        projection = json.load(handle)
    inventory = projection["construct_inventory"]
    findings = []

    # [P2-LOG-020] Step: assert no selector/XPath/reference channels.
    print("[P2:adeq:020] checking selector/XPath/reference channels",
          flush=True)
    if inventory["attribute_selectors"] != 0:
        findings.append("AttributeSelector elements present")
    if inventory["xpath_expressions"] != 0:
        findings.append("XPath expressions present")
    if inventory["policy_id_references"] != 0:
        findings.append("Policy(Set)IdReference elements present")
    print("[P2:adeq:022] selector/xpath/reference findings=%d"
          % len(findings), flush=True)

    # [P2-LOG-030] Step: assert only standard datatypes are used.
    print("[P2:adeq:030] checking datatype inventory", flush=True)
    exotic = [t for t in inventory["data_types"]
              if t not in STANDARD_DATATYPES]
    if exotic:
        findings.append("non-standard datatypes: %s" % exotic)
    print("[P2:adeq:032] datatypes=%s" % sorted(inventory["data_types"]),
          flush=True)

    # [P2-LOG-040] Step: assert no provider/preprocessor channels in pdp.
    print("[P2:adeq:040] checking pdp.xml provider channels", flush=True)
    try:
        pdp_root = etree.parse(pdp_path).getroot()
    except etree.XMLSyntaxError as exc:
        fail("pdp.xml syntax error: %s" % exc)
    children = sorted(set(localname(e) for e in pdp_root))
    provider_channels = [c for c in children if c != "policyProvider"]
    if provider_channels:
        findings.append("non-policy provider channels in pdp.xml: %s"
                        % provider_channels)
    print("[P2:adeq:042] pdp children=%s" % children, flush=True)

    verdict = "PASS" if not findings else "FAIL"
    # [P2-LOG-050] Step: write the adequacy certificate.
    print("[P2:adeq:050] verdict=%s" % verdict, flush=True)
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    sealed_pdp_sha = manifest["authzforce"]["fixture_files"]["pdp.xml"][
        "sha256"]
    with open(pdp_path, "rb") as handle:
        live_pdp_sha = hashlib.sha256(handle.read()).hexdigest()
    if live_pdp_sha != sealed_pdp_sha:
        fail("pdp.xml bytes differ from sealed manifest")
    certificate = {
        "certificate_id": "PC-XACML-S3PLUS-v1-adequacy",
        "verdict": verdict,
        "findings": findings,
        "channel_inventory": {
            "attribute_selectors": inventory["attribute_selectors"],
            "xpath_expressions": inventory["xpath_expressions"],
            "policy_id_references": inventory["policy_id_references"],
            "data_types": sorted(inventory["data_types"]),
            "pdp_child_elements": children,
        },
        "pr_instantiation_argument": (
            "Two admitted histories are P_R-equivalent iff all frozen "
            "designator results are extensionally equal under standard "
            "matching semantics. This instantiates PC's certificate "
            "relation (rather than merely asserting it) because: (a) the "
            "frozen policy queries authorization inputs ONLY through the "
            "inventoried designators (no selectors, XPath, references, "
            "or provider channels per the checks above); (b) the XACML "
            "standard defines designator retrieval/matching as the "
            "exclusive named-attribute access path (" + N1_RETRIEVAL +
            " " + N1_DESIGNATOR + "); (c) Target Match evaluation "
            "consumes exactly these bags (" + N1_MATCH + "). Hence the "
            "designator-result vector is the complete authorization-"
            "visible projection of this fixture."),
        "n1_locators": [N1_RETRIEVAL, N1_DESIGNATOR, N1_MATCH],
        "projection_sha256": projection["policy_sha256"],
        "sealed_pdp_sha256": sealed_pdp_sha,
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-060] Step: adequacy certification complete.
    print("[P2:adeq:060] adequacy certification complete", flush=True)
    if verdict != "PASS":
        fail("adequacy FAIL: %s" % findings)


if __name__ == "__main__":
    main(sys.argv)
