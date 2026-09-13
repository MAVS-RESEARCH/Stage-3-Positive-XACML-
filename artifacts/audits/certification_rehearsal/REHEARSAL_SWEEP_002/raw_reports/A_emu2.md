NON_BLIND_CERTIFIER_EMULATION — REHEARSAL_SWEEP_002 — REVISION_001
Panel A emulator-2 (Lambda). Contaminated, never blind. No prior sweep seen. Cannot certify or unlock.

Verdict: Lambda NOT FIXED (PARTIAL at best, AMBIGUOUS on constancy).

Q1 behavior change with all hashes unchanged: add second file under the frozen glob policies/*.xml (pdp.xml StaticPolicyProvider + PARENT_DIR glob). Engine/policy/provider-element/triple/pre_hash values all unchanged; effective policy set and evaluation change. Element-scoped C14N excludes provider siblings; policy_bytes covers policy.xml only.
Q2 listing-not-content: version triple without content hashes (indirection via packet manifest); policy_location sha equals the listing FILE hash, not member contents; resolved_defaults sha equals resolved_effective FILE hash.
Q3 constancy deferred not demonstrated: deferral record promises post==pre check at Phase-3 touch derivation; no post hash, no re-derived comparison, no frozen proof the Q1 drift is impossible. Future abort check is enforcement, not present justification. Under prompt preserve-ambiguity rule, NOT FIXED.
