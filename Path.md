# PC-XACML-S3+ Path

This file is the implementation trail for `WorkPlan.md`. It moves with the code. Every material step records what changed, what was verified, and whether the work still follows the plan -- with the same per-phase depth as `WorkPlan.md` (scope, files made, code produced + how coded, benchmarks, gate verdict). No implementation phase has been executed yet; Secs.1-3 below are the complete record to date. Secs.4-9 are the mandatory log templates to fill as work proceeds. A step that deviates from `WorkPlan.md` must say so explicitly and, if it touches worlds/target/interface/cost/anchor/freeze/expectation/criteria, open a new experiment version per spec Sec.6.3 instead of silently patching.

## 1. Source Review Log

Date: 2026-09-11 (UTC+05:00), workspace `<WORKSPACE>`.

Reviewed documents (deep read -- full text, not skim):

- `<AUTHOR-SPEC-SOURCE>`
  - 1663 lines / 9074 words / 66890 chars (via `Get-Content | Measure-Object`, `Select-String "^#+ "`).
  - 27 top-level sections `0`-`26` enumerated in WorkPlan; all normative values extracted:
    - System: OASIS XACML 3.0 + AuthzForce Core CE 21.2.0, tag `release-21.2.0`, commit `3cc0e988e1639da48184434cd5c918102ff5b499`, repo `https://github.com/authzforce/core`.
    - Fixture: `pdp-testutils/src/test/resources/conformance/others/StatusDetail.MissingAttributeDetail/` with 4 files; upstream blob SHAs `pdp.xml 01a0adc0...`, `request.xml ff6582db...`, `response.xml 835d4835...`, `policy.xml 698af364...`.
    - Fixture semantics: subject `Julius Hibbert`, resource `http://medico.com/record/patient/BartSimpson`, action `read`; missing `urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute` (`access-subject`, `xsd:string`, `MustBePresent="true"`, required value `riddle me this`); expected original response `Indeterminate / missing-attribute / MissingAttributeDetail(triple)`.
    - Standard lock: `https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html` with 7 anchor-relevant section families (Sec.7.3.5, MustBePresent, architecture, etc.).
    - Source classes N1/N2/N3/N4/X + hard rule (H/P_R/Lambda/Atom need >=1 N1/N2/N3).
    - Instance: worlds `x_permit="riddle me this"->Permit`, `x_nonpermit="not-riddle-me-this"->NotApplicable`; S0 = post-`Indeterminate` open fiber; sole action `q_supply_missing_attribute` cost 1, native PEP->PDP->response boundary, Lambda constant; successors S_permit/S_nonpermit.
    - Anchors H (request-context multimap, key `(Category,AttributeId,DataType,Issuer-or-null)`), P_R (frozen-policy AttributeDesignator projection), Lambda (pdp.xml/policy/provider/preprocessor/interface hashes), Atom (`xacml-request-transaction`), omega/Q/Succ+/A_Pi/c conventions.
    - Touch pseudocode (extensional pre/post compare -> E/R/A) + manual-label ban + predicted `{E}`.
    - Freeze order F000,F100,F010,F001,F110,F101,F011,F111 + predicted `K=[1,INF,1,1,INF,INF,1,INF]` + sole-action acceptability note.
    - 8-outcome taxonomy + 10-condition positive conjunction; repo layout; 4 schemas; 6-phase plan; anchor table; T1-T10; test matrix S/A/P/T/F/C/R rows; INV-01-20; deterministic analysis; interpretation; allowed/forbidden claims; paper role; SOURCE->COMMIT order; logging fields; AI policy; STOP-01-12; checklist; success sentence; 4 references.
  - Extraction method: `Read` (prompt copy, full text) + `Get-Content`/`Select-String` line/head counts on the Downloads copy; head lists matched (both docs identical -> "both the docs" resolved as the two identical copies of this single controlling spec; no second distinct spec exists).
- Target repo `https://github.com/MAVS-RESEARCH/Stage-3-Positive-XACML-` (cloned 2026-09-11 into `<REPO>/`):
  - `git log --oneline`: single commit `a4d4bfc Initial commit`; `git status`: clean; `git remote -v`: origin = target URL; content: `LICENSE` only.
  - No implementation, no results, no stale artifacts -> "clear previous results" satisfied by verification (nothing to delete; no result files existed). Only new post-change results will be present going forward.

Prior-work references consulted for format only (not normative): `Downloads\WorkPlan.md` (MAVS Ch10B, 1094 lines) and `Downloads\Path.md` (1872 lines) -- used to match the expected WorkPlan/Path depth and anti-overfitting explanation style. They impose no requirements on this experiment.

## 2. Current Repository State

Date: 2026-09-11, after Phase-2 2A execution + packet seal (see Sec.5) plus Amendment 001 implementation (see Sec.3.10) plus EOL-normalization follow-up plus one rejected non-conforming input (Sec.3.11) plus three valid nonunanimous verdicts (Sec.3.12); human blind adjudication pending (superseded as operative path); gate MODEL_ADJUDICATION_NONUNANIMOUS, failure-seal route; zero executions; target audit never ran.

- Local workspace: `<WORKSPACE>`; repo checkout: `<REPO>/`, branch `main`; Phase-1 commit `a4fc9be`; Phase-2 file set staged for commit after this log update (per Sec.3.2).
- New since Sec.4: `derived/` gains projection/adequacy/route-a/equivalence/Hx3/PR/Lambda/Atom/ledger+json+md; `artifacts/audits/` gains blind packet (20 files) + `H_provenance.json` + `phase2_status.json` (BLOCKED_PENDING_ADJUDICATION); `schemas/` gains ledger + verdict schemas; `src/` gains canonicalize/parse/adequacy/route-a (xacml) + prove/derive-H/PR/Lambda/Atom/checker (pc) + blind_adjudication (audit); `scripts/` gains `run_phase2.ps1`/`.sh` + `repro_compare.py`; `tests/` gains 6 Phase-2 files; `src/xacml/run_authzforce.py` gains evaluation-free `stage_completed_fixture()` (refactor verified: Phase-1 tests still 5/5 at change time).
- No completed-world PDP outputs exist anywhere in the checkout (scan empty); chronology test passes.
- Correction to Sec.4 record: the committed `external/MANIFEST.json` hash is `05f55f0a` (the `c0f4d89a` value noted in Sec.4 was a superseded intermediate seal overwritten by the final official run; committed == working tree verified via raw `cmd` redirect, since PowerShell pipes corrupt byte streams -- never verify hashes through them).
- Environment (pinned, actual, unchanged since Phase 1): Windows 11 build 26100 + PowerShell 5.1 host; CPython 3.13.7; lxml 6.1.1; pytest 9.0.2; Microsoft JDK 21.0.9 LTS; git 2.49.0; Apache Maven 3.9.9 (temp toolchain, outside repo). Full record: `artifacts/raw/environment.txt`. Instantiation deviation from the WSL2 pin is documented in Sec.4 (science unaffected).

## 3. Work Implemented So Far

### 3.1 Documentation Bootstrap (2026-09-11)

Files created:

- `WorkPlan.md` -- 6-phase plan (not 5: spec fixes 6; workload confirms 6 distinct gates) covering every spec section Secs.0-26 with per-phase scope/files/code-how/benchmarks/gates, plus scope boundary, no-training + anti-overfitting contract, repository contract, cross-cutting compliance map, and omission-traceability paragraph.
- `Path.md` -- this file (review log + state + this entry + Secs.4-9 phase templates).

Code produced:

- None. No benchmark, harness, parser, solver, or AuthzForce execution code exists yet. This is intentional per spec Sec.11-Phase1 para.1.1 (first commit = spec + plans, zero PC results from execution).

Commands and actions:

- `git clone https://github.com/MAVS-RESEARCH/Stage-3-Positive-XACML-` into workspace; verified with `git log/status/remote/branch`, `git show --stat HEAD`.
- `Get-ChildItem` on workspace + Downloads; `Measure-Object` + `Select-String` quantification of the spec; `Read` of spec head + prior WorkPlan/Path samples for style.
- Wrote `WorkPlan.md`, writing `Path.md` now.

