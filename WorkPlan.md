# PC-XACML-S3+ WorkPlan

## Source Authority

This WorkPlan is grounded in exactly one controlling document (verified in two identical copies):

1. `PC_STAGE3_POSITIVE_XACML_IMPLEMENTATION_SPEC.md`
   - Local copy: `C:\Users\Saif malik\Downloads\PC_STAGE3_POSITIVE_XACML_IMPLEMENTATION_SPEC.md` — 1663 lines, 9074 words, 66890 chars.
   - In-chat copy supplied in the user request — text-identical in all normative sections (verified by section-head diff: 27 top-level sections `0`–`26`, 6 implementation phases, identical pinned SHAs, identical freeze table).
   - Document type: frozen implementation specification / preregistration blueprint.
   - Experiment short name: `PC-XACML-S3+`, experiment ID: `PC-XACML-S3PLUS-v1`.
   - Target paper: Perceptive Closure, post-D33 external-positive Stage-III validation.
   - Primary system: OASIS XACML 3.0 + AuthzForce Core Community Edition 21.2.0, tag `release-21.2.0`, commit `3cc0e988e1639da48184434cd5c918102ff5b499`.
   - Primary fixture: `pdp-testutils/src/test/resources/conformance/others/StatusDetail.MissingAttributeDetail/`.
   - Style: deterministic, source-native, exact, non-statistical, fail-closed.
   - Core rule: if the external system does not independently justify H / P_R / Lambda / Atom, emit `NATIVE_ANCHOR_INSUFFICIENT`; never repair by choosing favorable semantics post-hoc.

The user instruction "study both the docs" was resolved as: (a) the in-chat spec text + (b) the Downloads file copy. Both were read (full head list extracted via `Select-String "^#+ "`); no second distinct spec exists. The target repo `https://github.com/MAVS-RESEARCH/Stage-3-Positive-XACML-` was cloned and inspected: it contained only `LICENSE` (commit `a4d4bfc Initial commit`), so there were no prior results to migrate and nothing to clear beyond confirming emptiness (see `Path.md` § Current Repository State).

When this WorkPlan adds operational detail (file names, function signatures, test commands), it never relaxes the spec. On any conflict, the spec wins and this plan must be amended with a new experiment version per spec §6.3.

## Mission

Answer one narrow reviewer-critical question (spec §0, §3):

> Can an independently engineered authorization system and its pre-existing governing specification/configuration naturally supply enough semantic information for PC to point-identify a nontrivial resource-freezing signature, without PC inventing the authorization-admission, certificate-representation, authority, or action/checkpoint boundaries after observing the result?

Formal question: let `Omega_ext` = frozen XACML standard + AuthzForce release/config + policy + original request + expected response; `Omega_exp` = preregistered wrapper (two latent worlds, unit-cost repair action, freeze-mask order, exact solver conventions, recording format); `Omega_star = Omega_ext ∪ Omega_exp`. Does `Omega_star` fix the PC semantic interface so that `|K_{Pi,Omega_star}| = 1` with a nontrivial all-freeze signature, without manual E/R/A labels?

Preregistered positive prediction (must be allowed to fail):

```text
T(q_supply_missing_attribute) = {E}
K_Pi = [1, INF, 1, 1, INF, INF, 1, INF]
|K_{Pi,Omega_star}| = 1, classification = STRUCTURAL_E_TOUCH_DEPENDENCE
```

Success is only `POSITIVE_NATIVE_STAGE3` if all 10 conditions in spec §8.1 hold. Any anchor ambiguity → `NATIVE_ANCHOR_INSUFFICIENT`. This is a source-native positive witness for D33 Stage III, paired with Polaris (natural negative) and PC-TAU (controlled geometry); it is not a prevalence, benchmark-superiority, safety, causal, or mechanism claim (spec §1.3–1.5, §17–§19).

## Scope Boundary

In scope (everything in spec §§2–26):

