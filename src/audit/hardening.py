"""Phase-2B-H hardening operations for PC-XACML-S3+.

Manages hardening rounds without ever touching the external specimen:
--init-round, --seal-round (invariant + exec-count + hardening tests),
--build-dev-packet (development packet for the next sweep, never final),
--assess-convergence (10-condition rule), --freeze (final bundle, then
locked), --verify-freeze, --reopen (SEMANTIC_FREEZE_REOPENED event),
--status. State lives in semantic_hardening/STATE.json. Subagent
outputs are consumed as NON_BLIND developmental input only and can
never enter certification namespaces (enforced by layout + gate code).

Step console lines use the [P2:hrd:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

BASE_SUBDIR = os.path.join("artifacts", "audits", "semantic_hardening")
IMMUTABLE_PREREG_KEYS = ("expected_touch", "expected_K", "unit_cost",
                         "freeze_order")
VOLATILE_KEYS = {"produced_utc", "sealed_utc", "probed_utc"}


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:hrd:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utcnow():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def base_dir(repo_root):
    """Return the hardening base directory."""
    return os.path.join(repo_root, *BASE_SUBDIR.split("/"))


def state_path(repo_root):
    """Return the hardening state file path."""
    return os.path.join(base_dir(repo_root), "STATE.json")


def load_state(repo_root):
    """Load hardening state, or a pristine default."""
    path = state_path(repo_root)
    if not os.path.isfile(path):
        return {"phase2_state": "SEMANTIC_HARDENING_ACTIVE", "rounds": [],
                "freeze": None, "reopens": []}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(repo_root, state):
    """Write hardening state deterministically."""
    state["updated_utc"] = utcnow()
    with open(state_path(repo_root), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")


def target_scan(repo_root):
    """Return completed/target output paths (must stay empty)."""
    hits = []
    for base in (os.path.join(repo_root, "artifacts"),
                 os.path.join(repo_root, "derived")):
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                lowered = name.lower()
                if (("target_" in lowered or "response_x_" in lowered)
                        and "blind_anchor_packet" not in dirpath
                        and "final_freeze" not in dirpath):
                    hits.append(os.path.join(dirpath, name))
    return hits


def external_snapshot(repo_root):
    """Hash every frozen external artifact + immutable prereg fields."""
    with open(os.path.join(repo_root, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    snap = {"fixture_files": {},
            "xacml_sha256": manifest["xacml"]["sha256"],
            "spec_raw": manifest["implementation_spec"]["sha256_raw"]}
    fixture = os.path.join(repo_root, "external", "authzforce", "fixture")
    for rel in ("pdp.xml", "request.xml", "response.xml",
                "policies/policy.xml"):
        snap["fixture_files"][rel] = sha256_file(
            os.path.join(fixture, rel))
    with open(os.path.join(repo_root, "prereg", "experiment.yaml"),
              encoding="utf-8") as handle:
        experiment = handle.read()
    snap["experiment_yaml_len"] = len(experiment)
    with open(os.path.join(repo_root, "prereg", "execution_inputs.json"),
              encoding="utf-8") as handle:
        snap["execution_inputs"] = json.load(handle)
    return snap


def check_invariant(repo_root, baseline):
    """NATURAL_STAGE3_INVARIANT: specimen unchanged since baseline."""
    # [P2-LOG-010] Step: verify the natural-stage-III invariant.
    print("[P2:hrd:010] checking NATURAL_STAGE3_INVARIANT", flush=True)
    live = external_snapshot(repo_root)
    problems = []
    if live["fixture_files"] != baseline.get("fixture_files"):
        problems.append("frozen fixture bytes changed")
    if live["xacml_sha256"] != baseline.get("xacml_sha256"):
        problems.append("frozen XACML bytes changed")
    if live["spec_raw"] != baseline.get("spec_raw"):
        problems.append("authoritative spec bytes changed")
    live_inputs = live.pop("execution_inputs")
    base_inputs = dict(baseline.get("execution_inputs", {}))
    for key in ("worlds", "action_interface", "freeze_order"):
        if live_inputs.get(key) != base_inputs.get(key):
            problems.append("immutable setup changed: " + key)
    with open(os.path.join(repo_root, "prereg", "experiment.yaml"),
              encoding="utf-8") as handle:
        content = handle.read()
    for key in IMMUTABLE_PREREG_KEYS:
        if key not in content:
            problems.append("prereg lost key: " + key)
    if problems:
        fail("invariant violated: %s" % problems)
    print("[P2:hrd:012] invariant holds", flush=True)
    return live


def cmd_init_round(args):
    """Create a new hardening round skeleton."""
    # [P2-LOG-020] Step: initialize a hardening round.
    print("[P2:hrd:020] initializing %s" % args.round, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    if (state.get("freeze") or {}).get("valid") and not args.allow_frozen:
        fail("semantic interface frozen; reopen first")
    round_dir = os.path.join(base_dir(repo_root), "rounds", args.round)
    for sub in ("mutations", "evidence"):
        os.makedirs(os.path.join(round_dir, sub), exist_ok=True)
    baseline = external_snapshot(repo_root)
    record = {"round_id": args.round, "sealed": False,
              "baseline_snapshot": baseline,
              "exec_count_at_seal": None}
    state["rounds"] = [r for r in state.get("rounds", [])
                       if r.get("round_id") != args.round] + [record]
    state["phase2_state"] = "SEMANTIC_HARDENING_ACTIVE"
    save_state(repo_root, state)
    print("[P2:hrd:022] round initialized", flush=True)


def run_hardening_tests(repo_root):
    """Run the deterministic hardening test files; require exit 0."""
    # [P2-LOG-030] Step: run hardening tests.
    print("[P2:hrd:030] running hardening tests", flush=True)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_hardening.py",
         "tests/test_final_certification.py", "-q"],
        cwd=repo_root, capture_output=True, text=True, timeout=600)
    print("[P2:hrd:032] pytest exit=%d" % completed.returncode, flush=True)
    if completed.returncode != 0:
        fail("hardening tests failed:\n"
             + completed.stdout[-2000:] + completed.stderr[-2000:])


def cmd_seal_round(args):
    """Seal a round: invariant + exec count + tests + record."""
    # [P2-LOG-040] Step: seal a hardening round.
    print("[P2:hrd:040] sealing %s" % args.round, flush=True)
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    rounds = [r for r in state.get("rounds", [])
              if r.get("round_id") == args.round]
    if not rounds:
        fail("round not initialized: " + args.round)
    record = rounds[0]
    live = check_invariant(repo_root, record["baseline_snapshot"])
    hits = target_scan(repo_root)
    if hits:
        fail("completed-world outputs exist: %s" % hits)
    print("[P2:hrd:042] exec count=0 confirmed", flush=True)
    run_hardening_tests(repo_root)
    record["sealed"] = True
    record["sealed_utc"] = utcnow()
    record["live_snapshot"] = live
    record["exec_count_at_seal"] = 0
    state["phase2_state"] = "SEMANTIC_HARDENING_MUTATION_REQUIRED"
    save_state(repo_root, state)
    with open(os.path.join(base_dir(repo_root), "rounds", args.round,
                           "round_seal.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:hrd:044] round sealed", flush=True)


def cmd_build_dev_packet(args):
    """Assemble a development packet for the next sweep (never final)."""
    # [P2-LOG-050] Step: build a development packet.
    print("[P2:hrd:050] building development packet", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    src_round = os.path.join(base_dir(repo_root), "rounds", args.round)
    dest = os.path.join(base_dir(repo_root), "dev_packets", args.round)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(os.path.join(repo_root, "artifacts", "audits",
                                 "blind_anchor_packet"),
                    os.path.join(dest, "base_packet"))
    evidence = os.path.join(src_round, "evidence")
    if os.path.isdir(evidence):
        shutil.copytree(evidence, os.path.join(dest, "new_evidence"))
    with open(os.path.join(dest, "DEVELOPMENT_ONLY.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write("Development packet for adversarial sweep %s.\n"
                     "NON-BLIND hardening material. NEVER a certification "
                     "packet; carries no seal.\n" % args.round)
    print("[P2:hrd:052] development packet staged", flush=True)


def load_ledger(repo_root):
    """Load the objection ledger."""
    with open(os.path.join(base_dir(repo_root), "objection_ledger.json"),
              "r", encoding="utf-8") as handle:
        return json.load(handle)


def cmd_assess_convergence(args):
    """Evaluate the 10-condition hardening convergence rule."""
    # [P2-LOG-060] Step: assess convergence.
    print("[P2:hrd:060] assessing convergence", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    ledger = load_ledger(repo_root)
    conditions = {}
    open_obs = [o for o in ledger["objections"]
                if o.get("resolution_status") == "OPEN"]
    conditions["1_no_open"] = not open_obs
    conditions["2_no_material_unresolved"] = not [
        o for o in open_obs if str(o.get("materiality", "")).startswith(
            "Material")]
    evidence_ok = True
    for record in ledger["objections"]:
        if record.get("resolution_status") == "OPEN":
            continue
        if not (record.get("files_changed") or record.get(
                "source_grounding_evidence") or record.get(
                    "independent_recheck")):
            evidence_ok = False
    conditions["3_chains_complete"] = evidence_ok and bool(
        ledger["objections"])
    packet_ok_path = os.path.join(base_dir(repo_root), "rounds",
                                  args.round, "evidence")
    required = ("request_diffs.json", "wrapper_evidence.json",
                "match_table.json", "lambda_manifest.json")
    conditions["4_packet_complete"] = all(
        os.path.isfile(os.path.join(packet_ok_path, name))
        for name in required)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_hardening.py",
         "tests/test_final_certification.py", "-q"],
        cwd=repo_root, capture_output=True, text=True, timeout=600)
    conditions["5_tests_pass"] = completed.returncode == 0
    state = load_state(repo_root)
    sealed_rounds = [r for r in state.get("rounds", []) if r.get("sealed")]
    conditions["6_hashes_unchanged"] = bool(sealed_rounds) and all(
        check_invariant_quiet(repo_root, r["baseline_snapshot"])
        for r in sealed_rounds)
    conditions["7_exec_zero"] = target_scan(repo_root) == []
    sweep_path = os.path.join(base_dir(repo_root), "reports",
                              "sweep_assessment_%s.json" % args.round)
    sweep = {}
    if os.path.isfile(sweep_path):
        with open(sweep_path, "r", encoding="utf-8") as handle:
            sweep = json.load(handle)
    conditions["8_no_new_material"] = sweep.get(
        "no_new_material_objection") is True
    conditions["9_redteam_clear"] = sweep.get("redteam_clear") is True
    conditions["10_system_unmodified"] = conditions["6_hashes_unchanged"]
    result = {"round": args.round, "conditions": conditions,
              "passed": all(conditions.values()),
              "assessed_utc": utcnow()}
    with open(os.path.join(base_dir(repo_root), "rounds", args.round,
                           "convergence.json"), "w", encoding="utf-8",
              newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:hrd:062] convergence passed=%s" % result["passed"],
          flush=True)
    if not result["passed"]:
        fail("convergence not satisfied")


def check_invariant_quiet(repo_root, baseline):
    """Return True iff the invariant holds (no exit)."""
    try:
        check_invariant(repo_root, baseline)
        return True
    except SystemExit:
        return False


FINAL_PROMPT = """# Final blind-certification prompt (frozen at semantic freeze)

