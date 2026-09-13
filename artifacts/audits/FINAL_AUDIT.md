# FINAL AUDIT — PC-XACML-S3PLUS-v1 (launch-003 positive seal)

Experiment: `PC-XACML-S3PLUS-v1`.
Outcome: `POSITIVE_NATIVE_STAGE3`.
Seal file: `artifacts/seal/FINAL_RESULT_LAUNCH.json` (separate file; historical `artifacts/seal/FINAL_RESULT.json` and `artifacts/seal/FINAL_RESULT_CYCLE_002.json` remain untouched).
Sealed UTC: `2026-09-12T19:11:05Z`.
This report is assembled from observed artifact hashes. No hand-typed numbers. No manuscript edits occurred before seal.

Outcome taxonomy (spec Sec. 8): exactly one outcome is emitted. The emitted outcome is `POSITIVE_NATIVE_STAGE3`. All ten Sec. 8.1 conditions hold (evidence in Sec. 16 of this report). No partial credit is reported as Stage-III positive. Historical negative seals are preserved, not reinterpreted.

## 1. External source provenance

- Primary system: OASIS XACML 3.0 + AuthzForce Core Community Edition 21.2.0, tag `release-21.2.0`, commit `3cc0e988e1639da48184434cd5c918102ff5b499`.
- Primary fixture: `StatusDetail.MissingAttributeDetail` (four files: `pdp.xml`, `request.xml`, `response.xml`, `policies/policy.xml`).
- Upstream Git blob SHAs match the four spec constants (verified by `src/provenance/verify_sources.py` at every phase; STOP-10).
- Local hashes: `external/MANIFEST.json` sha256 `05f55f0a2c95a338ad33ecc2cc21e613d7f0a932a4c5f7e7f8650dbfb4c9cbff`.
- OASIS core HTML frozen at `external/xacml/xacml-3.0-core-spec-cos01-en.html` (1257025 bytes; frozen copy authoritative from seal on).
- Authoritative spec: `IMPLEMENTATION_SPEC.md` (69241 bytes, 2351 lines; raw and LF-normalized sha256 `92c55d425531e578ad6ea266e7c6f1bd0418990bd973cd0033fcf6a20dc83963`).
- Prereg seal: `prereg/prereg_sha256.txt` sha `0e15fa28a97a`; covers `experiment.yaml` (`d3a6e7745221`), `expected_signature.json` (`382e6ab909ac`), `execution_inputs.json` (`04ec1aaa43e5`), `canary_expectations.json` (`1fae1a1eca00`), `allowed_claims.md` (`edade78312b0`).
- Frozen externals were never mutated. Phase-5 variants used isolated temporary copies only. `external/authzforce-repo` is a git-ignored pinned clone used only as the frozen PDP backend.

## 2. Original fixture reproduction

- Native PDP execution on the frozen original `request.xml` yields `Indeterminate` with `missing-attribute` status and the expected `MissingAttributeDetail` triple (Category access-subject, AttributeId `...:some-attribute`, DataType `xsd:string`).
- Record: `artifacts/raw/original_response_comparison.json` sha `649ff255effdafb21384d220632cf9d4eb7040509508c4ef4c5857c476ff2b21`, field `semantic_match: true`.
- Actual response bytes: `artifacts/raw/original_response_actual.xml` sha `cf2325f9f3d65a135bfe14c50571920bc7e422ea0ca2e862ec6d0c039b8d33ca` (565 bytes).
- This satisfies Sec. 8.1 condition 1.

## 3. Anchor-by-anchor provenance table

Ledger: `derived/anchor_ledger.json` sha `3ff36ae883a5ec346c2e3d5526d6629aa0ffb0cdef7f639cc3f85da2d227b595`. All nine records carry `ambiguity_status: FIXED` with `manual_semantic_choice_required: false`.

