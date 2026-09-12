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