- Pin AuthzForce at `release-21.2.0` / `3cc0e988e...`; freeze the 4 fixture files + OASIS XACML 3.0 core HTML; SHA-256 everything; reproduce the original `Indeterminate/missing-attribute` fixture; build the 2 completed world requests; seal `prereg/`.
- Anchor audit for H, P_R, Lambda, Atom, omega, Q, Succ+, c, A_Pi, terminal/open semantics with N1–N4/X provenance and FIXED-or-fail gate.
- Mechanical contract compilation (no touch field in input schema), mechanical `derive_touch` from extensional pre/post comparison, independent touch reimplementation, no-manual-label static audit.
- Exact exhaustive 8-freeze evaluation (F000,F100,F010,F001,F110,F101,F011,F111), independent solver, singleton + nontriviality records.
- Full Phase-5 falsification battery (§5.1–§5.13): hash-corruption, MustBePresent/wrong-category/wrong-datatype/irrelevant-attribute canaries, interface-preserving perturbations, interface-changing OUT_OF_SCOPE control, cost sweep (0.5/2/10), negative-world sweep, 4 anchor ablations, manual-label injection, leakage audit, clean reproduction.
- Seal: `FINAL_RESULT.json` populated from observed artifacts (never forced), `MANIFEST.sha256`, `CHANGELOG.md`, `FINAL_AUDIT.md`, deterministic `PC-XACML-S3PLUS-v1.tar.gz` + `.sha256`, claim wording locked to outcome.

Out of scope / forbidden:

- No third latent world; no redefinition of `x_permit`/`x_nonpermit` values or `Permit`/`NotApplicable` targets after observing PDP output.
- No policy / `pdp.xml` / engine / preprocessor / provider / identifier / middleware modification (spec §4.4, INV-01–02).
- No manual `{"touch": ["E"]}` or equivalent in any input; expected-signature file excluded from all computation imports (INV-15).
- No freeze that edits action internals or fabricates partial subactions (INV-12–13).
- No multi-system survey, no Polaris reuse as positive, no PC-supplied governance middleware (that would be PC-TAU, not this experiment).
- No manuscript edits before `FINAL_RESULT.json` seal; no forbidden claim strings from §18.2 even on success.
- No statistics (p-values, CIs, bootstraps) — analysis is deterministic exact enumeration (spec §16).

## No-Model-Training Policy and Anti-Overfitting Contract

There are no trainable ML models in this experiment. The decision function is the frozen external AuthzForce PDP + frozen policy; the PC harness is deterministic rule code (canonicalization, parser, exact solver). Therefore:

- No training run, no hyperparameter tuning, no validation-based selection exists. `prereg/expected_signature.json` + `prereg/experiment.yaml` play the role of the "training benchmark": they are sealed in Phase 1 before any touch/K computation and are never imported by computation modules.
- The "brutally tested on ENTIRELY different benchmarks" requirement is satisfied by the Phase-5 battery, which by construction uses artifacts disjoint from the sealed expectation:
  - Corruption benchmarks: 4/4 fixture byte-mutations + spec-file mutation (hash gate, not K gate).
  - Semantic canaries: `MustBePresent` removed/changed, wrong Category, wrong DataType, irrelevant extra attribute — none reuse the primary `x_permit`/`x_nonpermit` pair as success criteria; they assert rejection / projection-stability behavior.
  - Perturbation benchmarks: whitespace / order / formatting / path-relocation variants assert H/P_R/Lambda/T/K invariance under semantics-preserving transforms.
  - Negative-control interface benchmark: explicitly labeled `OUT_OF_SCOPE_INTERFACE_CHANGE` split (`q_construct_attribute` + `q_submit_request`) asserting `INTERFACE_CHANGED / THEOREM3_INVARIANCE_NOT_APPLICABLE`, never compared as a T3-equivalent K.
  - Cost benchmarks: 0.5 / 2 / 10 assert structural E-dependence invariance (finite entries rescale, E-freezes stay INF).
  - Negative-world benchmarks: preregistered `wrong-answer-1`, `wrong-answer-2` (plus any further strings frozen before execution) assert continued `NotApplicable` and open-fiber preservation without replacing primary `x_nonpermit`.
  - Ablation benchmarks: 4 single-anchor deletions each must kill `POSITIVE_NATIVE_STAGE3` eligibility.
  - Leakage benchmark: dependency-graph proof that `expected_signature.json` is read only by final comparison.
  - Clean-reproduction benchmark: fresh checkout rerun must yield byte-identical canonical result (modulo excluded run metadata).
- Overfitting analogues and defenses: post-hoc boundary selection (T1) → ledger frozen before touch; manual labeling (T2) → static scan + independent derivation; middleware semantics (T3) → immutability + Lambda hash equality; cost cherry-pick (T4) → cost sweep; hidden authority (T5) → Lambda hash; string-presence shortcut (T6) → category/datatype canaries; atomicity laundering (T7) → interface-change control; leakage (T8) → dependency audit; drift (T9) → pinned commit + re-verify every phase; relabeling (T10) → preregistered targets + abort.

## Repository Contract

Build the fresh repo exactly per spec §9 (names fixed; no extra result dirs at top level). `external/` is read-only after Phase 1. `expected_signature.json` lives only in `prereg/` and is never on a computation import path.

