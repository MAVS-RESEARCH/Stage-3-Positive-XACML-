"""Builder hardening tests: Detail cardinality + output-flow discipline.

Multi-Detail fixtures fail closed; builder never opens built-world or
response outputs as inputs (flow-read check in wrapper evidence).
"""
import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

EXTRA_DETAIL = ('<MissingAttributeDetail Category="urn:oasis:names:tc:xacml:'
                '1.0:subject-category:access-subject" AttributeId="urn:oasis:'
                'names:tc:xacml:2.0:conformance-test:other" DataType="http://'
                'www.w3.org/2001/XMLSchema#string"/>')


def stage_fixture(base, double_detail=False):
    """Stage frozen inputs in tmp, optionally with two Details."""
    import hardening_evidence as hev  # noqa: E402,E501
    os.makedirs(os.path.join(base, "policies"))
    os.makedirs(os.path.join(base, "out"))
    for rel in ("request.xml",):
        shutil.copyfile(os.path.join(REPO_ROOT, "external", "authzforce",
                                     "fixture", rel),
                        os.path.join(base, rel))
    shutil.copyfile(os.path.join(REPO_ROOT, "external", "authzforce",
                                 "fixture", "policies", "policy.xml"),
                    os.path.join(base, "policies", "policy.xml"))
    text = open(os.path.join(REPO_ROOT, "external", "authzforce",
                             "fixture", "response.xml"),
                encoding="utf-8").read()
    if double_detail:
        text = text.replace("<MissingAttributeDetail ", EXTRA_DETAIL
                            + "<MissingAttributeDetail ", 1)
    with open(os.path.join(base, "response.xml"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return hev


def run_builder(base):
    """Run the builder over a staged fixture; return exit code + output."""
    completed = subprocess.run(
        [sys.executable,
         os.path.join(REPO_ROOT, "src", "xacml",
                      "build_repaired_requests.py"),
         os.path.join(base, "request.xml"),
         os.path.join(base, "response.xml"),
         os.path.join(base, "policies", "policy.xml"), "riddle me this",
         "not-riddle-me-this", os.path.join(base, "out")],
        capture_output=True, text=True, timeout=120)
    return completed.returncode, completed.stdout + completed.stderr


def test_multi_detail_refused(tmp_path):
    """Two MissingAttributeDetail elements fail the build."""
    # [P2-LOG-D10] Test step: assert Detail cardinality gate.
    print("[P2:test:builder:010] detail cardinality", flush=True)
    stage_fixture(str(tmp_path / "fix"), double_detail=True)
    code, output = run_builder(str(tmp_path / "fix"))
    assert code != 0
    assert "expected exactly one MissingAttributeDetail" in output


def test_single_detail_builds(tmp_path):
    """Frozen single-Detail fixture builds both worlds."""
    # [P2-LOG-D12] Test step: assert nominal build path.
    print("[P2:test:builder:012] nominal build", flush=True)
    stage_fixture(str(tmp_path / "fix"))
    code, _output = run_builder(str(tmp_path / "fix"))
    assert code == 0
    assert os.path.isfile(os.path.join(str(tmp_path / "fix"), "out",
                                       "request_x_permit.xml"))


def test_flow_reads_no_outputs(tmp_path):
    """Wrapper evidence records zero output reads (flow check)."""
    # [P2-LOG-D14] Test step: assert flow discipline evidence.
    print("[P2:test:builder:014] flow discipline", flush=True)
    import hardening_evidence as hev
    out = str(tmp_path / "wrapper_evidence.json")
    hev.cmd_wrapper(_ns(
        builder=os.path.join(REPO_ROOT, "src", "xacml",
                             "build_repaired_requests.py"),
        runner=os.path.join(REPO_ROOT, "src", "xacml", "run_authzforce.py"),
        original=os.path.join(REPO_ROOT, "external", "authzforce",
                              "fixture", "request.xml"),
        permit=os.path.join(REPO_ROOT, "derived", "requests",
                            "request_x_permit.xml"),
        nonpermit=os.path.join(REPO_ROOT, "derived", "requests",
                               "request_x_nonpermit.xml"),
        response=os.path.join(REPO_ROOT, "external", "authzforce",
                              "fixture", "response.xml"),
        policy=os.path.join(REPO_ROOT, "external", "authzforce", "fixture",
                            "policies", "policy.xml"),
        execution_inputs=os.path.join(REPO_ROOT, "prereg",
                                      "execution_inputs.json"),
        out=out))
    import json
    with open(out, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert doc["flow_reads_outputs"] == []


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
