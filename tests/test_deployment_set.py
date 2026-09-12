"""Deployment-set gate tests (RS003-B01).

Synthetic temporary roots plus live-repo anchors: emit/check roundtrip,
added/removed/modified detection, count!=1 refusal, disjoint variants,
and live fixture vs ROUND_001 listing with builder out_dir separation.
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import verify_deployment_set as gate  # noqa: E402


def write(path, content):
    """Write text, creating parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def test_emit_then_check_roundtrip(tmp_path):
    """Emit writes a listing that check accepts (CLI + library)."""
    # [P2-LOG-T10] Test step: assert emit/check roundtrip.
    print("[P2:test:deployment:010] roundtrip", flush=True)
    fixture = str(tmp_path / "policies")
    os.makedirs(fixture)
    write(os.path.join(fixture, "policy.xml"), "<root/>\n")
    out = str(tmp_path / "listing.json")
    gate.main(["--repo-root", str(tmp_path), "--emit",
               "--fixture-dir", fixture, "--out", out])
    with open(out, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert len(doc["files"]) == 1
    assert doc["files"][0]["name"] == "policy.xml"
    assert gate.check(gate.live_listing(fixture), doc) == []
    gate.main(["--repo-root", str(tmp_path), "--check",
               "--fixture-dir", fixture, "--listing", out])


def test_detects_added_removed_modified(tmp_path):
    """Added/removed/modified files are all refused."""
    # [P2-LOG-T12] Test step: assert mutation detection.
    print("[P2:test:deployment:012] mutations", flush=True)
    fixture = str(tmp_path / "policies")
    os.makedirs(fixture)
    write(os.path.join(fixture, "policy.xml"), "v1")
    baseline = gate.live_listing(fixture)
    write(os.path.join(fixture, "extra.xml"), "new")
    assert gate.check(gate.live_listing(fixture), baseline) != []
    os.remove(os.path.join(fixture, "extra.xml"))
    os.remove(os.path.join(fixture, "policy.xml"))
    assert gate.check(gate.live_listing(fixture), baseline) != []
    write(os.path.join(fixture, "policy.xml"), "v1")
    assert gate.check(gate.live_listing(fixture), baseline) == []
    write(os.path.join(fixture, "policy.xml"), "v2-modified")
    assert any(p.startswith("modified:")
               for p in gate.check(gate.live_listing(fixture), baseline))


def test_count_not_one_refused(tmp_path):
    """Zero/two-file sets and two-file expected docs are refused."""
    # [P2-LOG-T14] Test step: assert count==1 enforcement.
    print("[P2:test:deployment:014] count", flush=True)
    fixture = str(tmp_path / "policies")
    os.makedirs(fixture)
    write(os.path.join(fixture, "policy.xml"), "a")
    single = gate.live_listing(fixture)
    write(os.path.join(fixture, "second.xml"), "b")
    assert any("count!=1" in p
               for p in gate.check(gate.live_listing(fixture), single))
    double = gate.live_listing(fixture)
    assert any("count!=1" in p for p in gate.check(double, double))
    assert any("count!=1" in p for p in gate.check(single, double))
    os.remove(os.path.join(fixture, "second.xml"))
    os.remove(os.path.join(fixture, "policy.xml"))
    assert gate.check(gate.live_listing(fixture), single) != []
    write(os.path.join(fixture, "policy.xml"), "a")
    sub = os.path.join(fixture, "sub")
    os.makedirs(sub)
    assert any("subdir" in p
               for p in gate.check(gate.live_listing(fixture), single))


def test_disjoint_variants(tmp_path, monkeypatch):
    """Sibling true; nested/trailing/relative/dotdot false."""
    # [P2-LOG-T16] Test step: assert disjoint path variants.
    print("[P2:test:deployment:016] disjoint", flush=True)
    base = str(tmp_path)
    policies = os.path.join(base, "policies")
    sibling = os.path.join(base, "out")
    nested = os.path.join(policies, "sub")
    os.makedirs(policies)
    os.makedirs(sibling)
    assert gate.disjoint(sibling, policies) is True
    assert gate.disjoint(policies, sibling) is True
    assert gate.disjoint(nested, policies) is False
    assert gate.disjoint(policies, nested) is False
    assert gate.disjoint(nested + os.sep, policies) is False
    assert gate.disjoint(policies, policies + os.sep) is False
    dotdot_same = os.path.join(base, "policies", "..", "policies")
    assert gate.disjoint(dotdot_same, policies) is False
    dotdot_nested = os.path.join(base, "out", "..", "policies", "sub")
    assert gate.disjoint(dotdot_nested, policies) is False
    dotdot_sibling = os.path.join(base, "policies", "..", "out")
    assert gate.disjoint(dotdot_sibling, policies) is True
    monkeypatch.chdir(base)
    assert gate.disjoint(os.path.join("policies", "sub"),
                         os.path.join("policies")) is False
    assert gate.disjoint("out", "policies") is True
    try:
        gate.main(["--repo-root", base, "--disjoint",
                   "--out-dir", nested, "--policies-dir", policies])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("overlap allowed")


def test_live_repo_check_passes():
    """Live fixture policies/ matches the ROUND_001 listing doc."""
    # [P2-LOG-T18] Test step: assert live single-policy deployment set.
    print("[P2:test:deployment:018] live check", flush=True)
    policies = os.path.join(REPO_ROOT, "external", "authzforce",
                            "fixture", "policies")
    listing = os.path.join(REPO_ROOT, "artifacts", "audits",
                           "semantic_hardening", "rounds",
                           "HARDENING_ROUND_001", "evidence",
                           "policy_dir_listing.json")
    with open(listing, encoding="utf-8") as handle:
        expected = json.load(handle)
    assert len(expected["files"]) == 1
    assert expected["files"][0]["name"] == "policy.xml"
    assert gate.check(gate.live_listing(policies), expected) == []


def test_live_builder_out_dir_disjoint():
    """Builder out_dir derived/requests sits outside the policies glob."""
    # [P2-LOG-T20] Test step: assert builder/policies separation.
    print("[P2:test:deployment:020] builder disjoint", flush=True)
    policies = os.path.join(REPO_ROOT, "external", "authzforce",
                            "fixture", "policies")
    out_dir = os.path.join(REPO_ROOT, "derived", "requests")
    assert gate.disjoint(out_dir, policies) is True
    assert gate.disjoint(out_dir + os.sep, policies + os.sep) is True
