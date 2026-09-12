# PROTOCOL AMENDMENT 007 — Split-Gate Semantic Certification and Execution Conformance

Experiment: `PC-XACML-S3PLUS-v1` (unchanged; no fork, no ID change).
Type: prospective gate-architecture correction, committed as a new commit. No
historical commit, panel, revision, packet, seal, round, sweep, assessment,
or result is rewritten, squashed, amended, deleted, overwritten, concealed,
or retroactively reinterpreted. Amendments 001–006 remain historical truth.
CYCLE_001 (`CERTIFICATION_FAILED_REPAIRABLE`) and CYCLE_002
(`CERTIFICATION_FAILED_IRREDUCIBLE`) remain sealed terminal history (see
`artifacts/audits/amendment_007_basis/HISTORICAL_BASIS.json`).

## 0. Why (measurement-gating deadlock, preserved)

The single-stage gate deadlocked: CYCLE_002 withheld unanimity over
run-dependent facts (post-execution equality, staged/deployed identity at
invocation, checkpoint ordering) that cannot exist before the execution they
describe, while the gate required them beforehand. That finding stands —
CYCLE_002 is not a success, AUD-C04/C05/C06 were not wrong, seals stay
sealed. With zero target executions observed, the deadlock is architectural,
not semantic: repair is a gate redesign separating what is knowable before
execution (Class S) from what is checkable only during/after it (Class R).
No semantic standard is weakened; nothing downstream has been observed, so
nothing downstream is reinterpreted.

Loop law: `while verified_source_grounded_material_defect_exists and
target_execution_count == 0: repair_defect()` — never positivity-seeking.

## 1. Historical basis (immutable)

`artifacts/audits/amendment_007_basis/HISTORICAL_BASIS.json` pins CYCLE_001,
CYCLE_002, AUD-C01–C06 raw/verdict/attestation/provenance hashes, revisions
001–004 packet hashes, FINAL_RESULT seals, CYCLE_002 objections/assessment,
external specimen hashes, and zero-execution proof. It states: CYCLE_002 is
terminal for the old single-stage architecture; Amendment 007 does NOT reopen
CYCLE_002; Amendment 007 creates a prospective pre-measurement split-gate
because no target-world result has ever been observed; no chair is recoded as
passing; the manuscript must disclose both failed panels and the redesign.

## 2. Class S vs Class R

CLASS S (pre-execution, required before launch): H/P_R definitions and
admitted interfaces; Lambda extensional definition, constituent set,
canonicalization/hash algorithm, static executable/configuration bytes; Atom
native transaction definition; wrapper/native boundary; frozen
requests/worlds; policy/configuration; source provenance; exact execution
procedure; exact future checkpoints; exact future conformance predicates,
producers, and verifiers. A Class-S defect blocks launch.

CLASS R (run-conformance, deferred only with frozen predicate): Lambda
pre/post invocation equality; actual runtime classpath identity; actual
deployed policy/config identity; actual staged request bytes; exact native
invocation occurrence; response-after-invocation ordering; checkpoint order;
permitted target-cycle count. Each deferred item must satisfy §6
admissibility; laundering a knowable static fact into Class R is
IMPROPER_DEFERRAL and blocks launch.

## 3. CYCLE-002 reassessment (new ledger, old ledger untouched)

`artifacts/audits/amendment_007_basis/REASSESSMENT.json` reclassifies each
C04–C06 objection as STATIC_REPAIR_REQUIRED, LEGITIMATE_RUN_CONFORMANCE_
OBLIGATION, STATIC_NONMATERIAL, SOURCE_REFUTED, DUPLICATE,
IRREDUCIBLE_SEMANTIC_AMBIGUITY, or UNRESOLVED, with repair pointers. Prior
"non-decisive because deferred measurement already blocks unanimity"
reasoning is explicitly reopened for static items. R7-01 (built artifacts),
R7-02 (lineage), R7-03 (invocation sources), R7-04 (tool-copy currency),
R7-05 (tree binding) are STATIC_REPAIR_REQUIRED; R7-06/R7-07 are
LEGITIMATELY_DEFERRED obligations; R7-08 is polish/duplicate.

## 4. Developmental swarm (non-blind, never certify)

