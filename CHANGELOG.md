# CHANGELOG

All notable changes to this experiment package. Post-preregistration changes to worlds, target, action interface, cost, anchor definitions, freeze order, expected signature, or success criteria require a new experiment version (`PC-XACML-S3PLUS-v2`, ...), not an unmarked patch.

## [Unreleased] — Phase 1 (planning)

- 2026-09-11: Repository created (`LICENSE` only).
- 2026-09-11: Added `WorkPlan.md` (6-phase plan) and `Path.md` (implementation trail). Docs bootstrap; no code, no execution results.
- 2026-09-11: WorkPlan audit hardening rounds 1–6 applied (spec-hash identity protocol, Phase 2B blinded adjudication, H-equivalence proof, P_R adequacy certificate, proven-Atom rule, completion-space closure certificate, sealed canary expectations, `execution_inputs.json` split, completed-execution ordering, environment pin, failure-seal path). Planning changes only; no prereg artifact existed yet, so no experiment-version change.

## [Phase 1] — 2026-09-11 — SOURCE LOCK AND NATIVE REPRODUCTION: PASS

- Locked AuthzForce `release-21.2.0` at `3cc0e988e1639da48184434cd5c918102ff5b499` (HEAD verified, tree clean); 4/4 fixture blob SHAs match; local SHA-256 manifest written.
- Froze OASIS XACML 3.0 core HTML (1257025 bytes; dynamic server content observed across retrievals, frozen copy authoritative).
- Sealed authoritative `IMPLEMENTATION_SPEC.md` (raw + LF-normalized SHA-256) and `prereg/` hashes.
- Built pinned PDP modules from source (Maven, JDK 21); compiled `PdpRunner` driver.
- Constructed both completed requests (INV-05/INV-06 asserted, unexecuted).
- Original fixture reproduces natively: Indeterminate/missing-attribute, semantic match.
- 11/11 Phase-1 tests pass; 10/10 gate boxes PASS. Bugs found by stress testing and fixed: destructive INV-05 assertion, manifest `verified_head` gap, prereg-hash test parser bug (see `Path.md` §4).
- Instantiation note: primary environment is the Windows 11 host + PowerShell (`run_phase1.ps1` authoritative, `.sh` twin); WSL2 was unavailable. No scientific content affected.

## [Phase 2] - 2026-09-11 - 2A COMPLETE, 2B PACKET SEALED, ADJUDICATION PENDING (BLOCKED, not failed)

- 2A extraction complete: 5-designator projection (canary exact), adequacy PASS (no selectors/XPath/references/providers), route (a) unavailable by javap probe + sequencing guard, route (b) equivalence VALID (4 rows), H x3, P_R relation, Lambda pre-hash, Atom NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER (pending 2B), ledger 9/9 FIXED with four PENDING_2B.
- Blind packet sealed (20 files, redaction-clean, corpus byte-identical); no qualifying human verdict exists, so `--assert-unlock` refuses (exit 4), the target audit stays locked, and zero completed-world PDP evaluations occurred.
- Content-addressed cross-artifact references (timestamps excluded from reference hashes); reproduce mode verifies derivations + ledger + packet (all match).
- Bugs found and fixed: DataType read from Attribute instead of AttributeValue (None coordinates), destructive-test path in synthetic verdict dirs, packet manifest backslash keys, adequacy manifest ordering, scanner false-positive methodology (verified via Python, not PowerShell matching).
- Status: BLOCKED_PENDING_ADJUDICATION. Unblocks on delivery of a qualifying independent blind verdict (AUD-XXX, never shown the expectations) via `--seal-verdict`, then rerun unlocks the target audit.

## [Amendment 001] - 2026-09-11 - COLD-MODEL ADJUDICATION SUBSTITUTION (prospective, pre-execution)

- No qualifying human adjudicator available in window; mandatory second-human rule replaced by mandatory three-instance cold-model unanimity protocol (`PROTOCOL_AMENDMENT_001.md` + seal). No estimand/mapping/world/target/cost/interface/expectation/criterion changed. Frozen prompt sealed; 18 adversarial gate controls green. Byte-regime stabilization included (`.gitattributes`, deterministic blob-SHA tooling, one documented packet rebuild with equivalence proof). Gate state: BLOCKED_PENDING_MODEL_ADJUDICATION; 0 completed evaluations; target audit locked.

## [Verdicts] - 2026-09-11 - THREE VALID NONUNANIMOUS RECORDS, FAILURE-SEAL ROUTE

