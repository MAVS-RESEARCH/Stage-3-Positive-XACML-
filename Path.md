# PC-XACML-S3+ Path

This file is the implementation trail for `WorkPlan.md`. It moves with the code. Every material step records what changed, what was verified, and whether the work still follows the plan — with the same per-phase depth as `WorkPlan.md` (scope, files made, code produced + how coded, benchmarks, gate verdict). No implementation phase has been executed yet; §§1–3 below are the complete record to date. §§4–9 are the mandatory log templates to fill as work proceeds. A step that deviates from `WorkPlan.md` must say so explicitly and, if it touches worlds/target/interface/cost/anchor/freeze/expectation/criteria, open a new experiment version per spec §6.3 instead of silently patching.

## 1. Source Review Log

Date: 2026-09-11 (UTC+05:00), workspace `C:\Users\Saif malik\Stage-3`.

Reviewed documents (deep read — full text, not skim):

- `C:\Users\Saif malik\Downloads\PC_STAGE3_POSITIVE_XACML_IMPLEMENTATION_SPEC.md`
  - 1663 lines / 9074 words / 66890 chars (via `Get-Content | Measure-Object`, `Select-String "^#+ "`).
  - 27 top-level sections `0`–`26` enumerated in WorkPlan; all normative values extracted:
    - System: OASIS XACML 3.0 + AuthzForce Core CE 21.2.0, tag `release-21.2.0`, commit `3cc0e988e1639da48184434cd5c918102ff5b499`, repo `https://github.com/authzforce/core`.
    - Fixture: `pdp-testutils/src/test/resources/conformance/others/StatusDetail.MissingAttributeDetail/` with 4 files; upstream blob SHAs `pdp.xml 01a0adc0…`, `request.xml ff6582db…`, `response.xml 835d4835…`, `policy.xml 698af364…`.
    - Fixture semantics: subject `Julius Hibbert`, resource `http://medico.com/record/patient/BartSimpson`, action `read`; missing `urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute` (`access-subject`, `xsd:string`, `MustBePresent="true"`, required value `riddle me this`); expected original response `Indeterminate / missing-attribute / MissingAttributeDetail(triple)`.
    - Standard lock: `https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html` with 7 anchor-relevant section families (§7.3.5, MustBePresent, architecture, etc.).
    - Source classes N1/N2/N3/N4/X + hard rule (H/P_R/Lambda/Atom need ≥1 N1/N2/N3).
    - Instance: worlds `x_permit="riddle me this"→Permit`, `x_nonpermit="not-riddle-me-this"→NotApplicable`; S0 = post-`Indeterminate` open fiber; sole action `q_supply_missing_attribute` cost 1, native PEP→PDP→response boundary, Lambda constant; successors S_permit/S_nonpermit.
    - Anchors H (request-context multimap, key `(Category,AttributeId,DataType,Issuer-or-null)`), P_R (frozen-policy AttributeDesignator projection), Lambda (pdp.xml/policy/provider/preprocessor/interface hashes), Atom (`xacml-request-transaction`), omega/Q/Succ+/A_Pi/c conventions.
    - Touch pseudocode (extensional pre/post compare → E/R/A) + manual-label ban + predicted `{E}`.
    - Freeze order F000,F100,F010,F001,F110,F101,F011,F111 + predicted `K=[1,INF,1,1,INF,INF,1,INF]` + sole-action acceptability note.
    - 8-outcome taxonomy + 10-condition positive conjunction; repo layout; 4 schemas; 6-phase plan; anchor table; T1–T10; test matrix S/A/P/T/F/C/R rows; INV-01–20; deterministic analysis; interpretation; allowed/forbidden claims; paper role; SOURCE→COMMIT order; logging fields; AI policy; STOP-01–12; checklist; success sentence; 4 references.
  - Extraction method: `Read` (prompt copy, full text) + `Get-Content`/`Select-String` line/head counts on the Downloads copy; head lists matched (both docs identical → "both the docs" resolved as the two identical copies of this single controlling spec; no second distinct spec exists).
