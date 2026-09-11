"""Phase-2 policy-adequacy test.

Asserts the policy-adequacy certificate (PASS, no hidden input
channels, instantiation argument with N1 locators).
"""
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_derived(name):
    """Load a JSON document from derived/."""
    with open(os.path.join(REPO_ROOT, "derived", name),
              encoding="utf-8") as handle:
        return json.load(handle)


def test_policy_adequacy_pass():
    """Adequacy certificate passes with no hidden channels."""
    # [P2-LOG-T20] Test step: assert adequacy certificate.
    print("[P2:test:adequacy:020] checking adequacy certificate",
          flush=True)
    certificate = load_derived("policy_adequacy_certificate.json")
    assert certificate["verdict"] == "PASS", certificate["findings"]
    channels = certificate["channel_inventory"]
    assert channels["attribute_selectors"] == 0
    assert channels["xpath_expressions"] == 0
    assert channels["policy_id_references"] == 0
    assert set(channels["data_types"]) <= {
        "http://www.w3.org/2001/XMLSchema#string",
        "http://www.w3.org/2001/XMLSchema#anyURI"}
    assert channels["pdp_child_elements"] == ["policyProvider"]
    argument = certificate["pr_instantiation_argument"]
    assert "7.3.5" in argument and "5.29" in argument
    assert len(certificate["n1_locators"]) >= 3