| PC object | Source classes | Evidence (artifact sha) | Status |
|---|---|---|---|
| H | N1 + N3 | `derived/H_initial.json` + `derived/h_equivalence_proof.json` (`2f89ae4d99ac`) + launch unanimity | FIXED |
| P_R | N1 + N3 | `derived/policy_projection.json` (`1816bf1b05a4`) + `derived/policy_adequacy_certificate.json` (`70137a9d8700`) + launch unanimity | FIXED |
| Lambda | N1/N2/N3 | frozen capability manifest + pre/post equality + launch unanimity | FIXED |
| Atom | N1 (+ X wrapper) | `derived/atom_record.json` (`8dbf228c5dada`) + wrapper evidence + launch unanimity | FIXED |
| omega | N1 + N3 | frozen response triple + `original_response_actual.xml` | FIXED |
| Q | N1 + X wrapper | prereg wrapper definition + `execution_inputs.json` (`04ec1aaa43e5`) | FIXED |
| Succ+ | N3 + X wrapper | two world files + native responses | FIXED |
| A_Pi | N3 execution | quarantined PDP decisions (Sec. 7) | FIXED |
| c | X (frozen) | unit normalization `1` in `execution_inputs.json` | FIXED |

Operative FIXED for H/P_R/Lambda/Atom is the launch-003 unanimous certification (Sec. 6) bound to the frozen ledger. Ledger `auditor_status` fields retaining the historical `PENDING_2B` label are superseded for the launch path by `TARGET_EXECUTION_AUTHORIZED.json`; no ledger bytes were rewritten after authorization.

## 4. Policy projection and adequacy certificate

- Projection: `derived/policy_projection.json` sha `1816bf1b05a4b99529958537f72fdbfcb753987113c5fc43297e14e3a7f401dd`. Mechanically extracted (no handwritten allowlist); contains the missing `some-attribute` designator with Category access-subject, AttributeId `...:some-attribute`, DataType `xsd:string`, MustBePresent true.
- Adequacy: `derived/policy_adequacy_certificate.json` sha `70137a9d8700167a295a5a9a2fc0c50a9c70d9c0ea149c4df4b9d0015623f7d2`, verdict PASS. Inventories every request-sensitive construct; no selectors, XPath, provider-dependent functions, or custom datatypes require capture beyond the designator projection. Records the P_R-instantiation justification with N1 locators.
- Relation: `derived/pr_relation.json` sha `252f78b3f4af4f701a1abeee137f7858252d9627cf3c009983861c9da098761f`.

## 5. H-equivalence proof

- Proof: `derived/h_equivalence_proof.json` sha `2f89ae4d99ac7d2728886e51a6e3dd4ca1a7e9f511275909359c971b326b0d1b`, verdict VALID.
- Route (a) (resolved-context capture) was unavailable by probe plus sequencing guard; route (b) (per-attribute extensional equality between canonical request XML and the resolved context, with cited XACML sections and fixture evidence) establishes H. Without this proof H would be `AMBIGUOUS`.
- Canonical histories: `derived/H_initial.json`, `derived/H_permit.json`, `derived/H_nonpermit.json` over the proven-equivalent source; single canonicalizer shared by H/P_R/Lambda paths.

## 6. Blind-adjudication record (cold-model; never human) and Amendment-001 disclosure