- AUD-M01/M02/M03 ingested valid (exits 0,0,0; tallies PARTIAL/PARTIAL/UNSUPPORTED/PARTIAL, PARTIAL x4, PARTIAL/PARTIAL/FIXED/PARTIAL). Amended gate exit 3 MODEL_ADJUDICATION_NONUNANIMOUS: positive Stage-III witness NOT obtained; routes to NATIVE_ANCHOR_INSUFFICIENT via failure-seal (formal seal = Phase-6 action). Target audit never ran; Phases 3+ untouched; 0 completed PDP evaluations throughout. One non-conforming AUD-2B7 chat input preserved as correspondence, not ingested.

## [Follow-up] - 2026-09-11 - EOL BLOB NORMALIZATION (no seal changes)

- `* -text diff` byte-regime was masked by stale git stat-cache; restaged blobs byte-faithful (8 files, EOL-only diffs); blob-SHA tooling made config-independent (equal to upstream constants). Fresh-clone proof: full suite 42 passed + 1 skipped with all seals intact.

## [Hardening 2B-H] - 2026-09-12 - ROUND_002 SEALED, CONVERGENCE 10/10, FINAL FROZEN (BLOCKED_PENDING_FINAL_CERTIFICATION)

- 86/86 objections RESOLVED (0 OPEN), including Wave-4 R3-01..R3-12 and hunt O-1..O-7 as R3-13..R3-19; all `external_semantics_changed=false`, no downstream-result use.
- Working-tree hardening: XACML schema fix (Attribute-level DataType removed), builder/phase-script input binding to sealed `execution_inputs.json`, refs-mode cross-artifact verification, envelope mechanical cross-checks, ledger scope corrections; derived artifacts rehashed (timestamp-strip only).
- HARDENING_ROUND_002 sealed (invariant holds, exec 0, tests green); convergence 10/10 PASS; final blind packet frozen (`4b9f6556bd9d1360`) with frozen prompt; `--verify-freeze` confirmed. Full suite 59 passed + 1 skipped. Zero completed PDP evaluations. Awaiting AUD-C01/02/03 final certification (unanimous FIXED required).

## [Amendment 003] - 2026-09-12 - PHASE 2B-R REHEARSAL SWEEP_001, REVISION_001 PRESERVED

- Inserted developmental Phase 2B-R between candidate freeze and external certification (`PROTOCOL_AMENDMENT_003.md`): contaminated subagent Panels A–E attack the frozen candidate AS-IS; reopen only on surviving source-grounded VALID_MATERIAL. Experiment ID unchanged; no history rewritten.
- `REHEARSAL_SWEEP_001`: 8 reports ingested, 25 objections normalized (8 DUPLICATE, 17 VALID_NONMATERIAL), 0 surviving material → `SEMANTIC_FREEZE_REVISION_001_PRESERVED`, no reopen. Harness + tests added (`certification_rehearsal.py`, 4 rehearsal tests); fixed pre-existing prereg-seal gap for the frozen final prompt (freeze-record coverage). Full suite 64 passed + 1 skipped. Zero executions; state `BLOCKED_PENDING_FINAL_CERTIFICATION`.

## [Amendment 003 continued] - 2026-09-12 - SWEEP_002 CLEAN, HOLDOUT REOPENED, ROUND_003 REPAIRED, BURN-IN CONVERGED (REVISION_002)

- `REHEARSAL_SWEEP_002` (fresh battery, no SWEEP_001 preload): 27 objections (16 DUPLICATE, 7 VALID_NONMATERIAL, 3 SOURCE_REFUTED, 1 OUT_OF_SCOPE), 0 material → clean; emulator PARTIALs dispositioned without weakening FIXED.
- `REHEARSAL_SWEEP_003_HOLDOUT` (falsification-only, no taxonomy): 11 objections, 1 `VALID_MATERIAL` (RS003-B01 staged set-exclusivity + builder self-pollution vector, overturning RS002-L01) → `SEMANTIC_FREEZE_REOPENED`, revision 002.
- `HARDENING_ROUND_003`: builder out_dir guard (pre+post-create, alias-hardened) + deployment-set gate module/tests + pre-eval wiring + listing pin + refreshed evidence; ledger 88/88; suite 70+1; convergence 10/10; refreeze verified (packet `fbd22e2c`, delta exactly 4 files; REVISION_001 snapshot preserved).
- Burn-in on REVISION_002: `SWEEP_004` (18/0) + `SWEEP_005` (8/0), no mutation between → `CERTIFICATION_REHEARSAL_CONVERGED`. Full rules + execution record in `PROTOCOL_AMENDMENT_003_ADDENDUM.md`. Zero executions; touch/K uncomputed; `BLOCKED_PENDING_FINAL_CERTIFICATION`.

