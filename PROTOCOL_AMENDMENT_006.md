# PROTOCOL AMENDMENT 006 — Unbounded Certification Panels

Experiment: `PC-XACML-S3PLUS-v1` (unchanged; no fork, no new ID, no reset).
Type: controller-generality amendment, committed as a new commit. No
historical commit, packet, revision, adjudication, failure, seal, round,
sweep, or amendment is rewritten, squashed, deleted, overwritten,
concealed, or retroactively reinterpreted. Amendments 001–005 remain
historical truth; this amendment supersedes ONLY the finite
panel-allocation limitation (explicit C01–C12 tables, tests, and range
rejects).

## 1. Rule

Auditor IDs are unbounded: `AUD-C<N>`, N ≥ 1 (`N<100` zero-padded:
`AUD-C04`…`AUD-C09`, then `AUD-C10`, …, `AUD-C99`, `AUD-C100`, …).
Panels are consecutive triples `(3k+1, 3k+2, 3k+3)`. Allocation is
deterministic from history: next panel starts at `max_used_N + 1`. No
panel table, no finite map, no future amendment for more IDs.

## 2. Preserved invariants (regression-tested, never decaying)

Unanimity; FIXED definition; packet-only evidence; external isolation;
attestations; source grounding; specimen immutability; burn-in gates;
zero-downstream-execution; completion criteria. Chairs never reused;
panels never mixed, replayed, or tie-broken with a fourth chair; a
revision change retires its whole panel. Loop condition remains
`while verified_source_grounded_material_defect_exists and
target_execution_count == 0: repair_defect()` — never positivity-seeking.

## 3. Cycle integration

Revision↔panel binding is explicit history plus generic rule
(rev ≤2→panel 1; rev 3→none; rev 4→panel 2; rev ≥5→panel index rev−3).
Cycle records bind revision/panel/hashes/tallies/decisions. Failed panels
recurse per Amendment 004/005 machinery (objection ledgers, subagent
swarms, burn-in, refreeze, fresh panel, handoff). Target execution stays
the permanent cutoff: afterwards no semantic-reopen transition is legal.
Handoff generation covers arbitrary panels with per-chair instantiated
cold-session prompts containing only IDs and operative hashes.