All subagents spawned under Amendment 007 are NON_BLIND_DEVELOPMENTAL: full
history and preregistered expectations visible, zero certification power.
Mandatory roles: protocol-circularity red team; static-vs-run boundary;
deferral-abuse hunter; Lambda static-closure; Lambda packet-reconstruction;
runtime/classpath closure; Atom static-boundary; staging/invocation;
provenance/history-integrity; packet-completeness; outcome-leakage;
alternative-semantics red team; independent reconstruction; global hostile
reviewer; state-machine safety; quarantine bypass; verifier independence;
post-execution mutation bypass. Central attack question: "Can any fact
knowable before execution be laundered into the deferred registry?" Any such
path is VALID_MATERIAL.

## 5. Static hardening (source-grounded, pre-launch)

Repair every STATIC_REPAIR_REQUIRED item with source-grounded evidence:
include built driver sources, POMs, and executed JAR bytes in the launch
packet with method records; content-pin the operative lineage current value
(history preserved, never rewritten); include complete static
invocation/staging/gate sources (PdpRunner, run_authzforce, phase scripts,
recompute, verify gates); enforce packet tool-copy currency; treat tree-sha
as provenance (file-level hashes operative); eliminate SKIP-over-operative
constituents at launch verify (recompute subset + deployment/classpath gates
+ conformance verifiers jointly cover the claim; recompute alone is
insufficient — documented limitation for launch chairs). Retain the smallest
complete extensional Lambda; every inclusion/exclusion carries a recorded
semantic reason. After each mutation: source verify → tests → natural-stage
invariant → execution count 0 → fresh attackers → repeat, until
NO_UNRESOLVED_STATIC_MATERIAL_DEFECT or genuine IRREDUCIBLE_SEMANTIC_
AMBIGUITY (then STOP NEGATIVE).

## 6. Run-conformance registry (frozen, machine-readable)

`artifacts/audits/launch/run_conformance_obligations.json` (+
`schemas/run_conformance_obligation.schema.json`) defines six obligations:
RC-CLASSPATH-ACTUAL, RC-DEPLOYMENT-ACTUAL, RC-REQUEST-ACTUAL, RC-LAMBDA-POST,
RC-ATOM-ORDER, RC-DEPS-CONSISTENT. Each records obligation_id, anchor,
proposition, reason_deferred (future-execution dependence), depends_on,
evidence_producer (frozen file + mode), code_sha256 (live file hashes,
re-verified at freeze via LAUNCH_FREEZE execution_code), produced artifacts,
canonicalization, deterministic pass_criterion, independent verifier A/B,
needs_decision_content=false, permitted_fields (hashes/counts/order/names
only — RC-REQUEST carries AttributeValue sha256, never plaintext),
prohibited_fields (Decision/Permit/NotApplicable/touch/K/classification/
expected_*), failure_outcome (EXECUTION_CONFORMANCE_FAIL; TERMINAL, no rerun,
no repair), and the no-post-execution-repair rule. The registry contains no
expected decisions, touch, K, or classification. Admissibility requires:
truth genuinely depends on the future run; semantic interpretation frozen;
evidence producer frozen; verifier frozen; binary mechanical predicate;
failure cannot trigger post-outcome repair.

## 7. Phase 2E — pre-execution launch certification

Fresh namespace AUD-L01/L02/L03 (L = LAUNCH; later L04–L06 if pre-execution
re-freeze is ever needed). Never reuse AUD-C01–C06; never recode old chairs.
Each chair receives ONLY the frozen launch packet, the frozen prompt
(`artifacts/audits/launch/launch_certification_prompt.txt`), and the verdict
schema — never expected touch/K/classification, desired result, manuscript
claims, prior panel outputs, or hardening history. Anchors judged
FIXED/PARTIAL/AMBIGUOUS/UNSUPPORTED with exact source locators; each
obligation judged LEGITIMATELY_DEFERRED/IMPROPER_DEFERRAL/UNSUPPORTED.
Attestation text must bind auditor ID AND launch packet_sha256 AND
prompt_sha256 (replay-across-revisions fix). Launch requires one complete
fresh triple with H/P_R/Lambda/Atom all FIXED unanimously AND every
obligation LEGITIMATELY_DEFERRED unanimously. No majority, no fourth chair,
no reconciliation. IMPROPER_DEFERRAL blocks launch as firmly as non-FIXED.
Ingest and unlock refuse once TARGET_EXECUTION_LOCK.json exists.

## 8. Burn-in (before launch chairs)

