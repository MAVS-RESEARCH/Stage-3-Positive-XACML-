"""Phase-1 ordering test: no completed-world execution in Phase 1.

Attribution rule (NOT an existence scan): Phase 2 legitimately creates
completed-world outputs, so this test asserts no completed-world
invocation/output ATTRIBUTABLE TO PHASE 1, namely (a) the execution
wrapper refuses completed mode under --phase1-only-original (exit 2),
(b) Phase-1-tagged logs contain zero completed-mode invocations,
(c) the Phase-1 sealed manifest/seal contains zero completed-world
entries, and (d) the Phase-1 sealed response artifacts carry
original-fixture (Indeterminate) semantics. A simulated post-Phase-2
tree regression case proves later completed outputs do not trip it.
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))

import run_authzforce  # noqa: E402

COMPLETED_LOG_MARKERS = ("mode=completed", "fixture_x_permit",
                         "fixture_x_nonpermit", "world=x_permit",
                         "world=x_nonpermit")
SEAL_MARKERS = ("x_permit", "x_nonpermit")


def phase1_log_files(root):
    """Return Phase-1-tagged log files under a checkout root."""
    logs_dir = os.path.join(root, "artifacts", "logs")
    if not os.path.isdir(logs_dir):
        return []
    return [os.path.join(logs_dir, name) for name in sorted(os.listdir(
        logs_dir)) if os.path.isfile(os.path.join(logs_dir, name))
        and "phase1" in name.lower()]


def check_no_completed_in_phase1_logs(root):
    """Assert Phase-1 logs show no completed-world invocation."""
    # [P1-LOG-T30] Test step: scan Phase-1-tagged logs only.
    print("[P1:test:ordering:030] scanning Phase-1 logs for completed "
          "invocations", flush=True)
    for path in phase1_log_files(root):
        with open(path, encoding="utf-8", errors="replace") as handle:
            content = handle.read()
        for marker in COMPLETED_LOG_MARKERS:
            assert marker not in content, (path, marker)


def check_phase1_seal_clean(root):
    """Assert the Phase-1 seal records zero completed-world entries."""
    # [P1-LOG-T32] Test step: scan Phase-1 sealed records only.
    print("[P1:test:ordering:032] scanning Phase-1 seal for completed "
          "entries", flush=True)
    manifest_path = os.path.join(root, "external", "MANIFEST.json")
    with open(manifest_path, encoding="utf-8") as handle:
        manifest_text = handle.read()
    json.loads(manifest_text)
    seal_path = os.path.join(root, "prereg", "prereg_sha256.txt")
    with open(seal_path, encoding="utf-8") as handle:
        seal_text = handle.read()
    for marker in SEAL_MARKERS:
        assert marker not in manifest_text, marker
        assert marker not in seal_text, marker


def check_phase1_responses_original(root):
    """Assert Phase-1 sealed responses are original-fixture outputs."""
    # [P1-LOG-T36] Test step: assert sealed responses are originals.
    print("[P1:test:ordering:036] checking sealed responses are original "
          "fixture outputs", flush=True)
    record_path = os.path.join(root, "artifacts", "raw",
                               "original_response_comparison.json")
    with open(record_path, encoding="utf-8") as handle:
        record = json.load(handle)
    assert record["semantic_match"] is True
    assert record["decision_actual"] == "Indeterminate"


def test_no_completed_invocation_in_phase1_logs():
    """No completed-mode invocation is attributable to Phase 1 logs."""
    check_no_completed_in_phase1_logs(REPO_ROOT)


def test_phase1_seal_contains_no_completed_outputs():
    """No completed-world entry is attributable to the Phase-1 seal."""
    check_phase1_seal_clean(REPO_ROOT)


def test_phase1_responses_are_original_fixture():
    """Phase-1 sealed responses carry original-fixture semantics."""
    check_phase1_responses_original(REPO_ROOT)


def test_completed_mode_refused():
    """--phase1-only-original refuses completed mode with exit code 2."""
    # [P1-LOG-T34] Test step: assert the ordering refusal path.
    print("[P1:test:ordering:034] asserting completed-mode refusal",
          flush=True)
    try:
        run_authzforce.main([
            "--mode", "completed", "--world", "x_permit",
            "--request", "request_x_permit.xml",
            "--phase1-only-original", "--repo-root", REPO_ROOT,
            "--java", "java", "--cp-file", "cp.txt",
            "--pdp-test-classes", "t", "--pdp-classes", "c",
            "--driver-classes", "d", "--work-dir", "w",
            "--out", "o.xml"])
    except SystemExit as exc:
        assert exc.code == 2, exc.code
    else:
        raise AssertionError("completed mode was not refused")


def test_future_completed_outputs_not_attributed_to_phase1(tmp_path):
    """Simulated post-Phase-2 tree must NOT trip the attribution rule."""
    # [P1-LOG-T38] Test step: regression case for the chronology bug.
    print("[P1:test:ordering:038] simulating post-Phase-2 tree",
          flush=True)
    logs_dir = tmp_path / "artifacts" / "logs"
    raw_dir = tmp_path / "artifacts" / "raw"
    logs_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)
    (logs_dir / "local_phase1_run.log").write_text(
        "[P1:run:022] ordering check passed\n", encoding="utf-8")
    (logs_dir / "local_phase2_run.log").write_text(
        "[P2:run:010] mode=completed world=x_permit\n"
        "staged fixture_x_permit\n",
        encoding="utf-8")
    (raw_dir / "response_x_permit_actual.xml").write_text(
        "<Response/>", encoding="utf-8")
    (raw_dir / "original_response_comparison.json").write_text(
        json.dumps({"semantic_match": True,
                    "decision_actual": "Indeterminate"}),
        encoding="utf-8")
    external_dir = tmp_path / "external"
    external_dir.mkdir()
    (external_dir / "MANIFEST.json").write_text(
        json.dumps({"authzforce": {"commit": "abc"}}), encoding="utf-8")
    prereg_dir = tmp_path / "prereg"
    prereg_dir.mkdir()
    (prereg_dir / "prereg_sha256.txt").write_text(
        "deadbeef  experiment.yaml\n", encoding="utf-8")
    root = str(tmp_path)
    check_no_completed_in_phase1_logs(root)
    check_phase1_seal_clean(root)
    check_phase1_responses_original(root)
    print("[P1:test:ordering:039] post-Phase-2 tree correctly unattributed",
          flush=True)