- Operative adjudication is three independently initialized cold-model adjudications over the sealed launch packet. No human adjudication occurred in this execution. Nothing in this report implies human involvement.
- Packet: `artifacts/audits/launch/launch_packet/` sha `8e23901d4643a42a4748af8894c0439f19f071f736d23225ea906aac97099ce6`. Prompt: `artifacts/audits/launch/launch_certification_prompt.txt` sha `251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865`. Registry: `artifacts/audits/launch/run_conformance_obligations.json` sha `d7641f64ced4092a23e7e75dcb26f00f5fa274f27ca3171b2d39792e6fe7e44a`. Freeze: `artifacts/audits/launch/LAUNCH_FREEZE.json` sha `d292a46aef93f7eadd3c0c2682a8304c549596d2d69b4a5f74cfe5c8fd20ac9c`, launch id `PC-XACML-S3PLUS-v1-launch-003`, panel AUD-L07/08/09, frozen UTC `2026-09-12T15:38:48Z`.
- Records (all `COLD_MODEL_INDEPENDENT`, verbatim non-exposure declaration, isolation affirmed, packet/prompt hashes match the freeze):
  - AUD-L07: verdict `d30d0e80e86287a4c1f44ca82d9a57f16a4fcfc351dfffad3f9e2e15d80c9f84`, provenance `1d02ec423db643a482b5de62af17b1cb7f2c43b4f48bda9de1e3d742e49d383f`, raw `b042c124e95f3cdc9152fed7879e2d4277639f0a8b1a38f1711173223ae47a1f`, attestation `c9569845a74c4f9ddaacedb97104385416c02e81414020d17c9fca348e430172`, ingested `2026-09-12T16:27:03Z`, verdicts H/P_R/Lambda/Atom all FIXED, six obligations all LEGITIMATELY_DEFERRED.
  - AUD-L08: verdict `875f76d2e0368e70c6d70ffb1297f8daf4df641d57d47972dbdb50063d38c4f5`, provenance `7d412a84a5d08e472b72285c89f4b7e81af8ca28ffe45544576cc37f8e808fde`, raw `7ff84dd595dd38821a93586bc60d90f2b7017599958cf50e21c35f66cb0753dc`, attestation `128ea5f878402fa0ca4b7bf724291253c1601bdffa61534abda4f7d4dcacd85e`, ingested `2026-09-12T17:52:07Z`, verdicts all FIXED, six obligations all LEGITIMATELY_DEFERRED.
  - AUD-L09: verdict `42b7b1ca25996b5aafc8aca31892a0bb9f05a1f57e28f7a79ae88f3e66f6956a`, provenance `8a8c5cf2d529803bba124d5ff4ccacb60fcd38ffad996e2eac51815e78b5955f`, raw `d0037768e6514bccdde6c33bf0208b30aa0d34baf2ab5053412576a6cda2c4d5`, attestation `7b9e1b5d6ed4b28ce3f77e0de654ab69fe73e8da41540f7db9c9f3e345238beb`, ingested `2026-09-12T16:27:09Z`, verdicts all FIXED, six obligations all LEGITIMATELY_DEFERRED.
- Authorization: `artifacts/audits/launch/TARGET_EXECUTION_AUTHORIZED.json` sha `e05e3111f0a3fc848d7f8333751038cd25e9df6ba23095c71c05b4cbde6e7909`, sealed `2026-09-12T17:52:10Z`, unanimous launch certification rule, bound to the packet/prompt hashes above.
- Amendment-001 disclosure: Because a qualifying human adjudicator was unavailable within the execution window, the preregistered blind-adjudication requirement was prospectively amended before any target-world execution to permit three independently initialized cold-model adjudications. Each adjudicator received the same sealed source-complete packet while being withheld the expected touch, freeze signature, classification, desired outcome, and manuscript claims. Positive continuation required unanimous FIXED judgments for H, P_R, Lambda, and Atom.
- The blind packet builder asserts candidate-mapping blind-safety and redaction (no expected touch, K, classification, or claim content in any adjudicator input); leakage audit (Sec. 13) confirms no expectation content in adjudicator inputs and no cross-adjudicator reads. In-session subagent adjudication is prohibited and was not used for certification.
- Ingest history for launch-003: AUD-L07 valid on first ingest; AUD-L09 valid on first ingest; AUD-L08 required three ingests (two procedural INVALID attempts preserved in the operator ingest record, followed by the valid record sealed above at `2026-09-12T17:52:07Z`). The INVALID attempts were procedural (binding/format), not merits reversals. Authorization was sealed only after all three valid unanimous records existed.

## 7. Native target decisions

