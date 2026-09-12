# PROTOCOL AMENDMENT 003 — ADDENDUM (Sections 7–17, received post-freeze)

Experiment: `PC-XACML-S3PLUS-v1` (unchanged).
This addendum records the operative rules received after REVISION_001 was
frozen. They were executed exactly as stated; this file is bound by git
commit (not by the REVISION_002 freeze hash, which seals the pre-addendum
amendment text). It will be folded into `frozen_files` at the next freeze
if any reopen occurs.

## 7. Automatic mutation loop (executed)

Holdout `REHEARSAL_SWEEP_003_HOLDOUT` returned `RS003-B01 VALID_MATERIAL`.
Therefore, autonomously and in order: REVISION_001 preserved byte-identically
(`final_freeze_REVISION_001/`, packet `4b9f6556`); `SEMANTIC_FREEZE_REOPENED`
emitted via `hardening.py --reopen`; revision incremented to 002;
`HARDENING_ROUND_003` repaired the defect with subagent implementation +
bypass red-team; all deterministic tests pass; frozen external hashes
unchanged; target executions 0; objection ledger appended (`H3-01`, `H3-02`,
88/88 valid); NEW candidate packet built; NEW freeze sealed (revision 2,
packet `fbd22e2c`); fresh sweeps `REHEARSAL_SWEEP_004/005` launched.
PARTIAL/AMBIGUOUS/UNSUPPORTED alone never triggered mutation; only
source-verified `VALID_MATERIAL` did.

## 8. Mutation boundary (observed)

Repairs touched only reconstruction/evidence/proofs/packet/provenance/
canonicalization/schemas/derivation/audit code/exposition: builder
out_dir guard, deployment-set gate module + phase-script pre-eval wiring,
listing pin, refreshed builder/wrapper/atom evidence, freeze revision
machinery. Immutable specimen untouched (release, commit, standard,
fixture, policy, PDP config/engine/semantics, worlds/values, targets,
Q meaning, cost, freeze order, solver, expected touch/K/classification,
success criteria). Zero completed target executions; touch/K/freezes
uncomputed throughout.

## 9. Anti-overfitting rule (observed)

No status-count convergence was used. Each mutation traces to an exact
substantive objection (RS003-B01 with live-code mechanism + blind-FIXED
impact). Fresh post-repair sweeps were asked "what else is wrong" with new
prompts and no prior taxonomy, not whether the previous criticism was fixed.

## 10. Two-sweep burn-in (satisfied, REVISION_002)

`REHEARSAL_SWEEP_004` (18 objections, 0 material) + `REHEARSAL_SWEEP_005`
(8 objections, 0 material): fresh instances, no mutation between, full
Panels A/B/C/D/E functions, no surviving `VALID_MATERIAL`/`UNRESOLVED`, no
new irreducible anchor objection, invariant PASS, tests PASS, exec/touch/K 0.
Second sweep received no first-sweep conclusions. `REHEARSAL_SWEEP_001/002`
count as history for superseded REVISION_001, not toward this burn-in.
Emitted: `CERTIFICATION_REHEARSAL_CONVERGED`
(`artifacts/audits/certification_rehearsal/CERTIFICATION_REHEARSAL_CONVERGED.json`).

## 11. PARTIAL vs materiality (applied)

SWEEP_001's three PARTIAL emulators were not treated as success or failure.
SWEEP_002 re-ran blind to them under the exact substantive standard; reasons
normalized one by one. Operative FIXED standard unchanged: no materially
different source-consistent interpretation remaining that could alter the
measured resource-specific interpretation under the stated interface.
Metaphysical uniqueness beyond the interface never required; rubric unchanged
by emulator conservatism. Genuine material ambiguity (RS003-B01) reopened and
hardened; verified-nonmaterial residuals recorded as such.

## 12. Holdout (executed pre-mutation; post-mutation holdout folded into 004/005)

`REHEARSAL_SWEEP_003_HOLDOUT` ran with falsification-only prompts and no
taxonomy (3 fresh agents) and found RS003-B01. Post-mutation, SWEEP_004's
red-team and SWEEP_005's falsifier served as the holdout function with new
prompts; no valid material objection survived. A further dedicated holdout
may still be run before consuming external chairs without invalidating
convergence.

## 13. Final refreeze (executed, revision 2)

REVISION_001 preserved (`final_freeze_REVISION_001/`, packet `4b9f6556`).
Operative `final_freeze/` rebuilt from `HARDENING_ROUND_003` evidence and
hash-verified (`--verify-freeze` exit 0): packet `fbd22e2c`, prompt
`4ec4f9b6e`, manifest/ledger/freeze hashes in `CERTIFICATION_REHEARSAL_CONVERGED.json`.
Packet delta vs REVISION_001 is exactly 4 refreshed files (builder copy,
wrapper evidence, listing, atom record); nothing else changed. Ancestry in
`SEMANTIC_REVISION_ANCESTRY.json`. Target executions 0, touch/K NOT_COMPUTED.
Labels: `CERTIFICATION_REHEARSAL_CONVERGED`,
`FINAL_SEMANTIC_INTERFACE_FROZEN`, `BLOCKED_PENDING_FINAL_CERTIFICATION`.

## 14. Phase 2C remains external (STOP)

No `AUD-C01/02/03` record was created from this session or any subagent.
External certification requires three fresh isolated instances receiving ONLY
the operative packet + prompt + schema — never hardening history, rehearsal
reports, prior adjudications, expected touch/K/classification, desired
outcome, manuscript claims, or session context. Only those records may unlock
the target audit.

## 15. Post-certification failure path (standing)

Preserve any failed certification completely. On a genuinely new material
defect: `SEMANTIC_FREEZE_REOPENED`, revision increment, 2B-H repair of the
grounded defect only, full rehearsal burn-in, refreeze, entirely NEW panel
with NEW auditor IDs. Never seat a fourth certifier over one frozen revision.

## 16. Irreducible stop (not triggered)

Hardening has not demonstrated unresolvable material ambiguity; every
material objection to date was repaired within the allowed boundary.
`IRREDUCIBLE_NATURAL_STAGE3_SEMANTIC_AMBIGUITY` not recorded.

## 17. Execution instruction (carried out)

Sweeps 002→003-holdout→reopen→ROUND_003→refreeze-002→004→005→converged→stop
at `BLOCKED_PENDING_FINAL_CERTIFICATION` with zero executions and no
downstream measurement observed.