## [Phase 2C] - 2026-09-12 - FREEZE-DIR WIRING REPAIR + AUD-C01 VALID (1/3)

- First real ingest exposed audit-code drift: certification read the freeze at `artifacts/audits/final_freeze/` (never created) instead of `semantic_hardening/final_freeze/` (operative). Retargeted `freeze_dir()` + synthetic test roots; suite 70+1 green, freeze verification green. No semantic change, zero executions.
- `AUD-C01` ingested valid (exit 0): H/P_R/Atom FIXED, Lambda PARTIAL.
- `AUD-C02` ingested valid (exit 0): identical shape (H/P_R/Atom FIXED, Lambda PARTIAL on blind verifiability). Awaiting AUD-C03 before gate judgment; unanimity already impossible.
- `AUD-C03` ingested valid (exit 0): H/P_R FIXED, Lambda+Atom PARTIAL. Gate exit 3 NONUNANIMOUS → failure-seal: `NATIVE_ANCHOR_INSUFFICIENT` (stopped_at_phase 2, downstream NOT_RUN_BY_PROTOCOL). Sec.15: no new material defect (all gaps duplicate rehearsal dispositions) → no reopen. Target audit never runs; touch/K/freezes uncomputed; 0 executions.

## [Amendment 004] - 2026-09-12 - PHASE 2D POST-CERT DEVELOPMENT → REVISION_004 CONVERGED

- Preserved failure as `POST_CERT_HARDENING_ROUND_000` (chair files/tallies, gate, freeze/result hashes, zero-exec proof). 9-agent specialist wave + wave-2 re-attack battery.
- `HARDENING_ROUND_004/005`: Lambda reconstruction (76-file set + tree + jars + recompute tool + vector), staged pre-eval equality, engine closure, staging certificate, locator table (13/13), world binding, packet completeness (+14 candidates, engine tree), panel continuity (C04–C06, record-freeze binding, revision eligibility). Ledger 94/94.
- Holdout-008 found RS008-CE1 (classpath/extension unpinned) → second reopen → `HARDENING_ROUND_006` (classpath manifest + gates). Snapshot incident: REVISION_003 partial snapshot mishandled; recovered byte-identical with marked wrappers (see Path.md §3.20).
- Burn-in on rev004 (`156e36d7`): sweeps 009 (8/0) + 010 (7/0) + holdout 011 (3/0), no mutation between → `POST_CERTIFICATION_HARDENING_CONVERGED`. Suite 87+1, freeze verified, 0 executions, touch/K uncomputed. State `BLOCKED_PENDING_NEW_FINAL_CERTIFICATION` (AUD-C04/C05/C06).

## [Amendment 005] - 2026-09-12 - RECURSIVE CERTIFICATION CYCLES, HANDOFF GENERATED

- Generic cycle machine (`certification_cycle.py` + schema + 6 tests): sealed CYCLE_001 (rev002/C01–C03, FAILED_REPAIRABLE, consumed by Phase 2D) + open CYCLE_002 (rev004/C04–C06); assess/decide consistency gates; panels through C10–C12 with revision binding, record-freeze binding, fourth-chair refusal.
- Adversarial review found 8 machinery holes; all repaired + tested. Independent rev004 re-verification 7/7 CONFIRM.
- `NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md` generated (C04–C06, operative hashes, cold-session + ingest instructions, leak-scanned). Suite 95+1, freeze verified, 0 executions. STOP at `FINAL_SEMANTIC_INTERFACE_FROZEN` + `BLOCKED_PENDING_NEW_FINAL_CERTIFICATION`.

## [Cycle 002] - 2026-09-12 - SECOND PANEL NONUNANIMOUS → TERMINAL NEGATIVE STOP