You are an independent final certifier. You receive a sealed final
blind packet: frozen external source material plus final proposed
mappings for four analysis fields named H, P_R, Lambda, and Atom.
Field definitions are in the packet. You have not seen any hardening
history, earlier adjudications, expected results, or manuscript claims,
and you must not seek them.

## Task

For EACH of H, P_R, Lambda, and Atom, judge whether the FINAL proposed
mapping is justified by the FROZEN SOURCES. Evaluate THESE mappings
only. Do not invent alternates. Do not repair weak mappings.

## Verdict scale (use exactly these values)

- FIXED: frozen sources independently justify the mapping. Cite exact
  source locators (file + section/line).
- PARTIAL: partial support with a material gap. State the gap.
- AMBIGUOUS: sources do not determine the mapping. State what is
  undetermined.
- UNSUPPORTED: contradiction or no basis. State why.

## Evidence rules

1. Inspect the complete source corpus, not only the index.
2. Every FIXED verdict requires at least one exact source locator.
3. Preserve ambiguity; forced positives from insufficient material are
   the worst possible output.
4. Treat positive and negative outcomes symmetrically.
5. For Atom, distinguish the native request/response transaction from
   experiment-authored request reconstruction.
6. Never infer, guess, or reconstruct any expected result, signature,
   classification, or desired outcome.