```text
PC-XACML-StageIII/  (this repo: Stage-3-Positive-XACML-)
├── README.md | LICENSE | IMPLEMENTATION_SPEC.md | CHANGELOG.md
├── pyproject.toml | requirements-lock.txt | .gitignore
├── WorkPlan.md | Path.md
├── prereg/experiment.yaml, expected_signature.json, allowed_claims.md, prereg_sha256.txt
├── external/MANIFEST.json, xacml/xacml-3.0-core-spec-cos01-en.html + SHA256SUMS,
│   └── authzforce/RELEASE.json, COMMIT.txt, fixture/pdp.xml, request.xml, response.xml,
│       policies/policy.xml, SHA256SUMS
├── derived/requests/request_x_permit.xml, request_x_nonpermit.xml,
│   policy_projection.json, anchor_ledger.json/.md, canonical_external_manifest.json
├── src/provenance/lock_sources.py, verify_sources.py
├── src/xacml/canonicalize_request.py, parse_policy.py, build_repaired_requests.py,
│   run_authzforce.py, parse_response.py
├── src/pc/models.py, derive_H.py, derive_PR.py, derive_Lambda.py, derive_atom.py,
│   derive_touch.py, compile_contract.py, solve_freezes.py
├── src/audit/independent_touch.py, independent_solver.py, check_no_manual_labels.py,
│   check_anchor_completeness.py, build_audit_report.py
├── schemas/anchor_ledger.schema.json, contract.schema.json, freeze_row.schema.json,
│   final_result.schema.json
├── tests/test_source_hashes.py, test_original_fixture.py, test_completed_world_decisions.py,
│   test_policy_projection.py, test_anchor_completeness.py, test_no_manual_touch_labels.py,
│   test_touch_derivation.py, test_all_freezes.py, test_cost_robustness.py,
│   test_interface_preserving_mutations.py, test_anchor_ablation.py,
│   test_parser_corruptions.py, test_clean_reproduction.py
├── artifacts/raw/, contracts/, freezes/, audits/, logs/, seal/
└── scripts/run_phase{1,2,3,4,5,6}.sh, reproduce_all.sh
```

Environment (spec §1.4-phase1): JDK 17 LTS+ (pin exact build for primary run), AuthzForce 21.2.0, one pinned Python minor for harness, locked XML parser version, recorded OS/build. `requirements-lock.txt` + `artifacts/raw/environment.txt` (`java -version`, `python --version`, `git --version`, pip freeze). No silent upgrades after prereg seal.

Per-phase discipline (spec §20): `SOURCE CHECK → DERIVE → ASSERT → SAVE RAW → INDEPENDENT CHECK → GATE → COMMIT`. Phase scripts are thin wrappers; final `reproduce_all.sh` replays them but raw per-phase artifacts remain.

Logging (spec §21): every execution record carries experiment_id, phase, UTC timestamp, experiment-repo commit, AuthzForce commit, external-manifest hash, prereg hash, contract hash if available, command, exit code, stdout/stderr hashes, output artifact hashes; append-only, never overwrite (deterministic run IDs + index).

AI assistance (spec §22): boilerplate/debugging allowed; AI may not choose anchors; every anchor cites external evidence; AI is analyst-suggestion not authority; post-Phase-2 AI anchor changes need new version/mutation record; expected-result files never given to anchor-inference agents except labeled adversarial review; final audit states AI usage.

---

## Phase 1 — External Source Lock and Native Reproduction

Scope: prove the experiment starts from a stable, independently authored artifact reproducible before PC touches it. Covers spec §§2, 4.1–4.2 (worlds/targets predeclared), 9–10.1, 11-Phase1, 14 rows S01–S03/N01, 15 INV-01–04/16–17, 23 STOP-01/10. No semantics, no touch, no K in this phase; first commit contains this spec + plans only, zero PC results from AuthzForce execution.

Files to make:

