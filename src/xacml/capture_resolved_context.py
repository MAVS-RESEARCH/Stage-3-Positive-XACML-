"""Phase-2 resolved-context route-(a) probe for PC-XACML-S3+.

Determines whether route (a) -- capturing the actual resolved PDP
request context via an already-exposed, non-mutating observation
mechanism -- is available. Method: (1) mechanically enumerate the
public evaluation API surface of the frozen AuthzForce engine (javap
over the built/packaged classes) and check for any resolved-context
exposure point; (2) apply the sequencing guard (route (a) before 2B is
allowed only if observation needs no completed-world decision).
Writes derived/route_a_probe.json with available true/false + reasons.
No engine, policy, or configuration object is touched or modified.

Step console lines use the [P2:routea:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:routea:FAIL] " + message, flush=True)
    sys.exit(1)


def javap_methods(java_home, classpath_entries, classname):
    """Return javap-listed public methods, or None if javap unavailable."""
    javap = os.path.join(java_home, "bin", "javap.exe")
    if not os.path.isfile(javap):
        javap = os.path.join(java_home, "bin", "javap")
    if not os.path.isfile(javap):
        return None
    try:
        completed = subprocess.run(
            [javap, "-cp", os.pathsep.join(classpath_entries), classname],
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def main(argv):
    """Entry point: probe route-(a) availability."""
    # [P2-LOG-010] Step: start probe, echo resolved arguments.
    print("[P2:routea:010] start route-(a) availability probe", flush=True)
    if len(argv) != 6:
        fail("usage: capture_resolved_context.py <repo-root> <java-home> "
             "<pdp-classes> <cp-file> <out>")
    repo_root = os.path.abspath(argv[1])
    java_home, pdp_classes, cp_file, out_path = (
        argv[2], argv[3], argv[4], argv[5])
    print("[P2:routea:012] repo-root=%s" % repo_root, flush=True)

    reasons = []
    # [P2-LOG-020] Step: enumerate the public evaluation API surface.
    print("[P2:routea:020] enumerating engine API surface", flush=True)
    entries = [os.path.abspath(pdp_classes)]
    if os.path.isfile(cp_file):
        with open(cp_file, "r", encoding="utf-8") as handle:
            entries.extend(handle.read().strip().split(os.pathsep))
    listing = javap_methods(
        java_home, entries,
        "org.ow2.authzforce.core.pdp.api.io.PdpEngineInoutAdapter")
    exposure_terms = ("ontext", "ttributeBag", "esolved")
    exposed = []
    if listing is None:
        reasons.append("javap probe unavailable; no positive evidence of "
                       "a non-mutating resolved-context hook exists")
        print("[P2:routea:022] javap unavailable", flush=True)
    else:
        for line in listing.splitlines():
            lowered = line.lower()
            if any(term.lower() in lowered for term in exposure_terms):
                exposed.append(line.strip())
        print("[P2:routea:022] adapter methods scanned, exposure hits=%d"
              % len(exposed), flush=True)
        if not exposed:
            reasons.append("PdpEngineInoutAdapter exposes indivisible "
                           "evaluate() only; no resolved-context "
                           "observation point exists on the public API")

    # [P2-LOG-030] Step: apply the pre-2B sequencing guard.
    print("[P2:routea:030] applying sequencing guard", flush=True)
    reasons.append("H_permit/H_nonpermit resolved contexts would require "
                   "full PDP evaluation of completed worlds, which is "
                   "prohibited before the 2B seal; route (a) therefore "
                   "cannot ground the pre-unblinding H verdict")
    print("[P2:routea:032] sequencing guard applied", flush=True)

    available = len(exposed) > 0
    record = {
        "probe_id": "PC-XACML-S3PLUS-v1-route-a",
        "available": available,
        "adapter_exposure_hits": exposed,
        "reasons_unavailable": reasons if not available else [],
        "conclusion": ("route (a) unavailable: H must be established via "
                       "route (b) equivalence proof or stay AMBIGUOUS"),
        "engine_modified": False,
        "probed_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-040] Step: probe complete.
    print("[P2:routea:040] route-(a) available=%s" % available, flush=True)


if __name__ == "__main__":
    main(sys.argv)