Datasets / external systems touched:

- None executed. No AuthzForce clone, no XACML download, no PDP run, no request built. Fixture SHAs recorded from spec text only, not yet verified against upstream (Phase 1 task).

Verification:

- WorkPlan<->spec compliance check performed at creation (see Sec.10 of this file for the standing checklist); Phase 1-6 gates all represented; INV-01-20, T1-T10, S/A/P/T/F/C/R IDs, STOP-01-12, outcome taxonomy, schemas, logging/AI rules all mapped. No test run yet (no tests exist).

WorkPlan compliance: YES -- follows WorkPlan "Repository Contract / Phase 1 para.1.1" (docs-first commit) and "No-Model-Training Policy" (no code claiming training). Deviation: none.

Models trained: none (and none planned -- deterministic experiment; see WorkPlan anti-circularity contract). Checks run: none yet. Circularity controls applied: n/a at doc stage beyond the sealed-expectation ordering and the Phase-2B blind-adjudication design in the WorkPlan.

### 3.2 Commit-and-Push Policy (standing instruction, 2026-09-11)

User instruction: commit and push after each instruction/phase is done. From this point on, every completed phase (Secs.4-9) ends with: update this file's phase log -> `git add` only the intended files -> commit with a phase-scoped message -> `git push` -> record the commit SHA and push result back into the phase log. This bootstrap commit (WorkPlan.md + Path.md, zero code per spec Sec.11-Phase1 para.1.1) is the first such commit.

### 3.3 WorkPlan Audit Mutation (2026-09-11, committed + pushed per Sec.3.2)

External audit returned 6 CRITICAL / 3 HIGH / 2 MEDIUM findings plus Phase-2B and singleton-table directives against `WorkPlan.md`. All were applied to `WorkPlan.md` (this file: only this log entry plus the Sec.3.1 wording fix above):
- Spec identity: retracted heading-based "text-identical" claim; `IMPLEMENTATION_SPEC.md` is the single authoritative byte sequence with raw + LF-normalized SHA-256 sealed in Phase 1; absolute local paths removed from sealed docs.
- Phase 2 split into 2A extraction + 2B blinded adjudication (redacted auditor packet, sealed verdict hashes before unblinding, disagreement resolves against the positive claim).
- H: resolved-PDP-context capture or per-attribute equivalence proof (`h_equivalence_proof.json`), else `AMBIGUOUS`.
- P_R: adequacy certificate (`policy_adequacy_certificate.json`) covering selectors/provider channels plus the N1-cited instantiation argument.
- Atom: hardcoded non-decomposability banned; auditor proves the boundary; Omega_ext/Omega_exp scope lock ("external semantics anchor the measured interface; the finite measurement wrapper itself is experiment-authored").
- Singleton: `completion_space_certificate.json` with `free_k_relevant_fields == 0` gates cardinality 1.
- Scanner: generic resource-enum constants allowed in the extractor; action-specific preassignments / input touch fields / `q -> E` tables / expectation reads banned.
- Language: "training/held-out/different benchmarks" and generalization claims purged; verification vs falsification vs sensitivity vs anti-circularity terminology throughout.
- Phase 5: exact sealed canary expectations (`prereg/canary_expectations.json`) required before any canary runs.
- Environment: single pinned primary environment (WSL2 Ubuntu LTS + exact JDK/Python/parser), `.sh` authoritative, same env for clean reproduction.
WorkPlan compliance: YES -- mutation implements the audit without relaxing any spec gate; recorded in `CHANGELOG.md` at Phase-1 time as a planning change (no prereg artifact existed yet, so no experiment-version change). Deviation: none.

### 3.4 WorkPlan Re-Audit Mutation (2026-09-11, committed + pushed per Sec.3.2)

Second audit round (1 stale assertion + 5 corrections + 1 wording fix), all applied to `WorkPlan.md` (this file: only this log entry):
1. Removed the premature "no second distinct spec exists" assertion -- copy identity/distinctness is UNKNOWN until Phase-1 hashing.
2. Phase 2B independence made mandatory: positive status requires a second-human adjudicator never shown the expectation; the primary analyst cannot be sole adjudicator; verdict carries a non-exposure attestation.
3. Scanner split into PRESENCE ALLOWED (the two sealed expectation files) vs USE FORBIDDEN (five computation stages); boxed rule "expected labels may exist as sealed predictions but may never enter computation."
4. Global modification ban rewritten: frozen primary `external/` immutable; spec-authorized Phase-5 temp-copy mutations labeled as controls, barred from the primary path.
5. Phase-1 gate 8 -> 10 boxes (added spec-hash seal + canary-expectations seal); Phase 6 fixed (CHANGELOG lifecycle clarified, 15 audit sections, 8 gate boxes).
6. "Machine-readable proof" -> "completion-space closure certificate" with the evidence -> audit -> certificate -> |K|=1 chain.
No spec requirement removed; six-phase structure and primary prediction intact.
WorkPlan compliance: YES. Deviation: none.

### 3.5 Phase-Ordering and Leakage-Hygiene Mutation (2026-09-11, committed + pushed per Sec.3.2)

Third audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Phase-1 execution bug fixed: `run_authzforce.py` supports both modes but Phase 1 invokes original-only (`--phase1-only-original` + gate assertion); completed requests are constructed, never executed; new `test_phase1_no_completed_execution.py`; order locked as Phase 1 -> 2A -> 2B seal -> unblind/target audit (first completed execution) -> Phase 3. Phase-1 scope wording corrected (native original-fixture reproduction is in scope; PC extraction/touch/freezes are not).
2. `prereg/execution_inputs.json` created in Phase 1 (non-outcome inputs only, schema-validated, hashed); boxed rule: all computation reads it, only final comparison reads expected outputs; compiler and scanner updated.
3. Auditor packet upgraded to full frozen corpus + excerpt index (no evidence-selection bias); H-capture restricted to already-exposed non-mutating mechanisms (no AuthzForce instrumentation, else equivalence proof or AMBIGUOUS).
4. Completion table gained the Y/outcome-semantics row (induced by omega/Succ+/A_Pi).
5. Phase-6 duplicate CHANGELOG bullet deleted (single lifecycle record); blind attestation uses anonymous auditor IDs in releases, identity-bearing original retained privately.
WorkPlan compliance: YES. Deviation: none.

### 3.6 Atom Scope, Canary Access, and Sealed-Verdict Reproduction Mutation (2026-09-11, committed + pushed per Sec.3.2)

Fourth audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Atom de-strictified to the controlling spec: `Atom` = native request/response transaction [N1], `Q`/wrapper = construct + invoke [N1+X]; `NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER` (four wrapper conditions) is fully valid positive -- `COMBINED_BOUNDARY_PROVEN` must not be demanded; `AMBIGUOUS` only for natively-unsupported transaction or overreaching wrapper. Fixed in Mission scope lock, Scope bullet, `derive_atom.py`, and compliance map.
2. Canary access matrix: primary computation -> `execution_inputs.json` only; canary execution writes raw outputs without reading expectations; new `src/audit/compare_canary_outcomes.py` opens `canary_expectations.json` afterward (`canary_*_raw.json` -> `canary_*_comparison.json`); final comparison alone opens `expected_signature.json`.
3. Blind verdict as sealed input: `run_phase2.sh --primary` (adjudicate + seal) / `--reproduce` (verify hashes, recompute deterministics, never regenerate judgment) / `--readjudicate` (optional fresh replication); `reproduce_all.sh` uses `--reproduce`; 5.13 updated.
WorkPlan compliance: YES. Deviation: none.

### 3.7 Ordering Edge Cases and Reproduction Isolation Mutation (2026-09-11, committed + pushed per Sec.3.2)

