# NON_BLIND_HARDENING_REVIEW -- packet completeness audit, Wave 1
# Role: packet-completeness / provenance audit. Developmental only.

## Presence table (claim -> cited evidence -> present-as-bytes?)
- H checkpoints: bags inline PRESENT; source file hashes PRESENT as values; S_permit/S_nonpermit request bytes ABSENT (hashes only); proof ref VALID + sibling copy PRESENT.
- H proof route-a premise -> derived/route_a_probe.json ABSENT; no_pip -> pdp.xml PRESENT; adequacy -> candidates copy PRESENT, full projection ABSENT; add-only claim -> request bytes ABSENT; coordinates-designed -> projection ABSENT; n1_locators -> ABSENT as resolvable bytes; equality-to-resolved uncheckable without repaired bytes + probe.
- PR rule+coords inline PRESENT; adequacy/projection hashes only; full projection ABSENT; derive_PR.py ABSENT.
- Adequacy PASS: inventory PRESENT via corpus; hashes only; full projection ABSENT; checker ABSENT.
- Lambda inputs PRESENT via corpus; derive_Lambda.py ABSENT; post null PRESENT.
- Atom native boundary + N1 locator ABSENT as bytes; construction counts/hashes only; builder ABSENT; preregistration PRESENT via candidates/execution_inputs.json.
- execution_inputs.json worlds/rule/freeze/sources inline PRESENT.
- Static consumers: derive_H needs 4 inputs (2/4 present); prove needs 7 (3/7); derive_PR 2 (1/2); derive_Lambda 3 (3/3); derive_atom 5 (2/5); check_policy_adequacy 3 (2/3).

## Objections (anchor=GLOBAL)
1. Repaired XML bytes cited, hash-only. Cat A/B. BLOCKING.
2. Route-a probe bytes absent. Cat B. BLOCKING.
3. Full projection absent (5 rows incl. duplicate action-id vs PR 4 coords). Cat A/B. BLOCKING (PR/adequacy uncheckable).
4. Wrapper bytes + builder absent; INV-05 uncheckable. Cat B. BLOCKING.
5. All stripped-text N1 locators unresolvable from packet bytes (raw HTML lines differ; index admits convenience-only). Cat C. MAJOR.
6. Manifest seals an incomplete set; omits Sec.3 files. Cat D. MAJOR.
7. Rubric lacks procedures for hash-only evidence, route-a/projection/builder gaps, locator resolution, manifest check, Q/wrapper/adequacy handling. Cat D. MAJOR.
8. Proponent verdicts (FIXED/VALID/PASS/PROVEN/INDEPENDENT_CHECK_PASS) embedded as candidate bytes used as self-evidence. Cat E. MINOR.
9. Repo-path references (derived/, external/) absent in packet layout (candidates/, corpus/). Cat G. MINOR (remap assumption).
10. Ledger-vs-derived hash drift (checkpoint hashes, produced_utc) unexplained; no derivation log. Cat D/E. MINOR.

## Repair file list (verbatim add, no execution, reseal only; corpus hashes unchanged)
derived/requests/request_x_permit.xml, request_x_nonpermit.xml, derived/policy_projection.json, derived/route_a_probe.json, src/xacml/build_repaired_requests.py, src/pc/derive_H.py, src/pc/derive_PR.py, src/pc/derive_Lambda.py, src/pc/derive_atom.py, src/pc/prove_h_equivalence.py, src/xacml/check_policy_adequacy.py, src/xacml/capture_resolved_context.py, plus frozen stripped-text spec with cited numbering OR explicit raw-HTML locator map replacing stripped-text lines, plus derivation-run log pinning produced_utc/normalization.

## Contamination check
No numeric expected touch/K/classification/desired-verdict strings in candidates/* or corpus/*. Negative mentions only (rubric expected-touch/K lines, index no-touch/K/outcomes line). No per-world Decision outcome bytes (generic Response/Decision/StatusCode class words only; execution_inputs target_semantics explicitly states no per-world outcomes). NAMING-LEVEL HINT FLAGGED (not numeric expectation): world labels + values disclose intended mapping via policy literal (execution_inputs worlds, H_permit values, policy.xml:19 riddle me this under Effect=Permit rule); proponent verdict tokens present. Recommendation: declare world-values as measurement inputs (blinded categories are outcomes, not inputs), never as evidence.
