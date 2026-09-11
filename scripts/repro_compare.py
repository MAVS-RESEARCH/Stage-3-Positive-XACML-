"""Phase-2 reproduce comparator (scripts/ helper, not harness logic).

Compares recomputed Phase-2 derivation outputs against committed ones,
excluding documented volatile run-timestamps (produced_utc, sealed_utc,
probed_utc, checkpoint_sha256). All cross-artifact references are
content-addressed, so any remaining difference is a real semantic
mismatch and fails closed. Also verifies blind-packet file hashes
against PACKET_MANIFEST.json.

Usage: repro_compare.py <deriv-compare|ledger-compare|packet-verify>
  <repo-root> <repro-dir>

Step console lines use the [P2:repro:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys

DROP = {"produced_utc", "sealed_utc", "probed_utc", "checkpoint_sha256"}
DERIV_PAIRS = [
    ("policy_projection.json", "policy_projection.json"),
    ("policy_adequacy_certificate.json", "policy_adequacy_certificate.json"),
    ("route_a_probe.json", "route_a_probe.json"),
    ("h_equivalence_proof.json", "h_equivalence_proof.json"),
    ("pr_relation.json", "pr_relation.json"),
    ("lambda_record.json", "lambda_record.json"),
    ("atom_record.json", "atom_record.json"),
    ("h/H_initial.json", "H_initial.json"),
    ("h/H_permit.json", "H_permit.json"),
    ("h/H_nonpermit.json", "H_nonpermit.json"),
    ("H_provenance.json", "../artifacts/audits/H_provenance.json"),
]


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:repro:FAIL] " + message, flush=True)
    sys.exit(1)


def norm(obj):
    """Strip documented volatile run-stamp keys recursively."""
    if isinstance(obj, dict):
        return {k: norm(v) for k, v in obj.items() if k not in DROP}
    if isinstance(obj, list):
        return [norm(v) for v in obj]
    return obj


def load(path):
    """Load a JSON document."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def deriv_compare(repo_root, repro_dir):
    """Compare recomputed derivations against committed artifacts."""
    # [P2-LOG-010] Step: normalized derivation comparison.
    print("[P2:repro:010] comparing recomputed derivations", flush=True)
    bad = []
    for temp_rel, committed_name in DERIV_PAIRS:
        left = norm(load(os.path.join(repro_dir, temp_rel)))
        if temp_rel.startswith("h/"):
            right = norm(load(os.path.join(repo_root, "derived",
                                           committed_name)))
        else:
            right = norm(load(os.path.join(repo_root, "derived",
                                           committed_name)))
        if left != right:
            bad.append(temp_rel)
            print("[P2:repro:012] MISMATCH %s" % temp_rel, flush=True)
    print("[P2:repro:014] mismatches=%s" % bad, flush=True)
    if bad:
        fail("recomputation mismatch: %s" % bad)


def ledger_compare(repo_root, repro_dir):
    """Compare a rebuilt ledger against the committed ledger."""
    # [P2-LOG-020] Step: normalized ledger comparison.
    print("[P2:repro:020] comparing rebuilt ledger", flush=True)
    left = norm(load(os.path.join(repro_dir, "ledger",
                                  "anchor_ledger.json")))
    right = norm(load(os.path.join(repo_root, "derived",
                                   "anchor_ledger.json")))
    match = left == right
    print("[P2:repro:022] ledger match=%s" % match, flush=True)
    if not match:
        fail("ledger mismatch")


def packet_verify(repo_root):
    """Verify blind-packet file hashes against its manifest."""
    # [P2-LOG-030] Step: packet hash verification.
    print("[P2:repro:030] verifying blind-packet hashes", flush=True)
    packet = os.path.join(repo_root, "artifacts", "audits",
                          "blind_anchor_packet")
    manifest_path = os.path.join(packet, "PACKET_MANIFEST.json")
    if not os.path.isfile(manifest_path):
        print("[P2:repro:031] packet manifest absent", flush=True)
        fail("blind packet absent")
    manifest = load(manifest_path)
    bad = []
    for rel, digest in manifest["files"].items():
        with open(os.path.join(packet, rel), "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        if actual != digest:
            bad.append(rel)
    print("[P2:repro:032] packet mismatches=%s" % bad, flush=True)
    if bad:
        fail("packet mismatch: %s" % bad)


def main(argv):
    """Entry point: dispatch the reproduce check."""
    # [P2-LOG-040] Step: dispatch reproduce check mode.
    print("[P2:repro:040] reproduce check invoked", flush=True)
    if len(argv) < 3:
        fail("usage: repro_compare.py "
             "<deriv-compare|ledger-compare|packet-verify> "
             "<repo-root> [repro-dir]")
    mode, repo_root = argv[1], argv[2]
    repro_dir = argv[3] if len(argv) > 3 else ""
    if mode == "deriv-compare":
        deriv_compare(os.path.abspath(repo_root),
                      os.path.abspath(repro_dir))
    elif mode == "ledger-compare":
        ledger_compare(os.path.abspath(repo_root),
                       os.path.abspath(repro_dir))
    elif mode == "packet-verify":
        packet_verify(os.path.abspath(repo_root))
    else:
        fail("unknown mode: " + mode)
    # [P2-LOG-050] Step: reproduce check complete.
    print("[P2:repro:050] reproduce check complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
