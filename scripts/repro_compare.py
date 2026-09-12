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


VOLATILE = {"produced_utc", "sealed_utc", "probed_utc",
            "checkpoint_sha256"}


def normalized_sha(path):
    """Normalized content hash per HASHING_CONVENTIONS."""
    with open(path, "r", encoding="utf-8") as handle:
        doc = json.load(handle)

    def strip(obj):
        if isinstance(obj, dict):
            return {k: strip(v) for k, v in obj.items()
                    if k not in VOLATILE}
        if isinstance(obj, list):
            return [strip(v) for v in obj]
        return obj

    return hashlib.sha256(
        json.dumps(strip(doc), sort_keys=True).encode("utf-8")).hexdigest()


def refs_verify(repo_root):
    """Verify every cross-artifact hash reference mechanically."""
    # [P2-LOG-034] Step: verify cross-artifact references.
    print("[P2:repro:034] verifying cross-artifact references", flush=True)
    derived = os.path.join(repo_root, "derived")
    problems = []

    def check(label, actual, expected):
        if actual != expected:
            problems.append(label)
            print("[P2:repro:036] REF-MISMATCH %s" % label, flush=True)

    ledger = load(os.path.join(derived, "anchor_ledger.json"))["anchors"]
    proof_path = os.path.join(derived, "h_equivalence_proof.json")
    provenance = load(os.path.join(
        repo_root, "artifacts", "audits", "H_provenance.json"))
    check("H.proof", provenance["proof"]["sha256"],
          normalized_sha(proof_path))
    for checkpoint in ("H_initial", "H_permit", "H_nonpermit"):
        check("ledger." + checkpoint,
              ledger["H"]["evidence"].get("checkpoint_sha256", {}).get(
                  checkpoint),
              normalized_sha(os.path.join(derived, checkpoint + ".json")))
    pr_relation = load(os.path.join(derived, "pr_relation.json"))
    check("PR.projection",
          pr_relation.get("projection_sha256"),
          normalized_sha(os.path.join(derived, "policy_projection.json")))
    check("PR.adequacy",
          pr_relation.get("adequacy_sha256"),
          normalized_sha(os.path.join(derived,
                                      "policy_adequacy_certificate.json")))
    ev_base = os.path.join(repo_root, "artifacts", "audits",
                           "semantic_hardening", "rounds",
                           "HARDENING_ROUND_001", "evidence")
    manifest = load(os.path.join(ev_base, "lambda_manifest.json"))
    canonical = json.dumps(
        {"components": manifest["components"],
         "exclusions": manifest["exclusions"]},
        sort_keys=True).encode("utf-8")
    check("lambda.pre_hash", manifest.get("pre_hash"),
          hashlib.sha256(canonical).hexdigest())
    wrapper = load(os.path.join(ev_base, "wrapper_evidence.json"))
    live_inputs = {
        "request.xml": os.path.join(
            repo_root, "external", "authzforce", "fixture",
            "request.xml"),
        "response.xml": os.path.join(
            repo_root, "external", "authzforce", "fixture",
            "response.xml"),
        "policy.xml": os.path.join(
            repo_root, "external", "authzforce", "fixture", "policies",
            "policy.xml"),
        "request_x_permit.xml": os.path.join(
            repo_root, "derived", "requests", "request_x_permit.xml"),
        "request_x_nonpermit.xml": os.path.join(
            repo_root, "derived", "requests", "request_x_nonpermit.xml"),
    }
    for key, path in live_inputs.items():
        with open(path, "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        check("wrapper.input." + key,
              wrapper.get("input_hashes", {}).get(key), actual)
    match_table = load(os.path.join(ev_base, "match_table.json"))
    with open(os.path.join(repo_root, "external", "authzforce",
                           "fixture", "policies", "policy.xml"),
              "rb") as handle:
        check("matchtable.policy",
              match_table.get("projection_sha256"),
              hashlib.sha256(handle.read()).hexdigest())
    ledger_full = load(os.path.join(derived, "anchor_ledger.json"))
    lambda_evidence = ledger_full.get("anchors", {}).get("Lambda", {}).get(
        "evidence", {})
    if "operative_manifest" not in lambda_evidence:
        problems.append("ledger-lambda-manifest-binding")
    with open(os.path.join(repo_root, "external", "authzforce",
                           "fixture", "response.xml"),
              "rb") as handle:
        live_response_sha = hashlib.sha256(handle.read()).hexdigest()
    check("envelope.response",
          ledger_full.get("anchors", {}).get("omega", {}).get(
              "evidence", {}).get("fixture_response_sha256"),
          live_response_sha)
    clone = os.path.join(repo_root, "external", "authzforce-repo")
    if os.path.isdir(os.path.join(clone, ".git")):
        for rel, digest in manifest["components"].get(
                "engine_sources", {}).get("files", {}).items():
            path = os.path.join(clone, *rel.split("/"))
            if not os.path.isfile(path):
                problems.append("engine-source-missing-" + rel)
                continue
            with open(path, "rb") as handle:
                check("engine." + rel, digest,
                      hashlib.sha256(handle.read()).hexdigest())
    else:
        print("[P2:repro:037] clone absent, engine hashes skipped",
              flush=True)
    with open(os.path.join(derived, "anchor_ledger.md"),
              encoding="utf-8") as handle:
        ledger_md = handle.read()
    for anchor in ("H", "P_R", "Lambda", "Atom"):
        if anchor not in ledger_md:
            problems.append("ledger-md-missing-" + anchor)
    print("[P2:repro:038] reference problems=%s" % problems, flush=True)
    if problems:
        fail("reference verification failed: %s" % problems)


def main(argv):
    """Entry point: dispatch the reproduce check."""
    # [P2-LOG-040] Step: dispatch reproduce check mode.
    print("[P2:repro:040] reproduce check invoked", flush=True)
    if len(argv) < 3:
        fail("usage: repro_compare.py "
             "<deriv-compare|ledger-compare|packet-verify|refs> "
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
    elif mode == "refs":
        refs_verify(os.path.abspath(repo_root))
    else:
        fail("unknown mode: " + mode)
    # [P2-LOG-050] Step: reproduce check complete.
    print("[P2:repro:050] reproduce check complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
