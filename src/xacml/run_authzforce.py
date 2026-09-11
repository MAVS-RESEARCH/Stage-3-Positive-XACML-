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
        # [P1-LOG-042] Step: completed mode stages a temp fixture copy.
        print("[P1:run:042] completed mode: staging temp fixture copy",
              flush=True)
        check_file(args.request, "completed request")
        run_fixture_dir = os.path.join(os.path.abspath(args.work_dir),
                                       "fixture_" + args.world)
        if os.path.isdir(run_fixture_dir):
            shutil.rmtree(run_fixture_dir)
        os.makedirs(os.path.join(run_fixture_dir, "policies"))
        shutil.copyfile(os.path.join(fixture_dir, "pdp.xml"),
                        os.path.join(run_fixture_dir, "pdp.xml"))
        shutil.copyfile(
            os.path.join(fixture_dir, "policies", "policy.xml"),
            os.path.join(run_fixture_dir, "policies", "policy.xml"))
        request_path = os.path.abspath(args.request)
        print("[P1:run:044] staged %s" % run_fixture_dir, flush=True)

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
    print("[P1:run:052] driver stdout: %s"
          % completed.stdout.strip().splitlines()[-1]
          if completed.stdout.strip() else "[P1:run:052] driver stdout empty",
          flush=True)
    if completed.returncode != 0:
        fail("PdpRunner exit=%d stderr=%s"
             % (completed.returncode, completed.stderr.strip()[-2000:]))
    if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
        fail("driver produced no response output")

    # [P1-LOG-060] Step: output confirmation.
    print("[P1:run:060] response bytes=%d out=%s"
          % (os.path.getsize(out_path), out_path), flush=True)

    # [P1-LOG-070] Step: run complete.
    print("[P1:run:070] native PDP execution complete", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