Fifth audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Route-(a) sequencing guard: pre-2B resolved-context observation allowed only if obtainable without producing/exposing a completed-world decision; otherwise deferred post-seal and excluded as sole basis for pre-unblinding H=`FIXED`.
2. 2B packet contents made explicit (INCLUDES: blind-safe 2A candidate mappings, adequacy/equivalence artifacts, `execution_inputs.json`, wrapper definition + diff evidence, full corpus, locator index; EXCLUDES: all expected outputs/outcomes/claims) with a packet-builder leakage re-scan.
3. Reproduction namespace isolation: `sealed_reference/` (read-only) vs `reproduction/<run_id>/` (write-only target); ordering tests scope to the current run, never historical sealed artifacts.
4. Git provenance: HEAD/clean verified once at lock time; later phases verify frozen SHA-256 + recomputed blob SHAs via `git hash-object` (no phantom working-tree re-checks); optional `--recheckout` disposable clone.
5. `execution_inputs.json` target semantics as a rule (canonical-Decision), never outcome mappings; contract target map flows from parsed PDP responses -> `A_Pi`.
6. Canary prose fixed to judged-after-raw-execution.
WorkPlan compliance: YES. Deviation: none.

### 3.8 Namespace, Scanner, and Failure-Seal Mutation (2026-09-11, committed + pushed per Sec.3.2)

Sixth audit round, all applied to `WorkPlan.md` (this file: only this log entry):
1. Reproduction isolation without new top-level dirs (spec Sec.9 layout untouched): sealed reference = immutable/tagged primary commit + its `artifacts/`; reproduction in temp fresh checkout `$TMPDIR/pc-xacml-repro-<run_id>/`; canonical outputs compared against hashed primary artifacts.
2. Scanner contradiction fixed: derived touch outputs (`touch.json`, independent-touch output) are PRESENCE ALLOWED with mandatory derivation provenance; FORBIDDEN = source preassignments, contract inputs, touch-accepting schemas, lookup tables, expectation imports into computation.
3. Failure-seal path: `run_phase6.sh --failure-seal` seals early-STOP negative outcomes (`stopped_at_phase`, `trigger`, downstream `NOT_RUN_BY_PROTOCOL`); downstream phases must not run after a fatal stop; separate failure-seal gate; stopped experiments stay auditable.
4. Anchor scope sentence: every ledger record gets independent locator verification; blind-`FIXED` (2B) required specifically for H, P_R, Lambda, Atom.
WorkPlan compliance: YES. Deviation: none.

### 3.9 Chronology Test and Target-Audit Unlock Mutation (2026-09-11, committed + pushed per Sec.3.2)

Seventh audit round, applied to `WorkPlan.md` plus the affected test code (plan/code consistency required):
1. Chronology test corrected to the attribution rule: `test_phase1_no_completed_execution.py` no longer scans for bare existence of completed outputs (Phase 2 legitimately creates them). It now asserts refusal exit 2, zero completed markers in Phase-1-tagged logs, zero completed entries in the Phase-1 seal, and original-fixture semantics in sealed Phase-1 responses -- plus a simulated post-Phase-2 regression case proving later outputs do not trip it. Verified: 13/13 tests pass; negative controls prove the checks fail on genuinely Phase-1-attributed violations and pass on clean + simulated post-Phase-2 trees.
2. Target-audit unlock conjunction: execution allowed iff verdict hash sealed AND H/P_R/Lambda/Atom all FIXED; any PARTIAL/AMBIGUOUS/UNSUPPORTED forbids completed-world execution and routes to `NATIVE_ANCHOR_INSUFFICIENT` + `--failure-seal`. Fixed in the unblinding rule, target-audit bullet, `run_phase2.sh` description, new `blind_adjudication.py --assert-unlock` gate mode (exit 0/3), and the compliance map. Stale hash-only unlock wording purged (verified by sweep).
WorkPlan compliance: YES. Deviation: none. No Phase-1 re-execution required (no completed execution occurred in Phase 1; established by the corrected attribution test).

### 3.10 Protocol Amendment 001 -- Cold-Model Adjudication (2026-09-11, committed + pushed per Sec.3.2)

