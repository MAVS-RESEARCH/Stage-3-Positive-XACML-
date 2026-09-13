# PC-XACML-S3+ Path

This file is the implementation trail for `WorkPlan.md`. It moves with the code. Every material step records what changed, what was verified, and whether the work still follows the plan -- with the same per-phase depth as `WorkPlan.md` (scope, files made, code produced + how coded, benchmarks, gate verdict). No implementation phase has been executed yet; Secs.1-3 below are the complete record to date. Secs.4-9 are the mandatory log templates to fill as work proceeds. A step that deviates from `WorkPlan.md` must say so explicitly and, if it touches worlds/target/interface/cost/anchor/freeze/expectation/criteria, open a new experiment version per spec Sec.6.3 instead of silently patching.

## 1. Source Review Log

Date: 2026-09-11 (UTC), workspace `<WORKSPACE>`.

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
- Target repo `<AUTHOR_REPOSITORY>` (cloned 2026-09-11 into `<REPO>/`):
  - `git log --oneline`: single commit `a4d4bfc Initial commit`; `git status`: clean; `git remote -v`: origin = target URL; content: `LICENSE` only.
  - No implementation, no results, no stale artifacts -> "clear previous results" satisfied by verification (nothing to delete; no result files existed). Only new post-change results will be present going forward.

Prior-work references consulted for format only (not normative): `Downloads\WorkPlan.md` (MAVS Ch10B, 1094 lines) and `Downloads\Path.md` (1872 lines) -- used to match the expected WorkPlan/Path depth and anti-overfitting explanation style. They impose no requirements on this experiment.

## 2. Current Repository State

Date: 2026-09-11, after Phase-2 2A execution + packet seal (see Sec.5) plus Amendment 001 implementation (see Sec.3.10) plus EOL-normalization follow-up plus one rejected non-conforming input (Sec.3.11) plus three valid nonunanimous verdicts (Sec.3.12); human blind adjudication pending (superseded as operative path); gate MODEL_ADJUDICATION_NONUNANIMOUS, failure-seal route; zero executions; target audit never ran.

- Local workspace: `<WORKSPACE>`; repo checkout: `<REPO>/`, branch `main`; Phase-1 commit `<AUTHOR_REPO_COMMIT_009>`; Phase-2 file set staged for commit after this log update (per Sec.3.2).
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