- `IMPLEMENTATION_SPEC.md` (verbatim copy of controlling spec), `README.md`, `CHANGELOG.md`, `.gitignore`, `pyproject.toml`, `requirements-lock.txt`.
- `external/authzforce/RELEASE.json` (tag/commit/URL), `COMMIT.txt` (`git rev-parse HEAD`), `fixture/{pdp.xml,request.xml,response.xml,policies/policy.xml}`, `SHA256SUMS` (local SHA-256 + upstream Git blob SHAs: `pdp.xml 01a0adc080253afc2c523a0b8e58e8578e8275eb`, `request.xml ff6582db3d9c2bd00ae87e69279c23057b14a47a`, `response.xml 835d483564a1c3ab052e0dbbd24c2258e5a5c295`, `policy.xml 698af364ba2db79534cc654765baaed4d1c8f867`).
- `external/xacml/xacml-3.0-core-spec-cos01-en.html` + `SHA256SUMS` (URL, retrieval timestamp, title/version, anchored sections: request context, Attributes/Attribute/AttributeValue, AttributeDesignator Category/Id/DataType/Issuer, §7.3.5 retrieval, MustBePresent, PDP/context-handler/PEP architecture, decision/status).
- `external/MANIFEST.json` + `derived/canonical_external_manifest.json`.
- `derived/requests/request_x_permit.xml`, `request_x_nonpermit.xml`.
- `artifacts/raw/environment.txt`, `original_response_actual.xml`, `original_response_expected.xml`, `original_response_comparison.json`.
- `prereg/experiment.yaml` (exact minimum fields per §10.1: worlds with `riddle me this`→Permit / `not-riddle-me-this`→NotApplicable, action `q_supply_missing_attribute` cost 1, freeze order, expected touch `[E]`, expected K, abort/allow flags), `expected_signature.json`, `allowed_claims.md` (verbatim §18 ladder), `prereg_sha256.txt`.
- `scripts/run_phase1.sh`, `tests/test_source_hashes.py`, `tests/test_original_fixture.py`.

Code to produce and how to code:

- `src/provenance/lock_sources.py`: clones `https://github.com/authzforce/core` to temp, checks out `3cc0e988e...`, asserts `rev-parse HEAD` equality + `status --porcelain` clean, copies only the 4 fixture files, computes Git blob SHA (`git hash-object`) + file SHA-256, downloads XACML HTML (record URL/timestamp), writes MANIFEST + SHA256SUMS. Pure stdlib + git subprocess; deterministic; fails closed on any mismatch.
- `src/provenance/verify_sources.py`: re-hashes every external file, re-checks blob SHAs and spec hash, re-asserts HEAD/clean; exit nonzero on drift; invoked at the top of every later phase script (STOP-10; full stop set STOP-01–STOP-12 enforced across phases, see gates).
- `src/xacml/build_repaired_requests.py`: parses `request.xml` with a locked parser (lxml pinned), locates subject Attributes, inserts exactly one `Attribute` with Category `access-subject`, AttributeId `...:some-attribute`, DataType `xsd:string`, value per world; asserts repaired-minus-original diff = single-Attribute addition (INV-05) and inter-world diff = AttributeValue only (INV-06); never hardcode a different category — read it from frozen MissingAttributeDetail/policy.
- `src/xacml/run_authzforce.py`: thin subprocess wrapper pinning JDK + AuthzForce 21.2.0 jars + `pdp.xml`/policy paths; runs original + both completed requests; captures stdout/stderr + exit codes into `artifacts/raw/`; no authorization logic in wrapper.
- `src/xacml/parse_response.py`: semantic XML comparison (canonicalize with exclusive C14N, compare Decision/StatusCode/MissingAttributeDetail triple, ignore whitespace) → `original_response_comparison.json` with `semantic_match: bool`.
- Tests: `test_source_hashes` (S01–S03: commit, blob, local hashes), `test_original_fixture` (N01: Indeterminate + `missing-attribute` + exact AttributeId/Category/DataType). Gate checklist per Phase-1 gate (8 boxes); failure → `SOURCE_REPRODUCTION_FAIL`, stop (STOP-01).

Benchmarks: no models trained; nothing to anti-overfit in ML sense. Phase-1 "training-equivalent" seal is `prereg_sha256.txt`; disjointness is temporal (sealed before Phases 2–4 read PDP semantics for anchoring).

## Phase 2 — Source-Native Semantic Anchor Audit

Scope: the most important phase — decide whether external semantics actually fix H, P_R, Lambda, Atom (plus omega/Q/Succ+/c/A_Pi/terminal-open) before any touch/K is computed (spec §§4–5, 12). No E/R/A/touch/Delta/freeze values may appear in extraction code. Any anchor needing "we choose to regard…" without N1/N2/N3 → `AMBIGUOUS` → top-level `NATIVE_ANCHOR_INSUFFICIENT`, stop positive claim (spec §2.8).

Files to make:

