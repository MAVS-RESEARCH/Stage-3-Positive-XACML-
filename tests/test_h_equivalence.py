"""Phase-2 H-equivalence test.

Asserts the route-b equivalence proof (VALID verdict, all global
conditions hold, four attribute rows with per-world values).
"""
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_h_equivalence_valid():
    """H-equivalence proof is VALID with four attribute rows."""
    # [P2-LOG-T22] Test step: assert equivalence proof.
    print("[P2:test:equivalence:022] checking H-equivalence proof",
          flush=True)
    with open(os.path.join(REPO_ROOT, "derived",
                           "h_equivalence_proof.json"),
              encoding="utf-8") as handle:
        proof = json.load(handle)
    assert proof["route"] == "b"
    assert proof["verdict"] == "VALID", proof["global_conditions"]
    assert all(c["holds"] for c in proof["global_conditions"])
    assert len(proof["attribute_rows"]) == 4
    by_id = {r["attribute_id"]: r for r in proof["attribute_rows"]}
    some = by_id["urn:oasis:names:tc:xacml:2.0:conformance-test:"
                 "some-attribute"]
    assert some["present_in_original"] is False
    assert some["permit_values"] == ["riddle me this"]
    assert some["nonpermit_values"] == ["not-riddle-me-this"]
    subject = by_id["urn:oasis:names:tc:xacml:1.0:subject:subject-id"]
    assert subject["present_in_original"] is True
    assert subject["permit_values"] == ["Julius Hibbert"]
    # [P2-LOG-T24] Test step: assert H provenance record.
    print("[P2:test:equivalence:024] checking H provenance", flush=True)
    with open(os.path.join(REPO_ROOT, "artifacts", "audits",
                           "H_provenance.json"),
              encoding="utf-8") as handle:
        provenance = json.load(handle)
    assert set(provenance["h_files"]) == {"H_initial", "H_permit",
                                          "H_nonpermit"}
    assert provenance["proof"]["verdict"] == "VALID"
