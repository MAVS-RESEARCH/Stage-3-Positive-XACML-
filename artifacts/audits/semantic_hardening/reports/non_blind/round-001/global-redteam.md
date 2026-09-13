# NON_BLIND_HARDENING_REVIEW -- global alternatives red team, Wave 1
# Role: alternative source-consistent mappings. Developmental only.

## Per-anchor alternatives
H-A1 full-context-multimap (include empty environment, envelope flags, IncludeInResult): basis request.xml:2,:18,:4,:9,:14; H_initial omits env. Diverges: candidate is designator-visible-bags-only. Materiality: NOT material to pairwise distinctness (env/flags constant across worlds), MATERIAL to frozenness/hash claim.
H-A2 raw-XML-infoset (byte-identical file): basis atom wrapper byte-copy stress + H source file hashes. Diverges: whitespace/order/IncludeInResult matter. Immaterial here, material to native-ness claim.
H-A3 resolved-post-handler context: basis data-flow optionally-adds + route-b pass-through assumption. Diverges: request bags vs PDP-visible bags. MATERIAL if handler adds/defaults anything.
P_R-B1 Match-outcome equivalence (per-Match TRUE/FALSE/INDETERMINATE, not bag equality): basis policy.xml:14-43 literals + Sec.7.6. Diverges on multi-valued/type-variant bags. IMMATERIAL to this pair (singletons separate under both), MATERIAL to general adequacy claim.
P_R-B2 full-request equality (finer, incl. environment/flags/Issuer raw): basis request.xml:18,:2 metadata gap + Issuer keyed-but-never-observed. Immaterial to pair, material to scope.
L-C1 narrow-executable (StaticPolicyProvider+policy only) vs L-C2 broad-capability (+handler/PIP/defaults/build/JVM/PARENT_DIR/maxPolicySetRefDepth): basis execution_inputs sources + pdp.xml:2,:7. Diverges on what post==pre must cover. MATERIAL to constant-Lambda design.
A-D1 native-transaction-only (construction as pre-step outside atom) vs bundled candidate: basis N1 data-flow covers PEP/handler/PDP only; construction_rule is X-class/prereg. MATERIAL to Q cost attachment + no-logic claim.
A-D2 paired-interval (pre original-response + post repaired-response = TWO evaluations, not one atom): basis atom_record pre/post + response.xml Indeterminate. MATERIAL to atomicity claim.

## Numbered material objections
1. H: H-A1 empty-envelope belongs in H (request.xml:2,:18; C-coverage).
2. H: H-A3 request-bags != resolved-context without handler dump (A-underidentification).
3. P_R: B1 defensible coarsening (policy.xml:14-43; B-scope).
4. P_R: B2 Issuer/envelope scope underdetermined (E-grounding).
5. Lambda: C2 frozenness needs broad pinned executable/env; glob defeats hermeticity (D-constancy).
6. Lambda: C1/C2 boundary ambiguous changes equality criterion (B-boundary).
7. Atom: D1 wrapper-vs-native split (B-boundary/F-composition).
8. Atom: D2 two-transaction interval, not one atom (B-boundary).

## Eliminated vs surviving
ELIMINATED by packet: selector/XPath/reference channels (adequacy zeros + policy scan: only 4 AttributeDesignators); PIP-injects-values (pdp sole policyProvider + no_pip); missing-is-different-attribute (response.xml:10 triple matches policy.xml:20 + omega ledger).
SURVIVING: objections 1-8 (need: empty-Category spec text; flag semantics; Issuer rule; handler/PIP dump or default config + build/JVM pin + resolved-glob listing; explicit Atom boundary diagram placing the build step).

## Cross-anchor consistency
Handler triple-counted (H pass-through + Lambda interface/preprocessor + Atom path, same N1 sentences): if handler is Lambda, H-A3 context is Lambda-state not history; if Atom path, defaults belong to neither H nor P_R hashes. Gap: empty environment + envelope flags owned by NONE (H omits, P_R excludes, Lambda excludes, Atom copies-but-drops-from-H-hash). Issuer shared by H/P_R with zero observations (jointly ungrounded). P_R 4 coords vs H 3->4 align only via adequacy cert; Lambda post==pre vs Atom pre/post hash different objects (capability vs responses): glob-resolution drift across worlds undetectable.