- `derived/policy_projection.json` (every reachable AttributeDesignator: RuleId/path, Category, AttributeId, DataType, Issuer, MustBePresent, match-function context) + `derived/H_initial.json`, `H_permit.json`, `H_nonpermit.json`.
- `derived/anchor_ledger.json` + `anchor_ledger.md` (one record per anchor per §10.2: anchor_id, pc_field, extensional definition, source_class, source_documents[{id, locator, artifact_sha256}], derivation_module, manual_semantic_choice_required, ambiguity_status, auditor_status).
- `artifacts/audits/H_provenance.json`, Lambda pre/post hashes, atom record (`atom_id: xacml-request-transaction`, pre/post checkpoints, `decomposable_in_primary_interface: false`), target audit outputs (raw PDP responses for both worlds).
- `schemas/anchor_ledger.schema.json`; `tests/test_policy_projection.py`, `test_anchor_completeness.py`; `scripts/run_phase2.sh`.

Code to produce and how to code:

- `src/xacml/parse_policy.py`: stdlib/lxml walker over `policy.xml` extracting all `AttributeDesignator` nodes with full coordinates; no handwritten allowlist (INV-07); canary assert: exactly finds `access-subject / ...:some-attribute / xsd:string / MustBePresent=true`; emit `policy_projection.json`.
- `src/pc/derive_H.py`: `canonical_H(request_xml) -> {(Category,AttributeId,DataType,Issuer-or-null): sorted bag of typed values}`; C14N XML, drop whitespace/order/paths/object-identity/logging/harness state; initial H has subject-id/resource-id/action-id, lacks `some-attribute`; successors add it. Independent of expected K (INV-08).
- `src/pc/derive_PR.py`: builds extensional equivalence predicate from frozen projection + XACML matching semantics (Category/Id/DataType/Issuer-aware bag equality); P_R object itself constant across repair, only presented histories change (INV-09).
- `src/pc/derive_Lambda.py`: canonical hashes of `pdp.xml`, `policy.xml`, provider config, preprocessor selection, attribute-provider set, native interface descriptor; asserts pre==post (repair needs no config change; else design violated).
- `src/pc/derive_atom.py`: emits the single transaction boundary record justified by XACML PEP→PDP→response architecture (N1); internal Java calls never exposed.
- `src/xacml/canonicalize_request.py` shared by H/P_R/Lambda paths (single canonicalizer to avoid divergent semantics).
- `src/audit/check_anchor_completeness.py`: JSON-schema validation + requires H=P_R=Lambda=Atom=omega=Q=Succ+=A_Pi=FIXED (c may be X-authored but frozen); used by gate and later by ablation tests (each single-anchor deletion must flip verdict).
- Target audit reuses `run_authzforce.py`/`parse_response.py` on completed requests: expect `x_permit→Permit`, `x_nonpermit→NotApplicable` → S0 open (fiber {permit, nonpermit}), terminals closed; else `TARGET_REPRODUCTION_FAIL` (STOP-02). Gate: 8 Phase-2 boxes; failure preserves negative finding, no relabeling.

Benchmarks (anti-overfitting for non-learned anchors): canary P01 (designator coordinates exact); A01–A04 (each anchor FIXED with N1/N2/N3 citation); N02/N03 (world decisions); every check asserts properties of frozen externals, never fits to `expected_signature.json` (kept unreadable to this phase; leakage audit in Phase 5 proves it).

## Phase 3 — Mechanical PC Contract Compilation

Scope: compile anchored semantics into the D33 contract with zero manual touch labels; derive touch mechanically; prove independence via second implementation + static scan; seal hashes (spec §§6, 10.3–10.4, 11-Phase3). Contract input schema must have no resource-touch field.

Files to make:

- `artifacts/contracts/pc_xacml_primary.contract.json` (§10.3 minimum: contract_id, worlds, S0, target map, H/PR/Lambda/omega/actions/successors/costs/atomicity/provenance).
- `artifacts/contracts/touch.json` (expected `{"q_supply_missing_attribute": ["E"]}` as output only).
- `artifacts/seal/phase3_manifest.json` (contract/touch/ledger/manifest SHA-256s).
- `src/pc/{models.py,compile_contract.py,derive_touch.py,solve_freezes.py (stub only here)}`, `src/audit/{independent_touch.py,check_no_manual_labels.py}`, `schemas/contract.schema.json`, `tests/test_no_manual_touch_labels.py`, `test_touch_derivation.py`, `scripts/run_phase3.sh`.

Code to produce and how to code:

