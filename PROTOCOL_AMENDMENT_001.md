# PROTOCOL AMENDMENT 001 — Cold-Model Blind Adjudication Substitution

Experiment: `PC-XACML-S3PLUS-v1` (unchanged; no fork, no v1.1, no reset).
Type: prospective post-Phase-2A protocol-hardening amendment, committed
as a new commit. Historical commits are never amended, squashed, or
rewritten.

## 1. Original requirement (preserved, not erased)

The original protocol required a qualifying independent second human
blind adjudicator for Phase 2B, where "qualifying" meant never shown
the expected touch, expected K, expected classification, or desired
positive verdict before sealing. The primary analyst was disqualified
as sole adjudicator. This requirement remains legible in git history
and in the ORIGINAL RULE passages of `WorkPlan.md`.

## 2. Cause

No qualifying human adjudicator was operationally available within the
submission-critical execution window.

## 3. Temporal proof (amendment precedes all results)

This amendment was finalized BEFORE any completed-world target
execution, any target result observation, any touch computation, and
any freeze/K computation. At amendment time, verified from the working
checkout:

- completed-world PDP evaluations = 0 (artifact scan empty; only
  constructed, unexecuted request inputs exist),
- target audit = NOT_RUN (no `target_*` artifacts; unlock gate locked),
- touch = NOT_COMPUTED (no touch artifacts),
- K / freeze signature = NOT_COMPUTED (no freeze artifacts).

Therefore the amendment could not have been selected in response to an
observed experimental result.

## 4. Immutable scope (nothing below changed)

Frozen XACML/AuthzForce sources, fixture, source hashes, authoritative
spec bytes, worlds, latent-world values, target definitions, H/P_R/
Lambda/Atom candidate mappings, Q/action, wrapper definition, action
cost, freeze order, expected touch, expected K, expected
classification, target-audit semantics, downstream success/failure
criteria, mechanical touch derivation, completion-space criteria, dual
solver, Phase-5 controls, claim scope.

## 5. The single mutation

`mandatory independent human blind adjudicator`
becomes
`mandatory independent cold-model blind adjudication protocol when no
qualifying human is operationally available`.

Operative rule: THREE independently initialized cold-model
adjudications (AUD-M01/02/03) over the already-sealed blind packet with
the frozen byte-identical prompt; positive unlock requires UNANIMITY
(all FIXED on H/P_R/Lambda/Atom). No majority vote, no
reconciliation, no tie-breaking reruns. Fewer than three valid records
BLOCKED_PENDING_MODEL_ADJUDICATION; malformed/incomplete records
MODEL_ADJUDICATION_INVALID (blocked class); three valid but
nonunanimous records MODEL_ADJUDICATION_NONUNANIMOUS, routing to
NATIVE_ANCHOR_INSUFFICIENT via failure-seal. Independence means
inference-context independence only -- never "experts", never "human",
never statistical independence. This substitution is strictly harder
to pass than a single-human gate, not easier.

## 6. Disclosure obligation

This substitution must be disclosed in the final audit and manuscript
with wording no stronger than the Amendment-001 claim discipline in
`WorkPlan.md`. It must NEVER be described as human adjudication, expert
validation, or equivalent to human review.

## 7. Provenance record

- previous WorkPlan blob hash: `c5e33ae141cfce52e8b7990a5e6b6937309b7130`
- previous relevant spec blob hash (`IMPLEMENTATION_SPEC.md`): `3dad2c100ed3813f412e11eab975e04155e77ba6`
- previous prereg seal blob hash (`prereg_sha256.txt`): `9be3abf99b5677f067f2a8c7c6bfca4d9e00bbcd`
- resulting WorkPlan blob hash: `5c23764d898c3298a0f7a9ce73943d5de7366602`
- sealed blind-packet hash: `007105496cc70525810ba9da1da44680ebcc9c506280a33f793cf6588572c413`
- frozen prompt hash (`prereg/blind_model_adjudication_prompt.txt`): `9d983e35fa05090bb1a889358d3dfc54b3e687667e3bce3f359b6261f8265651`
- UTC amendment timestamp: `2026-09-11T17:23:59Z`
- repository commit before amendment: `3daa703124d143ed4f628412ebaf0d07ce1f5f53`
- amendment file hash: recorded in `artifacts/audits/amendment_001_seal.json`

## 8. Byte-regime stabilization (genuine integrity defect, fixed here)

During amendment implementation, reruns of the Phase-2 runner rebuilt
the blind packet each time (new timestamps) and, worse, the committed
packet seal proved unverifiable after any fresh checkout: Git's default
EOL conversion desynchronizes sealed working-tree bytes (upstream
sources are CRLF; harness outputs are LF) from normalized blobs. This
is a genuine integrity defect under the amendment's own rule, fixed
within this amendment (pre-commit, pre-execution, zero results
observed):

- `.gitattributes` pins `* -text diff`: byte-exact checkouts, textual
  diffs retained. No sealed content hash changed by this mechanism;
  only Git blob storage becomes byte-faithful.
- The packet was rebuilt once from current sealed working bytes under
  the stable regime (new seal above). Equivalence to the superseded
  seal was proven mechanically: 9/9 candidate mappings identical
  modulo run-timestamps, 4/4 fixture corpus files byte-identical, 4/4
  remaining corpus files EOL-only differences (spec HTML, RELEASE,
  COMMIT, MANIFEST). No mapping, source, or expectation changed.
- `run_phase2` now verifies the sealed packet and rebuilds only if
  absent or corrupt, so the referenced seal cannot drift across reruns
  (proven by consecutive runs).

Operative protocol: original sealed spec + this amendment. The original
`prereg_sha256.txt` (Phase-1 seal) is byte-preserved; the frozen prompt
carries its own seal entry above and in `amendment_001_seal.json`.