- AUD-C04/C05/C06 all valid: H/P_R FIXED ×3, Lambda PARTIAL ×3, Atom 2×FIXED/1×PARTIAL. Gate exit 3.
- Defect ledger: 0 material, 0 unresolved (duplicates of known polish, by-design PENDING_TARGET items, overturn check negative). No pre-measurement revision can advance unanimity → `CERTIFICATION_FAILED_IRREDUCIBLE`, second seal `FINAL_RESULT_CYCLE_002.json` (`NATIVE_ANCHOR_INSUFFICIENT`). Historical seal untouched. Target audit never runs; 0 executions; touch/K/freezes uncomputed. Suite green, freeze verified.

## [Amendment 006] - 2026-09-12 - UNBOUNDED PANELS, PER-CHAIR HANDOFF

- Finite C01–C12 tables removed: generic `AUD-C<N>` chairs, consecutive-triple panels, `max_used+1` allocator, revision map + rev≥5 fallback, alias normalization, NON_BLIND-marker refusal, generalized rehearsal guards, per-chair instantiated handoff prompts.
- Adversarial review: 15 findings, all repaired + tested (crashes, validation, binding, advancement, coercion, stale messages). Suite 118+1, freeze verified, frozen bytes unchanged. STOP at `FINAL_SEMANTIC_INTERFACE_FROZEN` + `BLOCKED_PENDING_NEW_FINAL_CERTIFICATION` (AUD-C04/C05/C06).

## 2026-09-12 -- Protocol Amendment 007 split-gate development + launch freeze (pre-execution, zero target runs)

- Recovered interrupted Amendment-007 tree at <AUTHOR_REPO_COMMIT_030>; verified seals/specimen/zero-exec intact.
- Hostile developmental waves (deferral/Lambda/quarantine/state-machine/Atom + burn-in A/B + holdout); all VALID_MATERIAL repaired fail-closed (judge coverage+revocation, parser content-allowlist, runner authorization binding, cert lock+attestation binding, verifier hex+content rejection, lineage+manifest refresh, freeze self-manifest fix, env binding, 4 new tests).
- PROTOCOL_AMENDMENT_007.md full operative SS0-19; registry 6 obligations frozen; launch packet db661dd7 + prompt 251f7e58 + registry 12a46820 sealed and verified; suite 139+1 green.
- State BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION; handoff NEXT_EXTERNAL_LAUNCH_HANDOFF.md (AUD-L01/02/03). No target execution, no touch, no K.

## 2026-09-12 -- Launch-001 failed (L01-03 BLOCKED), repaired transparently, launch-002 frozen for L04-06 (pre-execution, zero target runs)

- Ingest 0/3 VALID (attestation binding/cross-read/paste-divergence); merits Lambda 3xPARTIAL packet-internal (driver staleness, pom collision, coordinates-only deps); launch-001 preserved.
- launch_freeze.py: staged-manifest rebind+recompute, distinct poms, 145-jar dependency content, 11-copy currency, freeze-code pinning, revision support, verify composite/drivers/lineage.
- Launch-002 packet a75ee3b05, staged pre 5ecdd192, panel AUD-L04/05/06; suite 141+1 green; handoff NEXT_EXTERNAL_LAUNCH_HANDOFF_L04-L06.md.
- State BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION (launch-002). No target execution, no touch, no K.

## 2026-09-12 -- Launch-002 failed (L04-06 BLOCKED), five repairs, launch-003 frozen for L07-09 (pre-execution, zero target runs)

- Ingest 0/3 VALID (binding/paste); merits Lambda 2xPARTIAL + 3xIMPROPER (dep opacity, remap, recompute subset, prose producers); launch-002 preserved.
- Repairs R7-12..16: file-hash dep binding, path_remap, extended recompute + builder lineage, JSONL chronology, --hash-cp, registry scoping; tests V60-V68.
- Launch-003 packet 8e23901d, staged pre 194fcbbe, panel AUD-L07/08/09; suite 146+1 green; handoff NEXT_EXTERNAL_LAUNCH_HANDOFF_L07-L09.md.
- State BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION (launch-003). No target execution, no touch, no K.

## 2026-09-12 -- Launch-003 unanimous PASS + TARGET_EXECUTION_AUTHORIZED (pre-execution, zero target runs at authorization)