- `src/pc/models.py`: frozen dataclasses for World/Checkpoint/Action/Successor/Contract with canonical JSON serialization (sorted keys, C14N) + sha helpers; no touch fields on input models.
- `src/pc/compile_contract.py`: inputs = external manifest + ledger + canonical original/completed requests + parsed PDP responses + prereg worlds/cost; builds graph `S0 --q--> {S_permit, S_nonpermit}` (sole repair action); computes open/closed from fiber/target homogeneity (`A_Pi(permit) != A_Pi(nonpermit)` ⇒ S0 open; singleton homogeneous fibers ⇒ terminals closed — never copy a `closed=true` literal); writes contract + hash. How: pure functions, no network, no expected-signature import (assert at import time that `prereg/expected_signature.json` is not on `sys.modules`/open fds in tests).
- `src/pc/derive_touch.py`: literal spec §6 pseudocode — for each successor compare `canonical_H/PR/Lambda` pre vs post, collect `"E"/"R"/"A"`; output `touch.json`. Expected `{E}` (H changes, PR relation constant, Lambda hash identical) but expectation never an input.
- `src/audit/independent_touch.py`: no import from `derive_touch` or its equality helpers; own C14N + own bag/hash compare; byte-compare result with primary (exact agreement required).
- `src/audit/check_no_manual_labels.py`: recursive regex/AST scan over `prereg/ derived/ src/ artifacts/contracts/input*` rejecting `touch`, `resource_touch`, `"E"`-as-label literals except in `prereg/expected_signature.json` and test fixtures explicitly marked `EXPECTED_OUTPUT_ONLY`; fails on any hit (also reused for mutation test 5.11).
- Gate (7 boxes): contract compiles, S0 open for preregistered reason, both successors closed, touch mechanical, dual-touch agreement, no manual labels in execution path, hashes sealed. Failure → `TOUCH_DERIVATION_MISMATCH` (or earlier anchor/source category).

Benchmarks: T01 primary touch `{E}`, T02 independent agreement — computed from disjoint code paths over the same frozen externals; overfitting impossible by construction (no parameters, no fitting; second path shares no code).

## Phase 4 — Exact All-Freeze Evaluation

Scope: compute the full 8-coordinate signature exactly with exhaustive search + independent solver; record singleton identification + nontriviality (spec §§7, 11-Phase4). Freeze order fixed: F000,F100,F010,F001,F110,F101,F011,F111.

Files to make:

- `artifacts/freezes/{F000,F100,F010,F001,F110,F101,F011,F111}.json` (per §10.4: freeze, frozen_resources, removed_actions, surviving_actions, proper_closer_exists, kappa, solver, contract_sha256) + consolidated `K_table.json`, `artifacts/freezes/identified_set.json` (`identified_set_cardinality: 1`, signature, basis string naming external provenance + wrapper).
- `src/pc/solve_freezes.py` (primary exhaustive solver), `src/audit/independent_solver.py`, `schemas/freeze_row.schema.json`, `tests/test_all_freezes.py`, `scripts/run_phase4.sh`.

Code to produce and how to code:

- `solve_freezes.py`: for freeze set S, `removed = {q : T(q) ∩ S ≠ ∅}` (D33 literal; never edit action interior, never fabricate subactions — INV-12–13, assert by operating only on action IDs); exhaustive policy-tree search over surviving actions (graph is 1-action/2-successor tiny — enumerate, no sampling); per freeze record reachable checkpoints, closer existence, worst positive-support branch cost, kappa (`1` vs `"INF"`), terminal classes. How: itertools over masks in prereg order, deterministic JSON, contract hash embedded per row.
- `independent_solver.py`: separate enumeration of surviving finite policy trees (no shared search code with primary); must agree on available set, closer existence, exact finite cost, all 8 coordinates.
- Expected table: F000→1, F100→INF, F010→1, F001→1, F110→INF, F101→INF, F011→1, F111→INF. Mismatch reported honestly (never overwritten); singleton claim allowed only if Phase-2 gate passed with single admissible completion; nontriviality iff ∃F≠F000 with kappa_F ≠ kappa_F000. Gate (6 boxes); solver disagreement → `SOLVER_MISMATCH`; trivial signature → `NONTRIVIALITY_FAIL`.

Benchmarks: F000–F111 rows are the "held-out geometry benchmark" — disjoint from Phase-3 touch derivation inputs (solver consumes touch output + contract, never the sealed expectation); dual-solver agreement is the anti-overfit proof (two codebases, one signature).

## Phase 5 — Falsification, Sensitivity, and Anti-Circularity Audit

Scope: mandatory even if K matches — try to break the positive reading (spec §11-Phase5, §§13–14 C/R rows). All variants are temporary copies, never mutate frozen `external/`; interface-changing variant explicitly labeled out-of-scope.

