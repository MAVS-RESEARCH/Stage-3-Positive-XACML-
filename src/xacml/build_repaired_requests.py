"""Phase-1 completed-request builder for PC-XACML-S3+.

Copies the frozen original request and inserts exactly one subject
Attribute carrying the world-specific missing-attribute value. Category,
AttributeId, and DataType are read from the frozen MissingAttributeDetail
and cross-checked against the frozen policy designator; no coordinate is
hardcoded. INV-05 (single-Attribute addition) and INV-06 (inter-world
difference is the AttributeValue only) are asserted by tree diff.

Step console lines use the [P1:build:NNN] tag, each marked by a
[P1-LOG-NNN] comment for Path.md citation.
"""

import copy
import os
import sys

from lxml import etree

XACML_STRING_DATATYPE = "http://www.w3.org/2001/XMLSchema#string"


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P1-LOG-900] Fail-closed termination marker for every abort path.
    print("[P1:build:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def find_child(parent, name):
    """Return the first child with the given local name or None."""
    for child in parent:
        if localname(child) == name:
            return child
    return None


def find_all(root, name):
    """Yield all descendants (inclusive) with the given local name."""
    for element in root.iter():
        if localname(element) == name:
            yield element


def read_missing_detail(response_path):
    """Read the (AttributeId, Category, DataType) triple from a response."""
    tree = etree.parse(response_path)
    details = list(find_all(tree.getroot(), "MissingAttributeDetail"))
    if len(details) != 1:
        fail("expected exactly one MissingAttributeDetail, found %d"
             % len(details))
    detail = details[0]
    triple = (detail.get("AttributeId"), detail.get("Category"),
              detail.get("DataType"))
    if any(value is None for value in triple):
        fail("MissingAttributeDetail lacks required coordinates")
    return triple


def read_policy_designators(policy_path, triple):
    """Return designators matching the triple; require MustBePresent true."""
    tree = etree.parse(policy_path)
    matches = []
    for designator in find_all(tree.getroot(), "AttributeDesignator"):
        candidate = (designator.get("AttributeId"),
                     designator.get("Category"),
                     designator.get("DataType"))
        if candidate == triple:
            matches.append(designator)
    if not matches:
        fail("no policy designator matches the missing-attribute triple")
    for designator in matches:
        if designator.get("MustBePresent") != "true":
            fail("matching designator lacks MustBePresent=true")
    return matches


def canonical(root):
    """Canonical serialization of a whole tree."""
    return etree.tostring(root, method="c14n")


def assert_single_attribute_addition(original_root, repaired_root, triple,
                                     value, name):
    """Assert INV-05: repaired differs from original by one Attribute only.

    Non-destructive: all removal checks run on a private deep copy so the
    tree under test is never mutated by its own assertion.
    """
    import copy as _copy
    probe_root = _copy.deepcopy(repaired_root)
    attribute_id, _category, datatype = triple
    repaired_subjects = [node for node in probe_root.iter()
                         if localname(node) == "Attributes"
                         and node.get("Category") == triple[1]]
    if len(repaired_subjects) != 1:
        fail("INV-05 violated for %s: subject node count changed" % name)
    original_values = set()
    for node in original_root.iter():
        if localname(node) == "Attribute":
            original_values.add(canonical(node))
    new_nodes = [node for node in repaired_subjects[0]
                 if localname(node) == "Attribute"
                 and canonical(node) not in original_values]
    if len(new_nodes) != 1:
        fail("INV-05 violated for %s: new Attribute count=%d"
             % (name, len(new_nodes)))
    added = new_nodes[0]
    if added.get("AttributeId") != attribute_id:
        fail("INV-05 violated for %s: wrong AttributeId" % name)
    if added.get("DataType") is not None:
        fail("INV-05 violated for %s: schema-illegal Attribute DataType"
             % name)
    values = [child for child in added
              if localname(child) == "AttributeValue"]
    if len(values) != 1 or values[0].text != value:
        fail("INV-05 violated for %s: wrong AttributeValue" % name)
    if values[0].get("DataType") != datatype:
        fail("INV-05 violated for %s: wrong value DataType" % name)
    parent = added.getparent()
    parent.remove(added)
    if canonical(probe_root) != canonical(original_root):
        fail("INV-05 violated for %s: residual difference remains" % name)
    live_values = [child.text for node in repaired_root.iter()
                   if localname(node) == "Attribute"
                   and node.get("AttributeId") == attribute_id
                   for child in node
                   if localname(child) == "AttributeValue"]
    if live_values != [value]:
        fail("INV-05 violated for %s: live tree lost the insert" % name)


def insert_attribute(request_tree, triple, value):
    """Insert one subject Attribute with the world value; return new tree."""
    attribute_id, category, datatype = triple
    root = request_tree.getroot()
    subject_nodes = [node for node in find_all(root, "Attributes")
                     if node.get("Category") == category]
    if len(subject_nodes) != 1:
        fail("expected exactly one subject Attributes node, found %d"
             % len(subject_nodes))
    subject = subject_nodes[0]
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}")[0] + "}"
    attribute = etree.SubElement(subject, namespace + "Attribute")
    attribute.set("AttributeId", attribute_id)
    # NOTE (hardening R2A-07): XACML 3.0 request Attribute elements carry
    # NO DataType attribute (it lives on AttributeValue only); emitting
    # one makes the request schema-invalid and the frozen validating
    # parser rejects it. Values below carry their DataType.
    attribute.set("IncludeInResult", "false")
    value_node = etree.SubElement(attribute, namespace + "AttributeValue")
    value_node.set("DataType", datatype)
    value_node.text = value
    return request_tree