- Controlled execution occurred only after authorization (point of no return sealed by `artifacts/seal/TARGET_EXECUTION_LOCK.json`, worlds `[x_nonpermit, x_permit]`, updated `2026-09-12T18:31:51Z`). Exactly one native cycle per world; hash-only capsules sealed before conformance.
- Capsules: `capsule_x_permit.json` sha `5505f58b3314afe6fd27d78384c795911a52f244f7fb47c557e8c6eb40bd60f7` (160 bytes, response sha `87f6336c52763de2810fa478d38695f229eeea8b4aaecd68e06b33c49ccef53b`, sealed `2026-09-12T18:31:45Z`); `capsule_x_nonpermit.json` sha `02de7d84c861f5e3c692bc4614b5a89f21cc10eb1e4cedc89bf85445ea1652aa` (167 bytes, response sha `67961314e19c0fc00df45eeff46d396778704a3461ba9c8a0f4b794889c17f10`, sealed `2026-09-12T18:31:51Z`).
- Dual mechanical conformance: `RUN_CONFORMANCE_PASS.json` sha `b79aef4f9968bb133c8f5667e96cf89eea929c292f7e3ec1937963c90b80075d`, verdict `RUN_CONFORMANCE_PASSED`, judged `2026-09-12T18:35:10Z` (verifiers A/B agree; coverage equals the frozen registry).
- Outcome opening (only after dual pass; this sealed record is the sole Decision source used downstream; quarantined responses were not otherwise opened): `artifacts/audits/launch/quarantine/outcome_opening.json` sha `1e80451f8272348597a23a16796f1f04ce41cdec9f9e61376289f6dec70e2fce`, decisions `x_permit=Permit`, `x_nonpermit=NotApplicable`, `match: true`, `conformance: RUN_CONFORMANCE_PASSED`, preregistered classes source `tests/test_completed_world_decisions.py N02/N03 (unlock-gated, written pre-execution)`.
- This satisfies Sec. 8.1 condition 2 (distinct preregistered target classes). S0 is open by heterogeneity; terminals are closed singletons (Sec. 8).

## 8. PC contract hash

- Contract: `artifacts/contracts/pc_xacml_primary.contract.json` sha `7510e78d57b6926263b4c44f8164e56b3b2cf4c1bc3dbed9a4f151d511ad2fd9`, produced `2026-09-12T18:46:17Z`.
- Graph: `S0 --q_supply_missing_attribute--> {S_permit, S_nonpermit}` (sole repair action). Target map built as parsed PDP responses to A_Pi to target map (never from preregistered outcomes); compiler received only `prereg/execution_inputs.json` for worlds/cost/interface/order plus the target-semantics rule.
- Checkpoints: S0 open (`heterogeneous fiber: Permit vs NotApplicable`, fiber `[x_permit, x_nonpermit]`); S_permit closed (singleton `Permit`); S_nonpermit closed (singleton `NotApplicable`). Openness computed from fiber homogeneity, never copied from a closed literal.
- Provenance binds anchor ledger, atom record, H triple, P_R relation, Lambda record, policy projection, request/response hashes, execution inputs, and external manifest.
- Phase-3 manifest: `artifacts/seal/phase3_manifest.json` sha `554e9d159472` binds contract, touch, ledger, external manifest, and execution inputs.

## 9. Primary and independent touch derivations

- Primary: `src/pc/derive_touch.py` (literal Sec. 6 pseudocode over canonical H/PR/Lambda pre/post). Independent: `src/audit/independent_touch.py` (no shared imports or equality helpers; own canonicalization and comparison). Byte-agreement required and observed.
- Output: `artifacts/contracts/touch.json` sha `123672b954f2f79c6d98220f260db2e9786e89fa6006a7ef7e9f991d013f2127`, content `q_supply_missing_attribute: [E]` (H changes; P_R relation constant; Lambda hash identical).
- No-manual-label audit: `src/audit/check_no_manual_labels.py` passes. Presence is allowed only in sealed predictions (`prereg/expected_signature.json`, expected-output fields of `prereg/experiment.yaml`) and in derivation outputs with provenance (`artifacts/contracts/touch.json`); use is forbidden everywhere in computation (source preassignments, input touch fields, schemas accepting touch inputs, expectation imports). Planted label-injection control is detected (Sec. 13).
- This satisfies Sec. 8.1 conditions 4 and 5.

## 10. Completion-space certificate

