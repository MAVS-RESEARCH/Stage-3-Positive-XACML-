"""Phase-2D post-certification development harness (Amendment 004).

Manages POST_CERT_HARDENING_ROUND_NNN under
artifacts/audits/post_cert_hardening/ WITHOUT touching sealed history:
--init-round, --seal-round (invariant + exec-0 + full suite), --status.
Reuses hardening.py snapshot/invariant/scan machinery. Historical freeze,
panel, seal, and result bytes are never modified here.

Step console lines use the [P2:pc:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

BASE_SUBDIR = os.path.join("artifacts", "audits", "post_cert_hardening")


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:pc:FAIL] " + message, flush=True)
    sys.exit(code)


def utcnow():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def base_dir(repo_root):
    """Return the post-cert base directory."""
    return os.path.join(repo_root, *BASE_SUBDIR.split("/"))


def state_path(repo_root):
    """Return the post-cert state file path."""
    return os.path.join(base_dir(repo_root), "STATE.json")


def load_state(repo_root):
    """Load post-cert state, or a pristine default."""
    path = state_path(repo_root)
    if not os.path.isfile(path):
        return {"phase": "POST_CERT_DEVELOPMENT_ACTIVE", "rounds": [],
                "revision_target": 3}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(repo_root, state):
    """Write post-cert state deterministically."""
    state["updated_utc"] = utcnow()
    with open(state_path(repo_root), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")


def harden():
    """Import the hardening machinery (snapshot/invariant/scan)."""
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.abspath(__file__))))
    import hardening
    return hardening


def cmd_init_round(args):
    """Create a new post-cert round skeleton with baseline snapshot."""
    # [P2-LOG-020] Step: initialize a post-cert round.
    print("[P2:pc:020] initializing %s" % args.round, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    hardening = harden()
    state = load_state(repo_root)
    round_dir = os.path.join(base_dir(repo_root), "rounds", args.round)
    for sub in ("mutations", "evidence"):
        os.makedirs(os.path.join(round_dir, sub), exist_ok=True)
    baseline = hardening.external_snapshot(repo_root)
    record = {"round_id": args.round, "sealed": False,
              "baseline_snapshot": baseline, "exec_count_at_seal": None}
    state["rounds"] = [r for r in state.get("rounds", [])
                       if r.get("round_id") != args.round] + [record]
    save_state(repo_root, state)
    print("[P2:pc:022] round initialized", flush=True)


def cmd_seal_round(args):
    """Seal a round: invariant + exec-0 + full deterministic suite."""
    # [P2-LOG-040] Step: seal a post-cert round.
    print("[P2:pc:040] sealing %s" % args.round, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    hardening = harden()
    state = load_state(repo_root)
    rounds = [r for r in state.get("rounds", [])
              if r.get("round_id") == args.round]
    if not rounds:
        fail("round not initialized: " + args.round)
    record = rounds[0]
    live = hardening.check_invariant(repo_root,
                                     record["baseline_snapshot"])
    hits = hardening.target_scan(repo_root)
    if hits:
        fail("completed-world outputs exist: %s" % hits)
    print("[P2:pc:042] exec count=0 confirmed", flush=True)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=repo_root, capture_output=True, text=True, timeout=900)
    print("[P2:pc:044] pytest exit=%d" % completed.returncode, flush=True)
    if completed.returncode != 0:
        fail("full suite failed:\n"
             + completed.stdout[-2000:] + completed.stderr[-2000:])
    record["sealed"] = True
    record["sealed_utc"] = utcnow()
    record["live_snapshot"] = live
    record["exec_count_at_seal"] = 0
    save_state(repo_root, state)
    with open(os.path.join(base_dir(repo_root), "rounds", args.round,
                           "round_seal.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:pc:046] round sealed", flush=True)


def cmd_status(args):
    """Print post-cert development status."""
    # [P2-LOG-060] Step: report post-cert status.
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    print("[P2:pc:060] phase=%s rounds=%d" % (
        state.get("phase"), len(state.get("rounds", []))), flush=True)


def main(argv=None):
    """Entry point: dispatch post-cert operations."""
    # [P2-LOG-070] Step: dispatch post-cert mode.
    print("[P2:pc:070] post-cert hardening invoked", flush=True)
    parser = argparse.ArgumentParser(description="Post-cert hardening.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--init-round", default="")
    parser.add_argument("--seal-round", default="")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    args.round = args.init_round or args.seal_round
    if args.init_round:
        cmd_init_round(args)
    elif args.seal_round:
        cmd_seal_round(args)
    elif args.status:
        cmd_status(args)
    else:
        fail("no post-cert operation given")
    # [P2-LOG-072] Step: post-cert operation complete.
    print("[P2:pc:072] post-cert operation complete", flush=True)


if __name__ == "__main__":
    main()