def write_request(tree, path):
    """Write a request tree deterministically (UTF-8, declaration)."""
    data = etree.tostring(tree, xml_declaration=True, encoding="UTF-8",
                          pretty_print=True)
    with open(path, "wb") as handle:
        handle.write(data)


def main(argv):
    """Entry point: build both completed world requests."""
    # [P1-LOG-010] Step: start build, echo resolved arguments.
    print("[P1:build:010] start completed-request build", flush=True)
    if len(argv) != 7:
        fail("usage: build_repaired_requests.py <request.xml> "
             "<response.xml> <policy.xml> <permit-value> "
             "<nonpermit-value> <out-dir>")
    request_path, response_path, policy_path = argv[1], argv[2], argv[3]
    permit_value, nonpermit_value, out_dir = argv[4], argv[5], argv[6]
    if not permit_value.strip() or not nonpermit_value.strip():
        fail("world values must be non-empty (preregistered literals)")
    print("[P1:build:012] out-dir=%s" % os.path.abspath(out_dir), flush=True)

    # [P1-LOG-020] Step: read coordinates from frozen response.
    print("[P1:build:020] reading MissingAttributeDetail", flush=True)
    triple = read_missing_detail(response_path)
    print("[P1:build:022] triple=%s" % (triple,), flush=True)

    # [P1-LOG-030] Step: cross-check against frozen policy designator.
    print("[P1:build:030] cross-checking policy designator", flush=True)
    designators = read_policy_designators(policy_path, triple)
    print("[P1:build:032] matching designators=%d MustBePresent=true"
          % len(designators), flush=True)

    # [P1-LOG-040] Step: build the permit-world request.
    print("[P1:build:040] building x_permit request", flush=True)
    original = etree.parse(request_path)
    permit_tree = insert_attribute(copy.deepcopy(original), triple,
                                   permit_value)

    # [P1-LOG-050] Step: build the nonpermit-world request.
    print("[P1:build:050] building x_nonpermit request", flush=True)
    nonpermit_tree = insert_attribute(copy.deepcopy(original), triple,
                                      nonpermit_value)

    # [P1-LOG-060] Step: assert INV-05 and INV-06.
    print("[P1:build:060] asserting INV-05 and INV-06", flush=True)
    assert_single_attribute_addition(original.getroot(),
                                     permit_tree.getroot(), triple,
                                     permit_value, "x_permit")
    print("[P1:build:062] INV-05 ok x_permit", flush=True)
    assert_single_attribute_addition(original.getroot(),
                                     nonpermit_tree.getroot(), triple,
                                     nonpermit_value, "x_nonpermit")
    print("[P1:build:063] INV-05 ok x_nonpermit", flush=True)
    if permit_value == nonpermit_value:
        fail("INV-06 violated: world values identical")
    print("[P1:build:064] INV-06 ok: values differ across worlds", flush=True)

    # [P1-LOG-070] Step: write both requests.
    print("[P1:build:070] writing completed requests", flush=True)
    os.makedirs(out_dir, exist_ok=True)
    permit_path = os.path.join(out_dir, "request_x_permit.xml")
    nonpermit_path = os.path.join(out_dir, "request_x_nonpermit.xml")
    write_request(permit_tree, permit_path)
    write_request(nonpermit_tree, nonpermit_path)
    print("[P1:build:072] wrote %s" % permit_path, flush=True)
    print("[P1:build:074] wrote %s" % nonpermit_path, flush=True)

    # [P1-LOG-080] Step: build complete.
    print("[P1:build:080] completed-request build complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