Files to make: `artifacts/audits/{corruption_*.json, canary_*.json, perturbation_*.json, cost_sweep.json, negative_world_sweep.json, ablation_*.json, leakage_graph.json, clean_repro.json}`, `tests/test_parser_corruptions.py` (C01–C03/C09/R01), `test_cost_robustness.py` (R03–R05), `test_interface_preserving_mutations.py` (R01–R02), `test_anchor_ablation.py` (C04–C07), `test_clean_reproduction.py` (R06), extensions to existing no-label/hash tests (C08–C09); `scripts/run_phase5.sh`.

Code/logic per control (how to code):

- 5.1 hash corruption: flip 1 byte in temp copies of each of the 4 fixtures + spec HTML; `verify_sources.py` must fail 5/5 (C09).
- 5.2 MustBePresent canary: temp policy with `MustBePresent` removed/changed → original missing-attribute behavior must no longer match frozen claim (proves harness sensitivity to governing semantics).
- 5.3 wrong category: repaired request with correct literal under wrong Category → must not satisfy designator (C01; proves Category-aware H/P_R, anti-T6).
- 5.4 wrong datatype: correct literal under incompatible type → PDP/parser must reflect XACML datatype semantics, no silent coercion (C02).
- 5.5 projection canary: unrelated extra attribute → H may grow, fixed P_R must not change unless policy references it (C03; H-vs-P_R distinction).
- 5.6 preserving perturbations: whitespace/format/semantically-irrelevant order/file-rename-with-reference-update → H/P_R/Lambda/T/K all unchanged (R01).
- 5.7 changing control: split into `q_construct_attribute` + `q_submit_request` in temp interface → audit verdict `INTERFACE_CHANGED / THEOREM3_INVARIANCE_NOT_APPLICABLE` (R02; anti-T7, never a T3 claim).
- 5.8 cost sweep 0.5/2/10: finite entries rescale, E-freezes stay INF, structural class invariant (R03–R05; anti-T4).
- 5.9 negative-world sweep: `wrong-answer-1`, `wrong-answer-2` (frozen pre-execution) each → `NotApplicable`, fiber stays open, E-class preserved; primary `x_nonpermit` never replaced.
- 5.10 ablations: delete H / P_R / Lambda / Atom provenance singly → `check_anchor_completeness` refuses positive each time (C04–C07).
- 5.11 label injection: plant forbidden touch literal in temp fixture → static audit fails (C08).
- 5.12 leakage: dependency graph (import scan + file-open trace) proving `expected_signature.json` reachable only from final comparison stage (anti-T8).
- 5.13 clean reproduction: fresh checkout → verify hashes → rebuild requests → rerun PDP → rebuild canonicals → recompile → re-derive (independent) → re-solve 8 freezes → canonical-JSON byte-compare (excluding timestamps/paths) (R06).
- Gate: all 13 boxes; failure → `INDEPENDENT_REPRODUCTION_FAIL` (or earlier specific category).

Benchmarks: this entire phase is the "ENTIRELY different benchmarks" suite — 30+ assertions over mutated/swept/ablated inputs disjoint from the sealed primary expectation; passing them is the overfitting refutation.

## Phase 6 — Seal, Independent Audit Package, and Manuscript-Ready Report

Scope: freeze a tamper-evident package whose claims cannot exceed the evidence; manuscript stays untouched until seal (spec §§8, 11-Phase6, 18–19, 24-seal). `FINAL_RESULT.json` populated from observed artifacts — never forced to the preregistered values.

Files to make:

- `artifacts/seal/FINAL_RESULT.json` (§6.1 fields: experiment_id, outcome ∈ 8-value taxonomy, external_system, authzforce_commit, fixture, anchor_status{H,PR,Lambda,Atom}, derived_touch, K, cardinality, primary_classification, manual_touch_labels_used, native_policy/engine_modified, claim_scope).
- `MANIFEST.sha256` (every reproduction-relevant artifact: externals, prereg, ledger, derived requests, PDP outputs, contract, touch, freeze rows, test results, audit report, source, lockfile).
- `CHANGELOG.md` (every post-prereg change; worlds/target/interface/cost/anchor/freeze/expectation/criteria changes → new experiment version).
- `artifacts/audits/FINAL_AUDIT.md` (12 required sections: provenance, fixture repro, anchor table, projection, target decisions, contract hash, dual touch, 8 freezes, solver agreement, falsification, limitations, allowed/forbidden claims).
- `PC-XACML-S3PLUS-v1.tar.gz` + `.sha256` (deterministic: sorted entries, fixed mtimes, no secrets/caches/usernames).
- `prereg/allowed_claims.md` enforcement: success → at most the two §18.1 paragraphs; always → none of the §18.2 strings; `NATIVE_ANCHOR_INSUFFICIENT` → only the §18.3 sentence, never a relabeled point estimate. Paper role per §19 (tiny main-paper footprint; Polaris-negative / XACML-positive / PC-TAU-geometry / LLM1-realizability composition).
- `scripts/run_phase6.sh` + `reproduce_all.sh`; `scripts/` + full `tests/` green.