- Certificate: `artifacts/seal/completion_space_certificate.json` sha `5842ab0f304b911b9647787e13defbdacd6e2d4d3a978e41c2913ef12c45c9b5`, verdict `COMPLETE`, `free_k_relevant_fields: 0`, produced `2026-09-12T18:46:29Z`.
- Machine-checked table (each row cites artifact hashes): X (prereg) NO; U_H (external + wrapper) NO; S/checkpoints (native/wrapper) NO; H (N1/N3 + equivalence) NO; P_R (N1/N3 + adequacy) NO; Lambda (N1/N2/N3) NO; omega (N1/N3) NO; Q (N1 + wrapper) NO; Succ+ (N3 + wrapper) NO; c (prereg normalization) NO; A_Pi (native execution) NO; Atom (N1/native interface) NO; Y (induced response representation) NO.
- Only this certificate authorizes `identified_set.json` cardinality 1. Any row not honestly NO would refuse cardinality 1 and forbid `POSITIVE_NATIVE_STAGE3`.
- Identified set: `artifacts/freezes/identified_set.json` sha `dee7864a7cbf0f57d7ec151581af0d9e603990c517913adc03949ac355107873`, cardinality `1`, signature `[1, INF, 1, 1, INF, INF, 1, INF]`, contract sha `7510e78d57b6926263b4c44f8164e56b3b2cf4c1bc3dbed9a4f151d511ad2fd9`.
- This satisfies Sec. 8.1 condition 7.

## 11. All eight freeze values

- Table: `artifacts/freezes/K_table.json` sha `d8007ab744914c6cb8bc94206cb92609d2d78b23f2e77828befe066fcef131ed`, order `[F000, F100, F010, F001, F110, F101, F011, F111]`, kappa `[1, INF, 1, 1, INF, INF, 1, INF]`, `nontrivial: true`, produced `2026-09-12T18:46:29Z`, solver `primary`, contract sha bound per row.
- Rows: F000 none to 1 (closer exists); F100 E to INF (no closer); F010 R to 1; F001 A to 1; F110 E,R to INF; F101 E,A to INF; F011 R,A to 1; F111 E,R,A to INF.
- Freeze rule is D33-literal (`T(q) intersect S != empty` removes the action; ID-only operations; no interior edits; no partial subactions).
- This satisfies Sec. 8.1 conditions 6 and 8 (nontrivial via every E-containing freeze differing from F000).

## 12. Independent solver agreement

- Primary: `src/pc/solve_freezes.py` (exhaustive enumeration over the tiny graph). Independent: `src/audit/independent_solver.py` (separate tree enumeration; no shared search code). Agreement required on available set, closer existence, exact finite cost, and all eight coordinates; observed agreement holds.
- Clean reproduction: `artifacts/audits/clean_repro.json` (control 5.13) reports `touch_match: true`, `k_match: true`, primary and reproduced kappa both `[1, INF, 1, 1, INF, INF, 1, INF]`, hashes verified, requests rebuilt, PDP reran in isolation, `pass: true`.
- This satisfies Sec. 8.1 condition 9 with Sec. 11.

## 13. Falsification tests (Phase-5 battery, 13/13)

All variants are temporary copies; frozen `external/` was never mutated. Each canary is judged against its sealed entry in `prereg/canary_expectations.json` (sha `1fae1a1eca00`).

- 5.1 source-hash corruption: 5/5 detected (`corruption_pdp.json`, `corruption_policy.json`, `corruption_request.json`, `corruption_response.json`, `corruption_spec.json`; each `detected: true`; frozen externals untouched).
- 5.2 MustBePresent canary: `canary_mustbepresent_removed_comparison.json` matches the sealed exact expectation (`pass: true`).
- 5.3 wrong-category canary: `canary_wrong_category_comparison.json` matches the sealed non-satisfying class.
- 5.4 wrong-datatype canary: `canary_wrong_datatype_comparison.json` matches the sealed finite permissible set (observed alternative within the XACML-dictated set; never silent coercion).
- 5.5 projection canary: `canary_irrelevant_extra_attribute_comparison.json` matches the sealed H-vs-P_R distinction.
- 5.6 preserving perturbations: `perturbation_whitespace.json`, `perturbation_order.json`, `perturbation_rename.json` each report H/P_R/Lambda/T/K unchanged.
- 5.7 changing control: `perturbation_interface_change.json` (and `interface_change.json`) report `INTERFACE_CHANGED` and `THEOREM3_INVARIANCE_NOT_APPLICABLE` for the split `q_construct_attribute + q_submit_request`; never a T3 claim.
- 5.8 cost sweep: `cost_sweep.json` (`0.5/2/10`) reports finite entries rescale, E-freezes stay INF, structural class invariant, dual agreement, `pass: true`.
- 5.9 negative-world sweep: `negative_world_sweep.json` plus `canary_wrong_answer_1/2_comparison.json` report each extra string stays `NotApplicable`, fiber open, E-class preserved, primary never replaced.
- 5.10 ablations: `ablation_H.json`, `ablation_P_R.json`, `ablation_Lambda.json`, `ablation_Atom.json` each report `refuses_positive: true`.
- 5.11 label injection: `label_injection.json` reports `detected: true`, `pass: true`.
- 5.12 leakage: `leakage_graph.json` reports `pass: true`, expected payload reachable only from the final comparison stage; 2A/2B paths never opened it; launch packet/prompt hashes match the freeze; no expectation content in adjudicator inputs; no cross-adjudicator reads.
- 5.13 clean reproduction: `clean_repro.json` reports `pass: true` (Sec. 12).
- Gate: 13/13 PASS. This satisfies Sec. 8.1 condition 10.

