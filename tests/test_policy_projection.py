"""Phase-2 policy-projection test (P01).

Asserts the mechanical projection: five designators with exact
coordinates, the missing-attribute canary triple with
MustBePresent=true, coverage of all four experiment-relevant
coordinates, and byte-identity with the sealed policy.
"""
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CANARY = ("urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
          "urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute",
          "http://www.w3.org/2001/XMLSchema#string")
RELEVANT = {
    ("urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
     "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
     "http://www.w3.org/2001/XMLSchema#string"),
    (CANARY[0], CANARY[1], CANARY[2]),
    ("urn:oasis:names:tc:xacml:3.0:attribute-category:resource",
     "urn:oasis:names:tc:xacml:1.0:resource:resource-id",
     "http://www.w3.org/2001/XMLSchema#anyURI"),
    ("urn:oasis:names:tc:xacml:3.0:attribute-category:action",
     "urn:oasis:names:tc:xacml:1.0:action:action-id",
     "http://www.w3.org/2001/XMLSchema#string"),
}


def test_policy_projection_exact():
    """P01: projection lists exact designator coordinates."""
    # [P2-LOG-T10] Test step: assert P01 projection contents.
    print("[P2:test:projection:010] checking P01 projection", flush=True)
    with open(os.path.join(REPO_ROOT, "derived",
                           "policy_projection.json"),
              encoding="utf-8") as handle:
        projection = json.load(handle)
    designators = projection["designators"]
    assert len(designators) == 5, len(designators)
    for designator in designators:
        for key in ("category", "attribute_id", "data_type",
                    "must_be_present", "rule_id", "match_function",
                    "path"):
            assert designator[key], (key, designator)
    canary = [d for d in designators
              if (d["category"], d["attribute_id"], d["data_type"])
              == CANARY and d["must_be_present"] == "true"]
    assert len(canary) == 1
    coords = set((d["category"], d["attribute_id"], d["data_type"])
                 for d in designators)
    assert RELEVANT.issubset(coords), RELEVANT - coords
    # [P2-LOG-T12] Test step: assert sealed policy identity.
    print("[P2:test:projection:012] checking sealed policy identity",
          flush=True)
    assert (projection["policy_sha256"]
            == projection["manifest_policy_sha256"])
    with open(os.path.join(REPO_ROOT, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    assert (manifest["authzforce"]["fixture_files"][
        "policies/policy.xml"]["sha256"]
        == projection["policy_sha256"])