Code to produce and how to code: `src/audit/build_audit_report.py` (assembles FINAL_AUDIT from artifact hashes + test JUnit XML — no hand-typed numbers; claim-string linter against §18.2 blocklist); seal builder (canonical JSON, `sha256sum` manifest, `tar --sort-name --mtime` archive); `schemas/final_result.schema.json` validation. Gate (6 boxes): outcome from artifacts, manifest complete, all tests pass, audit generated, archive reproducible, claims match outcome, no post-hoc semantic edits. Any post-seal semantic change → new version, never silent patch.

---

## Cross-Cutting Compliance Map

- Schemas (§10): `experiment.yaml` fields, ledger record (`FIXED/PARTIAL/AMBIGUOUS/UNSUPPORTED`, only FIXED allowed for positive set), contract (no touch input), freeze row — each with JSON Schema in `schemas/` and validation in tests.
- Outcome taxonomy (§8): exactly one of 8 outcomes; §8.1 10-condition conjunction for positive; `Path.md` records which outcome fired and why.
- Anchor table (§12): H(N1+N3), P_R(N1+N3), Lambda(N1/N2/N3), Atom(N1), omega(N1+N3), Q(N1+X), Succ+(N3+X), A_Pi(N3 exec), c(X-frozen) — every ledger record cites its row; missing row → gate fail.
- Threats T1–T10 (§13): each has code defense + named test (see Phase 5 mapping); audit report §11 lists verdicts.
- Tests (§14): S01–S03, N01–N03, A01–A04, P01, T01–T02, F000–F111, C01–C09, R01–R06 — all mandatory, none deletable post-seal without new version; `tests/` file ↔ ID mapping in table above.
- Invariants INV-01–INV-20 (§15): asserted in code (INV-01 policy bytes frozen, INV-02 pdp.xml frozen, INV-03 original request frozen, INV-04 original response frozen, INV-05 repaired diff = single Attribute, INV-06 inter-world diff = AttributeValue only, INV-07 projection parser-derived, INV-08 H K-independent, INV-09 P_R K-independent, INV-10 Lambda K-independent, INV-11 touch-from-comparison-only, INV-12 freezes remove actions only, INV-13 never edit action interiors, INV-14 targets from PDP execution, INV-15 expected-import ban, INV-16 provenance on artifacts, INV-17 drift fails closed, INV-18 ambiguity fails closed, INV-19 disagreement fails closed, INV-20 claim gating post-seal) + doc-checked in reviews.
- Analysis (§16): deterministic 8-step pipeline, no statistics; objects `K_Pi`, `|K|`, success conjunction.
- Interpretation (§17) + claims (§18) + paper role (§19): quoted verbatim in `allowed_claims.md`; linter-enforced.
- Order (§20), logging (§21), AI policy (§22), stops STOP-01 (source repro), STOP-02 (targets distinct), STOP-03 (H), STOP-04 (P_R), STOP-05 (Lambda), STOP-06 (Atom), STOP-07 (manual labels), STOP-08 (touch agree), STOP-09 (solver agree), STOP-10 (drift), STOP-11 (frozen policy/config), STOP-12 (no target redefinition) (§23), checklist (§24), success sentence (§25), references (§26: OASIS URL, core repo, release/commit, fixture path — frozen as local copies/hashes).

## Verification That Nothing Was Omitted

Traceability (spec → plan): §0→Mission; §1→Mission/Out-of-scope; §2→Phase 1; §3→Mission; §4→Phases 1–2; §5→Phase 2; §6→Phase 3; §7→Phase 4; §8→Phase 6 + gates; §9→Repository Contract; §10→Cross-cutting + Phases 1/3/4/6; §11→Phases 1–6 (unmerged, in order); §12→Phase 2 + map; §13→Phase 5 + map; §14→per-phase Tests; §15→per-phase Code asserts; §16→Phase 4/6; §17–19→Phase 6; §20→Repository Contract discipline; §21→Contract logging; §22→Contract AI; §23→per-phase gates; §24→Phase 6 gate; §25→Mission; §26→Phase 1 + §6.5 bundle. Phase count is 6 (not 5) because the spec fixes 6 phases; workload confirms it (each phase has distinct gate/failure outcome). `Path.md` mirrors this plan phase-for-phase and records compliance/deviation for every implemented step.