## 14. Source, action-interface, and history limitations

- Single-case witness: one fixture, one policy, two worlds, one repair action. No prevalence, benchmark-superiority, safety, causal, or mechanism claim is made.
- Sole-action structure is acceptable here by design; geometry diversity is established elsewhere (controlled finite-substitution evidence), not by this case.
- Native boundary only: the result is structural E-dependence relative to the declared native request interface. The interface-changing split is explicitly out of scope for invariance.
- Cost is an experiment-authored normalization; the structural classification is cost-invariant over the swept finite values.
- History disclosure (Amendment-007 split-gate; no history rewritten): the original single-stage architecture deadlocked (CYCLE_001 rev002/C01-C03 nonunanimous; CYCLE_002 rev004/C04-C06 nonunanimous; both preserved as `NATIVE_ANCHOR_INSUFFICIENT` seals). Pre-execution launch attempts L01-L03 were BLOCKED (0/3 valid ingest; procedural binding/cross-read/paste gaps; merits showed packet-internal Lambda gaps that were then repaired). Launch-002 attempts L04-L06 were BLOCKED (0/3 valid ingest; procedural binding/paste gaps; merits showed dependency/lineage/producer gaps that were then repaired). Launch-003 (packet `8e23901d`, prompt `251f7e58`, registry `d7641f64`) passed unanimously (AUD-L07/08/09 all FIXED with all obligations LEGITIMATELY_DEFERRED) after two procedural corrections on the L08 ingest path; authorization, controlled execution, dual conformance, and outcome opening followed in order. No post-first-execution semantic mutation occurred; a failed run would have been terminal evidence.
- Residuals: frozen launch-packet and conformance-evidence files preserve local dependency-cache absolute paths as run-conformance evidence; they are retained byte-identical for audit integrity and are excluded from the neutral-reference rule that all new Phase-6 sealed documents satisfy. Transient swap-window and toolchain-substitution residuals were documented for chairs before launch. No post-seal semantic change is permitted; any such change requires a new experiment version.
- AI assistance: coding, test generation, debugging, and prose assistance only. AI did not choose anchors; every anchor cites external evidence; expected-result files were never provided to anchor-inference paths except as labeled adversarial review; the launch packet and its adjudicators never received expected touch/K/classification/claim content. No models were trained (deterministic harness).

## 15. Allowed and forbidden claims

Allowed positive wording (spec Sec. 18.1):

> We additionally audited a pre-existing XACML/AuthzForce authorization fixture whose policy, request-context semantics, PDP configuration, and native request/response interface were fixed independently of PC. These external artifacts were sufficient to anchor the PC admission, policy-visible representation, authority/configuration, and atomic request boundary for the measured case. Without manual E/R/A action labels, PC mechanically derived a pure evidence-admission repair and a singleton nontrivial all-freeze signature. This is an external positive Stage-III witness, not a prevalence claim.

Stronger but still acceptable only because every audit passes:

> Unlike Polaris, whose raw repository semantics leave the E/R boundary underidentified, the XACML case contains an independently specified authorization interface sufficient for conditional PC point identification.