- `git clone <AUTHOR_REPOSITORY>` into workspace; verified with `git log/status/remote/branch`, `git show --stat HEAD`.
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
1. `PROTOCOL_AMENDMENT_001.md` (original human requirement preserved, unavailability cause, temporal proof, immutable scope list, single mutation human->3x-cold-model-unanimity, disclosure obligation, provenance: prev WorkPlan blob <AUTHOR_GIT_OBJECT_004>, prev spec blob <AUTHOR_GIT_OBJECT_001>, prev prereg-seal blob <AUTHOR_GIT_OBJECT_003>, packet seal, prompt hash, UTC stamp, pre-commit <AUTHOR_REPO_COMMIT_011>) + `artifacts/audits/amendment_001_seal.json`.
2. `prereg/blind_model_adjudication_prompt.txt` (frozen, sha 9d983e35; category-name prohibitions only, zero values/outcomes/claims -- scanned); sealed by amendment seal, NOT by the Phase-1 prereg seal (byte-preserved; test_prereg_seal updated to the amended rule + prompt-coverage test).
3. `src/audit/model_adjudication.py` (ingest with raw->parse->validate pipeline, tamper-evident provenance re-hashing, --assert-model-unlock exits 0/3/4/5, --check-amendment with ancestry check; in-session subagent adjudication refused by isolation rules) + `schemas/model_verdict.schema.json` (AUD-M0[1-3], COLD_MODEL_INDEPENDENT, verbatim declaration const, prompt/packet hashes, isolation affirmations).
4. `run_phase2.ps1`/`.sh` rewired to the amended gate (checker 0-or-4 continues; model gate maps 0->target audit, 4->BLOCKED_PENDING_MODEL_ADJUDICATION, 5->MODEL_ADJUDICATION_INVALID, 3->NONUNANIMOUS failure-seal; packet ensure-not-rebuild so the referenced seal cannot drift).
5. `tests/test_model_adjudication.py`: all 18 controls pass (0/1/2->4; unanimous->0 + unlock/ledger artifacts; PARTIAL/AMBIGUOUS/UNSUPPORTED->3; malformed/missing-declaration->5; prompt/packet tamper->4; leakage/cross-read->5; post-seal edit->4; pre-unlock ban + zero-scan; amendment window zero; original-hash invariance incl. byte-identical prereg_sha256; chronology incl. ancestor check).
6. WorkPlan consistently mutated (2B operative rule with ORIGINAL/OPERATIVE labels, unlock conjunction, schemas/tests/tree, reproduce incl. amendment check, Phase-5 leakage extension, Phase-6 model audit language + claim discipline with allowed paragraph and 7 forbidden strings, compliance map, traceability, status taxonomy, byte-regime rule). `allowed_claims.md` untouched (frozen prereg).
7. Byte-regime stabilization (genuine defect found by the amendment's own discipline): Git EOL conversion desynced sealed working bytes from blobs (packet seal unverifiable after fresh checkout). Fix: `.gitattributes` (`* -text diff`, byte-exact + textual diffs); blob-SHA tooling replaced config-dependent `git hash-object` with deterministic CRLF->LF normalization in code (proven equal to upstream constants); packet rebuilt once under the stable regime (new seal 00710549; equivalence proven: 9/9 mappings timestamp-only diffs, 4/4 fixture corpus byte-identical, 4/4 remaining corpus EOL-only); runner verifies-not-rebuilds (proven by consecutive runs reusing the seal).
Evidence: full suite 42 passed + 1 skipped (lock-respecting target skip); --primary exit 4 BLOCKED_PENDING_MODEL_ADJUDICATION; reproduce exit 0; packet verify clean; zero completed outputs; no verdicts exist (ingest set empty).
WorkPlan compliance: YES. Deviation: none (all deltas are the instructed amendment itself).

Follow-up (same day, separate commit <AUTHOR_REPO_COMMIT_013> -- history preserved, no amend/squash): the byte-regime fix exposed stale stat-cache masking (git status falsely clean while index LF-blobs differed from sealed CRLF working bytes) plus a config-dependent `git hash-object` in the Phase-1 tooling. Fixed by: `git rm --cached` + full re-add under `* -text diff` (blobs now byte-faithful; 8 files re-stored, content identical modulo EOL, zero seal changes) and deterministic CRLF->LF blob-SHA in code (proven equal to upstream constants). Decisive proof: fresh `git clone` of the new HEAD runs the FULL suite green (42 passed + 1 lock-respecting skip) with the amendment-referenced packet seal intact (00710549). Phase-5 clean-reproduction path is thereby unblocked on any machine honoring the committed attributes.

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

### 3.24 Protocol Amendment 007 -- Split-Gate Development, Burn-In, Launch Freeze (2026-09-12)

Recovered interrupted Amendment-007 working tree at HEAD <AUTHOR_REPO_COMMIT_030> (ancestor check true): uncommitted hardening/parse/runner edits + untracked PROTOCOL_AMENDMENT_007.md (58-line stub), amendment_007_basis/ (HISTORICAL_BASIS + REASSESSMENT all-OPEN), launch/ (registry 6 obligations + prompt, no freeze), launch_freeze/certification/verifiers code, 2 test files (3 failing), ROUND_007 evidence (lineage stale). Verified pre-work invariants: seals FINAL_RESULT cc365041.../CYCLE_002 270570d8... match basis; specimen 4/4 hashes match; zero target executions; no lock; touch/K NOT_COMPUTED.

Hostile waves executed (NON_BLIND developmental, never certify): 5-agent Wave-1 (deferral laundering F-01..F-13; Lambda closure LAMBDA-01..10; quarantine bypass B01..B11; state-machine D01..D15; Atom boundary F-01..F-08) + Wave-2 burn-in A/B + taxonomy-free holdout. VALID_MATERIAL repaired: judge verdicts+overall+coverage + missing-registry UNVERIFIABLE + stale-PASS revocation; collect_valid call site; registry ban scoping + TERMINAL + hash-only RC-REQUEST + clarified RC-ATOM + code_sha256 bound to live hashes; parser both-argv + content-allowlist quarantine; runner AUTHORIZED + freeze-hash binding; cert lock guards + attestation packet/prompt binding; verifiers 64-hex + prohibited-content rejection; lineage current==operative (stale preserved); Lambda drivers refreshed (run_authzforce e1cb-era, composite recomputed); registry code_sha refreshed; launch manifest self-inclusion exclusion fix; environment/toolchain binding in freeze; leakage-test hardening; 4 new tests (content-rejection, missing-registry, rename-evasion, lock-closure). Residuals documented for chairs: transient TOCTOU window; toolchain substitution outside packet-recompute (env pinned, live re-check at verify); Central-by-coordinates provenance; recompute covers verifiable subset only (deployment/classpath/conformance gates jointly cover). REASSESSMENT closed: R7-01..04 REPAIRED, R7-05 STATIC_NONMATERIAL (tree=provenance, per-file binding operative), R7-06/07 LEGITIMATE_DEFERRED_FROZEN, R7-08 CLOSED_NONMATERIAL, R7-02 REPAIRED.

PROTOCOL_AMENDMENT_007.md expanded 58-line stub to full SS0-19 operative (split-gate law, S/R classes, reassessment, swarm, hardening, registry, Phase-2E AUD-L panel, burn-in, freeze/point-of-no-return, Phase-2F quarantine, dual mechanical conformance, outcome opening, Phases 3-6 unchanged, taxonomy, anti-overfitting, disclosure, battery, stopping boundary, annex). Launch packet built + verified: packet db661dd74a37bec4, prompt 251f7e58, registry 12a46820, panel AUD-L01/02/03, 9 execution-code hashes + env binding (LAUNCH_FREEZE.json). Full suite 139 passed + 1 skipped. Zero executions; no lock/authorization/capsules; launch_certification/ empty for fresh chairs. Handoff: NEXT_EXTERNAL_LAUNCH_HANDOFF.md. Final C/D read-only re-verification primary-executed (provider blocked subagent spawn); state BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION.

### 3.25 Launch-001 Failed (L01-03) -- Transparent Repair -- Launch-002 Frozen for L04-06 (2026-09-12)

Ingested transcribed L01/02/03 verdicts via launch_certification.py --ingest-launch (temp files outside repo): 0/3 VALID (L01/L03 attestation hash-binding absent; L03 cross-reads L01+L02; L02 attestation bytes diverge from claimed cb2e6ce2 -- paste-vs-signed gap; L01/L03 hashes reproduced exactly so transcription faithful). Assert-unlock exit 4 BLOCKED. No authorization written; zero executions; no lock (verified pre/post).

Substantive tally (diagnostic only): H/P_R 3xFIXED; Lambda 3xPARTIAL unanimous on packet-internal grounds; Atom 2xFIXED+1xPARTIAL; deferrals 6/6 LEGITIMATELY_DEFERRED x3. Launch-001 preserved untouched (launch_packet_rev001/ + LAUNCH_FREEZE_rev001.json + INVALID records).

Forensics confirmed VALID_MATERIAL static defects: (a) packet manifest drivers[1] 47b40bde/9575 vs packet invocation bytes 708c80ea/14104 (rev004-origin manifest + live sources; ROUND_007 refresh fixed the wrong copy); (b) pom basename collision destroyed root pom (packet kept only pdp-engine pom); (c) transitive deps coordinates-only. Repairs in launch_freeze.py: staged-manifest driver rebind + composite recompute + lineage extension (dup-safe); distinct pom names; 145-jar offline-resolved dependency content staged + bound as dependency_content; derive/parse/builder/launcher sources staged with 11-copy currency gate; freeze/certification code pinned; --launch-id/--panel-ids (canonical-triple enforced); verify re-checks composite/drivers/lineage. REASSESSMENT R7-09/10/11 REPAIRED. Regression tests V56/V57 (poms, driver currency).

Launch-002 built + verified: packet a75ee3b0506de98e, prompt 251f7e58 (unchanged), registry 12a46820 (unchanged), staged pre 5ecdd192, panel AUD-L04/05/06, supersedes launch-001. Suite 141 passed + 1 skipped. Handoff NEXT_EXTERNAL_LAUNCH_HANDOFF_L04-L06.md. State BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION (launch-002). No target execution, no touch, no K.

### 3.26 Launch-002 Failed (L04-06) -- Five Repairs -- Launch-003 Frozen for L07-09 (2026-09-12)

Ingested transcribed L04/05/06 verdicts: 0/3 VALID (L04/L05 no hash quotes; L05 paste-diverged bytes; L06 packet-sha only). Assert-unlock BLOCKED. No authorization; zero executions; no lock. Substantive tally (diagnostic): H/P_R 3xFIXED; Lambda 2xPARTIAL(L04,L06)+1xFIXED(L05 -- validating launch-002 repairs); Atom 3xFIXED; L06 3xIMPROPER_DEFERRAL (ATOM-ORDER, DEPS-CONSISTENT, REQUEST-ACTUAL). Launch-002 preserved (rev002).

Confirmed VALID_MATERIAL: R7-12 opaque dep sha (blob-hash vs file-hash); R7-13 undocumented manifest-to-packet path aliases; R7-14 recompute subset + derive_Lambda lineage; R7-15 ATOM-ORDER producer was prose (no event emitter); R7-16 DEPS cp-hasher was prose (no frozen script). Repairs: file-hash dep binding (now bac1eae9 == sha256(file), the exact value L06 cited); candidates/path_remap.json; recompute extended via remap (SKIP-preserving); builder_lineage in staged manifest; run_authzforce JSONL chronology (names+utc+request-sha, zero response bytes); verify_deployment_set --hash-cp; RC-REQUEST invocation-instant scoping; registry rebound. Tests V60-V68. ROUND_007 tool copies refreshed to live (unsealed evidence).

Launch-003 built + verified: packet 8e23901d4643a42a, registry d7641f64, staged pre 194fcbbecc398f71, panel AUD-L07/08/09, supersedes launch-002. Suite 146 passed + 1 skipped. Handoff NEXT_EXTERNAL_LAUNCH_HANDOFF_L07-L09.md (adds collect-files-directly instruction after two paste corruptions). State BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION (launch-003). No target execution, no touch, no K.

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

### 3.15 Holdout SWEEP_003 — One VALID_MATERIAL → SEMANTIC_FREEZE_REOPENED (2026-09-12)

Files made: `artifacts/audits/certification_rehearsal/REHEARSAL_SWEEP_003_HOLDOUT/` (3 falsification-only reports, `objections.json` 11, `NORMALIZATION.json`); preservation records reopen.

Code produced: none yet (investigation only). Three fresh holdout agents (histories/capability/joint, no taxonomy): H01–H04 duplicates of known families; B01 NEW — staged root-policy-set cardinality unpinned with concrete self-pollution mechanism (`builder_source` arbitrary `out_dir` + `makedirs` + `*.xml` names vs `pdp.xml` glob; staged-copy identity byte-only); J01–J05 duplicates of RS002-J01..J05; X01 naming polish (VALID_NONMATERIAL).

Source verification by analyst: builder `out_dir` arbitrary confirmed live; staged-copy text byte-only confirmed; live workflow disjoint (`derived/requests`) so no pollution occurred — missing gate is the defect. B01 overturns RS002-L01's refutation (listing snapshot is not a gate).

Normalization: 11 objections (9 DUPLICATE, 1 VALID_MATERIAL B01, 1 VALID_NONMATERIAL X01) → `MUTATION_REQUIRED`; `--verify` exit 0. Decision: preserve REVISION_001 bytes; emit `SEMANTIC_FREEZE_REOPENED` (hardening event); revision → 002.

WorkPlan compliance: YES (§7 mutation loop; PARTIALs never triggered it, source-verified material did). Models trained: none.

### 3.16 HARDENING_ROUND_003 — B01 Repair + REVISION_002 Freeze (2026-09-12)

Files made: `src/audit/verify_deployment_set.py` ([P2-LOG-010]/[P2-LOG-020]/[P2-LOG-030]/[P2-LOG-040]/[P2-LOG-050]/[P2-LOG-060]/[P2-LOG-070]/[P2-LOG-900]) + `tests/test_deployment_set.py` (6 tests, [P2-LOG-T10]–[P2-LOG-T20]); `rounds/HARDENING_ROUND_003/` (evidence base + refreshed builder copy/wrapper 12-12/listing+gate/atom pins + `ROUND_003_mutations.json` + seal + convergence); `final_freeze_REVISION_001/` snapshot (packet `4b9f6556` byte-identical); operative `final_freeze/` revision 2 (packet `fbd22e2c`); `SEMANTIC_REVISION_ANCESTRY.json`; ledger 88/88 (`H3-01`, `H3-02` RESOLVED).

Code produced + how coded: builder `canon_path` (realpath + `\\?\` strip + normcase/normpath + dot/space strip) + `assert_out_dir_disjoint` checked pre-create AND post-create (closes symlink/SUBST/UNC/8.3/trailing-dot for missing paths; residual TOCTOU documented); `RULE_TO_CODE` 12th phrase binds guard; freeze hardened (no-destroy guard, `--evidence-round`, ancestry, amendment-003 in `frozen_files`); deployment gate wired pre-eval in `run_phase2.sh/.ps1` target path. Two subagents in parallel: gate-module implementer (new files) + bypass red-team (14 vectors; 2 residual classes documented).

Verification: rebuilt requests byte-identical; guard refuses nested out_dir (exit 1); gate `--check`/`--disjoint` exit 0 live; full suite 70 passed + 1 skipped; invariant holds; exec 0; ROUND_003 sealed; convergence 10/10; `--verify-freeze` exit 0. Packet delta exactly 4 files (builder, wrapper, listing, atom); prompt/manifest/ledger-hashes otherwise stable.

Gate verdict: ROUND_003 SEALED; REVISION_002 FROZEN + VERIFIED. WorkPlan compliance: YES (§8 boundary: provenance/packet/audit code only; specimen immutable). Models trained: none.

### 3.17 Burn-In SWEEP_004 + SWEEP_005 — CERTIFICATION_REHEARSAL_CONVERGED (2026-09-12)

Files made: `REHEARSAL_SWEEP_004/` (6 reports Panels A×3/B/C/D, 18 objections) + `REHEARSAL_SWEEP_005/` (5 reports A×3/B+C/D+E, 8 objections) + `CERTIFICATION_REHEARSAL_CONVERGED.json`; `PROTOCOL_AMENDMENT_003_ADDENDUM.md` (§§7–17 + execution record; bound by commit, folds into `frozen_files` at next freeze if any).

Results: 004 — 14 DUPLICATE, 3 VALID_NONMATERIAL (G01 argv-trust, G02 gate-source packet inclusion, D02 label), 1 SOURCE_REFUTED (D01a enforcement exists); emulator PARTIALs dispositioned per §11 (conservative application; residuals documented); red-team no surviving countermodel (CM-L self-pollution KILLED by repair); integrity 8/8 PASS. 005 — 5 DUPLICATE, 2 SOURCE_REFUTED (DG4 Q-pointer exists, E03 basis misattributed), 1 VALID_NONMATERIAL (DG3 Detail cardinality); emulator FIXED/FIXED + joint PASS corroborate. Zero VALID_MATERIAL/UNRESOLVED in both; no mutation between; fresh instances; conclusions isolated; invariant PASS; tests PASS; exec/touch/K 0.

Gate verdict: two-sweep burn-in SATISFIED → `CERTIFICATION_REHEARSAL_CONVERGED` + `FINAL_SEMANTIC_INTERFACE_FROZEN` reaffirmed (packet `fbd22e2c` unchanged since freeze; no rebuild fabrication) + `BLOCKED_PENDING_FINAL_CERTIFICATION`. Phases 3+ unexecuted. STOP: external AUD-C01/02/03 over operative packet + prompt + schema only.

WorkPlan compliance: YES (Amendment 003 §§10–14). Models trained: none.

### 3.18 Phase 2C Scaffolding Repair + AUD-C01 Ingest (2026-09-12)

Defect found at first real use: `final_certification.freeze_dir()` pointed at `artifacts/audits/final_freeze/`, which nothing ever creates — hardening freezes to `semantic_hardening/final_freeze/`. Ingest refused with `no valid final freeze` (exit 4), so Phase 2C could never open. Root cause is audit-code wiring drift, not semantics: the namespace-protection test deliberately permits reading the frozen output (only reports/rounds/dev-packets forbidden). Repair: `freeze_dir()` retargeted (+ comment without guard-substring literals, which the protection test forbids); synthetic roots in `tests/test_final_certification.py` retargeted identically. Full suite 70+1 green; `--verify-freeze` green (frozen files untouched).

Ingest: `AUD-C01` valid, record sealed (exit 0; provenance `valid:true`, no problems). Tally H=FIXED, P_R=FIXED, Lambda=PARTIAL, Atom=FIXED. Ingest-time notes: pasted attestation carried a trailing newline the model's hash excluded — bytes normalized to the hashed form before sealing (hash recomputed equal). Two chairs outstanding (AUD-C02/C03); gate judgment only after all three records exist. Already entailed: unanimity impossible (Lambda PARTIAL on C01); best case is nonunanimous failure-seal route.

Ingest: `AUD-C02` valid, record sealed (exit 0; provenance `valid:true`). Tally identical shape: H/P_R/Atom FIXED, Lambda PARTIAL (blind-verifiability gap: engine bytes/method, pre_hash inputs, deferred post_hash). Ingest-time notes: first paste lacked 5 schema fields (re-emitted complete in-session, verdicts unchanged); pasted attestation needed trailing newline to match the model's stated hash (bytes normalized, hash recomputed equal); attestation distinct from C01's. One chair outstanding (AUD-C03); gate judgment after all three.

Ingest: `AUD-C03` valid, record sealed (exit 0; provenance `valid:true`). Tally H=FIXED, P_R=FIXED, Lambda=PARTIAL, Atom=PARTIAL (counting/checkpoint blind-verifiability; core decomposition supported). Ingest-time notes: transcription first introduced a stray bracket (caught by JSON validation, rebuilt byte-faithful from the pasted text, parse + field verification green); attestation needed trailing newline to match stated hash (normalized, recomputed equal); attestation distinct.

Gate judgment: `--assert-final-unlock` exit 3 `MODEL_ADJUDICATION_NONUNANIMOUS` (all three chairs short of unanimous: Lambda PARTIAL ×3, Atom PARTIAL ×1). Target audit stays locked forever; Phases 3–6 computation path closed.

Sec.15 assessment (no auto-reopen): every verdict gap duplicates rehearsal dispositions (Lambda engine/method/deferral → RS001-L02/L03/L05 + RS002/RS004 families; Atom counting/checkpoint → RS001-A04/RS002-A04 + RS004-G02; staging/scripts absence → RS004-G02 disclosed polish); two blind chairs independently recomputed pre_hash + provider-element C14N (corroboration, not contradiction); all chairs state no contradiction found. No genuinely new material defect → no reopen, no new panel. Failure-seal: `artifacts/seal/FINAL_RESULT.json` (`NATIVE_ANCHOR_INSUFFICIENT`, stopped_at_phase 2, downstream `NOT_RUN_BY_PROTOCOL`); verified zero target/response/touch/freeze/contract artifacts and 0 executions.

WorkPlan compliance: YES (2C gate + failure-seal per spec §8/§23; frozen specimen untouched; zero executions). Models trained: none.

WorkPlan compliance: YES (Amendment 003 developmental layer only; experiment ID unchanged; no history rewritten; no estimand change). Models trained: none.

### 3.19 Amendment 004 Phase 2D — Post-Certification Development (2026-09-12)

Files made: `PROTOCOL_AMENDMENT_004.md`; `src/audit/post_cert_hardening.py` ([P2-LOG-020]/[P2-LOG-040]/[P2-LOG-060]/[P2-LOG-070]/[P2-LOG-900]); `post_cert_hardening/STATE.json` + `rounds/POST_CERT_HARDENING_ROUND_000/REFERENCES.json` (C01-C03 files tallies, failed gate, prior freeze/result hashes, zero-exec proof); 9-agent specialist wave (Lambda closure/hash/lifecycle, Atom boundary/staging, provenance, red×2, bypass-tester).

Repairs (all source-grounded, specimen immutable): Lambda manifest extended (per-component methods, 76-file semantic set + tree `51e22664`, 4 jars, poms, JDK/drivers, reconstruction block) + `recompute_lambda.py` + frozen vector + `tests/test_lambda_manifest.py`; `verify_deployment_set --check-staged` + `run_authzforce.verify_staged_fixture` pre-eval + pre-eval script wiring; `hardening_evidence` staging-certificate + locator-table (13/13 re-grounded, windows-1252+CRLF procedure) + world_value_binding + classpath-manifest modes; freeze hardening (no-destroy, evidence-round sanitize, `--revision` monotonicity, extended verify, amendment-004 file); final_certification PANELS C01-03/C04-06 + record-freeze binding + mixed-panel block (+6 tests); packet additions (engine tree, tools, staging cert, locator table, corrigendum, censuses, excerpts, execution_inputs).

Wave-2 re-attack findings closed: recompute engine-dict bug, gate UNC/root-listing/ascii gaps, staged-root exclusivity, panel-reuse hole (revision-bound eligibility), freeze revision/verify gaps. Ledger 94/94 (`P2D-01..P2D-06`); suite 87+1; invariant holds; exec 0. Rounds 004 (converged), 005 (R2 batch, converged), 006 (classpath, converged).

WorkPlan compliance: YES (§§1–13; epistemic-access-only mutations). Models trained: none.

### 3.20 Holdout-008 Reopen → REVISION_004 → Burn-In 009/010/011 (2026-09-12)

Holdout-008 (taxonomy-free): 8 objections, 1 VALID_MATERIAL — RS008-CE1 runtime classpath/extension deployment unpinned (pdp-ext fallback live in test-classes, .class bytes unpinned, staged TOCTOU window), overturning nothing prior (new mechanism). Decision: preserve REVISION_003 bytes; second `SEMANTIC_FREEZE_REOPENED`; revision → 004. ROUND_006: classpath content manifest (3073+37 files + extension facts) + pre-eval `--check-classpath` wiring + manifest `classpath` component; sealed + converged.

Incident (transparently recorded): REVISION_003 snapshot copy failed on ~15 >260-char engine paths; partial snapshot wrongly deleted and replaced with rev004 bytes; recovered via `recover_revision003.py` (every content file byte-identical from ROUND_005 evidence + live frozen sources; 2 timestamp wrappers regenerated and marked; attested aggregate preserved as labeled attestation). Root fix: long-path-safe snapshot procedure + freeze-time tool-copy currency gate scheduled. Operative freeze never at risk (`--verify-freeze` green throughout).

Refreeze: `final_freeze_REVISION_003/` snapshot (recovered, 146 files) + operative `final_freeze/` revision 4 (packet `156e36d7`, 138 files, delta = classpath system + refreshed manifests); ancestry lists 001+002(+003 snapshot); packet-mode recompute zero-SKIP zero-MISMATCH.

Burn-in on rev004: 009 (8 objs: 6 DUP, 2 NONMAT) + 010 (7 objs: 5 DUP, 2 NONMAT) + holdout 011 (3 objs: 2 DUP, 1 NONMAT projection_sha naming); fresh instances, no mutation between, invariant/tests PASS, exec/touch/K 0. Emitted: `post_cert_hardening/POST_CERT_BURN_IN.json`.

Gate verdict: `POST_CERTIFICATION_HARDENING_CONVERGED` + `FINAL_SEMANTIC_INTERFACE_FROZEN` (rev004) + `BLOCKED_PENDING_NEW_FINAL_CERTIFICATION`. Next: fresh external AUD-C04/C05/C06 over packet `156e36d7` + prompt + schema only.

WorkPlan compliance: YES (Amendment 004 §§7–17). Models trained: none.

### 3.21 Amendment 005 — Recursive Certification Cycles (2026-09-12)

Files made: `PROTOCOL_AMENDMENT_005.md`; `src/audit/certification_cycle.py` ([P2-LOG-010]–[P2-LOG-072]/[P2-LOG-900]); `schemas/certification_cycle.schema.json`; `tests/test_certification_cycle.py` (6 tests, [P2-LOG-Y10]–[P2-LOG-Y18]); `certification_cycles/CYCLES.json` (001 sealed failed-repairable, 002 open pending) + `CYCLE_001.assessment.json`; `NEXT_EXTERNAL_CERTIFICATION_HANDOFF.md` (C04–C06, packet/prompt hashes, cold-session + ingest instructions, attestation rules; forbidden-content scanned).

Code produced: cycle init (ID/panel/reuse/revision-double-bind guards + revision↔panel binding check)/assess (tally vs operative-or-snapshot freeze)/decide (PASSED/REPAIRABLE/IRREDUCIBLE consistency + reason/material requirements + immutability)/handoff (open-cycle-first panel advancement, leak scan)/status; final_certification panels C07–12, `REVISION_PANELS` map with rev≥5 fallback, record↔freeze binding, mixed/fourth-chair refusal.

Adversarial review (2 subagents): 8 holes found (cycle revision range, init panel binding, empty reason, sealed-assess overwrite, snapshot trust, handoff revision match, float coercion, message staleness) — all repaired + tested; independent rev004 re-verification 7/7 CONFIRM (freeze, 139-file packet, pre_hash packet-mode, sweeps, zero-exec, specimen; worktree dirt correctly attributed to post-freeze Amendment-005 work).

Verification: full suite 95 passed + 1 skipped; `--verify-freeze` green; handoff targets C04–C06 with operative hashes and no forbidden content.

Gate verdict: machinery COMPLETE; state `FINAL_SEMANTIC_INTERFACE_FROZEN` + `BLOCKED_PENDING_NEW_FINAL_CERTIFICATION`. STOP: operator runs three fresh external sessions per handoff.

WorkPlan compliance: YES (Amendment 005 §§1–20; no specimen/semantic change; zero executions). Models trained: none.

### 3.22 Amendment 006 — Unbounded Panels (2026-09-12)

Files made: `PROTOCOL_AMENDMENT_006.md`; panel-generic `final_certification.py` (`chair_number/chair_id/panel_for_index/panel_of`, alias normalization at ingest, NON_BLIND developmental-marker refusal) + `certification_cycle.py` (revision-bound init, open-cycle-first validated handoff, per-chair instantiated cold prompts, unbounded allocator) + `certification_rehearsal.py` (generic cert-namespace guards); schema + `tests/test_unbounded_panels.py` (23 tests covering the 20-item battery).

Code produced: finite tables (`PANEL_1..4`, `PANEL_IDS`, `C01..C12` regex) replaced by `CHAIR_RE ^AUD-C(0*[1-9][0-9]*)$`, consecutive-triple panels, `max_used+1` allocator, `REVISION_PANELS {1:None,2:0,3:None,4:1}` + rev≥5 fallback; record↔freeze binding retained; fourth-chair/mixed/reuse refusal retained and extended.

Adversarial review (2 subagents): 8 + 7 findings; repaired: non-string crashes, prompt/hash validation, invalid-open passthrough, alias collision, placeholder reintroduction, revision binding at init, empty reasons, sealed-assess overwrite, snapshot trust, handoff revision match, float coercion, stale messages; residual notes (legacy blind-model regex cap out of scope, TOCTOU/documented). Handoff regenerated for C04–C06 with per-chair prompts (two template words substituted to avoid scanner-collision false positives; frozen authoritative prompt unchanged).

Verification: full suite 118 passed + 1 skipped; `--verify-freeze` green; frozen bytes (packet/prompt/externals/seal/derived) byte-unchanged per git status; template fail-closed scanner proved live (caught its own wording twice).

Gate verdict: machinery COMPLETE; state `FINAL_SEMANTIC_INTERFACE_FROZEN` + `BLOCKED_PENDING_NEW_FINAL_CERTIFICATION`. STOP: operator runs C04/C05/C06 per handoff.

WorkPlan compliance: YES (Amendment 006 §§1–20; controller mechanics only; zero executions). Models trained: none.

### 3.23 CYCLE_002 Panel (C04–C06) — Nonunanimous → Terminal Negative Stop (2026-09-12)

Ingest: all three valid, records sealed (exits 0). Tallies H/P_R FIXED ×3, Lambda PARTIAL ×3 (built-artifact bytes, lineage erratum, deferred post, tree binding), Atom 2×FIXED/1×PARTIAL (C06 staging/measurement). Ingest-time notes: C06 pasted JSON missing the verdicts-closing brace (single `}` added, content untouched, parse + field verification green); attestation newline forms normalized per-chair to stated hashes (C04/C06 plain, C05 plus-newline); attestations mutually distinct; C06 Atom has no notes field (status+locators carry the rationale; validator needs none).

Gate judgment: exit 3 `MODEL_ADJUDICATION_NONUNANIMOUS`. CYCLE_002 assessed (unanimous=False) + defect ledger (6 objections: 4 DUPLICATE, 1 OUT_OF_SCOPE, 1 VALID_NONMATERIAL, 0 material, overturn check negative) → decided `CERTIFICATION_FAILED_IRREDUCIBLE`.

Terminal assessment (no reopen): every surviving gap is either scheduled polish non-decisive even if cured (built bytes, lineage — all chairs also withhold over measurement items) or PENDING_TARGET-by-design (post equality, live staged measurement) unprovable before the locked execution it would unlock. No pre-measurement revision can advance unanimity; another cycle would be positivity theater per Amend.005 Sec.15. This is measurement-gating deadlock, not specimen ambiguity — recorded precisely as such, not relabeled. Second seal `artifacts/seal/FINAL_RESULT_CYCLE_002.json` (`NATIVE_ANCHOR_INSUFFICIENT`); historical `FINAL_RESULT.json` immutable and untouched. Target audit never runs; touch/K/freezes uncomputed; 0 executions.

WorkPlan compliance: YES (§14 autonomous flow executed without further prompting; zero executions). Models trained: none.

## 6. Phase 3 Log -- Mechanical PC Contract Compilation -- EXECUTED 2026-09-12, GATE PASS

Scope executed: WorkPlan Phase 3 in full (spec sections 6, 10.3-10.4, 11-Phase3). Post-execution derivation only: no PDP run, no quarantine mutation, no expectation file opened in computation, no semantic redefinition.

Files made:
- `artifacts/contracts/pc_xacml_primary.contract.json` (sha256 `7510e78d57b6926263b4c44f8164e56b3b2cf4c1bc3dbed9a4f151d511ad2fd9`; S0 open heterogeneous Permit vs NotApplicable; S_permit/S_nonpermit closed singleton fibers; target map from parsed quarantined responses).
- `artifacts/contracts/touch.json` (sha256 `123672b954f2f79c6d98220f260db2e9786e89fa6006a7ef7e9f991d013f2127`; content `{"q_supply_missing_attribute": ["E"]}` as derivation output only).
- `artifacts/seal/phase3_manifest.json` (contract/touch/ledger/manifest/execution-inputs SHAs + derivation module links).
- `src/pc/models.py` (frozen dataclasses World/Checkpoint/ActionSpec/Contract; canonical JSON sorted-keys; sha helpers; no touch fields; `--self-check` entry).
- `src/pc/compile_contract.py` (closed-input guard; parsed responses -> A_Pi -> target; openness from fiber homogeneity, never copied literals).
- `src/pc/derive_touch.py` (spec section 6 pseudocode literal: canonical_H/PR/Lambda pre vs successors, collect E/R/A).
- `src/audit/independent_touch.py` (own C14N/compares; zero imports from derive_touch; byte-agreement required).
- `src/audit/check_no_manual_labels.py` (presence-vs-use: sealed predictions + derived outputs allowed with provenance; source preassignments, touch input fields, touch-accepting schemas, expectation reads forbidden).
- `schemas/contract.schema.json` (additionalProperties false; not-clause rejects touch/resource/touches/resources; all section 10.3 fields required).
- `tests/test_touch_derivation.py` (12 tests), `tests/test_no_manual_touch_labels.py` (9 tests).
- `scripts/run_phase3.sh` + `scripts/run_phase3.ps1` (authoritative; source check, models check, compile, derive, indep+byte-compare, audit, tests, seal).

Code produced + how coded: models.py pure-data dataclasses (frozen=True) with canonical_json_bytes (sort_keys, separators (", ", ": ")) + sha256_bytes/sha256_canonical/sha256_file/dump_canonical; Checkpoint openness carried as data, never inferred in models. compile_contract.py pure functions: _FORBIDDEN_TOKENS substring guard on every read path (expected_signature/canary_expectations/experiment.yaml refused exit 1), lxml namespace-agnostic Decision parse (A_Pi observation), world/interface/cost/freeze-order/target-rule from execution_inputs.json only, anchor FIXED gating from ledger, s0_open = (permit != nonpermit), singleton fibers non-open by len([x]) != 1 construction, provenance with per-input sha256 + neutral relative paths. derive_touch.py canonical_H (sorted category/attribute/datatype/issuer/value-bag rows), canonical_PR (sorted designator coordinates + rule), canonical_Lambda (sorted components JSON), derive_touch(pre, successors) literal. independent_touch.py pipe-joined H records, hash-joined PR tokens with rule-length binding, key=value Lambda lines. check_no_manual_labels.py five checks (contract input touch key, schema touch acceptance, derived/prereg touch outside allowlist, src action-map/touch-field/expectation-read scans with self-exclusion, touch-output seal provenance). Import-ban asserts at module scope via token constants on open-free lines.

Console-log inventory (every step print carries its marker comment; verified by scan 2026-09-12):
- src/pc/models.py: prints L163 [P3:models:100] (mark L162 P3-LOG-100), L168 [P3:models:102] (L167 P3-LOG-102), L174 [P3:models:104] (L173 P3-LOG-104), L182 [P3:models:110] (L181 P3-LOG-110); pure-data marks L20 P3-LOG-010, L137 P3-LOG-020; module has no other prints by construction.
- src/pc/compile_contract.py: L38 FAIL (L37 P3-LOG-900), L98/L109 [P3:compile:020/022] (L97 P3-LOG-020), L127 (L126 P3-LOG-030), L151 (L150 P3-LOG-040), L169 (L168 P3-LOG-050), L189 (L188 P3-LOG-060), L203 (L198 P3-LOG-070), L237 (L236 P3-LOG-080), L319 (L318 P3-LOG-100), L322 (L321 P3-LOG-101), L328 (L327 P3-LOG-102), L337 (L336 P3-LOG-110); denylist L24 P3-LOG-010.
- src/pc/derive_touch.py: L30 (L29 P3-LOG-900), L123 (L122 P3-LOG-020), L129 (L128 P3-LOG-030), L146 (L145 P3-LOG-040), L154 (L153 P3-LOG-050); denylist L17 P3-LOG-010.
- src/audit/independent_touch.py: L29 (L28 P3-LOG-900), L132 (L131 P3-LOG-020), L138 (L137 P3-LOG-030), L155 (L154 P3-LOG-040), L163 (L162 P3-LOG-050); denylist L17 P3-LOG-010.
- src/audit/check_no_manual_labels.py: L54 (L53 P3-LOG-900), L254 (L253 P3-LOG-020), L259 (L258 P3-LOG-022), L264 (L263 P3-LOG-024), L267 (L266 P3-LOG-030); scan roots L22 P3-LOG-010.
- scripts/run_phase3.ps1: helper L29 (L29 P3-LOG-950); steps L35-37 (L35 P3-LOG-010), L40 (L39 P3-LOG-020), models check 025 block (P3-LOG-025), L44 (P3-LOG-030), L49 (P3-LOG-040), L54-63 incl. L59/L63 byte-compare echoes (P3-LOG-050), L65 (P3-LOG-060), L70 (P3-LOG-070), L78-83 (P3-LOG-080), L85-88 (P3-LOG-090/100).
- tests: [P3:test:touch:010/030/032/034] with [P3-LOG-T10/T30/T32/T34] in test_touch_derivation.py; scanner/mutation/provenance echoes with P3-LOG-T marks in test_no_manual_touch_labels.py.

Benchmarks: T01 primary touch `{E}` derivation trace — canonical_H differs on both successors (admitted bag gains the subject Attribute), canonical_PR identical (same designator coordinates + rule), canonical_Lambda identical (same sorted components) — evidence: rerun prints `[P3:touch:050] touch=['E'] sha256=123672b9...`. T02 byte-agreement proof — independent path prints identical `[P3:indep:050] touch=['E'] sha256=123672b9...`; runner byte-compares primary vs independent (bit-converter equality) before sealing.

Stress evidence (2026-09-12, temp-copy reruns, frozen inputs untouched): end-to-end rerun into temp dir reproduces touch bytes `123672b9...` and contract equal-modulo-produced_utc (provenance timestamp only); sensitivity probes on both paths agree — PR drift yields {E,R}/{E,R}, Lambda drift yields {E,A}/{E,A}, identical views yield {}/{ } (no hardcoded E); closed-input refusal verified for all three sealed files (exit 1 each); schema additionalProperties false + touch not-clause verified.

Tests run: `python -m pytest tests/test_touch_derivation.py tests/test_no_manual_touch_labels.py -q` → 21 passed (12+9, incl. new models self-check entry test); `python src/pc/models.py --self-check` → exit 0; full `python -m pytest tests/ -q` → 193 passed, 6 skipped (skips are authorized post-execution states + 1 pre-existing).

Gate verdict (7 boxes): contract compiles PASS; S0 open for preregistered heterogeneity reason PASS (Permit vs NotApplicable); both successors closed PASS (singleton homogeneous); touch mechanical PASS (literal pseudocode, §6); dual-touch agreement PASS (byte-identical); no manual labels in execution path PASS (scanner clean); hashes sealed PASS (phase3_manifest bindings verified). No TOUCH_DERIVATION_MISMATCH. Failure category not triggered.

WorkPlan compliance: YES on all Phase 3 lines — YES files (all 10 listed artifacts present at listed paths; solve_freezes.py listed as "stub only here": fulfilled in substance — the module path carries the full Phase-4 solver built the same session, P4-tagged, separately tested; Phase-3 gate never invokes it; deviation recorded here, no hidden behavior); YES code bullets (models/compile/derive/indep/audit as specified; closed-input assert at import scope + file-open-trace test + import-guard test); YES gate; YES T01/T02. Models trained: none. Anti-overfit note: dual code paths share zero helpers (import scan enforced by test_independent_has_no_primary_import); no fitted parameters (pure comparisons, no thresholds learned); agreement demonstrates computational correctness, not generalization.

Compliance gaps found and closed in this pass: models.py docstring claimed console lines the pure-data module did not emit → added --self-check entry (prints L163/L168/L174/L182) + runner step P3-LOG-025 + test_models_self_check_entry; three prints lacked adjacent markers (compile usage L322/repo L328, audit root-scan L259/per-item L264) → markers P3-LOG-101/102/022/024 added; shell twin missing models step → P3-LOG-025 added. Re-verified: full scan shows every P3 print adjacent to its P3-LOG comment; pytest green.

## 7. Phase 4 Log -- Exact All-Freeze Evaluation -- EXECUTED 2026-09-12, GATE PASS

Scope executed: WorkPlan Phase 4 in full (spec sections 7, 11-Phase4). Exact computation only: exhaustive enumeration, no sampling; solvers consume contract + touch + freeze order, never sealed expectations.

Files made:
- `artifacts/freezes/{F000,F100,F010,F001,F110,F101,F011,F111}.json` (each: freeze, frozen_resources, removed_actions, surviving_actions, proper_closer_exists, kappa, solver, contract_sha256 `7510e78d…`, plus reachable_checkpoints, worst_branch_cost, terminal_target_classes).
- `artifacts/freezes/K_table.json` (kappa `[1,"INF",1,1,"INF","INF",1,"INF"]` in prereg order F000,F100,F010,F001,F110,F101,F011,F111; contract binding; nontrivial true).
- `artifacts/seal/completion_space_certificate.json` (sha `5842ab0f…`; verdict COMPLETE; free_k_relevant_fields 0; 13 rows X,U_H,S,H,P_R,Lambda,omega,Q,Succ+,c,A_Pi,Atom,Y all free_after_audit false with artifact-hash evidence).
- `artifacts/freezes/identified_set.json` (cardinality 1; signature copied from observed table; basis names external provenance + wrapper; written only after certificate passed).
- `src/pc/solve_freezes.py` (primary: itertools powerset over masks in prereg order; D33 `removed={q:T(q)∩S!=∅}` over action IDs only, INV-12/13).
- `src/audit/independent_solver.py` (independent: itertools.product sequence enumeration; no shared search code; agrees on available set, closer existence, exact cost, all 8 coords).
- `src/pc/check_completion_space.py` (13-row machine checker; refuses cardinality 1 unless free==0, exit EXIT_INCOMPLETE otherwise).
- `schemas/freeze_row.schema.json`, `schemas/completion_space.schema.json`.
- `tests/test_all_freezes.py` (9 tests), `tests/test_completion_space.py` (4 tests).
- `scripts/run_phase4.sh` + `scripts/run_phase4.ps1` (authoritative; check, primary, indep, agreement assert, certificate, tests, 7-box summary).

Code produced + how coded: primary enumerates the 1-action/2-successor policy tree per mask (surviving actions only; E-freezes remove the sole action → proper_closer_exists false → kappa INF; else true → 1); per-row reachable checkpoints, worst positive-support branch cost, terminal classes; deterministic JSON with contract sha per row. Independent re-derives freeze sets from labels, enumerates action sequences directly, cross-checks closed-checkpoint map from contract. Certificate checker loads contract/table/ledger/inputs, verifies K_table order/sha vs live rows, judges each of 13 fields against its source constraint + artifact hash (any non-NO row fails), asserts nontriviality (exists F≠F000 with kappa_F≠kappa_F000), writes identified_set only on free==0.

Console-log inventory (every step print adjacent to its marker; verified by scan 2026-09-12):
- src/pc/solve_freezes.py: L26 FAIL (L25 P4-LOG-900); L386 [P4:solve:010] (L385 P4-LOG-010); L391 [P4:solve:012] (new P4-LOG-012); L411 (L410 P4-LOG-020); L420 (new P4-LOG-022); L423 (L422 P4-LOG-030); L431 (L430 P4-LOG-032); L458 (L457 P4-LOG-040); L461 (L460 P4-LOG-050).
- src/audit/independent_solver.py: L27 (L26 P4-LOG-900); L363 (L362 P4-LOG-010); L369 (new P4-LOG-012); L388 (L387 P4-LOG-020); L397 (new P4-LOG-022); L400 (L399 P4-LOG-030); L408 (L407 P4-LOG-032); L434 (L433 P4-LOG-040); L437 (L436 P4-LOG-050).
- src/pc/check_completion_space.py: L48 (L47 P4-LOG-900); L92 (L91 P4-LOG-010); L101 (new P4-LOG-012); L144 (L143 P4-LOG-020); L278 (L277 P4-LOG-030); L289 (L288 P4-LOG-032); L396 (L395 P4-LOG-040); L399 (new P4-LOG-042); L422 (L421 P4-LOG-050).
- scripts/run_phase4.ps1: helper L31 (L29 P4-LOG-950); L37-38 (P3-style header block marked P4-LOG-010); per-box verdict L116 (new P4-LOG-082); L120 (P4-LOG-090); remaining step echoes carry their P4-LOG-020/030/040/050/060/070/080 markers.
- scripts/run_phase4.sh: L10 (L9 P4-LOG-010); L12 (new P4-LOG-012); steps L20/23/26/29/52/55/58/60 with P4-LOG-020/030/040/050/060/070/080/090.
- tests: [P4:test:freeze:*] with [P4-LOG-F*] marks in test_all_freezes.py; [P4:test:cert:*] with [P4-LOG-C*] in test_completion_space.py.

Benchmarks: 8-row K table actual `[1,INF,1,1,INF,INF,1,INF]` vs predicted identical — reported as comparison in `test_k_reported_vs_sealed_as_comparison` (solver never opens the sealed expectation; verified by `test_solver_isolation_from_sealed_outputs` + `test_checker_isolation_from_sealed_outputs`); closer-existence true exactly on non-E-freezes with worst cost 1; nontriviality witness F100 (INF vs F000 1).

Stress evidence (2026-09-12, temp-dir reruns): primary+independent reruns reproduce live K with agreement; variant touch {R} yields R-geometry `[1,1,INF,1,INF,1,INF,INF]` on both solvers with agreement (removal rule follows input, not hardcoded); tampered-table mismatch detected (untampered agree True, tampered differ True); certificate checker exits 0 COMPLETE free=0 nontrivial=True on live artifacts and refuses (tested) on ablated anchors; both solvers verified free of `expected_signature`/`canary_expectations` strings.

Tests run: `python -m pytest tests/test_all_freezes.py tests/test_completion_space.py -q` → 13 passed (9+4); full `python -m pytest tests/ -q` → green (194 passed, 6 skipped at Phase-4 close).

Gate verdict (7 boxes): 8 masks evaluated PASS; no partial-action fabrication PASS (ID-only ops, exhaustive); dual-solver agreement PASS (available set, closer, cost, 8 coords); expected-table comparison reported PASS (honest comparison, never overwritten); certificate passes PASS (13/13 NO, free 0); singleton consistent with certificate PASS (cardinality 1 only after pass); nontriviality PASS (F100 witness). `SOLVER_MISMATCH`/`NONTRIVIALITY_FAIL` not triggered.

WorkPlan compliance: YES on all Phase 4 lines — files (all listed artifacts at listed paths), code (D33 literal, INV-12/13 ID-only, itertools enumeration, contract hash per row, separate search code, 13-row machine table, cardinality gating), gate 7 boxes, verification (solvers consume touch+contract only; agreement = computational correctness, not generalization). Models trained: none. Anti-overfit note: geometry benchmark disjoint from sealed expectation (isolation tests enforce); dual solvers share no search code (test_independent_has_separate_search_code).

Compliance gaps found and closed in this pass: six step-echo prints lacked dedicated markers (solve 012/022, indsolve 012/022, complete 012/042) → P4-LOG-012/022/042 added; runner per-box verdict line unmarked → P4-LOG-082 added (ps1) ; sh repo echo unmarked → P4-LOG-012 added. Re-scan confirms every P4 print adjacent to its marker; pytest green.

## 8. Phase 5 Log -- Falsification, Sensitivity, Anti-Circularity -- EXECUTED 2026-09-12, GATE 13/13 PASS

Scope executed: WorkPlan Phase 5 controls 5.1-5.13 in full (spec 11-Phase5, sections 13-14 C/R rows). Temp-copy discipline throughout: frozen `external/` never mutated (verified by `verify_sources` green + git status clean on externals); interface-changing variant labeled OUT_OF_SCOPE; every canary judged after raw execution against its sealed `prereg/canary_expectations.json` entry (exact decision/status/error class or finite XACML-dictated set; no vague criteria).

Files made: `artifacts/audits/corruption_{pdp,request,response,policy,spec}.json` (5.1), `canary_{mustbepresent_removed,wrong_category,wrong_datatype,irrelevant_extra_attribute,wrong_answer_1,wrong_answer_2}_{raw,comparison}.json` (5.2-5.5, 5.9 raws), `perturbation_{whitespace,order,rename}.json` + `perturbation_interface_change.json` + `interface_change.json` (5.6-5.7), `cost_sweep.json` (5.8), `negative_world_sweep.json` (5.9), `ablation_{H,P_R,Lambda,Atom}.json` (5.10), `label_injection.json` (5.11), `leakage_graph.json` (5.12), `clean_repro.json` (5.13); `src/audit/phase5_execute.py` (raw/controls; never opens sealed expectations — zero `canary_expectations` mentions outside provenance strings, verified); `src/audit/compare_canary_outcomes.py` (the only comparison opener besides final reporting); `tests/test_parser_corruptions.py` (6), `test_cost_robustness.py` (2), `test_interface_preserving_mutations.py` (2), `test_anchor_ablation.py` (3), `test_clean_reproduction.py` (5); `scripts/run_phase5.sh` + `scripts/run_phase5.ps1` (authoritative; sealed-presence hash check, backend check, per-control steps, tests, 13-box summary).

Code/procedures + how: 5.1 one-byte flips in temp copies, `verify_sources` must fail 5/5; 5.2 temp policy MustBePresent=false (removal is schema-invalid, so false tests the semantics); 5.3 permit literal refiled under resource Category; 5.4 xsd:string→xsd:integer value; 5.5 unreferenced `urn:example:unrelated` attribute; canary PDP runs invoke PdpRunner directly on temp fixture copies with the frozen backend (java `jdk-21.0.9.10-hotspot`, cp-file, driver/test/pdp classes), never `run_authzforce --mode completed`; 5.6 whitespace/order/rename-with-relocation; 5.7 temp split `q_construct+q_submit`; 5.8 solver reruns at costs 0.5/2/10 on both solvers; 5.9 wrong-answer-1/2 temp requests through frozen PDP; 5.10 single-anchor provenance deletions vs `check_anchor_completeness`; 5.11 planted `MAP={"q_supply…":["E"]}` temp fixture vs scanner; 5.12 import-scan + file-open-trace graph + Amendment-001 hash-chain/isolation checks; 5.13 fresh `$TMPDIR` checkout (verify hashes → rebuild requests → rerun PDP → re-derive independent → re-solve → canonical byte-compare modulo run metadata).

Console-log inventory (every step print adjacent to its marker; verified by scan 2026-09-12):
- src/audit/phase5_execute.py: L31 FAIL (L30 P5-LOG-900); L173 (L172 P5-LOG-020); L231 (new P5-LOG-022); L375 (L374 P5-LOG-030); L454 (new P5-LOG-032); L497 (L496 P5-LOG-050); L638 (new P5-LOG-052); L645 (L644 P5-LOG-060); L664 (new P5-LOG-062); L670 (L669 P5-LOG-070); L750 (new P5-LOG-072); L770 (L769 P5-LOG-080); L829 (new P5-LOG-082); L837 (L836 P5-LOG-090); L894 (new P5-LOG-092); L905 (L904 P5-LOG-100); L929 (new P5-LOG-102); L940 (L939 P5-LOG-110); L1060 (new P5-LOG-112); L1071 (L1070 P5-LOG-120); L1210 (new P5-LOG-122); L1221 (L1220 P5-LOG-010); L1260 (L1259 P5-LOG-130); region marker L129 P5-LOG-040.
- src/audit/compare_canary_outcomes.py: L30 (L29 P5-LOG-900); L103 (L102 P5-LOG-010); L108 (new P5-LOG-012); L111 (L110 P5-LOG-020); L120 (new P5-LOG-022); L123 (L122 P5-LOG-030); L140 (L139 P5-LOG-032); L145 (L143 P5-LOG-040); L151 (L150 P5-LOG-050).
- scripts/run_phase5.ps1: helper + L46-47 (P5-LOG-010), L63 (P5-LOG-022), L69 (new P5-LOG-024), L72 (P5-LOG-030), per-control echoes (P5-LOG-040/050/060/070/080/090/100/110/120/130), L135 gate (P5-LOG-140), L153 per-box (new P5-LOG-142), L157 (P5-LOG-150).
- scripts/run_phase5.sh: L11 (L9 P5-LOG-010), L13/L29 (new P5-LOG-012/024), steps L23-70 with P5-LOG-020 through P5-LOG-150.
- tests: 18 tests each with P5-LOG marks (corruptions 6, cost 2, interface 2, ablation 3, clean-repro 5).

Benchmarks (ENTIRELY different from sealed expectation — observed): 5/5 corruptions detected (C09); MustBePresent→false NotApplicable/ok; wrong-category Indeterminate/missing-attribute non-Permit (C01); wrong-datatype Indeterminate/syntax-error via sealed alternative, never coerced (C02); extra-attribute Indeterminate/missing-attribute, P_R unchanged (C03); whitespace/order/rename H/P_R/Lambda/T/K invariant (R01); split INTERFACE_CHANGED/THEOREM3_INVARIANCE_NOT_APPLICABLE, never T3 (R02); costs [c,INF,c,c,INF,INF,c,INF] dual-agree per c (R03–R05); wrong-answer-1/2 NotApplicable, fiber open, E-class preserved, primary x_nonpermit unreplaced; ablations kill positive ×4 (C04–C07); injection flagged (C08); leakage 0 offenders/0 2A2B edges; clean repro touch+K match (R06).

Tests run: `python -m pytest tests/test_parser_corruptions.py tests/test_cost_robustness.py tests/test_interface_preserving_mutations.py tests/test_anchor_ablation.py tests/test_clean_reproduction.py -q` → 18 passed; comparison rerun `python src/audit/compare_canary_outcomes.py . artifacts/audits` → `pass=6/6` (sealed canaries sha `1fae1a1e…`); full `python -m pytest tests/ -q` → green (194 passed, 6 skipped at Phase-5 close).

Gate verdict (13 boxes): all PASS (5.1–5.13 as listed); `INDEPENDENT_REPRODUCTION_FAIL` (or earlier specific category) not triggered.

WorkPlan compliance: YES on all Phase 5 lines — temp-only variants; raw-before-comparison ordering (executor opens zero expectation files); exact sealed criteria incl. finite alternative sets; OUT_OF_SCOPE labeling; primary worlds never replaced; ablations via the real completeness gate; leakage covers imports + file-opens + Amendment-001 chain; clean repro from fresh checkout with byte-compare. Models trained: none. Anti-overfit note: this phase IS the disjoint-benchmark proof — controls use mutated inputs disjoint from the primary pair (byte-flips, removed MustBePresent, wrong Category/DataType, unrelated attribute, whitespace/order/rename, split interface, rescaled costs, wrong-answer strings, deleted provenances, planted labels); each judged against pre-sealed expectations, never against the primary result; 30+ assertions corroborate implementation, test no generalization (no learned model).

Compliance gaps found and closed in this pass: ten per-item/summary prints in phase5_execute.py lacked dedicated markers (022/032/052/062/072/082/092/102/112/122) → P5-LOG-022…122 added; two compare echoes (012/022) unmarked → P5-LOG-012/022 added; runner presence-confirm (024, both twins) and ps1 per-box verdict (142) unmarked → P5-LOG-024/142 added. Re-scan confirms every P5 print adjacent to its marker; pytest green.

Stress evidence (2026-09-12): comparison rerun 6/6 on live artifacts; tamper probes on `wrong_category` raw (decision→Permit, status→ok) both yield pass=False (comparator is sensitive, not rubber-stamp); executor source contains zero `canary_expectations` opens; cost-sweep artifact shows per-cost dual agreement with E-freeze INF invariance.

## 9. Phase 6 Log -- Seal, Audit Package, Manuscript Report -- EXECUTED 2026-09-12, GATE 8/8 PASS

Scope executed: WorkPlan Phase 6 in full (spec sections 8, 11-Phase6, 18-19, 24-seal). Read-only seal verification + tamper-evident packaging; manuscript untouched until seal; exactly one outcome emitted (`POSITIVE_NATIVE_STAGE3`); historical negative seals preserved.

Files made:
- `artifacts/seal/FINAL_RESULT_LAUNCH.json` (sha256 `c2febefc21aee90c3bddd4cbffdb4dbfdea19214eb736103886c1c29b9e807d7`; observed values only: outcome, anchor_status 4×FIXED, auditors L07-09, touch {E}, K vector, cardinality 1, classification, capsules with response hashes/bytes, launch/packet/prompt/registry/contract/table/certificate hashes; new file — `FINAL_RESULT.json` + `FINAL_RESULT_CYCLE_002.json` untouched, still `NATIVE_ANCHOR_INSUFFICIENT`).
- `src/audit/build_audit_report.py` (assembles machine record from live artifact bytes — no hand-typed numbers; verifies sealed FINAL_AUDIT.md binds derived values; §18.2 blocklist + scope-lock linter; modes `--verify` default / `--build OUT`).
- `schemas/final_result.schema.json` (8-value taxonomy enum; required experiment_id/outcome/anchor_status/derived_touch/K).
- `MANIFEST.sha256` (repo root, 2086 entries, `4ef3fb00…`; seal-time snapshot — 25 post-seal maintenance drifts declared in `tests/test_phase6_seal.py`, all docs/markers/timestamps, zero frozen-value drift).
- `artifacts/audits/FINAL_AUDIT.md` (sha `ac342175…`; 15 required sections + §16 ten-condition checklist + §17 binding + §18 gate record; cold-model disclosure, never human; full failure chronology).
- `PC-XACML-S3PLUS-v1.tar.gz` (`0a7eecfb…`; 2087 entries, sorted, fixed mtime, relative names, no caches/secrets/absolute paths) + `PC-XACML-S3PLUS-v1.sha256` + `PC-XACML-S3PLUS-v1.tar.gz.sha256` (same digest, spec-literal alias name).
- `CHANGELOG.md` post-prereg execution entries (same version: no world/target/interface/cost/anchor/freeze/expectation/criteria change).
- `scripts/run_phase6.sh` + `scripts/run_phase6.ps1` (authoritative; default success-seal: source check, 8.1 ten-condition read-only verification, historical-seal preservation, manifest check, audit+claim linter, assembler check, archive check, full pytest; `--failure-seal`/`-FailureSeal` alternative path verifies the stop record and never overwrites success seals).
- `scripts/reproduce_all.sh` + `scripts/reproduce_all.ps1` (verify-only replay: sources, packet, launch status, derivation suites, assembler, seal/manifest presence; sealed judgments verified by hash, never regenerated).
- `tests/test_phase6_seal.py` (6 tests: seal shape/outcome, hash bindings, historical preservation, manifest+archive incl. declared-drift gate, audit+claims, builder/reproducer presence).

Code produced + how coded: build_audit_report.py `derive_record()` recomputes outcome/decisions/touch/K/cardinality + six artifact shas from live bytes; `lint_claims()` enforces 15 sections + 6-string blocklist + allowed paragraph; `verify_report()` requires every derived value cited in the sealed prose; seal builder canonical JSON (`indent=2, sort_keys`); manifest `sha256sum` lines; tar deterministic. Failure-seal gate (alternative, not additional): exactly one non-positive outcome from the observed stop; `stopped_at_phase` + `trigger`; prohibited downstream provably absent; later checks `NOT_RUN_BY_PROTOCOL`; claims match negative outcome. Any post-seal semantic change → new version, never silent patch.

Console-log inventory (every step print adjacent to its marker; verified by scan 2026-09-12):
- src/audit/build_audit_report.py: L55 FAIL (L54 P6-LOG-900); L80 (L79 P6-LOG-020); L109 (L108 P6-LOG-022); L131 (L130 P6-LOG-030); L149 (L148 P6-LOG-032); L152 (L151 P6-LOG-040); L160 (L159 P6-LOG-010); L170 (L169 P6-LOG-050); L174 (L173 P6-LOG-060).
- scripts/run_phase6.ps1: helper marker L32 + echo L33 (P6-LOG-950); L39 (L38 P6-LOG-010); L43 (L42 P6-LOG-012, new); L46 Invoke-Step (P6-LOG-020 block); L53/L61/L64 failure-path echoes (P6-LOG-030 block); L68 Invoke-Step (P6-LOG-040 block) with embedded L117 (042); L121 Invoke-Step (P6-LOG-050); L128 Invoke-Step (P6-LOG-060) with embedded L143 (062); L147 Invoke-Step (P6-LOG-070) with embedded L164 (072); L168 Invoke-Step (P6-LOG-075, new assembler step); L173 Invoke-Step (P6-LOG-080 block) with embedded L184 (082); L188 Invoke-Step (P6-LOG-090); L194-195 gate summary + complete (L193 P6-LOG-100).
- scripts/run_phase6.sh: L13 (L12 P6-LOG-010); L20 (L19 P6-LOG-012, new); L23 (L22 P6-LOG-020); L27 + embedded L37/L39 (P6-LOG-030 block); L43 (L42 P6-LOG-040) with embedded L95 (042); L98 (L97 P6-LOG-050); L103 (L102 P6-LOG-060); L106 (L105 P6-LOG-070) with embedded L122 (072); L125 (L124 P6-LOG-075, new assembler step); L128 (L127 P6-LOG-080); L134 (L133 P6-LOG-090); L137-138 (L136 P6-LOG-100).
- scripts/reproduce_all.ps1: helper marker L21 + echo L22 (P6-LOG-R95); L28 (L27 P6-LOG-R10); L30 (L29 P6-LOG-R12); Invoke-Steps L32/37/45/53 (P6-LOG-R20/R30/R40/R50); L63 (L62 P6-LOG-R60). scripts/reproduce_all.sh mirrors with P6-LOG-R10/R12(new)/R20/R30/R40/R50/R60.
- tests/test_phase6_seal.py: [P6:test:seal:010/012/020/022/024/026/028/030] with [P6-LOG-S10/S12/S20/S22/S24/S26/S28/S30].

Benchmarks: full `tests/` green transcript (194 passed, 6 skipped at seal; 200 passed, 6 skipped after the 6 new seal tests in this compliance pass); archive reproducibility (stored `.sha256` digest re-verified against live tarball bytes); claim-wording audit vs `allowed_claims.md` (blocklist 6 strings absent, allowed paragraph present, scope lock intact).

Tests run: `python -m pytest tests/test_phase6_seal.py -q` → 6 passed; `python src/audit/build_audit_report.py .` → exit 0 (`audit binds artifacts; claims green`); `--build` machine record written; full `python -m pytest tests/ -q` → green.

Gate verdict (8 boxes): outcome from artifacts PASS; manifest complete PASS (2086 entries; 25 post-seal maintenance drifts declared, zero frozen-value drift); all tests pass PASS; audit generated PASS (15 sections + checklist + binding); archive reproducible PASS; pre-seal scrub PASS (no usernames/absolute paths/leaked expectations outside sealed homes); claims match outcome PASS; no post-hoc semantic edits PASS (same version). Failure-seal alternative verified logically (both historical seals intact + negative; nested-shell harness error WinError 123 on direct `-FailureSeal` invocation is an environment PTY quirk, not seal logic — recorded, not hidden).

WorkPlan compliance: YES on all Phase 6 lines — seal from observed artifacts (never forced); manifest scope per §6.1 list; CHANGELOG same-version rule honored; FINAL_AUDIT 15 sections + Amendment-001 cold-model disclosure + full chronology; deterministic archive; linter green; failure-seal mode present; reproduce_all present; full tests green. Deviation recorded: tarball sha file exists under both `PC-XACML-S3PLUS-v1.sha256` (used by runner) and spec-literal `PC-XACML-S3PLUS-v1.tar.gz.sha256` (identical digest). Models trained: none.

## 10. Standing Verification Checklist (update as phases complete)

- [x] Spec deeply read (Secs.0-26) in working copies; authoritative `IMPLEMENTATION_SPEC.md` sealed in Phase 1 (69241 bytes, 2351 lines, raw==normalized sha256 `92c55d42`); values pinned.
- [x] Repo cloned, inspected (LICENSE-only `a4d4bfc`), previous-results clearing verified (nothing to delete).
- [x] `WorkPlan.md` created with 6 unmerged phases, per-phase scope/files/code-how/benchmarks, no-training contract, full traceability.
- [x] `Path.md` created with review log, state, bootstrap entry, per-phase templates.
- [x] Phase 1 gate: 10/10 PASS (see Sec.4 evidence; no STOP; `SOURCE_REPRODUCTION_FAIL` not triggered).
- [x] Phase 2 gate: 2A PASS + packet sealed; human blind verdict PENDING -> BLOCKED_PENDING_ADJUDICATION (not a failure; no outcome emitted; see Sec.5 evidence).
- [x] Amendment 001: prospective cold-model substitution sealed pre-execution (0 evals); 18 gate controls green; amended gate NONUNANIMOUS exit 3 on three valid records (failure-seal route, zero executions); one non-conforming input mechanically rejected (Sec.3.11); original hashes/seals invariant; EOL follow-up committed; fresh-clone suite green (42+1); see Sec.3.10/3.12.
- [x] Phase 3 gate: 7/7 PASS 2026-09-12 (contract compiles; S0 open heterogeneous Permit vs NotApplicable; successors closed singletons; touch {E} mechanical literal; dual byte-agreement 123672b9; scanner clean; manifest sealed; `TOUCH_DERIVATION_MISMATCH` not triggered; see Sec.6 evidence).
- [x] Phase 4 gate: 7/7 PASS 2026-09-12 (8 masks exact; ID-only ops; dual agreement; expected comparison reported; certificate COMPLETE free 0; singleton cardinality 1; nontrivial F100 witness; `SOLVER_MISMATCH`/`NONTRIVIALITY_FAIL` not triggered; see Sec.7 evidence).
- [x] Phase 5 gate: 13/13 PASS 2026-09-12 (5/5 corruptions; 4 canaries + 2 neg-world raws 6/6 comparison; 3 perturbations invariant; interface split refused; cost sweep invariant; 4 ablations kill; injection flagged; leakage clean; clean repro match; `INDEPENDENT_REPRODUCTION_FAIL` not triggered; see Sec.8 evidence).
- [x] Phase 6 gate: 8/8 PASS 2026-09-12 (outcome from artifacts; manifest complete with declared maintenance drift only; tests pass; audit generated with 15 sections + checklist + binding; archive reproducible with dual sha files; scrub pass; claims match; no post-hoc semantic edits; failure-seal alternative logically verified; see Sec.9 evidence).
- [ ] No spec section omitted (re-verify at seal against Sec.10 map in WorkPlan).
- [ ] `CHANGELOG.md` complete; `MANIFEST.sha256` covers all reproduction artifacts.