At least two clean fresh developmental sweeps after the LAST Amendment-007
or static mutation, with no mutation between; zero VALID_MATERIAL; zero
UNRESOLVED; explicit deferral-abuse attack; explicit post-execution-bypass
attack; taxonomy-free holdout; full suite green; source/specimen integrity
green; completed executions 0; touch/K/freezes NOT_COMPUTED. Holdout finding
of VALID_MATERIAL reopens Amendment 007 or static hardening and restarts
burn-in. Then freeze LAUNCH_SEMANTIC_PACKET, RUN_CONFORMANCE_REGISTRY,
TARGET_EXECUTION_CODE, CONFORMANCE_VERIFIER_A/B (hashes immutable in
LAUNCH_FREEZE.json, including environment/toolchain binding).

## 9. Launch freeze (point of semantic finality)

`src/audit/launch_freeze.py --build-launch-packet` assembles
`artifacts/audits/launch/launch_packet/` (operative rev004 bytes + static
additions: invocation sources, recompute/verify/verifiers, execution inputs,
POMs, executed JARs, registry, prompt; lineage current refreshed to
operative with history append; tool-copy currency gated; clone pristine
gated; zero-execution gated) and seals LAUNCH_FREEZE.json (packet/prompt/
registry hashes, execution_code hashes, environment binding, panel,
completed_executions 0). `--verify-launch` re-checks packet bytes, aggregate,
prompt, registry, execution code, extra-file absence, and the execution lock.
After AUD-L01/L02/L03 unanimous pass: PREEXECUTION_SEMANTIC_CERTIFICATION_
PASSED + TARGET_EXECUTION_AUTHORIZED (bound to packet/prompt/registry
hashes). From authorization onward no changes to H/P_R/Lambda/Atom, worlds,
requests, targets, cost, Q, freeze order, semantic definitions, conformance
predicates, producers, or verifiers. Pre-first-invocation bug → revoke
authorization, preserve the failed launch, repair transparently, re-freeze,
fresh panel. THE FIRST COMPLETED-WORLD PDP INVOCATION IS THE PERMANENT POINT
OF NO RETURN (sealed by artifacts/seal/TARGET_EXECUTION_LOCK.json; reopen
and completed-mode execution refuse thereafter).

## 10. Phase 2F — controlled target execution (post-authorization only)

`src/xacml/run_authzforce.py --mode completed` refuses without a valid
TARGET_EXECUTION_AUTHORIZED bound to the live LAUNCH_FREEZE. It stages
verified fixture copies, pre-verifies, invokes exactly one native cycle per
world, post-re-verifies (transient-swap window documented residual;
persistent drift fails closed), seals hash-only outcome capsules
(`artifacts/audits/launch/quarantine/capsule_<world>.json`: sha256 + bytes,
never Decision content), appends the execution lock, and logs exit
codes/byte counts only. Run-conformance evidence (hashes/counts/order/names)
is separated from target outcome artifacts (raw response bytes, quarantined,
hashed, sealed). The conformance path never parses Decisions (dual verifiers
enforce 64-hex evidence shape and prohibited-content rejection).

## 11. Post-execution conformance (mechanical, dual)

`src/audit/conformance_verify_a.py` and `conformance_verify_b.py` are
independent implementations over identical evidence format (no shared
helpers). Per obligation: SATISFIED/FAILED/UNVERIFIABLE. Both must agree on
verdicts AND overall; coverage must equal the frozen registry; missing
registry fails closed to UNVERIFIABLE; stale PASS records are revoked on any
non-pass. `judge_conformance` seals exactly one outcome:
RUN_CONFORMANCE_PASSED (all SATISFIED), EXECUTION_CONFORMANCE_FAIL (any
FAILED), EXECUTION_CONFORMANCE_UNVERIFIABLE, or EXECUTION_CONFORMANCE_
VERIFIER_MISMATCH. Any non-pass is TERMINAL for this experiment instance:
no semantic hardening, no rerun after a completed world has been invoked.
The quarantined outcome is preserved without use.

## 12. Outcome opening (only after dual pass)