No other positive claim is made. In particular, none of the six Sec. 18.2 strings appears in this report (verified by linter against `prereg/allowed_claims.md`), and the Omega_ext/Omega_exp scope lock is observed: external semantics anchor the measured interface, while the finite measurement wrapper (two latent worlds, unit-cost repair, freeze order, solver conventions, recording format) is experiment-authored. The paper role is tiny (spec Sec. 19): Polaris-negative, XACML-positive, controlled-geometry, realizability composition; no manuscript edits occurred before seal.

## 16. Sec. 8.1 checklist evidence (ten conditions)

1. Fixture reproduces: Sec. 2 (`semantic_match: true`). PASS.
2. Distinct targets: Sec. 7 (`Permit` vs `NotApplicable`, `match: true`, conformance passed). PASS.
3. Four anchors FIXED: Sec. 3 ledger plus Sec. 6 unanimous FIXED with authorization. PASS.
4. No manual labels: Sec. 9 (audit passes; contract has no touch field). PASS.
5. Touch uniquely derived: Sec. 9 (`{E}` with manifest binding). PASS.
6. Eight freezes exact: Sec. 11 (all rows bound to the contract hash). PASS.
7. Cardinality 1: Sec. 10 (certificate `free_k_relevant_fields: 0`, `COMPLETE`). PASS.
8. Nontrivial: Sec. 11 (`nontrivial: true`; E-freezes differ from F000). PASS.
9. Dual recomputation agrees: Sec. 9 plus Sec. 12 (touch bytes, solver coordinates, clean reproduction). PASS.
10. Phase-5 13/13: Sec. 13 (all controls pass). PASS.

Emitted outcome `POSITIVE_NATIVE_STAGE3` is therefore the honest taxonomy result. Any single failure would have emitted the corresponding honest outcome (`TOUCH_DERIVATION_MISMATCH`, `SOLVER_MISMATCH`, `NONTRIVIALITY_FAIL`, or `INDEPENDENT_REPRODUCTION_FAIL`) instead; none fired.

## 17. Files and hashes (reproduction binding)

- Seal: `artifacts/seal/FINAL_RESULT_LAUNCH.json` sha `c2febefc21aee90c3bddd4cbffdb4dbfdea19214eb736103886c1c29b9e807d7` (this report binds the pre-tarball hash; `MANIFEST.sha256` binds the final bytes).
- Manifest: `MANIFEST.sha256` (repo root) binds every reproduction-relevant artifact (see Sec. 18).
- Archive: `PC-XACML-S3PLUS-v1.tar.gz` plus `.sha256` (deterministic; sorted entries; fixed mtimes; relative names; no caches, secrets, or absolute entry paths).
- Tests: full suite green at seal (see Sec. 18). Commands run are recorded in `scripts/run_phase6.sh` (POSIX twin) and `scripts/run_phase6.ps1` (authoritative on the pinned host).

## 18. Seal verification (Phase-6 gate)

- Outcome generated from artifacts (Sec. 16), never forced to preregistered values (final comparison only reads `prereg/expected_signature.json`).
- Manifest complete (covers spec, externals except the git-ignored backend clone, prereg including execution inputs and canary expectations, ledger, adequacy and equivalence certificates, launch packet and verdicts with hashes, derived requests, PDP outputs, contract, touch output, completion-space certificate, freeze rows, test results, this audit report, source, scripts, and lockfile; deeply nested upstream-source copies exceeding the host path-length limit are bound via their packet manifests plus packet shas and are verifiable on POSIX or long-path hosts).
- All tests pass (full suite green; 193 passed, 6 skipped at seal).
- Audit report generated (this file, 15 required sections plus checklist and binding).
- Archive reproducible (rebuild yields identical `.sha256`).
- Pre-seal scrub passes over all new sealed documents (no OS usernames, no absolute local paths, no expectation strings outside their sealed homes; frozen-history residuals disclosed in Sec. 14, not rewritten).
- Allowed claims exactly match the outcome (Sec. 15; linter green).
- No post-hoc semantic edits (worlds, target, interface, cost, anchors, freeze order, expectations, and criteria unchanged since prereg; same experiment version).