Eighth change set, the first protocol amendment (past planning-only mutations). All applied pre-execution (0 completed PDP evaluations, target audit NOT_RUN, touch/K NOT_COMPUTED -- verified by artifact scan), committed as a NEW post-Phase-2A commit; history untouched (no amend/squash/fork/version change; experiment stays PC-XACML-S3PLUS-v1):
1. `PROTOCOL_AMENDMENT_001.md` (original human requirement preserved, unavailability cause, temporal proof, immutable scope list, single mutation human->3x-cold-model-unanimity, disclosure obligation, provenance: prev WorkPlan blob c5e33ae1, prev spec blob 3dad2c10, prev prereg-seal blob 9be3abf9, packet seal, prompt hash, UTC stamp, pre-commit 3daa703) + `artifacts/audits/amendment_001_seal.json`.
2. `prereg/blind_model_adjudication_prompt.txt` (frozen, sha 9d983e35; category-name prohibitions only, zero values/outcomes/claims -- scanned); sealed by amendment seal, NOT by the Phase-1 prereg seal (byte-preserved; test_prereg_seal updated to the amended rule + prompt-coverage test).
3. `src/audit/model_adjudication.py` (ingest with raw->parse->validate pipeline, tamper-evident provenance re-hashing, --assert-model-unlock exits 0/3/4/5, --check-amendment with ancestry check; in-session subagent adjudication refused by isolation rules) + `schemas/model_verdict.schema.json` (AUD-M0[1-3], COLD_MODEL_INDEPENDENT, verbatim declaration const, prompt/packet hashes, isolation affirmations).
4. `run_phase2.ps1`/`.sh` rewired to the amended gate (checker 0-or-4 continues; model gate maps 0->target audit, 4->BLOCKED_PENDING_MODEL_ADJUDICATION, 5->MODEL_ADJUDICATION_INVALID, 3->NONUNANIMOUS failure-seal; packet ensure-not-rebuild so the referenced seal cannot drift).
5. `tests/test_model_adjudication.py`: all 18 controls pass (0/1/2->4; unanimous->0 + unlock/ledger artifacts; PARTIAL/AMBIGUOUS/UNSUPPORTED->3; malformed/missing-declaration->5; prompt/packet tamper->4; leakage/cross-read->5; post-seal edit->4; pre-unlock ban + zero-scan; amendment window zero; original-hash invariance incl. byte-identical prereg_sha256; chronology incl. ancestor check).
6. WorkPlan consistently mutated (2B operative rule with ORIGINAL/OPERATIVE labels, unlock conjunction, schemas/tests/tree, reproduce incl. amendment check, Phase-5 leakage extension, Phase-6 model audit language + claim discipline with allowed paragraph and 7 forbidden strings, compliance map, traceability, status taxonomy, byte-regime rule). `allowed_claims.md` untouched (frozen prereg).
7. Byte-regime stabilization (genuine defect found by the amendment's own discipline): Git EOL conversion desynced sealed working bytes from blobs (packet seal unverifiable after fresh checkout). Fix: `.gitattributes` (`* -text diff`, byte-exact + textual diffs); blob-SHA tooling replaced config-dependent `git hash-object` with deterministic CRLF->LF normalization in code (proven equal to upstream constants); packet rebuilt once under the stable regime (new seal 00710549; equivalence proven: 9/9 mappings timestamp-only diffs, 4/4 fixture corpus byte-identical, 4/4 remaining corpus EOL-only); runner verifies-not-rebuilds (proven by consecutive runs reusing the seal).
Evidence: full suite 42 passed + 1 skipped (lock-respecting target skip); --primary exit 4 BLOCKED_PENDING_MODEL_ADJUDICATION; reproduce exit 0; packet verify clean; zero completed outputs; no verdicts exist (ingest set empty).
WorkPlan compliance: YES. Deviation: none (all deltas are the instructed amendment itself).

Follow-up (same day, separate commit 43cbdc3 -- history preserved, no amend/squash): the byte-regime fix exposed stale stat-cache masking (git status falsely clean while index LF-blobs differed from sealed CRLF working bytes) plus a config-dependent `git hash-object` in the Phase-1 tooling. Fixed by: `git rm --cached` + full re-add under `* -text diff` (blobs now byte-faithful; 8 files re-stored, content identical modulo EOL, zero seal changes) and deterministic CRLF->LF blob-SHA in code (proven equal to upstream constants). Decisive proof: fresh `git clone` of the new HEAD runs the FULL suite green (42 passed + 1 lock-respecting skip) with the amendment-referenced packet seal intact (00710549). Phase-5 clean-reproduction path is thereby unblocked on any machine honoring the committed attributes.

### 3.11 Non-Conforming Adjudication Input AUD-2B7 -- Received, Rejected, Gate Unchanged (2026-09-11, committed + pushed per Sec.3.2)

A single chat-text input claiming auditor ID AUD-2B7 arrived in-session (verdicts H=PARTIAL, P_R=FIXED, Lambda=AMBIGUOUS, Atom=PARTIAL, overall NO), preserved byte-faithfully (to transcription fidelity) at `artifacts/audits/correspondence/2026-09-11-aud-2b7-input.txt` with a disposition header. It is correspondence, NOT evidence, and was NOT ingested:
1. Count: ONE input; the amended gate requires THREE valid records (0/3 -> BLOCKED).
2. Identity: AUD-2B7 is not in {AUD-M01, AUD-M02, AUD-M03} (schema pattern ^AUD-M0[1-3]$).
3. Form: chat prose, not schema-conformant verdict.json (no verdict_id/qualification/prompt_sha256/packet_sha256/isolation object; unattributable attestation string).
4. Content is non-unanimous anyway (PARTIAL/AMBIGUOUS present), so it could never unlock even if valid.
5. Human-path reading likewise insufficient (single record; human-only unlock superseded by Amendment 001).
Mechanical proof (not fiat): `--ingest` of the input on an isolated temp root exits 5 INVALID (raw JSON unparseable); `--assert-model-unlock` on the real repo exits 4 with 0/3 valid records. Full suite still 42 passed + 1 skipped; zero target outputs; no verdict records created; no Phase-3+ execution. Its substantive objections are neither accepted nor rebutted as findings -- non-evidence cannot move the gate in either direction (no forced failure-seal on invalid input, no credit toward unanimity).
WorkPlan compliance: YES. Deviation: none.

### 3.12 Three Cold-Model Verdicts Ingested -- Gate NONUNANIMOUS, Failure-Seal Route (2026-09-11, committed + pushed per Sec.3.2)

Externally supplied raw verdicts for AUD-M01/M02/M03 arrived as chat text and were transcribed byte-faithfully (manual transcription caveat recorded here: no external byte reference exists; hashes below are of the transcribed files) to temp files OUTSIDE the repo, then ingested strictly via `model_adjudication.py --ingest` with zero hand-editing:
- AUD-M01 ingest exit 0 (valid). Tally: H PARTIAL, P_R PARTIAL, Lambda UNSUPPORTED, Atom PARTIAL.
- AUD-M02 ingest exit 0 (valid). Tally: H PARTIAL, P_R PARTIAL, Lambda PARTIAL, Atom PARTIAL.
- AUD-M03 ingest exit 0 (valid). Tally: H PARTIAL, P_R FIXED, Lambda PARTIAL, Atom PARTIAL.
- Amended gate `--assert-model-unlock` exit 3: MODEL_ADJUDICATION_NONUNANIMOUS (all three adjudicators listed). No anchor reaches unanimous FIXED (closest is P_R at 2/3; Lambda draws the sole UNSUPPORTED).
- Official `run_phase2.ps1 -Mode primary` reproduced the same path (packet verified + reused, seal intact) and wrote phase2_status MODEL_ADJUDICATION_NONUNANIMOUS, then threw the designed failure-seal-route error WITHOUT executing the target audit and WITHOUT touching Phase 3+.
Outcome determination (mechanical, not discretionary): the positive Stage-III witness is NOT obtained. Per the amended protocol the experiment routes to NATIVE_ANCHOR_INSUFFICIENT via failure-seal (formal seal = Phase-6 action, not executed this turn). This is the fail-closed design working: independent adjudication declined to certify point identification, so no touch/K/result was manufactured.
Observations recorded without invented criteria: all three verdicts carry the identical attestation_hash 9531a83c... (protocol requires presence, not distinctness -- noted, not failed); transcription fidelity is best-effort manual; verdict contents are neither endorsed nor rebutted as findings beyond the gate verdict (non-evidence cannot move the gate, and here the valid records moved it exactly as specified: to failure-seal).
Tests evolved to the new true state (same strictness, documented): test_15 now asserts gate exit 3 with zero outputs (was: exit 4 with zero records); test_16 now asserts three valid provenances exist with zero outputs (was: records absent). Full suite 42 passed + 1 lock-respecting skip. Seals intact (packet 00710549, prompt, spec, prereg). Zero completed PDP evaluations before, during, and after ingestion.
WorkPlan compliance: YES. Deviation: none.

## 4. Phase 1 Log -- External Source Lock and Native Reproduction -- EXECUTED 2026-09-11, PASS

Scope executed: Sec.1.1-1.7 ALL done, no deferral. No PC semantic-anchor extraction, touch derivation, or freeze computation occurred; only external-source locking and native original-fixture reproduction, per the corrected scope. Completed requests constructed, never executed (ordering enforced in code + test).

Files made (sha256 prefix in brackets):
- `IMPLEMENTATION_SPEC.md` [92c55d42] 69241 bytes: byte-exact copy of `<AUTHOR-SPEC-SOURCE>`; raw == LF-normalized hash (file is LF); 2351 lines sealed.
- `README.md`, `CHANGELOG.md` (skeleton + Phase-1 execution entry), `.gitignore`, `pyproject.toml`, `requirements-lock.txt` (lxml 6.1.1, pytest 9.0.2, CPython 3.13.7).
- `external/authzforce/RELEASE.json`, `COMMIT.txt` (`3cc0e988...`), `fixture/{pdp,request,response}.xml` + `policies/policy.xml` (blob SHAs == all four spec constants; content sha256 `2c3ceab0`, `8c733c46`, `f78d839f`, `8475166c`), `SHA256SUMS`, `external/MANIFEST.json` [c0f4d89a] (+ `derived/canonical_external_manifest.json`, identical).
- `external/xacml/xacml-3.0-core-spec-cos01-en.html` (1257025 bytes [8da7d21f]) + `SHA256SUMS`. OBSERVED: three independent retrievals produced three distinct hashes at identical byte length (dynamic server content); the frozen copy is authoritative from seal on; lock reuses it by hash on reruns (`[P1:lock:071]` path).
- `external/authzforce-repo/` pinned clone (git-ignored): tag `release-21.2.0`, HEAD `3cc0e988...`, porcelain clean at lock; Maven-built 21.2.0 modules + test-classes resident for the driver.
- `derived/requests/request_x_permit.xml` [7e28c8c3] / `request_x_nonpermit.xml` [f5c3b09f]: single-Attribute inserts, values `riddle me this` / `not-riddle-me-this`, INV-05/INV-06 asserted.
- `artifacts/raw/environment.txt` [3e65858a] (scrub-safe: versions only, no usernames/paths), `original_response_actual.xml` [cf2325f9] (565 bytes: Indeterminate/missing-attribute/expected triple), `original_response_expected.xml` (frozen copy), `original_response_comparison.json` (`semantic_match: true`).
- `prereg/experiment.yaml`, `expected_signature.json`, `execution_inputs.json` [04ec1aaa] (outcome-free: verified by test), `canary_expectations.json` [1fae1a1e] (6 sealed canaries + 1 acceptable alternative), `allowed_claims.md`, `prereg_sha256.txt` [0e15fa28].
- `schemas/execution_inputs.schema.json`, `schemas/canary_expectations.schema.json`.
- `scripts/run_phase1.ps1` (authoritative) + `scripts/run_phase1.sh` (POSIX twin).
- `tests/test_source_hashes.py`, `test_original_fixture.py`, `test_phase1_no_completed_execution.py`, `test_prereg_seal.py` (box-[10] enforcement; tree extension documented here).

Code produced + how coded (stdlib + lxml + pinned JDK/Maven toolchain; deterministic; fail-closed exits 1, ordering refusal exit 2):
- `src/provenance/lock_sources.py`: shallow tag clone (reuse-if-verified) -> rev-parse HEAD assert -> porcelain-clean assert -> copy 4 files -> `git hash-object` blob compare vs spec constants -> sha256 -> XACML freeze (download once, hash-reuse after) -> RELEASE/COMMIT/SHA256SUMS/MANIFEST.
- `src/provenance/seal_spec.py`: byte copy -> raw + LF-normalized sha256 + counts -> MANIFEST update -> `prereg_sha256.txt` over prereg files + spec lines.
- `src/provenance/verify_sources.py`: manifest lock-record check -> per-file sha256 + `git hash-object` recompute (no working tree needed) -> xacml + spec hashes -> optional `--recheckout` disposable clone.
- `src/xacml/build_repaired_requests.py`: dynamic triple from MissingAttributeDetail -> policy-designator cross-check (no hardcoded category) -> insert per world -> non-destructive INV-05 (probe-copy + live-tree guard) + INV-06 -> deterministic write.
- `src/xacml/PdpRunner.java`: mirrors upstream `XacmlXmlPdpTestHelper` (`PdpEngineConfiguration` from `pdp.xml`, `newXacmlJaxbInoutAdapter`, `TestUtils.createRequest`, `evaluate`, marshal via `printResponse`); no authorization logic; compiled to temp classes (tree extension recorded here as required backend detail).
- `src/xacml/run_authzforce.py`: modes original/completed; `--phase1-only-original` refuses completed with exit 2; completed mode stages temp fixture copies (unused in Phase 1).
- `src/xacml/parse_response.py`: namespace-flexible Decision/StatusCode/MissingAttributeDetail extraction -> comparison record; mismatch exits 1.

Console-log convention: the Python harness has no JS runtime, so console logging is `print("[P1:<module>:<NNN>] ...", flush=True)`; every step line is preceded by a `# [P1-LOG-<NNN>]` identifying comment (PowerShell: `Write-Output`, POSIX sh: `echo`). Full line index (print line / comment line):
- lock_sources.py: FAIL 52/51; 010 102/101; 012 107; 020 85/84; 022 87; 024 96; 030 113/112; 032 115; 040 120/119; 042 124; 050 133/132; 052 151/150; 070 173/172; 071 186 (reuse branch, covered by 070 comment); 072 206/205; 080 210/209; 090 241/240.
- seal_spec.py: FAIL 24/23; 010 36/35; 012 41; 020 47/46; 022 54/53; 030 58/57; 032 60; 040 63/62; 042 68; 050 93/92; 060 96/95; 062 109/108; 070 117/116.
- verify_sources.py: FAIL 27/26; 010 52/51; 012 61; 020 71/70; 022 75; 030 82/81; 032 93/92; 040 96/95; 042 101; 050 104/103; 052 115; 060 119/118; 062 135; 070 140/139.
- build_repaired_requests.py: FAIL 26/25; 010 172/171; 012 179; 020 182/181; 022 184; 030 187/186; 032 189; 040 193/192; 050 199/198; 060 204/203; 062 208; 063 212; 064 215; 070 218/217; 072 224; 074 225; 080 228/227.
- run_authzforce.py: FAIL 25/24; REFUSE 32/31; 010 67/66; 012 69; 020 74/73; 022 82; 030 92/91; 032 104; 040 111/110; 042 117/116; 044 131; 050 142/141; 052 148; 060 159/158; 070 163/162.
- parse_response.py: FAIL 21/20; 010 64/63; 012 69; 020 74/73; 022 76; 030 80/79; 032 82; 040 87/86; 050 100/99.
- run_phase1.ps1: helper comment 39; 010 comment 45/print 46; 020 comment 54; 030 comment 59; 040 comment 64/print 65; 042 print 80; 050 comment 82; 060 comment 90/print 91; 064 print 108; 070 comment 110; 080 comment 120; 090 comment 132/print 133; 100 comment 143; 110 comment 151/print 152; 112 prints ~157-160; 120 comment 169/print 170. (Invoke-Step calls log their tag via the helper.)
- run_phase1.sh: comment+echo pairs at lines 6/7, 9, 13/14, 16/17, 19/20, 23, 24/25, 27/28, 36, 38, 39/40, 42/43, 45/46, 48, 50/51, 53/54, 55/56.
- tests: hashes T10 34/33, T11 43/42, T12 55/54, T13 77/76, T14 88/87; fixture T20 44/43, T22 59/58; ordering T30 41/40, T32 53/52, T36 70/69, T34 98/97, T38 118/117, T39 148; prereg T40 33/32, T42 62/61, T44 79/78.

Commands executed (official path `scripts/run_phase1.ps1`, three consecutive full runs, final exit 0; run log `artifacts/logs/local_phase1_run.log` [f2298169]):
- lock (HEAD `3cc0e988`, clean, 4/4 blobs); seal (spec 69241 bytes, 2351 lines, raw==normalized `92c55d42`); env record; `mvn -pl pdp-testutils -am package` BUILD SUCCESS (Maven 3.9.9 quirk found: unquoted dotted `-D` args misparse under `mvn.cmd`+PowerShell; quoted form used); classpath build; `javac` PdpRunner exit 0; build requests (triple read dynamically, 1 designator MBP=true, INV-05 x2 + INV-06); original PDP run (565-byte Indeterminate response); compare `semantic_match: true`; pytest 11 passed; gate 10/10 PASS.

Tests run: `python -m pytest tests/test_source_hashes.py tests/test_original_fixture.py tests/test_phase1_no_completed_execution.py tests/test_prereg_seal.py -s` -> 11 passed. `verify_sources.py .` -> complete, 4 files.

Stress results (evidence):
- S1a rebuild determinism: rebuilt permit sha256 identical (`7e28c8c3`); permit != nonpermit (`f5c3b09f`) != original. S1b PDP rerun: byte-identical (`cf2325f9`).
- S2 tamper: 1-byte flips in temp copies of all 4 fixtures + spec detected 5/5 via hash/blob mismatch.
- S3 ordering refusal: `--mode completed --phase1-only-original` -> `[P1:run:REFUSE]` exit 2 (CLI + in-process test).
- S4 idempotence: three consecutive official script runs, final two exit 0 with identical sealed hashes (spec-reuse path `[P1:lock:071]` exercised).
- S5 misuse: bad argv -> `[P1:build:FAIL]` exit 1; mutated Mutated-copy comparison -> `semantic_match: False` exit 1 (temp files only; frozen externals untouched).
- Bugs caught by stress/audit and fixed before seal: (i) destructive INV-05 assertion stripped the insert from both written files (files == original; caught by S1 hash equality) -> non-destructive probe-copy + live-tree guard, verified by per-world value readback; (ii) manifest lacked `verified_head`, failing `verify_sources` -> added at lock; (iii) prereg-hash test misparsed `spec:` lines -> fixed; (iv) missing `derived/` makedirs; (v) PS1 `Stop` preference aborting on native stderr -> explicit exit-code checks; (vi) `environment.txt` username leak via Maven path -> first-line-only probes.

Gate verdict (10/10 PASS): [1] commit pinned (HEAD log + COMMIT.txt + test) [2] tree clean (porcelain log) [3] 4 blobs match (per-file log + test) [4] local manifest (MANIFEST + SHA256SUMS + test) [5] spec frozen (1257025 bytes + test) [6] original reproduces (Indeterminate/missing-attribute/triple + comparison + test) [7] requests constructed unexecuted (INV logs + determinism + ordering test + refusal) [8] prereg hashed (seal log + test) [9] spec hashes sealed (raw/norm + test) [10] canary + execution inputs sealed, schema-conformant, outcome-free (seal log + test). No failure -> no STOP; outcome remains open for Phase 2.

WorkPlan compliance: YES, with two instantiation deviations (no scientific content affected, no version change): (a) primary environment is the Windows 11 + PowerShell host (WSL2 not installed and no reboot permitted; Git Bash absent), so `run_phase1.ps1` is authoritative and `run_phase1.sh` its POSIX twin; (b) `src/xacml/PdpRunner.java` added as the required native-execution backend detail, and `tests/test_prereg_seal.py` added as the box-[10] enforcement test (both WorkPlan-consistent, tree extensions recorded here). Text operations on docs must use Python, never PowerShell Get/Set-Content (a scrub pass double-encoded Path.md unicode; repaired to pure ASCII, verified 0 non-ASCII bytes).
Models trained: none (deterministic harness; no learning anywhere). Sealed expectations (`expected_signature.json`, canary outcomes) opened by no computation step; Phase-1 outputs contain no expected-decision content (verified by test).

## 5. Phase 2 Log -- Source-Native Semantic Anchor Audit -- 2A EXECUTED, 2B PACKET SEALED, HUMAN VERDICT PENDING (BLOCKED, not failed)

Scope executed: Sec.2.1-2.5 + 2.7-2.8 fully (2A extraction, adequacy/equivalence proofs, ledger, blind packet + machinery); Sec.2.6 target audit NOT executed (locked by the unlock rule -- no qualifying blind verdict exists); Sec.2B human adjudication PENDING. No E/R/A/touch literals in extraction code (grep-verified; ledger confirmed clean by independent Python scan after a PowerShell-regex false positive).

Files made (sha256 prefix):
- `derived/policy_projection.json` [81643475]: 5 designators, exact coordinates, canary triple MBP=true, construct inventory (0 selectors/XPath/references), policy hash matches seal.
- `derived/policy_adequacy_certificate.json` [6059e016]: PASS; pdp children == [policyProvider]; P_R-instantiation argument with N1 locators (7.3.5/5.29/Match).
- `derived/route_a_probe.json` [a13f17e2]: route (a) unavailable -- javap scan of PdpEngineInoutAdapter found 0 exposure points (real probe, not fallback) + sequencing guard (completed contexts would need full evaluation).
- `derived/h_equivalence_proof.json` [fbc814fa]: route b, VALID; 4 global conditions hold; 4 attribute rows (some-attribute absent originally, world values exact).
- `derived/H_initial.json` [83360d81] (3 entries) / `H_permit.json` [012bc20d] / `H_nonpermit.json` [cfde8e17] (4 entries); `artifacts/audits/H_provenance.json` [5ea0229e].
- `derived/pr_relation.json` [e39e2103]: bag-equality rule over 5 frozen coordinates, constant-across-repair, content-addressed refs.
- `derived/lambda_record.json` [d28a41f9]: pre_hash `bb2c3c94...`; providers=1, attr_providers=0, preprocessors=default-absent; post pending Phase 3.
- `derived/atom_record.json` [9f42eff6]: NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER, four wrapper evidences (N1 dataflow locators; counts 3/4/4 distinct; builder static scan clean of auth logic + decision literals; prereg match), auditor_status PENDING_2B.
- `derived/anchor_ledger.json` [91307c2e] + `.md` [c436f5fb]: 9/9 FIXED (four PENDING_2B, five INDEPENDENT_CHECK_PASS), no touch/E/R/A labels.
- `artifacts/audits/blind_anchor_packet/` (20 files, seal `d9f2d3d2`): candidates (ledger draft, adequacy, equivalence, atom, PR, Lambda, Hx3, execution_inputs) + full corpus byte-identical to sealed sources + rubric + locator_index + manifest; redaction-clean over analyst-authored parts.
- `artifacts/audits/phase2_status.json` [42c24072]: BLOCKED_PENDING_ADJUDICATION. `schemas/anchor_ledger.schema.json`, `schemas/blind_verdict.schema.json`.

Code produced + how coded (stdlib + lxml + javap probe; deterministic; fail-closed exit 1; checker exits 0/2/4; unlock exits 0/3/4):
- `src/xacml/canonicalize_request.py` (shared C14N loader), `parse_policy.py` (no allowlist, canary assert, manifest cross-check), `check_policy_adequacy.py` (channel inventory + pdp seal check + instantiation argument), `capture_resolved_context.py` (javap API-surface scan + sequencing guard -> route_a_probe.json), `src/pc/prove_h_equivalence.py` (route-b conditions + 4 rows), `derive_H.py` (proof-gated, H_provenance with content-addressed proof ref), `derive_PR.py`, `derive_Lambda.py` (mechanical pdp.xml facts, seal cross-check), `derive_atom.py` (four wrapper evidences incl. builder AST scan), `check_anchor_completeness.py` (assembler + validator, exits 0 complete / 2 anchor-failure / 4 blind-pending), `src/audit/blind_adjudication.py` (--build-packet / --seal-verdict / --assert-unlock), `scripts/repro_compare.py` (normalized reproduce comparator), `scripts/run_phase2.ps1` (.ps1 authoritative, modes primary/reproduce/readjudicate) + `.sh` twin (completed with real invocations).
- N1 locators used (frozen HTML stripped-text lines, verified by probe): dataflow 1755-1784, glossary 931/1007/1016, 5.29 406-407, MBP 6292-6294, 7.3.5 8405-8424, Match 8577-8594, rule eval 2308-2322, StatusDetail 491-494.

Console-log line index (print line / comment line; convention as Sec.4: Python print == console log):
- canonicalize L37/36, L49, L56/55, L62/61, FAIL L22/21.
- parse_policy L78/77, L82, L86/85, L105, L108/107, L134, L139/138, L145, L169/168, FAIL L33/32.
- check_policy_adequacy L63/62, L75/74, L83, L87/86, L92, L96/95, L106, L110/109, L156/155, FAIL L48/47.
- capture_resolved_context L52/51, L59, L63/62, L76, L82, L90/89, L95, L115/114, FAIL L27/26.
- prove_h_equivalence L114/113, L135/134, L143/142, L171, L174/173, L210/209, L235/234, FAIL L55/54.
- derive_H L115/114, L126, L131/130, L156/155, L173/172, L176/175, FAIL L26/25.
- derive_PR L62/61, L71, L77/76, L105/104, FAIL L26/25.
- derive_Lambda L58/57, L66/65, L79, L94/93, L125/124, FAIL L29/28.
- derive_atom L93/92, L101/100, L110/109, L123, L126/125, L132, L135/134, L144, L174/173, FAIL L47/46.
- check_anchor_completeness L186/185, L192, L201/200, L302/301, L306, L310/309, L314, L322, L332/331, FAIL L38/37.
- blind_adjudication L156/155, L207/206, L212, L215/214, L219, L236/235, L265/264, L282, L288/287, L292, L297, L302, L308, L311, L318/317, FAIL L83/82.
- repro_compare L63/62, L75/76, L84/83, L90, L98/97, L108, L116/115, L134/133, FAIL L41/40.
- run_phase2.ps1 L62/61, L72, L82, L94/L109 backend, L112-L170 phase steps (020/025/030/040/042/050/052/060/062/064/066/070/080/085/090/100/102/110/115/120), L201 blocked exit, FAIL-helper L39.
- run_phase2.sh comment+echo pairs L7/8, L10, L17/16, L21, L23, L27, L29, L32, L37, L40-L49 derivations, L52, L56/57, L61, L64, L71.
- tests: projection T10 32/31, T12 52/51; adequacy T20 22/21; equivalence T22 15/14, T24 35/34; completeness T30 23/22, T32 32/31, T34 52/51, T35 57, T36 74/73; blind T40 37/36, T42 65/64, T44 101/100; target T50 28/27, T52 50/49, T54 59/58, T56 68/67.

Commands executed: official `scripts/run_phase2.ps1 -Mode primary` (exit 4 BLOCKED, full 2A chain + packet seal in `artifacts/logs/local_phase2_run.log` [6d146beb]); `Mode reproduce` (exit 0: derivations/ledger/packet all match); three primary runs total (idempotent, exit 4 each).

Tests run: full suite 23 passed + 1 skipped (target audit skips while locked, zero evaluation). Breakdown: P01 projection, adequacy PASS, equivalence VALID + provenance, ledger states + blocked-exit-4 + Lambda-ablation refusal, packet integrity + unlock-logic matrix (missing->4, tampered->4, PARTIAL->3, all-FIXED->0 on synthetic temp roots), target lock-skip + evaluation-free staging unit. Phase-1 suite re-run: 13 passed (chronology holds; no completed outputs exist anywhere in checkout -- scan empty).

Stress results (evidence):
- ST-determinism: reproduce mode recomputes all derivations + ledger + packet from scratch: mismatches=[], ledger match=True, packet mismatches=[].
- ST-tamper: 1-byte flips in temp copies of packet file + derived H file detected (hash mismatch); seal tamper -> unlock exit 4.
- ST-ablation: H(AMBIGUOUS)/P_R(FAIL)/Atom(AMBIGUOUS) verdict flips in temp roots -> checker exit 2 (failure-seal eligible); Lambda-file removal -> non-zero (committed test).
- ST-unlock matrix (committed test, synthetic temp roots): absent->4, tampered->4, PARTIAL->3, all-FIXED->0. Real path: absent -> 4 (this run).
- ST-leakage: zero `open()` calls on expected_signature/canary_expectations/experiment.yaml across src/{pc,xacml} + blind_adjudication (4 string hits all verified as denylist literals, never opened); zero touch/E/R/A label literals in extraction code and ledger (Python-verified after a PowerShell-regex false positive).
- ST-idempotence: repeated primary runs exit 4 with identical per-file packet hashes; reproduce exit 0.
- Bugs caught and fixed before seal: (i) DataType read from Attribute instead of AttributeValue (None coordinates) in prove/derive_H; (ii) synthetic-verdict temp dirs missing artifacts/ layer; (iii) packet manifest backslash keys (normalized to forward slashes); (iv) adequacy manifest ordering (use-before-assign); (v) timestamp/location-coupled cross-references replaced by content-addressed hashes (projection/adequacy/proof refs); (vi) moottom inline-python fragility replaced by committed repro_compare.py; (vii) H_provenance.json gap vs WorkPlan file list.

Gate verdict: 2A boxes PASS (H provenance, P_R mechanical, Lambda fixed with equality criterion sealed for Phase 3, Atom justified pending 2B, no manual labels, ledger FIXED + independently checked); target-decision boxes PENDING (locked, not failed); blind-agreement boxes PENDING (no qualifying human verdict). Overall: BLOCKED_PENDING_ADJUDICATION -- NOT a failure, NO outcome emitted (the exactly-one-outcome rule binds at Phase-6 seal), downstream Phases 3-5 correctly unexecuted.

WorkPlan compliance: YES, with documented deltas (no scientific content affected, no version change): (a) Windows/PowerShell host instantiation as in Sec.4; (b) `stage_completed_fixture()` extracted for evaluation-free unit testing (behavior identical, Phase-1 tests unaffected); (c) `scripts/repro_compare.py` added as the fragile-inline-python replacement (scripts/ helper, harness tree untouched); (d) text edits to docs via Edit tool only (PowerShell text cmdlets corrupt unicode/pipes -- established Sec.4 rule).
Models trained: none (deterministic rule code throughout). Sealed expectations opened by no computation step (leakage evidence above); packet contains zero expected outputs (redaction-tested).
Handoff to unblock: deliver a `blind_anchor_verdict.json` per `rubric.md` from a qualifying independent adjudicator (AUD-XXX, never shown the expectations) -> `--seal-verdict` -> rerun `--primary` unlocks the target audit.

### 3.13 Semantic Hardening 2B-H (ROUND_002 sealed), Convergence 10/10, Final Freeze (2026-09-12)

Files made: `src/audit/hardening.py` ([P2-LOG-010]/[P2-LOG-020]/[P2-LOG-030]/[P2-LOG-040]/[P2-LOG-050]/[P2-LOG-060]/[P2-LOG-070] + [P2-LOG-900]), `hardening_evidence.py` ([P2-LOG-010]/[P2-LOG-020]/[P2-LOG-050]), `objection_ledger.py`, `final_certification.py` ([P2-LOG-900]); `tests/test_hardening.py` ([P2-LOG-H10]-[P2-LOG-H20]), `tests/test_final_certification.py`; `src/xacml/ParseProof.java`; `artifacts/audits/semantic_hardening/` (STATE, `objection_ledger.json` 86/86 RESOLVED + `.md`, `rounds/HARDENING_ROUND_001` 49 files sealed, `rounds/HARDENING_ROUND_002` evidence 4+`n4_excerpts`/mutations/`round_seal.json`/`convergence.json`, `reports/sweep_assessment_HARDENING_ROUND_002.json`, `final_freeze/FINAL_BLIND_PACKET` sha `4b9f6556bd9d1360`); `prereg/final_certification_prompt.txt`.

Code produced + how coded: hardening rounds enforce NATURAL_STAGE3_INVARIANT (fixture/XACML/spec/execution-inputs) + zero completed evaluations + hardening tests at seal; evidence builders are static only (diffs/wrapper/match-table/lambda-manifest, no PDP evaluation, no touch/K); convergence checks 10 conditions (no open, chains complete, packet complete, tests, hashes unchanged, exec zero, sweep no-new-material + redteam clear, system unmodified); freeze copies frozen corpus + ROUND_001 candidates + prompt, writes packet manifest + `FINAL_ANCHOR_LEDGER.json` (PENDING_FINAL_CERTIFICATION), locks to `BLOCKED_PENDING_FINAL_CERTIFICATION` with `--verify-freeze`.

Hardening mutations in this commit (all `external_semantics_changed=false`): schema-illegal Attribute-level DataType removed (value-level only, R2A-07); builder non-empty world-value guard; `run_phase1` binds world values from sealed `execution_inputs.json`; forward-slash request paths; `repro_compare.py` refs mode (H/PR/Lambda/wrapper/match-table/ledger-manifest/envelope/engine/clone-absent-skip) + dead-branch removal + single VOLATILE set (`produced_utc/sealed_utc/probed_utc/checkpoint_sha256`); checker envelope cross-checks (frozen triple, single-result, world files, rule/cost binding); ledger scope notes (A_Pi [N3,X], Q/Succ+/c FIXED-as-definition, Lambda operative-manifest binding, omega verified locators); derived H/proof/provenance rehashes from timestamp-strip normalization only.

Verification: full suite 59 passed + 1 skipped (fixed `test_checker_refuses_ablation` isolated root to provide frozen `response.xml` for the new R3-15 omega cross-check); `refs` mode exit 0; ROUND_002 seal exit 0 (invariant holds, exec 0, hardening tests exit 0); convergence 10/10 PASS; freeze exit 0; `--verify-freeze` confirmed. Zero completed-world PDP evaluations throughout (target scan empty).

Gate verdict: HARDENING_ROUND_002 SEALED; convergence PASS; freeze VALID; state `BLOCKED_PENDING_FINAL_CERTIFICATION` (not a failure, no outcome emitted; Phases 3+ still unexecuted by protocol). Next unblock: three cold-model final chairs AUD-C01/02/03 over the frozen final packet via `final_certification.py --ingest-final` + `--assert-final-unlock` (unanimous FIXED required).

WorkPlan compliance: YES (hardening/freeze/certification are evidence-strengthening only; no worlds/target/interface/cost/anchor/freeze/expectation/criteria changed; see WorkPlan Phase-2 hardening paragraph). Models trained: none.

### 3.14 Amendment 003 Phase 2B-R Rehearsal SWEEP_001 — REVISION_001 PRESERVED (2026-09-12)

Files made: `PROTOCOL_AMENDMENT_003.md`; `src/audit/certification_rehearsal.py` ([P2-LOG-005]/[P2-LOG-008]/[P2-LOG-010]/[P2-LOG-020]/[P2-LOG-030]/[P2-LOG-040]/[P2-LOG-050]/[P2-LOG-060]/[P2-LOG-070]/[P2-LOG-900]); `tests/test_certification_rehearsal.py` ([P2-LOG-R10]-[P2-LOG-R16]); `artifacts/audits/certification_rehearsal/REHEARSAL_SWEEP_001/` (`SWEEP.json` revision `SEMANTIC_FREEZE_REVISION_001` packet `4b9f6556`, 8 raw reports Panels A–E, `objections.json` 25 normalized, `NORMALIZATION.json`); fixed `tests/test_prereg_seal.py` ([P2-LOG-T48] freeze coverage for `prereg/final_certification_prompt.txt`, pre-existing gap from the freeze commit).

Code produced + how coded: sweep binds packet/prompt/manifest/freeze hashes + commit at init, refuses cert-mimic IDs and unlabeled/cert-identity reports, validates dispositions (`VALID_MATERIAL` needs grounding, `REVIEWER_ERROR` needs refuting evidence, cert-namespace leak refused), verifies freeze-drift + exec-0 + namespace + ledger validity. Eight contaminated subagents (3 emulators H+P_R/Lambda/Atom, packet/provenance/locator specialist, invariant specialist, red-team countermodels CM1–CM4, global joint JO-01–JO-05, evidence adversary) attacked REVISION_001 AS-IS; all outputs labeled NON_BLIND, none entered cert namespaces.

Verification: normalization total=25, surviving=0, material=0 (`NO_SURVIVING_MATERIAL`: 8 DUPLICATE of R3 dispositions, 17 VALID_NONMATERIAL harness/doc polish); `--verify` exit 0; full suite 64 passed + 1 skipped; target scan empty (0 executions); freeze packet/prompt/manifest hashes unchanged.

Gate verdict: `SEMANTIC_FREEZE_REVISION_001_PRESERVED`, no `SEMANTIC_FREEZE_REOPENED` (reopen requires surviving VALID_MATERIAL; none survived source verification). State remains `BLOCKED_PENDING_FINAL_CERTIFICATION`; Phases 3+ unexecuted; next unblock is genuinely fresh external AUD-C01/02/03 over the preserved freeze.

WorkPlan compliance: YES (Amendment 003 developmental layer only; experiment ID unchanged; no history rewritten; no estimand change). Models trained: none.

## 6. Phase 3 Log -- Mechanical PC Contract Compilation -- TEMPLATE

Scope executed: [Sec.3.1-3.7].
Files made: [`pc_xacml_primary.contract.json` (+sha), `touch.json`, `phase3_manifest.json`, schemas, tests].
Code produced + how coded: [`models.py` (frozen dataclasses, canonical JSON), `compile_contract.py` (inputs->graph S0->{S_permit,S_nonpermit}->fiber-homogeneity open/closed), `derive_touch.py` (Sec.6 pseudocode literal), `independent_touch.py` (no shared imports, own C14N), `check_no_manual_labels.py` (scan roots + allowlist); import-ban assert details].
Benchmarks: [T01 `{E}` derivation trace (which of H/PR/Lambda changed), T02 byte-agreement proof].
Tests run: [`test_no_manual_touch_labels`, `test_touch_derivation` -- commands + results].
Gate verdict: [7 Phase-3 boxes; on mismatch -> `TOUCH_DERIVATION_MISMATCH`].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [dual code paths, zero shared helpers, no fitted parameters].

## 7. Phase 4 Log -- Exact All-Freeze Evaluation -- TEMPLATE

Scope executed: [Sec.4.1-4.6; freeze order as run].
Files made: [`F000...F111.json` + `K_table.json` + `identified_set.json`; solver sources; schema].
Code produced + how coded: [`solve_freezes.py` (D33 removal rule `T(q)intersectS!=EMPTY`, ID-only ops per INV-12/13, exhaustive enumeration), `independent_solver.py` (separate tree enumeration); agreement diff].
Benchmarks: [8-row K table actual vs predicted `[1,INF,1,1,INF,INF,1,INF]`; closer-existence + cost per row; nontriviality witness freeze ID].
Tests run: [`test_all_freezes` -- command + results].
Gate verdict: [6 Phase-4 boxes; solver mismatch -> `SOLVER_MISMATCH`; trivial -> `NONTRIVIALITY_FAIL`; honest-mismatch handling if applicable].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [geometry benchmark disjoint from sealed expectation; dual solvers].

## 8. Phase 5 Log -- Falsification, Sensitivity, Anti-Circularity -- TEMPLATE

Scope executed: [Sec.5.1-5.13; note temp-copy discipline -- `external/` never mutated].
Files made: [`artifacts/audits/*` (14+ JSONs), 5 test files, `run_phase5.sh`].
Code/procedures + how: [per-control method: byte-flip script, MustBePresent strip, wrong-category/datatype builders, extra-attribute injector, perturbation set (whitespace/order/format/rename), OUT_OF_SCOPE split, cost sweep 0.5/2/10, wrong-answer-1/2 sweep, 4 ablations, label-injection, leakage graph builder (import+open-trace), clean-rerun procedure].
Benchmarks (ENTIRELY different from sealed expectation): [C01-C09, R01-R06 actual verdicts -- 5/5 corruptions detected, canary rejections, invariance holds, INTERFACE_CHANGED verdict, cost-structure invariance, ablation kills x4, injection detected, leakage clean, byte-identical repro].
Tests run: [all Phase-5 tests -- commands + results].
Gate verdict: [13 boxes; on fail -> `INDEPENDENT_REPRODUCTION_FAIL` or specific category].
WorkPlan compliance: [YES/NO + detail]. Models trained: none. Anti-overfit note: [this phase IS the brutal-disjoint-benchmark proof -- list disjointness per control].

## 9. Phase 6 Log -- Seal, Audit Package, Manuscript Report -- TEMPLATE

Scope executed: [Sec.6.1-6.6].
Files made: [`FINAL_RESULT.json` (observed-values evidence), `MANIFEST.sha256`, `CHANGELOG.md` entries, `FINAL_AUDIT.md` (12 sections), `PC-XACML-S3PLUS-v1.tar.gz` + `.sha256`, `run_phase6.sh`/`reproduce_all.sh`].
Code produced + how coded: [`build_audit_report.py` (hash-assembled numbers, Sec.18.2 blocklist linter), seal builder (canonical JSON, `tar --sort-name --mtime`), `final_result.schema.json` validation].
Benchmarks: [full `tests/` green transcript; archive reproducibility (re-tar hash match); claim-wording audit vs `allowed_claims.md`].
Gate verdict: [6 Phase-6 boxes; outcome emitted (one of 8); manuscript rule observed -- no paper edits before seal].
WorkPlan compliance: [YES/NO + detail; post-seal changes -> new version]. Models trained: none.

## 10. Standing Verification Checklist (update as phases complete)

- [x] Spec deeply read (Secs.0-26) in working copies; authoritative `IMPLEMENTATION_SPEC.md` sealed in Phase 1 (69241 bytes, 2351 lines, raw==normalized sha256 `92c55d42`); values pinned.
- [x] Repo cloned, inspected (LICENSE-only `a4d4bfc`), previous-results clearing verified (nothing to delete).
- [x] `WorkPlan.md` created with 6 unmerged phases, per-phase scope/files/code-how/benchmarks, no-training contract, full traceability.
- [x] `Path.md` created with review log, state, bootstrap entry, per-phase templates.
- [x] Phase 1 gate: 10/10 PASS (see Sec.4 evidence; no STOP; `SOURCE_REPRODUCTION_FAIL` not triggered).
- [x] Phase 2 gate: 2A PASS + packet sealed; human blind verdict PENDING -> BLOCKED_PENDING_ADJUDICATION (not a failure; no outcome emitted; see Sec.5 evidence).
- [x] Amendment 001: prospective cold-model substitution sealed pre-execution (0 evals); 18 gate controls green; amended gate NONUNANIMOUS exit 3 on three valid records (failure-seal route, zero executions); one non-conforming input mechanically rejected (Sec.3.11); original hashes/seals invariant; EOL follow-up committed; fresh-clone suite green (42+1); see Sec.3.10/3.12.
- [ ] Phase 3 gate (TOUCH_DERIVATION_MISMATCH or dual-agreement pass).
- [ ] Phase 4 gate (SOLVER_MISMATCH / NONTRIVIALITY_FAIL or K pass).
- [ ] Phase 5 gate (13/13 falsification pass).
- [ ] Phase 6 gate (sealed outcome + reproducible archive + claim-locked audit).
- [ ] No spec section omitted (re-verify at seal against Sec.10 map in WorkPlan).
- [ ] `CHANGELOG.md` complete; `MANIFEST.sha256` covers all reproduction artifacts.