- Ingest 3/3 VALID: AUD-L07 valid (ingested 16:27:03Z), AUD-L09 valid (16:27:09Z), AUD-L08 valid (17:52:07Z) after two procedural INVALID attempts preserved in the operator ingest record (binding/format; not merits reversals). All three verdicts unanimously FIXED on H/P_R/Lambda/Atom with all six obligations LEGITIMATELY_DEFERRED; packet 8e23901d and prompt 251f7e58 match the freeze on every record.
- Authorization sealed as `artifacts/audits/launch/TARGET_EXECUTION_AUTHORIZED.json` (17:52:10Z), bound to packet/prompt/registry hashes under the Amendment-007 unanimous rule. Launch-001 (L01-03 BLOCKED) and launch-002 (L04-06 BLOCKED) preserved as `launch_packet_rev001/` + `LAUNCH_FREEZE_rev001.json` and `launch_packet_rev002/` + `LAUNCH_FREEZE_rev002.json`. No target execution had occurred at authorization; point of no return not yet crossed.

## 2026-09-12 -- Phase-2F controlled execution + dual conformance + outcome opening (post-authorization)

- Point of no return sealed by `artifacts/seal/TARGET_EXECUTION_LOCK.json` (worlds x_nonpermit/x_permit; updated 18:31:51Z). Exactly one native PDP cycle per world; hash-only capsules sealed before conformance (x_permit 160 bytes 87f6336c / 18:31:45Z; x_nonpermit 167 bytes 67961314 / 18:31:51Z).
- Dual mechanical conformance: `RUN_CONFORMANCE_PASS.json` (judged 18:35:10Z, RUN_CONFORMANCE_PASSED; verifiers A/B agree; coverage equals the frozen registry).
- Outcome opening (sole Decision source downstream): `quarantine/outcome_opening.json` records x_permit Permit and x_nonpermit NotApplicable (match true, conformance passed), matching preregistered N02/N03 classes from `tests/test_completed_world_decisions.py`.

## 2026-09-12 -- Phase 3 mechanical contract + touch sealed (post-execution)

- Contract `artifacts/contracts/pc_xacml_primary.contract.json` (produced 18:46:17Z; sha 7510e78d) compiled from observed PDP responses via the target-semantics rule; S0 open by heterogeneity, both successors closed singletons; no touch field in inputs.
- Touch `artifacts/contracts/touch.json` (sha 123672b9) mechanically derived as q_supply_missing_attribute [E] with dual-implementation byte-agreement; no-manual-label audit passes. Manifest `artifacts/seal/phase3_manifest.json` binds contract/touch/ledger/manifest/inputs.

## 2026-09-12 -- Phase 4 exact freezes + completion certificate sealed

- Eight rows F000/F100/F010/F001/F110/F101/F011/F111 plus `K_table.json` (produced 18:46:29Z; sha d8007ab7) record K [1, INF, 1, 1, INF, INF, 1, INF] with per-row contract binding; dual-solver agreement holds; nontrivial true.
- Completion certificate `artifacts/seal/completion_space_certificate.json` (sha 5842ab0f; COMPLETE; free fields 0) authorizes `identified_set.json` cardinality 1 (sha dee7864a).

## 2026-09-12 -- Phase 5 falsification battery 13/13 PASS

- Corruption 5/5 detected; MustBePresent/wrong-category/wrong-datatype/irrelevant-attribute canaries match sealed expectations; whitespace/order/rename preserve H/P_R/Lambda/T/K; interface split refused from T3 invariance; cost sweep 0.5/2/10 preserves structure; negative-world sweep preserves open fiber and E-class; four ablations each refuse positive; label injection detected; leakage graph passes; clean reproduction byte-matches (touch and K). Frozen externals untouched throughout.

## 2026-09-12 -- Phase 6 positive seal (this entry)

- Worlds, target, action interface, cost, anchor definitions, freeze order, expected signature, and success criteria unchanged since prereg; same experiment version `PC-XACML-S3PLUS-v1` (no fork, no v1.1, no reset).
- New positive seal `artifacts/seal/FINAL_RESULT_LAUNCH.json` (POSITIVE_NATIVE_STAGE3; observed values only) written as a separate file; historical `artifacts/seal/FINAL_RESULT.json` (CYCLE_001) and `artifacts/seal/FINAL_RESULT_CYCLE_002.json` (CYCLE_002) remain untouched.
- Added `artifacts/audits/FINAL_AUDIT.md` (15 required sections plus checklist and binding), repo-root `MANIFEST.sha256`, deterministic `PC-XACML-S3PLUS-v1.tar.gz` + `.sha256`, and `scripts/run_phase6.sh` / `scripts/run_phase6.ps1` (default success-seal; `--failure-seal` mode for stopped experiments).
- Full suite green at seal (193 passed, 6 skipped). No post-seal semantic change permitted; any such change requires a new experiment version.