## Output (two artifacts)

1. A verdict JSON object with shape: {"verdict_id": "AUD-C0X-verdict",
   "auditor_id": "AUD-C0X", "qualification": "COLD_MODEL_INDEPENDENT",
   "verdicts": {"H": {"status": "...", "locators": ["..."],
   "notes": "..."}, "P_R": {...}, "Lambda": {...}, "Atom": {...}},
   "attestation_hash": "<sha256 of artifact 2>",
   "declaration": "I was not supplied an expected touch set, expected "
   "freeze signature or K vector, expected classification, desired "
   "experiment outcome, or manuscript claim. I made these judgments "
   "solely from the contents of the sealed blind packet.",
   "prompt_sha256": "<frozen prompt hash from freeze record>",
   "packet_sha256": "<frozen packet hash from freeze record>",
   "isolation": {"fresh_context": true,
   "no_prior_experiment_context": true,
   "other_outputs_unavailable": true}}.
2. A SEPARATE attestation text file naming your auditor ID (e.g.
   AUD-C01), stating in your own words that you received only the
   final packet and this prompt, saw no other outputs, and share no
   context with other certifiers. Its sha256 must equal
   attestation_hash. Keep each attestation text distinct across
   certifiers.

Output the verdict JSON and the attestation text separately. No other
content.
"""

# Final-packet candidate manifest: (source path, packet relative path).
FINAL_CANDIDATES = [
    ("rounds/HARDENING_ROUND_001/evidence/h_r1.json",
     "candidates/h_r1.json"),
    ("rounds/HARDENING_ROUND_001/evidence/pr_r1.json",
     "candidates/pr_r1.json"),
    ("rounds/HARDENING_ROUND_001/evidence/atom_r1.json",
     "candidates/atom_record.json"),
    ("rounds/HARDENING_ROUND_001/evidence/env_inertness.json",
     "candidates/env_inertness.json"),
    ("rounds/HARDENING_ROUND_001/evidence/issuer_rule.json",
     "candidates/issuer_rule.json"),
    ("rounds/HARDENING_ROUND_001/evidence/canonicalization_scope.json",
     "candidates/canonicalization_scope.json"),
    ("rounds/HARDENING_ROUND_001/evidence/parser_fidelity.json",
     "candidates/parser_fidelity.json"),
    ("rounds/HARDENING_ROUND_001/evidence/match_table.json",
     "candidates/match_table.json"),
    ("rounds/HARDENING_ROUND_001/evidence/lambda_manifest.json",
     "candidates/lambda_manifest.json"),
    ("rounds/HARDENING_ROUND_001/evidence/lambda_deferral.json",
     "candidates/lambda_deferral.json"),
    ("rounds/HARDENING_ROUND_001/evidence/resolved_effective.json",
     "candidates/resolved_effective.json"),
    ("rounds/HARDENING_ROUND_001/evidence/preprocessor_resolved.json",
     "candidates/preprocessor_resolved.json"),
    ("rounds/HARDENING_ROUND_001/evidence/version_manifest.json",
     "candidates/version_manifest.json"),
    ("rounds/HARDENING_ROUND_001/evidence/policy_dir_listing.json",
     "candidates/policy_dir_listing.json"),
    ("rounds/HARDENING_ROUND_001/evidence/adequacy_extended.json",
     "candidates/adequacy_extended.json"),
    ("rounds/HARDENING_ROUND_001/evidence/invocation_record.json",
     "candidates/invocation_record.json"),
    ("rounds/HARDENING_ROUND_001/evidence/locator_map_raw_html.json",
     "candidates/locator_map.json"),
    ("rounds/HARDENING_ROUND_001/evidence/route_a_scope.json",
     "candidates/route_a_scope.json"),
    ("rounds/HARDENING_ROUND_001/evidence/request_diffs.json",
     "candidates/request_diffs.json"),
    ("rounds/HARDENING_ROUND_001/evidence/wrapper_evidence.json",
     "candidates/wrapper_evidence.json"),
    ("rounds/HARDENING_ROUND_001/evidence/rubric_supplement.md",
     "rubric_supplement.md"),
    ("rounds/HARDENING_ROUND_001/evidence/freeze_methodology.json",
     "methodology.json"),
    ("rounds/HARDENING_ROUND_001/evidence/boundary_allocation.json",
     "candidates/boundary_allocation.json"),
    ("rounds/HARDENING_ROUND_001/evidence/blindness_boundary.md",
     "blindness_boundary.md"),
    ("rounds/HARDENING_ROUND_001/evidence/repaired_bytes/"
     "request_x_permit.xml", "candidates/repaired_request_x_permit.xml"),
    ("rounds/HARDENING_ROUND_001/evidence/repaired_bytes/"
     "request_x_nonpermit.xml",
     "candidates/repaired_request_x_nonpermit.xml"),
    ("rounds/HARDENING_ROUND_001/evidence/wrapper_source/"
     "build_repaired_requests.py", "candidates/builder_source.py"),
]

FINAL_RUBRIC = """# Final certification rubric

