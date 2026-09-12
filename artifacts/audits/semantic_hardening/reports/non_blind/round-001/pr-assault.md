# NON_BLIND_HARDENING_REVIEW -- P_R assault, Wave 1, HARDENING_ROUND_001 input
# Role: P_R / policy-visible representation. Developmental only.

## DEV verdicts
- pr_relation.json: DEV-PARTIAL (coordinates correct, rule over-general).
- policy_adequacy_certificate.json: DEV-PARTIAL (channels partially inventoried).
- policy_projection.json: DEV-PASS as representation (5 designators, 2 datatypes, 0 selectors/XPath/refs/obligations).
- policy.xml ground truth: SOURCE-PASS (all MustBePresent=true, no Issuer, 2 literals share action-id coordinate).
- pdp.xml: SOURCE-PASS but UNDER-CONSTRAINED by certificate.
- derive_PR.py: DEV-PARTIAL (bakes over-fine rule). parse_policy.py: DEV-PASS. check_policy_adequacy.py: DEV-PARTIAL (checks subset).

## Admitted-interface bag states (initial + 2 worlds)
C1 subject-id fixed TRUE; C2 some-attribute missing->Indeterminate / riddle->TRUE / other->FALSE (sole varying coordinate); C3 resource-id fixed TRUE; C4 action-id one bag two Matches. No duplicates/multi-bags/non-null Issuers/empty bags occur: bag-identity partition == Match-vector partition here.

## Objections (anchor=P_R)
O1 -- Bag-identity finer than Match-equivalence (duplicates/extra values collapse under existential Match; shared C4 coordinate proof). Category C. MATERIAL generally, IMMATERIAL on admitted singleton triple; rule as stated quantifies unboundedly so FALSE as stated.
O2 -- Issuer pooling glossed (designator omits Issuer; pooling rule unquoted). Category C. Same materiality shape as O1.
O3 -- Error vs empty conflated (all MBP=true; missing=>Indeterminate per N1; rule has no Indeterminate token; P_R(missing,missing) undecided). Category F. MATERIAL (C2 missing state is in the triple).
O4 -- Channel inventory lossy (obligations_advice/match_functions/rule_combining collected but unasserted; pdp check top-level names only). Category B. PARTIALLY MATERIAL.
O5 -- Glob expansion unbounded (${PARENT_DIR}/policies/*.xml never resolved to file set). Category B/E. MATERIAL to exclusivity.
O6 -- 5-to-4 dedup unexplained in evidence (action-id x2 -> 1 coordinate). Category F. LOW materiality, representation gap.

## Repairs (evidence/representation only)
R1: interface-scoped coincidence lemma (Match-vector relation == bag-identity on admitted histories) + duplicate/extra/Issuer note with policy.xml:34-43 proof.
R2: error token in rule + certificate (missing+MBP=true => Indeterminate token; empty unreachable here).
R3: mirror full inventory in certificate + glob-resolution artifact + quote pdp.xml location string.
R4: dedup rationale note (5 occurrences -> 4 coordinates; action bag held once, evaluated twice).

## Falsifiers
N1 quote on cardinality/duplicates beyond Match truth; Issuer-distinguishing quote/probe; MBP-missing-yields-empty-bag quote/probe; schema-level Target-grammar exhaustiveness proof; sealed single-file glob manifest; existing dedup rationale locator.
