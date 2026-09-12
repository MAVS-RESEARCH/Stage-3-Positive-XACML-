# PROTOCOL AMENDMENT 005 — Recursive Certification Cycles

Experiment: `PC-XACML-S3PLUS-v1` (unchanged; no fork, no new ID, no reset).
Type: procedural-generalization amendment, committed as a new commit. No
historical commit, packet, revision, adjudication, failure, seal, or
amendment is rewritten, squashed, deleted, overwritten, or concealed.
Amendments 001–004 remain historical truth.

## 1. Why

Amendment 004 proved the pattern once (failed C01–C03 panel → Phase 2D →
revision 004 → burn-in → pending C04–C06). Amendment 005 generalizes it into
a standing recursive state machine so every future valid external failure
automatically becomes the attack set for another pre-measurement hardening
cycle — while `completed_target_world_executions == 0`.

## 2. Cycle machine

`CERTIFICATION_CYCLE_001/002/003/...` under
`artifacts/audits/certification_cycles/`, managed by
`src/audit/certification_cycle.py` (`--init-cycle`, `--assess-cycle`,
`--decide-cycle`, `--handoff`, `--status`). Each cycle binds one frozen
semantic revision to one fresh three-chair panel, then resolves to exactly
one of `CERTIFICATION_PASSED`, `CERTIFICATION_FAILED_REPAIRABLE`, or
`CERTIFICATION_FAILED_IRREDUCIBLE`. Sealed cycles are immutable; new
information creates new cycles/rounds/revisions, never edits.

## 3. Sacred externals

Only genuinely fresh isolated external sessions certify — never this
session's subagents (all `NON_BLIND_DEVELOPMENTAL`, may inspect anything
because they do not certify). Auditor IDs advance monotonically and are
never reused: C01–C03 (historical), C04–C06 (next), then C07–C09,
C10–C12, etc. Panels are fixed triples evaluated whole; never seat a
fourth chair over one revision, never complete across panels, never reuse
an ID. Revision↔panel binding is explicit (`REVISION_PANELS`: rev ≤2 →
panel 1, rev 3 → none (rehearsal-only), rev 4 → panel 2, rev ≥5 → panel
index rev−3), enforced at unlock alongside record↔freeze hash binding.

## 4. Failed-panel response (automatic)

On a valid nonunanimous panel, without returning for instructions: seal the
panel (raws, verdicts, attestations, provenance, packet/prompt hashes,
revision, exec count 0), extract every non-FIXED rationale into a
certification-objection ledger, classify each (`VALID_MATERIAL`,
`VALID_NONMATERIAL`, `DUPLICATE`, `SOURCE_REFUTED`, `OUT_OF_SCOPE`,
`REVIEWER_ERROR`, `IRREDUCIBLE`, `UNRESOLVED`) by independent frozen-source
verification, and spawn the full specialist battery (H, P_R, Lambda, Atom,
provenance, completeness, alt-semantics, cross-anchor, bypass, independent
reconstruction, plus as demanded). PARTIAL alone never authorizes mutation —
only exact substantive defects do. A certifier may overturn a rehearsal
disposition; re-verify, and reopen on a real defect.

## 5. Loop discipline

Per verified defect: attack → propose → source-check → implement → test →
fresh-attacker bypass/alt-interpretation → repeat; a repair that moves the
ambiguity is a new defect. Continue `ANALYZE→SPAWN→ATTACK→MUTATE→TEST→
RED-TEAM→SEAL→FRESH-ATTACK` until `NO_UNRESOLVED_SOURCE_GROUNDED_MATERIAL_
DEFECT` or proven `IRREDUCIBLE_NATURAL_STAGE3_SEMANTIC_AMBIGUITY`. Never
`while not positive: mutate`; never "the certifier wants FIXED" as a
reason. Specimen/Worlds/targets/Q/cost/order/solver/expected-touch/K/
classification stay immutable (`NATURAL_STAGE3_INVARIANT = PASS`); only
reconstruction, proofs, evidence, provenance, completeness,
canonicalization, manifests, audit machinery, locators, and harness
correctness may change. Downstream stays closed (exec/touch/K verified 0/
uncomputed) until a fresh unanimous panel unlocks.

## 6. Revisions, rounds, burn-in, freeze, handoff

Each repairable failure: `SEMANTIC_FREEZE_REOPENED`, revision+1, versioned
hardening rounds (hashes, objections, reports, mutations, tests, red-team,
unresolved, naturalness, zero-exec proof), full burn-in (two clean sweeps +
holdout, same gates as Amendments 003–004), new freeze preserving all
priors, then STOP and generate `NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md`
(next IDs, packet/prompt paths+hashes, schema, cold-session instructions,
ingest commands, attestation/isolation rules — never history, prior
results, expected values, desired outcome, or claims). When verdicts
arrive: ingest all three; unanimous FIXED → `FINAL_CERTIFICATION_PASSED`,
unlock, close the loop to downstream-motivated mutation; else seal, assess,
and either recurse (new panel IDs) or stop negative on true irreducibility.

## 7. Claims

Full chronology disclosed (hardening → failed panels/seals → post-cert
development → new revisions → fresh panels, zero pre-cert target
execution). Never "one-shot confirmation"; always "iterative
pre-measurement hardening with fresh blind certification per operative
revision." The anti-circularity anchor stands: no downstream result was
observed during any revision or hardening cycle.
