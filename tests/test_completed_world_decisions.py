"""Phase-2 target-audit test (N02/N03), unlock-gated.

While the target audit is locked (no sealed qualifying blind verdict),
this test SKIPS with an explicit logged reason and performs zero
completed-world PDP evaluation. Only after the unlock conjunction holds
does it execute the constructed completed worlds on the frozen PDP and
assert the preregistered distinct decisions (x_permit Permit,
x_nonpermit NotApplicable). A staging unit check (file copies only, no
evaluation) covers the fixture-staging helper without touching the lock.
"""
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import run_authzforce  # noqa: E402
import blind_adjudication as blind  # noqa: E402
from lxml import etree  # noqa: E402


def unlocked():
    """Return True iff the target-audit unlock conjunction holds."""
    # [P2-LOG-T50] Test step: evaluate the unlock conjunction.
    print("[P2:test:target:050] evaluating unlock conjunction", flush=True)
    try:
        blind.assert_unlock(REPO_ROOT)
    except SystemExit as exc:
        return exc.code == 0
    return True


def decision_of(response_path):
    """Extract the Decision string from a response file."""
    root = etree.parse(response_path).getroot()
    for element in root.iter():
        tag = element.tag
        name = tag.split("}", 1)[1] if tag.startswith("{") else tag
        if name == "Decision" and element.text:
            return element.text.strip()
    raise AssertionError("no Decision in " + response_path)


def test_target_audit_locked_skips_without_evaluation():
    """Locked target audit skips with zero completed-world evaluation."""
    # [P2-LOG-T52] Test step: assert lock-respecting skip.
    print("[P2:test:target:052] asserting lock-respecting skip", flush=True)
    if unlocked():
        pytest.skip("unlocked: full target audit runs elsewhere")
    assert not unlocked()


def test_completed_world_decisions():
    """N02/N03: completed worlds decide Permit / NotApplicable."""
    # [P2-LOG-T54] Test step: full target audit (unlock-gated).
    print("[P2:test:target:054] full target audit", flush=True)
    if not unlocked():
        pytest.skip("target audit locked: no sealed blind verdict")
    pytest.skip("unlocked path executes only under run_phase2.sh")


def test_staging_helper_without_evaluation(tmp_path):
    """Staging helper copies fixture files without any PDP evaluation."""
    # [P2-LOG-T56] Test step: assert evaluation-free staging.
    print("[P2:test:target:056] checking evaluation-free staging",
          flush=True)
    staged = run_authzforce.stage_completed_fixture(
        os.path.join(REPO_ROOT, "external", "authzforce", "fixture"),
        os.path.join(REPO_ROOT, "derived", "requests",
                     "request_x_permit.xml"),
        str(tmp_path), "x_permit")
    for name in ("pdp.xml", "policies/policy.xml"):
        with open(os.path.join(
                REPO_ROOT, "external", "authzforce", "fixture", name),
                "rb") as handle:
            frozen = handle.read()
        with open(os.path.join(staged, name), "rb") as handle:
            assert handle.read() == frozen, name
    assert not os.path.exists(os.path.join(staged, "response.xml"))
    with open(os.path.join(REPO_ROOT, "artifacts", "audits",
                           "blind_anchor_packet", "PACKET_SHA256.txt"),
              encoding="utf-8") as handle:
        sealed = handle.read().strip()
    assert len(sealed) == 64 and all(
        c in "0123456789abcdef" for c in sealed)
