"""Phase-1 native PDP execution wrapper for PC-XACML-S3+.

Invokes the frozen AuthzForce PDP (built from the pinned commit) on one
XACML request via the PdpRunner driver and writes the raw response.
Modes: `original` (frozen fixture request) and `completed` (a constructed
world request in a temporary fixture copy). `--phase1-only-original`
refuses `completed` mode: completed-world execution is prohibited until
the Phase-2 target audit after the sealed 2B verdict. The wrapper performs
no authorization logic of its own.

Step console lines use the [P1:run:NNN] tag, each marked by a
[P1-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P1-LOG-900] Fail-closed termination marker for every abort path.
    print("[P1:run:FAIL] " + message, flush=True)
    sys.exit(1)


def refuse(message):
    """Emit a Phase-1 ordering refusal and exit with code 2."""
    # [P1-LOG-901] Ordering-refusal marker (distinct exit code 2).
    print("[P1:run:REFUSE] " + message, flush=True)
    sys.exit(2)


def parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the frozen AuthzForce PDP on one request.")
    parser.add_argument("--mode", required=True,
                        choices=["original", "completed"])
    parser.add_argument("--world", default="",
                        help="world label, required in completed mode")
    parser.add_argument("--phase1-only-original", action="store_true")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--java", required=True)
    parser.add_argument("--cp-file", required=True)
    parser.add_argument("--pdp-test-classes", required=True)
    parser.add_argument("--pdp-classes", required=True)
    parser.add_argument("--driver-classes", required=True)
    parser.add_argument("--request", default="",
                        help="request path, required in completed mode")
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args(argv)


def check_file(path, label):
    """Fail closed if an expected file is missing."""
    if not os.path.isfile(path):
        fail("missing %s: %s" % (label, path))


def seal_outcome_capsule(repo_root, world, response_path):
    """Hash-seal raw response bytes without opening outcome content.

    The capsule carries hashes and byte counts only — never Decision,
    status, or detail content. Parsing waits on the conformance gate.
    """
    # [P1-LOG-063] Step: seal outcome capsule (hash only).
    import json
    from datetime import datetime, timezone
    capsule_dir = os.path.join(repo_root, "artifacts", "audits", "launch",
                               "quarantine")
    os.makedirs(capsule_dir, exist_ok=True)
    with open(response_path, "rb") as handle:
        digest = hashlib.sha256()
        total = 0
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
            total += len(chunk)
    record = {"capsule_id": "PC-XACML-S3PLUS-v1-outcome-%s" % world,
              "world": world,
              "response_sha256": digest.hexdigest(),
              "response_bytes": total,
              "sealed_utc": datetime.now(timezone.utc).strftime(
                  "%Y-%m-%dT%H:%M:%SZ")}
    path = os.path.join(capsule_dir, "capsule_%s.json" % world)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P1:run:063] outcome capsule sealed bytes=%d" % total,
          flush=True)


def write_execution_lock(repo_root, world):
    """Record the permanent point of no return for completed worlds."""
    # [P1-LOG-064] Step: seal first-invocation lock (Amendment 007).
    # After this file exists, no semantic/harness reopen is legal.
    import json
    from datetime import datetime, timezone
    seal_dir = os.path.join(repo_root, "artifacts", "seal")
    os.makedirs(seal_dir, exist_ok=True)
    path = os.path.join(seal_dir, "TARGET_EXECUTION_LOCK.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as handle:
            record = json.load(handle)
    else:
        record = {"lock_id": "PC-XACML-S3PLUS-v1-target-lock",
                  "worlds": []}
    if world not in record["worlds"]:
        record["worlds"].append(world)
        record["worlds"].sort()
    record["updated_utc"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P1:run:064] execution lock recorded worlds=%s"
          % record["worlds"], flush=True)


def stage_completed_fixture(fixture_dir, request_path, work_dir, world):
    """Stage a temp fixture copy for one completed world (no evaluation).

    Copies pdp.xml + policies/ from the frozen fixture; the caller
    supplies the constructed request. Performs no PDP evaluation.
    """
    # [P1-LOG-042] Step: completed mode stages a temp fixture copy.
    print("[P1:run:042] completed mode: staging temp fixture copy",
          flush=True)
    if not os.path.isfile(request_path):
        fail("completed request missing: " + request_path)
    run_fixture_dir = os.path.join(os.path.abspath(work_dir),
                                   "fixture_" + world)
    if os.path.isdir(run_fixture_dir):
        shutil.rmtree(run_fixture_dir)
    os.makedirs(os.path.join(run_fixture_dir, "policies"))
    shutil.copyfile(os.path.join(fixture_dir, "pdp.xml"),
                    os.path.join(run_fixture_dir, "pdp.xml"))
    shutil.copyfile(
        os.path.join(fixture_dir, "policies", "policy.xml"),
        os.path.join(run_fixture_dir, "policies", "policy.xml"))
    print("[P1:run:044] staged %s" % run_fixture_dir, flush=True)
    return run_fixture_dir


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_staged_fixture(fixture_dir, run_fixture_dir):
    """Prove staged copies equal frozen bytes with an exclusive set.

    Lambda_after_request_repair_pre_evaluation: same capability bytes the
    frozen manifest pins, checked after staging and before any evaluation.
    No PDP runs here; pure byte/config equality, not decision equality.
    """
    # [P1-LOG-046] Step: verify staged capability equals frozen.
    print("[P1:run:046] verifying staged fixture equals frozen", flush=True)
    for rel in ("pdp.xml", os.path.join("policies", "policy.xml")):
        frozen = os.path.join(fixture_dir, *rel.split("/"))
        staged = os.path.join(run_fixture_dir, *rel.split("/"))
        if not os.path.isfile(staged):
            fail("staged copy missing: " + rel)
        if sha256_file(staged) != sha256_file(frozen):
            fail("staged copy drifted: " + rel)
    staged_policies = os.path.join(run_fixture_dir, "policies")
    names = sorted(os.listdir(staged_policies))
    if names != ["policy.xml"]:
        fail("staged policy set not exclusive: %s" % names)
    root_names = sorted(os.listdir(run_fixture_dir))
    if root_names != ["pdp.xml", "policies"]:
        fail("staged root not exclusive: %s" % root_names)
    print("[P1:run:048] staged fixture verified", flush=True)


def main(argv):
    """Entry point: execute one native PDP request/response cycle."""
    # [P1-LOG-010] Step: start run, echo mode and ordering flag.
    print("[P1:run:010] start native PDP execution", flush=True)
    args = parse_args(argv)
    print("[P1:run:012] mode=%s world=%s phase1_only_original=%s"
          % (args.mode, args.world or "-",
             args.phase1_only_original), flush=True)

    # [P1-LOG-020] Step: enforce Phase-1 original-only ordering.
    print("[P1:run:020] enforcing execution ordering", flush=True)
    if args.phase1_only_original and args.mode != "original":
        refuse("completed-world execution is prohibited in Phase 1; "
               "it unlocks only at the Phase-2 target audit")
    if args.mode == "completed" and not args.world:
        fail("completed mode requires --world")
    if args.mode == "completed" and not args.request:
        fail("completed mode requires --request")
    if args.mode == "completed":
        # [P1-LOG-024] Step: Amendment-007 launch-authorization gate.
        # Completed-world invocation is forbidden until a sealed
        # TARGET_EXECUTION_AUTHORIZED.json exists (D14 fix). This is
        # the point-of-no-return guard: no target execution before
        # unanimous pre-execution launch certification.
        repo_probe = os.path.abspath(args.repo_root)
        auth_path = os.path.join(repo_probe, "artifacts", "audits",
                                 "launch", "TARGET_EXECUTION_AUTHORIZED.json")
        try:
            with open(auth_path, encoding="utf-8") as handle:
                auth = json.load(handle)
        except (OSError, ValueError):
            auth = {}
        if auth.get("authorized") is not True:
            fail("completed-world execution forbidden before "
                 "TARGET_EXECUTION_AUTHORIZED")
        try:
            with open(os.path.join(repo_probe, "artifacts", "audits",
                                   "launch", "LAUNCH_FREEZE.json"),
                      encoding="utf-8") as handle:
                freeze_record = json.load(handle)
        except (OSError, ValueError):
            freeze_record = {}
        for key in ("packet_sha256", "prompt_sha256"):
            if auth.get(key) != freeze_record.get(key):
                fail("authorization not bound to live launch freeze: " +
                     key)
    print("[P1:run:022] ordering check passed", flush=True)

    repo_root = os.path.abspath(args.repo_root)
    fixture_dir = os.path.join(repo_root, "external", "authzforce",
                               "fixture")
    for name in ("pdp.xml", "request.xml", "response.xml",
                 "policies/policy.xml"):
        check_file(os.path.join(fixture_dir, name), "frozen fixture " + name)

    # [P1-LOG-030] Step: resolve backend artifacts.
    print("[P1:run:030] resolving PDP backend artifacts", flush=True)
    for path, label in ((args.java, "java executable"),
                        (args.cp_file, "dependency classpath file"),
                        (args.driver_classes, "driver classes dir")):
        if not os.path.exists(path):
            fail("missing " + label + ": " + path)
    driver_class = os.path.join(args.driver_classes, "PdpRunner.class")
    check_file(driver_class, "compiled PdpRunner")
    for path, label in ((args.pdp_test_classes, "pdp test-classes dir"),
                        (args.pdp_classes, "pdp classes dir")):
        if not os.path.isdir(path):
            fail("missing " + label + ": " + path)
    print("[P1:run:032] backend artifacts present", flush=True)

    os.makedirs(os.path.abspath(args.work_dir), exist_ok=True)
    out_path = os.path.abspath(args.out)

    if args.mode == "original":
        # [P1-LOG-040] Step: original mode uses the frozen fixture in place.
        print("[P1:run:040] original mode: frozen fixture in place",
              flush=True)
        run_fixture_dir = fixture_dir
        request_path = os.path.join(fixture_dir, "request.xml")
    else:
        run_fixture_dir = stage_completed_fixture(
            fixture_dir, os.path.abspath(args.request),
            args.work_dir, args.world)
        request_path = os.path.abspath(args.request)
        verify_staged_fixture(fixture_dir, run_fixture_dir)

    with open(args.cp_file, "r", encoding="utf-8") as handle:
        deps_cp = handle.read().strip()
    classpath = os.pathsep.join([os.path.abspath(args.driver_classes),
                                 os.path.abspath(args.pdp_test_classes),
                                 os.path.abspath(args.pdp_classes),
                                 deps_cp])
    cmd = [args.java, "-cp", classpath, "PdpRunner",
           run_fixture_dir, request_path, out_path]
    # [P1-LOG-050] Step: invoke the native PDP driver.
    print("[P1:run:050] invoking PdpRunner mode=%s" % args.mode, flush=True)
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True,
                                   timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        fail("PdpRunner invocation failed: %s" % exc)
    # Outcome-hygiene: logs carry exit code + byte counts only, never
    # driver stdout/stderr content (which may carry Decision text).
    print("[P1:run:052] driver exit=%d stdout_bytes=%d stderr_bytes=%d"
          % (completed.returncode, len(completed.stdout or ""),
             len(completed.stderr or "")), flush=True)
    if completed.returncode != 0:
        fail("PdpRunner exit=%d (stderr withheld from logs)" %
             completed.returncode)
    if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
        fail("driver produced no response output")

    # [P1-LOG-060] Step: output confirmation.
    print("[P1:run:060] response bytes=%d out=%s"
          % (os.path.getsize(out_path), out_path), flush=True)
    if args.mode == "completed":
        # [P1-LOG-062] Step: post-invocation staged re-verification.
        # Shrinks the verify-to-use window: staged bytes re-hashed after
        # the subprocess returns; any mid-run mutation fails closed here.
        verify_staged_fixture(fixture_dir, run_fixture_dir)
        seal_outcome_capsule(repo_root, args.world, out_path)
        write_execution_lock(repo_root, args.world)

    # [P1-LOG-070] Step: run complete.
    print("[P1:run:070] native PDP execution complete", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