Judge H, P_R, Lambda, Atom as FIXED / PARTIAL / AMBIGUOUS /
UNSUPPORTED against frozen sources only. Cite exact locators.
Preserve ambiguity. Never infer desired results. See the frozen
prompt for the full procedure including hash-only evidence rules,
locator resolution via the verified map, and verdict-token
separation.
"""


def cmd_freeze(args):
    """Build and seal the FINAL semantic bundle, then lock."""
    # [P2-LOG-070] Step: freeze the final semantic interface.
    print("[P2:hrd:070] freezing final semantic interface", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    state = load_state(repo_root)
    convergence_path = os.path.join(
        base_dir(repo_root), "rounds", args.round, "convergence.json")
    if not os.path.isfile(convergence_path):
        fail("no convergence assessment for " + args.round)
    with open(convergence_path, "r", encoding="utf-8") as handle:
        if not json.load(handle).get("passed"):
            fail("convergence did not pass")
    harden_base = base_dir(repo_root)
    freeze_dir_path = os.path.join(harden_base, "final_freeze")
    if os.path.isdir(freeze_dir_path):
        shutil.rmtree(freeze_dir_path)
    packet = os.path.join(freeze_dir_path, "FINAL_BLIND_PACKET")
    os.makedirs(os.path.join(packet, "candidates"))
    os.makedirs(os.path.join(packet, "corpus", "fixture", "policies"))
    corpus = (
        ("external/xacml/xacml-3.0-core-spec-cos01-en.html",
         "corpus/xacml-3.0-core-spec-cos01-en.html"),
        ("external/authzforce/fixture/pdp.xml",
         "corpus/fixture/pdp.xml"),
        ("external/authzforce/fixture/request.xml",
         "corpus/fixture/request.xml"),
        ("external/authzforce/fixture/response.xml",
         "corpus/fixture/response.xml"),
        ("external/authzforce/fixture/policies/policy.xml",
         "corpus/fixture/policies/policy.xml"),
        ("external/authzforce/RELEASE.json", "corpus/RELEASE.json"),
        ("external/authzforce/COMMIT.txt", "corpus/COMMIT.txt"),
        ("external/MANIFEST.json", "corpus/MANIFEST.json"),
    )
    for src_rel, dst_rel in corpus:
        shutil.copyfile(os.path.join(repo_root, *src_rel.split("/")),
                        os.path.join(packet, *dst_rel.split("/")))
    for src_rel, dst_rel in FINAL_CANDIDATES:
        src = os.path.join(harden_base, *src_rel.split("/"))
        if not os.path.isfile(src):
            fail("final candidate missing: " + src_rel)
        shutil.copyfile(src, os.path.join(packet, *dst_rel.split("/")))
    n4_src = os.path.join(harden_base, "rounds", args.round, "evidence",
                          "n4_excerpts")
    if os.path.isdir(n4_src):
        shutil.copytree(n4_src, os.path.join(packet, "n4_excerpts"))
    with open(os.path.join(packet, "locator_index_final.md"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write("# Final locator index: verified raw-HTML map is at "
                     "candidates/locator_map.json.\n")
    with open(os.path.join(packet, "rubric_final.md"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(FINAL_RUBRIC)
    manifest_entries = {}
    for base, _dirs, files in os.walk(packet):
        for name in files:
            path = os.path.join(base, name)
            key = os.path.relpath(path, packet).replace(os.sep, "/")
            manifest_entries[key] = sha256_file(path)
    manifest_json = json.dumps(
        {"packet_id": "PC-XACML-S3PLUS-v1-final-packet",
         "sealed_utc": utcnow(), "files": manifest_entries},
        indent=2, sort_keys=True)
    with open(os.path.join(packet, "PACKET_MANIFEST.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(manifest_json)
    packet_sha = hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()
    with open(os.path.join(packet, "PACKET_SHA256.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(packet_sha + "\n")
    print("[P2:hrd:071] final packet sealed sha=%s" % packet_sha[:16],
          flush=True)
    prompt_path = os.path.join(repo_root, "prereg",
                               "final_certification_prompt.txt")
    with open(prompt_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(FINAL_PROMPT)
    prompt_sha = sha256_file(prompt_path)
    with open(os.path.join(repo_root, "derived",
                           "anchor_ledger.json"),
              encoding="utf-8") as handle:
        envelope = json.load(handle)["anchors"]
    final_anchors = {}
    for anchor in ("H", "P_R", "Lambda", "Atom", "omega", "Q", "Succ+",
                   "c", "A_Pi"):
        record = dict(envelope[anchor])
        record["auditor_status"] = "PENDING_FINAL_CERTIFICATION"
        final_anchors[anchor] = record
    with open(os.path.join(freeze_dir_path, "FINAL_ANCHOR_LEDGER.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"ledger_id": "PC-XACML-S3PLUS-v1-final-ledger",
                   "anchors": final_anchors}, handle, indent=2,
                  sort_keys=True)
        handle.write("\n")
    with open(os.path.join(repo_root, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    interface = {
        "interface_id": "PC-XACML-S3PLUS-v1-final",
        "h_definition": "request-context multimap + absent_required + "
                        "empty_categories + environment scope (h_r1)",
        "pr_definition": "interface-scoped Match-vector coincidence "
                         "with error tokens (pr_r1)",
        "lambda_definition": "extensional component manifest with "
                             "reconstructible pre_hash (lambda_manifest)",
        "atom_definition": "NATIVE_TRANSACTION_PROVEN + "
                           "RECONSTRUCTION_AS_WRAPPER with in-packet "
                           "wrapper evidence (atom_r1)",
        "source_locators": "candidates/locator_map.json (verified)",
        "packet_sha256": packet_sha,
        "prompt_sha256": prompt_sha,
        "frozen_source_refs": {
            "authzforce_commit": manifest["authzforce"]["commit"],
            "xacml_sha256": manifest["xacml"]["sha256"],
        },
        "mutation_history": [r.get("round_id") for r in state.get(
            "rounds", []) if r.get("sealed")],
        "completed_executions": len(target_scan(repo_root)),
    }
    with open(os.path.join(freeze_dir_path, "SEMANTIC_INTERFACE_FINAL.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(interface, handle, indent=2, sort_keys=True)
        handle.write("\n")
    frozen_files = {}
    for rel in ("prereg/final_certification_prompt.txt",
                "derived/anchor_ledger.json",
                "external/MANIFEST.json",
                "external/authzforce/fixture/pdp.xml",
                "external/authzforce/fixture/policies/policy.xml",
                "external/authzforce/fixture/request.xml",
                "external/authzforce/fixture/response.xml",
                "external/xacml/xacml-3.0-core-spec-cos01-en.html",
                "PROTOCOL_AMENDMENT_001.md"):
        frozen_files[rel] = sha256_file(os.path.join(
            repo_root, *rel.split("/")))
    freeze_record = {
        "freeze_id": "PC-XACML-S3PLUS-v1-freeze",
        "frozen": True,
        "revision": len(state.get("reopens", [])) + 1,
        "round": args.round,
        "packet_sha256": packet_sha,
        "prompt_sha256": prompt_sha,
        "frozen_files": frozen_files,
        "completed_executions": len(target_scan(repo_root)),
        "superseded": False,
        "frozen_utc": utcnow(),
    }
    if freeze_record["completed_executions"] != 0:
        fail("completed executions exist; freeze forbidden")
    with open(os.path.join(freeze_dir_path, "FINAL_SEMANTIC_FREEZE.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(freeze_record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(freeze_dir_path, "SEMANTIC_INTERFACE_FROZEN"),
              "w", encoding="utf-8", newline="\n") as handle:
        handle.write("SEMANTIC_INTERFACE_FROZEN=true\n")
    state["freeze"] = {"valid": True, "round": args.round,
                       "frozen_utc": freeze_record["frozen_utc"],
                       "superseded": False,
                       "revision": freeze_record["revision"]}
    state["phase2_state"] = "FINAL_SEMANTIC_INTERFACE_FROZEN"
    save_state(repo_root, state)
    print("[P2:hrd:072] freeze marker written", flush=True)
    state["phase2_state"] = "BLOCKED_PENDING_FINAL_CERTIFICATION"
    save_state(repo_root, state)
    print("[P2:hrd:074] resting state BLOCKED_PENDING_FINAL_CERTIFICATION",
          flush=True)


def cmd_verify_freeze(args):
    """Re-verify a sealed freeze against live bytes."""
    # [P2-LOG-080] Step: verify freeze integrity.
    print("[P2:hrd:080] verifying freeze integrity", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    freeze_path = os.path.join(base_dir(repo_root), "final_freeze",
                               "FINAL_SEMANTIC_FREEZE.json")
    if not os.path.isfile(freeze_path):
        fail("no sealed freeze present")
    with open(freeze_path, "r", encoding="utf-8") as handle:
        record = json.load(handle)
    for rel, digest in record.get("frozen_files", {}).items():
        with open(os.path.join(repo_root, rel), "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        if actual != digest:
            fail("frozen file drifted: " + rel)
    print("[P2:hrd:082] freeze integrity confirmed", flush=True)


def cmd_reopen(args):
    """Record a SEMANTIC_FREEZE_REOPENED event (failure path only)."""
    # [P2-LOG-090] Step: reopen a frozen interface after failure.
    print("[P2:hrd:090] recording freeze reopen", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    if target_scan(repo_root):
        fail("target executions exist; reopen forbidden")
    state = load_state(repo_root)
    if not state.get("freeze", {}).get("valid"):
        fail("no valid freeze to reopen")
    state["freeze"]["valid"] = False
    state["freeze"]["superseded"] = True
    event = {"event": "SEMANTIC_FREEZE_REOPENED", "reason": args.reason,
             "material_evidence": args.evidence, "utc": utcnow(),
             "new_packet_required": True, "new_auditor_ids_required": True}
    state["reopens"].append(event)
    state["freeze"]["reopen_event"] = event
    state["phase2_state"] = "SEMANTIC_HARDENING_ACTIVE"
    save_state(repo_root, state)
    with open(os.path.join(base_dir(repo_root),
                           "SEMANTIC_FREEZE_REOPENED.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(event, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:hrd:092] reopen recorded", flush=True)


def cmd_status(args):
    """Print the current Phase-2 state summary."""
    # [P2-LOG-100] Step: report hardening status.
    print("[P2:hrd:100] hardening status", flush=True)
    state = load_state(args.repo_root)
    print("[P2:hrd:102] state=%s rounds=%d freeze=%s reopens=%d" % (
        state.get("phase2_state"),
        len(state.get("rounds", [])),
        (state.get("freeze") or {}).get("valid", False),
        len(state.get("reopens", []))), flush=True)


def main(argv):
    """Entry point: dispatch hardening operations."""
    # [P2-LOG-110] Step: dispatch hardening mode.
    print("[P2:hrd:110] hardening invoked", flush=True)
    parser = argparse.ArgumentParser(description="Hardening ops.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--init-round", default="")
    parser.add_argument("--allow-frozen", action="store_true")
    parser.add_argument("--seal-round", default="")
    parser.add_argument("--build-dev-packet", default="")
    parser.add_argument("--assess-convergence", default="")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--freeze-round", default="")
    parser.add_argument("--verify-freeze", action="store_true")
    parser.add_argument("--reopen", action="store_true")
    parser.add_argument("--reason", default="")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    args.round = (args.init_round or args.seal_round
                  or args.build_dev_packet or args.assess_convergence
                  or args.freeze_round)
    if args.init_round:
        cmd_init_round(args)
    elif args.seal_round:
        cmd_seal_round(args)
    elif args.build_dev_packet:
        cmd_build_dev_packet(args)
    elif args.assess_convergence:
        cmd_assess_convergence(args)
    elif args.freeze:
        cmd_freeze(args)
    elif args.verify_freeze:
        cmd_verify_freeze(args)
    elif args.reopen:
        cmd_reopen(args)
    elif args.status:
        cmd_status(args)
    else:
        fail("one hardening mode is required")


if __name__ == "__main__":
    main(sys.argv[1:])
