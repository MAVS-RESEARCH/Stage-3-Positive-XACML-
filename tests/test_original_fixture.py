"""Phase-1 original-fixture test (N01).

Asserts the frozen PDP returns the frozen missing-attribute semantics on
the frozen original request: Decision Indeterminate, StatusCode
missing-attribute, and the exact MissingAttributeDetail triple. Also
asserts the sealed comparison record reports a semantic match.
"""
import json
import os

from lxml import etree

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPECTED_DETAIL = {
    "AttributeId": "urn:oasis:names:tc:xacml:2.0:conformance-test:"
                   "some-attribute",
    "Category": "urn:oasis:names:tc:xacml:1.0:subject-category:"
                "access-subject",
    "DataType": "http://www.w3.org/2001/XMLSchema#string",
}
MISSING_ATTRIBUTE_STATUS = \
    "urn:oasis:names:tc:xacml:1.0:status:missing-attribute"


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def find_first(root, name):
    """Return the first descendant with the given local name or None."""
    for element in root.iter():
        if localname(element) == name:
            return element
    return None


def test_original_fixture_semantics():
    """N01: original request reproduces the missing-attribute fixture."""
    # [P1-LOG-T20] Test step: assert N01 native fixture semantics.
    print("[P1:test:fixture:020] checking N01 fixture semantics",
          flush=True)
    actual_path = os.path.join(REPO_ROOT, "artifacts", "raw",
                               "original_response_actual.xml")
    root = etree.parse(actual_path).getroot()
    decision = find_first(root, "Decision")
    assert decision is not None and decision.text.strip() == "Indeterminate"
    status = find_first(root, "StatusCode")
    assert status is not None
    assert status.get("Value") == MISSING_ATTRIBUTE_STATUS
    detail = find_first(root, "MissingAttributeDetail")
    assert detail is not None
    for key, value in EXPECTED_DETAIL.items():
        assert detail.get(key) == value, key
    # [P1-LOG-T22] Test step: assert the sealed comparison record.
    print("[P1:test:fixture:022] checking comparison record", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "raw",
                           "original_response_comparison.json"),
              encoding="utf-8") as handle:
        record = json.load(handle)
    assert record["semantic_match"] is True
    assert record["decision_actual"] == "Indeterminate"
    assert record["decision_expected"] == "Indeterminate"
