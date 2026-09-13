# PC-XACML-S3+ — Source-Native Positive Stage-III Identification Experiment

Deterministic, source-native, exact, non-statistical, fail-closed experiment package.

- Controlling specification: `IMPLEMENTATION_SPEC.md` (authoritative byte sequence; hashes in `external/MANIFEST.json` and `prereg/prereg_sha256.txt`).
- Execution plan: `WorkPlan.md`. Implementation trail: `Path.md`.
- Primary system: OASIS XACML 3.0 + AuthzForce Core Community Edition 21.2.0 (`release-21.2.0`, commit `3cc0e988e1639da48184434cd5c918102ff5b499`).
- Primary fixture: `StatusDetail.MissingAttributeDetail`.

## Layout

`prereg/` sealed preregistration. `external/` read-only frozen sources (after Phase 1). `derived/` mechanically derived inputs. `src/` harness (`provenance/`, `xacml/`, `pc/`, `audit/`). `schemas/` JSON schemas. `tests/` verification tests. `artifacts/` run outputs (`raw/`, `contracts/`, `freezes/`, `audits/`, `logs/`, `seal/`). `scripts/` phase runners.

## Reproduction

Primary environment is recorded in `artifacts/raw/environment.txt`. Phase scripts: `scripts/run_phase<N>.ps1` (authoritative on the pinned Windows host) with POSIX twins `run_phase<N>.sh`. Full replay: `scripts/reproduce_all.sh` / `reproduce_all.ps1` (uses `--reproduce` modes; sealed human-judgment artifacts verified by hash, never regenerated).

## Outcome

Exactly one top-level outcome is emitted into `artifacts/seal/FINAL_RESULT.json` (success path or `--failure-seal` path). No manuscript claims are made before the seal.
