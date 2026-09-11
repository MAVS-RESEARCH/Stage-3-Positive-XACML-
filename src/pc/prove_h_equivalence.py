"""Phase-2 H-equivalence proof (route b) for PC-XACML-S3+.

Proves extensional equality between canonical request XML and the PDP
resolved evaluation context for every experiment-relevant attribute:
global conditions (no PIP, no selectors, default preprocessing,
request-only attributes) plus one row per attribute coordinate with
request-side evidence and N1 locators. Requires route (a) unavailable
(see route_a_probe.json); if any condition fails the verdict is
AMBIGUOUS (a legitimate scientific output routed by the checker, not a
crash). Output: derived/h_equivalence_proof.json.

Step console lines use the [P2:heq:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from lxml import etree

N1_735 = ("Sec. 7.3.5 Attribute Retrieval (frozen stripped-text lines "
          "8405-8424): the PDP SHALL request attribute values in the "
          "request context from the context handler; missing attribute "
          "with MustBePresent=false yields an empty bag, with "
          "MustBePresent=true yields Indeterminate.")
N1_DATAFLOW = ("Data-flow model (frozen stripped-text lines 1755-1784): "
               "the context handler constructs the XACML request context, "
               "optionally adds attributes, and sends it to the PDP; the "
               "PDP requests additional attributes from the handler only "
               "via PIP, of which this fixture configures none.")
N1_DESIGNATOR = ("Sec. 5.29 AttributeDesignator (frozen stripped-text "
                 "lines 406-407); MustBePresent semantics (frozen "
                 "stripped-text lines 6292-6294).")
RELEVANT_COORDINATES = [
    ("urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
     "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
     "http://www.w3.org/2001/XMLSchema#string"),
    ("urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
     "urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute",
     "http://www.w3.org/2001/XMLSchema#string"),
    ("urn:oasis:names:tc:xacml:3.0:attribute-category:resource",
     "urn:oasis:names:tc:xacml:1.0:resource:resource-id",
     "http://www.w3.org/2001/XMLSchema#anyURI"),
    ("urn:oasis:names:tc:xacml:3.0:attribute-category:action",
     "urn:oasis:names:tc:xacml:1.0:action:action-id",
     "http://www.w3.org/2001/XMLSchema#string"),
]


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:heq:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_bags(path):
    """Map (category, id, datatype, issuer) to sorted value lists.

    Effective datatype follows XACML 3.0: Attribute/@DataType when
    present, else the (single, asserted uniform) AttributeValue datatype.
    """
    root = etree.parse(path).getroot()
    bags = {}
    for container in root.iter():
        if localname(container) != "Attributes":
            continue
        category = container.get("Category")
        for attribute in container:
            if localname(attribute) != "Attribute":
                continue
            values = sorted(
                (child.text or "") for child in attribute
                if localname(child) == "AttributeValue")
            child_types = set(
                child.get("DataType") for child in attribute
                if localname(child) == "AttributeValue")
            declared = attribute.get("DataType")
            if declared is not None:
                effective = declared
            elif len(child_types) == 1:
                effective = child_types.pop()
            else:
                fail("ambiguous effective datatype in %s attribute %s"
                     % (path, attribute.get("AttributeId")))
            key = (category, attribute.get("AttributeId"), effective,
                   attribute.get("Issuer"))
            bags.setdefault(key, []).extend(values)
    return {key: sorted(values) for key, values in bags.items()}


def main(argv):
    """Entry point: prove request/context extensional equality."""
    # [P2-LOG-010] Step: start proof, echo resolved arguments.
    print("[P2:heq:010] start H-equivalence proof", flush=True)
    if len(argv) != 9:
        fail("usage: prove_h_equivalence.py <request.xml> <permit.xml> "
             "<nonpermit.xml> <projection.json> <adequacy.json> "
             "<route_a.json> <pdp.xml> <out>")
    (request_path, permit_path, nonpermit_path, projection_path,
     adequacy_path, route_a_path, pdp_path, out_path) = argv[1:9]
    for path in (request_path, permit_path, nonpermit_path,
                 projection_path, adequacy_path, route_a_path, pdp_path):
        if not os.path.isfile(path):
            fail("missing input: " + path)

    with open(route_a_path, "r", encoding="utf-8") as handle:
        route_a = json.load(handle)
    with open(adequacy_path, "r", encoding="utf-8") as handle:
        adequacy = json.load(handle)
    with open(projection_path, "r", encoding="utf-8") as handle:
        projection = json.load(handle)

    conditions = []
    # [P2-LOG-020] Step: verify route (a) is unavailable.
    print("[P2:heq:020] checking route-(a) status", flush=True)
    conditions.append({
        "condition": "route_a_unavailable",
        "holds": route_a.get("available") is False,
        "evidence": "derived/route_a_probe.json",
    })

    # [P2-LOG-030] Step: verify global no-enrichment conditions.
    print("[P2:heq:030] checking no-enrichment conditions", flush=True)
    pdp_children = sorted(set(
        localname(e) for e in etree.parse(pdp_path).getroot()))
    conditions.append({
        "condition": "no_pip_configured",
        "holds": pdp_children == ["policyProvider"],
        "evidence": "pdp.xml child elements=%s" % pdp_children,
    })
    conditions.append({
        "condition": "no_selector_input_channels",
        "holds": adequacy.get("verdict") == "PASS",
        "evidence": "derived/policy_adequacy_certificate.json",
    })
    designator_coords = set(
        (d["category"], d["attribute_id"], d["data_type"])
        for d in projection["designators"])
    original_bags = request_bags(request_path)
    request_coords = set((c, i, t) for (c, i, t, _u) in original_bags)
    permit_bags = request_bags(permit_path)
    nonpermit_bags = request_bags(nonpermit_path)
    conditions.append({
        "condition": "completed_requests_add_only_declared_attribute",
        "holds": (set((c, i, t) for (c, i, t, _u) in permit_bags)
                  == request_coords | set([RELEVANT_COORDINATES[1]])
                  and set((c, i, t) for (c, i, t, _u) in nonpermit_bags)
                  == request_coords | set([RELEVANT_COORDINATES[1]])),
        "evidence": "derived/requests/request_x_*.xml bag coordinates",
    })
    print("[P2:heq:032] conditions checked=%d" % len(conditions), flush=True)

    # [P2-LOG-040] Step: build per-attribute equality rows.
    print("[P2:heq:040] building per-attribute rows", flush=True)
    def coord_values(bags, coordinate):
        """Return the sorted values for one coordinate, or []."""
        for (cat, aid, typ, _iss), values in bags.items():
            if (cat, aid, typ) == coordinate:
                return values
        return []

    rows = []
    for coordinate in RELEVANT_COORDINATES:
        present_original = coord_values(original_bags, coordinate) != []
        rows.append({
            "category": coordinate[0],
            "attribute_id": coordinate[1],
            "data_type": coordinate[2],
            "present_in_original": present_original,
            "permit_values": coord_values(permit_bags, coordinate),
            "nonpermit_values": coord_values(nonpermit_bags, coordinate),
            "equality_argument": (
                "Request-side values pass to the resolved context "
                "unchanged: the handler has no PIP source to add values "
                "from, no selector/XPath channel reads other XML, and "
                "Sec. 7.3.5 retrieval reads exactly these named bags; "
                "MustBePresent error semantics operate on the same bags."),
            "n1_locators": [N1_735, N1_DATAFLOW, N1_DESIGNATOR],
        })
    designator_cover = all(c in designator_coords for c in
                           RELEVANT_COORDINATES)
    conditions.append({
        "condition": "all_relevant_coordinates_designed",
        "holds": designator_cover,
        "evidence": "derived/policy_projection.json designator set",
    })

    verdict = "VALID" if all(c["holds"] for c in conditions) else "AMBIGUOUS"
    # [P2-LOG-050] Step: write the equivalence proof.
    print("[P2:heq:050] verdict=%s" % verdict, flush=True)
    proof = {
        "proof_id": "PC-XACML-S3PLUS-v1-h-equivalence",
        "route": "b",
        "verdict": verdict,
        "global_conditions": conditions,
        "attribute_rows": rows,
        "input_hashes": {
            "request.xml": sha256_file(request_path),
            "request_x_permit.xml": sha256_file(permit_path),
            "request_x_nonpermit.xml": sha256_file(nonpermit_path),
        },
        "provenance": {
            "spec_sha256": "see external/MANIFEST.json xacml.sha256",
            "policy_sha256": projection["policy_sha256"],
        },
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(proof, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-060] Step: proof complete.
    print("[P2:heq:060] H-equivalence proof complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