- Target repo `https://github.com/MAVS-RESEARCH/Stage-3-Positive-XACML-` (cloned 2026-09-11 into `C:\Users\Saif malik\Stage-3\Stage-3-Positive-XACML-`):
  - `git log --oneline`: single commit `a4d4bfc Initial commit`; `git status`: clean; `git remote -v`: origin = target URL; content: `LICENSE` only.
  - No implementation, no results, no stale artifacts → "clear previous results" satisfied by verification (nothing to delete; no result files existed). Only new post-change results will be present going forward.

Prior-work references consulted for format only (not normative): `Downloads\WorkPlan.md` (MAVS Ch10B, 1094 lines) and `Downloads\Path.md` (1872 lines) — used to match the expected WorkPlan/Path depth and anti-overfitting explanation style. They impose no requirements on this experiment.

## 2. Current Repository State

Date: 2026-09-11.

- Local workspace: `C:\Users\Saif malik\Stage-3`; repo checkout: `C:\Users\Saif malik\Stage-3\Stage-3-Positive-XACML-`, branch `main`, clean, at `a4d4bfc`.
- Files present after clone: `LICENSE` only. After this documentation step: `LICENSE`, `WorkPlan.md` (this plan's companion), `Path.md` (this file). No `external/`, `src/`, `artifacts/`, `prereg/`, `derived/`, `tests/`, `scripts/` yet — those are built in Phases 1–6 per WorkPlan.
- Previous-results clearing: confirmed — repo had zero result artifacts at clone; the only files with prior provenance are `LICENSE` (kept) and the two new planning docs. All future results will be post-change artifacts under `artifacts/` + `derived/` + `prereg/` with hashes in `Path.md` phase logs.
- Environment so far: Windows PowerShell 5.1 host; JDK/Python/AuthzForce versions not yet pinned (Phase 1 task → `artifacts/raw/environment.txt` + `requirements-lock.txt`). No dependency upgrades possible yet (nothing installed).

## 3. Work Implemented So Far

### 3.1 Documentation Bootstrap (2026-09-11)

Files created:

- `WorkPlan.md` — 6-phase plan (not 5: spec fixes 6; workload confirms 6 distinct gates) covering every spec section §§0–26 with per-phase scope/files/code-how/benchmarks/gates, plus scope boundary, no-training + anti-overfitting contract, repository contract, cross-cutting compliance map, and omission-traceability paragraph.
- `Path.md` — this file (review log + state + this entry + §§4–9 phase templates).

Code produced:

- None. No benchmark, harness, parser, solver, or AuthzForce execution code exists yet. This is intentional per spec §11-Phase1 ¶1.1 (first commit = spec + plans, zero PC results from execution).

Commands and actions:

- `git clone https://github.com/MAVS-RESEARCH/Stage-3-Positive-XACML-` into workspace; verified with `git log/status/remote/branch`, `git show --stat HEAD`.
- `Get-ChildItem` on workspace + Downloads; `Measure-Object` + `Select-String` quantification of the spec; `Read` of spec head + prior WorkPlan/Path samples for style.
- Wrote `WorkPlan.md`, writing `Path.md` now.

Datasets / external systems touched:

- None executed. No AuthzForce clone, no XACML download, no PDP run, no request built. Fixture SHAs recorded from spec text only, not yet verified against upstream (Phase 1 task).

Verification:

- WorkPlan↔spec compliance check performed at creation (see §10 of this file for the standing checklist); Phase 1–6 gates all represented; INV-01–20, T1–T10, S/A/P/T/F/C/R IDs, STOP-01–12, outcome taxonomy, schemas, logging/AI rules all mapped. No test run yet (no tests exist).

WorkPlan compliance: YES — follows WorkPlan "Repository Contract / Phase 1 ¶1.1" (docs-first commit) and "No-Model-Training Policy" (no code claiming training). Deviation: none.

Models trained: none (and none planned — deterministic experiment; see WorkPlan anti-circularity contract). Checks run: none yet. Circularity controls applied: n/a at doc stage beyond the sealed-expectation ordering and the Phase-2B blind-adjudication design in the WorkPlan.

### 3.2 Commit-and-Push Policy (standing instruction, 2026-09-11)

User instruction: commit and push after each instruction/phase is done. From this point on, every completed phase (§§4–9) ends with: update this file's phase log → `git add` only the intended files → commit with a phase-scoped message → `git push` → record the commit SHA and push result back into the phase log. This bootstrap commit (WorkPlan.md + Path.md, zero code per spec §11-Phase1 ¶1.1) is the first such commit.

### 3.3 WorkPlan Audit Mutation (2026-09-11, committed + pushed per §3.2)

External audit returned 6 CRITICAL / 3 HIGH / 2 MEDIUM findings plus Phase-2B and singleton-table directives against `WorkPlan.md`. All were applied to `WorkPlan.md` (this file: only this log entry plus the §3.1 wording fix above):
- Spec identity: retracted heading-based "text-identical" claim; `IMPLEMENTATION_SPEC.md` is the single authoritative byte sequence with raw + LF-normalized SHA-256 sealed in Phase 1; absolute local paths removed from sealed docs.
- Phase 2 split into 2A extraction + 2B blinded adjudication (redacted auditor packet, sealed verdict hashes before unblinding, disagreement resolves against the positive claim).
- H: resolved-PDP-context capture or per-attribute equivalence proof (`h_equivalence_proof.json`), else `AMBIGUOUS`.
- P_R: adequacy certificate (`policy_adequacy_certificate.json`) covering selectors/provider channels plus the N1-cited instantiation argument.
- Atom: hardcoded non-decomposability banned; auditor proves the boundary; Omega_ext/Omega_exp scope lock ("external semantics anchor the measured interface; the finite measurement wrapper itself is experiment-authored").
- Singleton: `completion_space_certificate.json` with `free_k_relevant_fields == 0` gates cardinality 1.
- Scanner: generic resource-enum constants allowed in the extractor; action-specific preassignments / input touch fields / `q → E` tables / expectation reads banned.
- Language: "training/held-out/different benchmarks" and generalization claims purged; verification vs falsification vs sensitivity vs anti-circularity terminology throughout.
- Phase 5: exact sealed canary expectations (`prereg/canary_expectations.json`) required before any canary runs.
- Environment: single pinned primary environment (WSL2 Ubuntu LTS + exact JDK/Python/parser), `.sh` authoritative, same env for clean reproduction.
WorkPlan compliance: YES — mutation implements the audit without relaxing any spec gate; recorded in `CHANGELOG.md` at Phase-1 time as a planning change (no prereg artifact existed yet, so no experiment-version change). Deviation: none.

### 3.4 WorkPlan Re-Audit Mutation (2026-09-11, committed + pushed per §3.2)

Second audit round (1 stale assertion + 5 corrections + 1 wording fix), all applied to `WorkPlan.md` (this file: only this log entry):
1. Removed the premature "no second distinct spec exists" assertion — copy identity/distinctness is UNKNOWN until Phase-1 hashing.
2. Phase 2B independence made mandatory: positive status requires a second-human adjudicator never shown the expectation; the primary analyst cannot be sole adjudicator; verdict carries a non-exposure attestation.
3. Scanner split into PRESENCE ALLOWED (the two sealed expectation files) vs USE FORBIDDEN (five computation stages); boxed rule "expected labels may exist as sealed predictions but may never enter computation."
4. Global modification ban rewritten: frozen primary `external/` immutable; spec-authorized Phase-5 temp-copy mutations labeled as controls, barred from the primary path.
5. Phase-1 gate 8 → 10 boxes (added spec-hash seal + canary-expectations seal); Phase 6 fixed (CHANGELOG lifecycle clarified, 15 audit sections, 8 gate boxes).
6. "Machine-readable proof" → "completion-space closure certificate" with the evidence → audit → certificate → |K|=1 chain.
No spec requirement removed; six-phase structure and primary prediction intact.
WorkPlan compliance: YES. Deviation: none.

### 3.5 Phase-Ordering and Leakage-Hygiene Mutation (2026-09-11, committed + pushed per §3.2)

Third audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Phase-1 execution bug fixed: `run_authzforce.py` supports both modes but Phase 1 invokes original-only (`--phase1-only-original` + gate assertion); completed requests are constructed, never executed; new `test_phase1_no_completed_execution.py`; order locked as Phase 1 → 2A → 2B seal → unblind/target audit (first completed execution) → Phase 3. Phase-1 scope wording corrected (native original-fixture reproduction is in scope; PC extraction/touch/freezes are not).
2. `prereg/execution_inputs.json` created in Phase 1 (non-outcome inputs only, schema-validated, hashed); boxed rule: all computation reads it, only final comparison reads expected outputs; compiler and scanner updated.
3. Auditor packet upgraded to full frozen corpus + excerpt index (no evidence-selection bias); H-capture restricted to already-exposed non-mutating mechanisms (no AuthzForce instrumentation, else equivalence proof or AMBIGUOUS).
4. Completion table gained the Y/outcome-semantics row (induced by omega/Succ+/A_Pi).
5. Phase-6 duplicate CHANGELOG bullet deleted (single lifecycle record); blind attestation uses anonymous auditor IDs in releases, identity-bearing original retained privately.
WorkPlan compliance: YES. Deviation: none.

### 3.6 Atom Scope, Canary Access, and Sealed-Verdict Reproduction Mutation (2026-09-11, committed + pushed per §3.2)

Fourth audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Atom de-strictified to the controlling spec: `Atom` = native request/response transaction [N1], `Q`/wrapper = construct + invoke [N1+X]; `NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER` (four wrapper conditions) is fully valid positive — `COMBINED_BOUNDARY_PROVEN` must not be demanded; `AMBIGUOUS` only for natively-unsupported transaction or overreaching wrapper. Fixed in Mission scope lock, Scope bullet, `derive_atom.py`, and compliance map.
2. Canary access matrix: primary computation → `execution_inputs.json` only; canary execution writes raw outputs without reading expectations; new `src/audit/compare_canary_outcomes.py` opens `canary_expectations.json` afterward (`canary_*_raw.json` → `canary_*_comparison.json`); final comparison alone opens `expected_signature.json`.
3. Blind verdict as sealed input: `run_phase2.sh --primary` (adjudicate + seal) / `--reproduce` (verify hashes, recompute deterministics, never regenerate judgment) / `--readjudicate` (optional fresh replication); `reproduce_all.sh` uses `--reproduce`; 5.13 updated.
WorkPlan compliance: YES. Deviation: none.

### 3.7 Ordering Edge Cases and Reproduction Isolation Mutation (2026-09-11, committed + pushed per §3.2)

Fifth audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Route-(a) sequencing guard: pre-2B resolved-context observation allowed only if obtainable without producing/exposing a completed-world decision; otherwise deferred post-seal and excluded as sole basis for pre-unblinding H=`FIXED`.
2. 2B packet contents made explicit (INCLUDES: blind-safe 2A candidate mappings, adequacy/equivalence artifacts, `execution_inputs.json`, wrapper definition + diff evidence, full corpus, locator index; EXCLUDES: all expected outputs/outcomes/claims) with a packet-builder leakage re-scan.
3. Reproduction namespace isolation: `sealed_reference/` (read-only) vs `reproduction/<run_id>/` (write-only target); ordering tests scope to the current run, never historical sealed artifacts.
4. Git provenance: HEAD/clean verified once at lock time; later phases verify frozen SHA-256 + recomputed blob SHAs via `git hash-object` (no phantom working-tree re-checks); optional `--recheckout` disposable clone.
5. `execution_inputs.json` target semantics as a rule (canonical-Decision), never outcome mappings; contract target map flows from parsed PDP responses → `A_Pi`.
6. Canary prose fixed to judged-after-raw-execution.
WorkPlan compliance: YES. Deviation: none.

### 3.8 Namespace, Scanner, and Failure-Seal Mutation (2026-09-11, committed + pushed per §3.2)

Sixth audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Reproduction isolation without new top-level dirs (spec §9 layout untouched): sealed reference = immutable/tagged primary commit + its `artifacts/`; reproduction in temp fresh checkout `$TMPDIR/pc-xacml-repro-<run_id>/`; canonical outputs compared against hashed primary artifacts.
2. Scanner contradiction fixed: derived touch outputs (`touch.json`, independent-touch output) are PRESENCE ALLOWED with mandatory derivation provenance; FORBIDDEN = source preassignments, contract inputs, touch-accepting schemas, lookup tables, expectation imports into computation.
3. Failure-seal path: `run_phase6.sh --failure-seal` seals early-STOP negative outcomes (`stopped_at_phase`, `trigger`, downstream `NOT_RUN_BY_PROTOCOL`); downstream phases must not run after a fatal stop; separate failure-seal gate; stopped experiments stay auditable.
4. Anchor scope sentence: every ledger record gets independent locator verification; blind-`FIXED` (2B) required specifically for H, P_R, Lambda, Atom.
WorkPlan compliance: YES. Deviation: none.

## 4. Phase 1 Log — External Source Lock and Native Reproduction — TEMPLATE (fill during implementation)

Scope executed: [which of §1.1–1.7 done; note any deferral].
Files made: [list with byte sizes + SHA-256: IMPLEMENTATION_SPEC.md, external/*, prereg/*, derived/requests/*, artifacts/raw/*, scripts/run_phase1.sh, tests/*].
Code produced + how coded: [`lock_sources.py` (clone→checkout→HEAD/clean asserts→copy 4 files→blob+SHA256→spec download→MANIFEST), `verify_sources.py`, `build_repaired_requests.py` (single-Attribute diff asserts INV-05/06), `run_authzforce.py` (pinned JDK/jars), `parse_response.py` (C14N semantic compare); libraries/versions; determinism notes].
Benchmarks: [S01–S03 hashes, N01 semantic match — actual vs expected triple; prereg seal hash].
Tests run: [`test_source_hashes`, `test_original_fixture` — command, exit code, failures].
Gate verdict: [8 Phase-1 boxes PASS/FAIL; on FAIL → outcome `SOURCE_REPRODUCTION_FAIL`, stop per STOP-01/10].
WorkPlan compliance: [YES/NO + detail; deviations + version decision].
Models trained: none. Anti-overfit note: [prereg sealed before Phase 2; expectation file untouched by computation].

## 5. Phase 2 Log — Source-Native Semantic Anchor Audit — TEMPLATE

Scope executed: [§2.1–2.8; ledger records completed].
Files made: [`policy_projection.json` (designator count + canary triple), `H_*.json`, `anchor_ledger.json/.md`, `H_provenance.json`, Lambda pre/post hashes, atom record, target outputs, schema, tests].
Code produced + how coded: [`parse_policy.py` (no allowlist, canary assert), `derive_H/PR/Lambda/atom.py` + `canonicalize_request.py` (C14N rules, K-independence), `check_anchor_completeness.py`; confirm zero E/R/A/touch literals in extraction code (grep evidence)].
Benchmarks: [P01 exact coordinates, A01–A04 FIXED + N-class citations per anchor, N02/N03 Permit/NotApplicable transcripts; S0-open/terminals-closed derivation].
Tests run: [`test_policy_projection`, `test_anchor_completeness`, target audit — commands + results].
Gate verdict: [8 Phase-2 boxes; on ambiguity → `NATIVE_ANCHOR_INSUFFICIENT`, preserve negative finding, no relabeling].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [anchors cite N1–N4, never X-alone for H/P_R/Lambda/Atom; expected_signature unread — leakage evidence ref].

## 6. Phase 3 Log — Mechanical PC Contract Compilation — TEMPLATE

Scope executed: [§3.1–3.7].
Files made: [`pc_xacml_primary.contract.json` (+sha), `touch.json`, `phase3_manifest.json`, schemas, tests].
Code produced + how coded: [`models.py` (frozen dataclasses, canonical JSON), `compile_contract.py` (inputs→graph S0→{S_permit,S_nonpermit}→fiber-homogeneity open/closed), `derive_touch.py` (§6 pseudocode literal), `independent_touch.py` (no shared imports, own C14N), `check_no_manual_labels.py` (scan roots + allowlist); import-ban assert details].
Benchmarks: [T01 `{E}` derivation trace (which of H/PR/Lambda changed), T02 byte-agreement proof].
Tests run: [`test_no_manual_touch_labels`, `test_touch_derivation` — commands + results].
Gate verdict: [7 Phase-3 boxes; on mismatch → `TOUCH_DERIVATION_MISMATCH`].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [dual code paths, zero shared helpers, no fitted parameters].

## 7. Phase 4 Log — Exact All-Freeze Evaluation — TEMPLATE

Scope executed: [§4.1–4.6; freeze order as run].
Files made: [`F000…F111.json` + `K_table.json` + `identified_set.json`; solver sources; schema].
Code produced + how coded: [`solve_freezes.py` (D33 removal rule `T(q)∩S≠∅`, ID-only ops per INV-12/13, exhaustive enumeration), `independent_solver.py` (separate tree enumeration); agreement diff].
Benchmarks: [8-row K table actual vs predicted `[1,INF,1,1,INF,INF,1,INF]`; closer-existence + cost per row; nontriviality witness freeze ID].
Tests run: [`test_all_freezes` — command + results].
Gate verdict: [6 Phase-4 boxes; solver mismatch → `SOLVER_MISMATCH`; trivial → `NONTRIVIALITY_FAIL`; honest-mismatch handling if applicable].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [geometry benchmark disjoint from sealed expectation; dual solvers].

## 8. Phase 5 Log — Falsification, Sensitivity, Anti-Circularity — TEMPLATE

Scope executed: [§5.1–5.13; note temp-copy discipline — `external/` never mutated].
Files made: [`artifacts/audits/*` (14+ JSONs), 5 test files, `run_phase5.sh`].
Code/procedures + how: [per-control method: byte-flip script, MustBePresent strip, wrong-category/datatype builders, extra-attribute injector, perturbation set (whitespace/order/format/rename), OUT_OF_SCOPE split, cost sweep 0.5/2/10, wrong-answer-1/2 sweep, 4 ablations, label-injection, leakage graph builder (import+open-trace), clean-rerun procedure].
Benchmarks (ENTIRELY different from sealed expectation): [C01–C09, R01–R06 actual verdicts — 5/5 corruptions detected, canary rejections, invariance holds, INTERFACE_CHANGED verdict, cost-structure invariance, ablation kills ×4, injection detected, leakage clean, byte-identical repro].
Tests run: [all Phase-5 tests — commands + results].
Gate verdict: [13 boxes; on fail → `INDEPENDENT_REPRODUCTION_FAIL` or specific category].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [this phase IS the brutal-disjoint-benchmark proof — list disjointness per control].

## 9. Phase 6 Log — Seal, Audit Package, Manuscript Report — TEMPLATE

Scope executed: [§6.1–6.6].
Files made: [`FINAL_RESULT.json` (observed-values evidence), `MANIFEST.sha256`, `CHANGELOG.md` entries, `FINAL_AUDIT.md` (12 sections), `PC-XACML-S3PLUS-v1.tar.gz` + `.sha256`, `run_phase6.sh`/`reproduce_all.sh`].
Code produced + how coded: [`build_audit_report.py` (hash-assembled numbers, §18.2 blocklist linter), seal builder (canonical JSON, `tar --sort-name --mtime`), `final_result.schema.json` validation].
Benchmarks: [full `tests/` green transcript; archive reproducibility (re-tar hash match); claim-wording audit vs `allowed_claims.md`].
Gate verdict: [6 Phase-6 boxes; outcome emitted (one of 8); manuscript rule observed — no paper edits before seal].
WorkPlan compliance: [YES/NO + detail; post-seal changes → new version]. Models trained: none.

## 10. Standing Verification Checklist (update as phases complete)

- [x] Spec deeply read (1663 lines, §§0–26) in both copies; values pinned.
- [x] Repo cloned, inspected (LICENSE-only `a4d4bfc`), previous-results clearing verified (nothing to delete).
- [x] `WorkPlan.md` created with 6 unmerged phases, per-phase scope/files/code-how/benchmarks, no-training contract, full traceability.
- [x] `Path.md` created with review log, state, bootstrap entry, per-phase templates.
- [ ] Phase 1 gate (SOURCE_REPRODUCTION_FAIL or pass).
- [ ] Phase 2 gate (NATIVE_ANCHOR_INSUFFICIENT or all-FIXED pass).
- [ ] Phase 3 gate (TOUCH_DERIVATION_MISMATCH or dual-agreement pass).
- [ ] Phase 4 gate (SOLVER_MISMATCH / NONTRIVIALITY_FAIL or K pass).
- [ ] Phase 5 gate (13/13 falsification pass).
- [ ] Phase 6 gate (sealed outcome + reproducible archive + claim-locked audit).
- [ ] No spec section omitted (re-verify at seal against §10 map in WorkPlan).
- [ ] `CHANGELOG.md` complete; `MANIFEST.sha256` covers all reproduction artifacts.
