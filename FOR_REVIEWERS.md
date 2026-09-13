# For Reviewers

> **Start here.** This is a short map of the artifact: what it supports,
> where the final result is, and where to look if you want more detail.

## What this artifact is

This is a deterministic, source-native executable witness for a Stage-III
identification claim using OASIS XACML 3.0 with the frozen AuthzForce
engine. It supports the paper's narrow specification-witness claim only:
that the stated touch/freeze signature was observed on this frozen
system. External sources were frozen before measurement, and run outputs
are sealed artifacts verified by hash rather than regenerated claims.
It is not prevalence, production-safety, or deployment evidence.

## `WorkPlan.md` and `Path.md`

**`WorkPlan.md` = what was supposed to happen.** It is the
experiment/design specification: planned phases, gates, requirements, and
acceptance criteria.

**`Path.md` = what actually happened.** It is the execution ledger:
implementation steps, tests, failures, deviations, and gate outcomes.

You do not need to read either front-to-back. They are there for reviewers
who want to inspect the original protocol or execution history.

## Main result

Authoritative result: `artifacts/seal/FINAL_RESULT_LAUNCH.json`.

- Outcome `POSITIVE_NATIVE_STAGE3` (`launch-003`); decisions `Permit`
  (`x_permit`) and `NotApplicable` (`x_nonpermit`)
- Touch `{E}`; freeze signature `[1, INF, 1, 1, INF, INF, 1, INF]`,
  identified-set cardinality `1`, completion `COMPLETE`
- Falsification battery `13/13`
- Earlier `NATIVE_ANCHOR_INSUFFICIENT` seals (`FINAL_RESULT.json`,
  `FINAL_RESULT_CYCLE_002.json`) are historical negative evidence and are
  intentionally retained; `launch-003` is the final result

## Where to look

1. `artifacts/seal/FINAL_RESULT_LAUNCH.json` — authoritative final seal
2. `artifacts/seal/completion_space_certificate.json` — completion verdict
3. `artifacts/freezes/K_table.json` — observed freeze signature
4. `artifacts/audits/FINAL_AUDIT.md` — section-by-section audit record
5. `WorkPlan.md` — protocol specification, if deeper provenance is needed
6. `Path.md` — execution ledger, if deeper provenance is needed

## Quick verification

Reproduction is more involved than one check; see `README_REVIEW.md`.
The fastest read-only inspection is opening the authoritative seal and the
completion certificate listed above. `REVIEW_SHA256SUMS.txt` authenticates
the reviewer bytes covered in this snapshot.

## Scope / important interpretation

The later `launch-003` positive seal is authoritative. Earlier
`NATIVE_ANCHOR_INSUFFICIENT` records are retained history, not the final
answer. This artifact is a single-system witness only, not a claim about
XACML in general or about deployment safety.

## Reviewer snapshot

This is an anonymous reviewer snapshot. Detailed reproduction and
integrity information is in `README_REVIEW.md` and
`ANONYMIZATION_REPORT.json`.
