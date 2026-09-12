# PROTOCOL AMENDMENT 003 — Autonomous Adversarial Certification Rehearsal (Phase 2B-R)

Experiment: `PC-XACML-S3PLUS-v1` (unchanged; no fork, no new ID, no reset).
Type: prospective developmental-layer amendment, committed as a new commit.
Historical commits, hardening rounds, adjudications, freezes, and Amendments
001/002-equivalent hardening history are never amended, squashed, deleted, or
rewritten.

## 1. Operative state at amendment time (verified from working checkout)

- repository commit: `36423ca`
- Phase 1: COMPLETE; Phase 2A: COMPLETE
- HARDENING_ROUND_000/001/002 preserved; ROUND_002 convergence 10/10 PASS
- candidate final semantic packet frozen and verified
  (`FINAL_BLIND_PACKET` sha `4b9f6556bd9d136010adfc0bd5f140b3da7b02daf6485d666a05b63c1`)
- frozen prompt `prereg/final_certification_prompt.txt`
  sha `4ec4f9b6e21794f8068d225bf7b6825c8ab3f3a4ca1b43161fef504b08dcbdf3`
- state: `BLOCKED_PENDING_FINAL_CERTIFICATION`
- AUD-C01/C02/C03: NOT RUN; completed-world PDP evaluations = 0
- target audit = NOT_RUN; touch = NOT_COMPUTED; K = NOT_COMPUTED
- freeze lattice = NOT_COMPUTED; Phases 3+ = NOT_RUN
- no downstream Stage-III measurement result observed

Therefore this amendment cannot have been selected in response to an observed
measurement result.

## 2. Immutable scope (nothing below changed)

Experiment ID, frozen XACML/AuthzForce sources, fixture bytes, source hashes,
authoritative spec bytes, worlds and latent values, target semantics, H/P_R/
Lambda/Atom candidate mappings, Q/action and wrapper definition, unit cost,
freeze order, expected touch/K/classification, success/failure criteria,
mechanical derivation rules, certification unanimity rule, and claim scope.

## 3. The single mutation: insert Phase 2B-R

New order (in place, no fork):

```text
Phase 2A — Source-Native Extraction
  -> Phase 2B-H — Iterative Semantic Hardening
  -> Phase 2B-F — Candidate Semantic Freeze (REVISION_001 preserved)
  -> Phase 2B-R — Autonomous Adversarial Certification Rehearsal (NEW)
  -> [reopen to 2B-H iff a real source-grounded defect survives]
  -> Final Semantic Freeze (fresh bytes + hashes)
  -> Phase 2C — Fresh External Blind Certification (AUD-C01/02/03)
  -> Target Audit -> Phase 3+
```

Current freeze is redesignated `SEMANTIC_FREEZE_REVISION_001` and preserved
byte-identically. Phase 2B-R attacks REVISION_001 AS-IS first.

## 4. Contamination rule (subagents authorized, never blind)

The task-delegation/subagent system is explicitly authorized during 2B-R and
must be used aggressively. Every subagent spawned from this session is assumed
context-contaminated (may know history, critiques, expected touch/K/
classification, desired result). Therefore every subagent output is labeled
`NON_BLIND_CERTIFICATION_REHEARSAL` or `NON_BLIND_ADVERSARIAL_REVIEW`. Such
outputs may attack, emulate, inspect, propose, implement, test, and challenge,
but may NEVER populate AUD-C01/C02/C03, count toward certification, unlock the
target audit, or be described as blind/independent/external. Namespace
separation enforces this in code and schema.

## 5. Rehearsal harness (developmental only)

- implementation: `src/audit/certification_rehearsal.py`
- artifacts: `artifacts/audits/certification_rehearsal/` with immutable sweep
  IDs `REHEARSAL_SWEEP_001`, `REHEARSAL_SWEEP_002`, ...
- NEVER writes into `artifacts/audits/final_certification/` or any AUD-C
  namespace (fail-closed guard + tests).
- Each sweep records: freeze revision, packet/prompt/manifest hashes, subagent
  identities/roles, raw reports, parsed objections, locators, materiality,
  source-verification outcomes, surviving/dismissed objections with reasons,
  mutation-required flag, invariant result, execution count, timestamp, commit.
- Rehearsal prompt = substantive final-certification standard plus the header:
  `THIS IS A NON_BLIND DEVELOPMENTAL REHEARSAL. THIS OUTPUT CANNOT CERTIFY
  OR UNLOCK THE EXPERIMENT.`

## 6. Mandatory panels per sweep

- PANEL A (emulators): >=3 subagents, each given the candidate packet + frozen
  prompt + rubric/schema, judging H/P_R/Lambda/Atom as
  FIXED/PARTIAL/AMBIGUOUS/UNSUPPORTED; isolated from each other; labeled
  `NON_BLIND_CERTIFIER_EMULATION`.
- PANEL B (specialists): H/context, P_R/relation, Lambda/capability,
  Atom/transaction+wrapper, packet completeness, provenance/hash integrity,
  locator correctness, natural-Stage-III invariant.
- PANEL C (alternative-semantics red team): construct materially different
  source-consistent countermodels that would undermine FIXED.
- PANEL D (global reviewer): cross-anchor leakage (H/Lambda misallocation,
  unmodeled P_R channels, Atom-hidden decisions, wrapper drift, joint-proof
  gaps).
- PANEL E (evidence adversary): reconstruct mappings directly from frozen
  sources + exact code/requests/canonicals; report reconstruction failures.

## 7. Objection normalization (no automatic patching)

Every objection is normalized into the rehearsal objection ledger with:
objection ID, sweep, freeze revision, anchor, claim attacked, source locator,
counterinterpretation, materiality, outside-information dependence,
contradiction of frozen evidence, missing evidence, definition incompleteness,
implementation-bug flag, downstream-resource effect, disposition.

Allowed dispositions: `VALID_MATERIAL`, `VALID_NONMATERIAL`, `DUPLICATE`,
`SOURCE_REFUTED`, `OUT_OF_SCOPE`, `REVIEWER_ERROR`, `IRREDUCIBLE`,
`UNRESOLVED`. `REVIEWER_ERROR` requires exact frozen-source evidence showing
the criticism is factually wrong; mere disagreement never qualifies.
`VALID_MATERIAL` requires a source-grounded defect that could change a
certifier's FIXED judgment or downstream resource interpretation.

## 8. Reopen rule (conservative)

Do NOT reopen on PARTIAL/AMBIGUOUS/UNSUPPORTED alone. Reopen (`SEMANTIC_FREEZE_REOPENED`
+ return to 2B-H) IFF at least one `VALID_MATERIAL` objection survives source
verification. Otherwise REVISION_001 stands and the protocol proceeds to a
fresh final freeze + genuinely fresh external Phase 2C. All reopen/preserve
decisions record exact evidence and hashes.

## 9. Guards (fail-closed)

- external-system invariant holds at sweep open and close
- completed-world execution count stays 0 (target scan empty)
- touch/K/freeze lattice uncomputed; Phases 3+ not run
- rehearsal never imports expected-signature content into judgments as ground
  truth; contamination is labeled, never laundered into certification
- certification namespaces (`final_certification/`, `AUD-C0X`) refuse
  rehearsal IDs, rehearsal labels, and in-session subagent provenance

## 10. Disclosure obligation

Phase 2B-R is developmental attack infrastructure, not evidence of external
validity. It must never be described as blind certification, independent
validation, or external review. The final audit states sweep IDs, surviving
vs dismissed objections with reasons, any reopen lineage, and the fresh
final-freeze hashes consumed by Phase 2C.