After PREEXECUTION_SEMANTIC_CERTIFICATION_PASSED + RUN_CONFORMANCE_PASSED,
`src/xacml/parse_response.py` opens quarantined responses (content-bound
allowlist: pre-pass only byte-identical frozen originals parse; post-pass
any file parses). Then: compare x_permit/x_nonpermit against preregistered
target classes, construct A_Pi, determine S0/terminals, compile the Phase-3
contract, derive touch, compute K, run Phase 5. Mismatch emits
TARGET_REPRODUCTION_FAIL with no semantic repair. Pre-pass rename-evasion is
blocked by the content allowlist (filename gate retained defense-in-depth).

## 13. Phases 3–6 (unchanged)

Mechanical contract + dual touch + no-manual-label audit; eight freezes +
independent solver + completion-space certificate; falsification battery;
final seal + provenance + claim gating + deterministic package. Expected
touch/K/classification/solver semantics frozen; POSITIVE_NATIVE_STAGE3 only
on the original conjunction. Amendment 007 does not make the experiment
positive; it makes the frozen experiment logically executable.

## 14. Outcome taxonomy (additive only)

Historical eight outcomes preserved; historical FINAL_RESULT files retain
original taxonomy and bytes. Added execution-integrity outcomes:
EXECUTION_CONFORMANCE_FAIL, EXECUTION_CONFORMANCE_UNVERIFIABLE,
EXECUTION_CONFORMANCE_VERIFIER_MISMATCH — frozen-run conformance failures
only, never relabeled as semantic underidentification.

## 15. Anti-outcome-overfitting (post-invocation freeze)

After first completed-world invocation, forever forbidden for this instance:
redefine H/P_R/Lambda/Atom; add/remove constituents from observed behavior;
change Atom boundary, requests, worlds, targets, costs, touch rules, freeze
order, conformance predicates; rerun a failed measurement for a favorable
result. A failed run is evidence.

## 16. Claim discipline (disclosure)

On success the manuscript states: original single-stage architecture;
C01–C03 failure; source-grounded hardening; C04–C06 failure; preserved
NATIVE_ANCHOR_INSUFFICIENT seals; pre-execution measurement-gating
circularity diagnosis with zero target executions; prospective Amendment 007
split (static mappings + all future conformance predicates frozen and
freshly certified before the first target execution; post-execution only
preregistered mechanical predicates evaluated before outcomes were used); no
post-first-execution semantic mutation. Allowed paragraph as instructed in
the amendment brief. Never: previous panels passed; original protocol
succeeded; C04–C06 mistaken for blocking; redesign preregistered; post-run
evidence known pre-run; gate weakened until pass.

## 17. Test battery (adversarial, pre-launch)

Split-gate tests (`tests/test_launch_split.py`, `tests/test_builder_hardening.py`)
cover: static-vs-deferred labeling; JAR/POM/driver visibility; lineage
currency; packet-only recomputation; legitimate deferral shape; producer/
verifier freeze; decision/touch/K quarantine; unanimous-FIXED launch;
IMPROPER_DEFERRAL block; pre-authorization execution refusal; code-hash
drift block; request/classpath/deployment mismatch failure; Lambda pre/post
failure; order violation failure; verifier outcome-blindness (hex-shape +
prohibited-content rejection); verifier agreement (verdicts + overall +
coverage); parser quarantine (filename + content allowlist, both argv,
rename-evasion); lock closure (ingest/unlock/verify/build refuse
post-invocation); stale-PASS revocation; attestation revision binding;
missing-registry fail-closed; historical-seal stability; specimen stability;
expectation isolation. Known residuals documented for chairs: transient
TOCTOU swap window; toolchain (JDK/lxml/Saxon) substitution outside
packet-only recompute (environment binding recorded, live re-check at
verify); Central-by-coordinates provenance.

## 18. Stopping boundary (this session)

Development stops at AMENDMENT_007_SPLIT_GATE_FROZEN +
NO_UNRESOLVED_STATIC_MATERIAL_DEFECT +
BLOCKED_PENDING_PREEXECUTION_LAUNCH_CERTIFICATION with
completed_target_world_executions = 0, touch = NOT_COMPUTED, K =
NOT_COMPUTED. AUD-L01/L02/L03 are never manufactured in-session; target
worlds never execute here; touch never derives; K never computes.

## 19. Annex (frozen at launch)

Launch packet manifest + PACKET_SHA256; registry sha; prompt sha;
execution-code hashes; environment binding; panel IDs; handoff paths under
`artifacts/audits/launch/` and per-chair records under
`artifacts/audits/launch_certification/`. This document's hash and the
launch commit are reported at freeze.
