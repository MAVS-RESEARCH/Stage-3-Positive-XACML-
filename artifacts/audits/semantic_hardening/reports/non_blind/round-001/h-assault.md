# NON_BLIND_HARDENING_REVIEW -- H assault, Wave 1, HARDENING_ROUND_001 input
# Role: H / resolved-context semantics. Developmental engineering input
# ONLY. Never certification evidence. Never unlocks anything.

## DEV verdicts (ROUND_000 items)
(1) Handler MAY-add / env SHALL-supply: PARTIAL. No-PIP + no-selector added, but MAY-add text still permits non-PIP addition.
(2) Repaired bytes hash-only: PARTIAL. Bytes exist in repo derived/requests/ but blind packet still hash-refs only.
(3) Issuer-or-null vs wildcard: AMBIGUOUS. Keying preserved, matching rule uncited.
(4) Canonicalization scope: AMBIGUOUS. Empty env dropped, IncludeInResult/whitespace/order rules unstated.

## Objections
O1 -- h_equivalence_proof route-b "only via PIP" gloss vs frozen data-flow (handler optionally adds; PDP requests additional via PIP; does not forbid handler-initiated env/date/time defaults). N1_DATAFLOW in prove module adds "only via PIP" gloss. Material YES.
O2 -- H_initial.json drops empty environment container with no empty-vs-absent marker and no spec locator. Material YES for H-as-full-context; NO for decision (no env designator), but breaks extensional claim.
O3 -- Issuer-or-null key vs Issuer-absent wildcard: matching rule uncited (Sec.7.3.5 lines never quoted on Issuer). Material YES.
O4 -- Effective-type rule (Attribute vs AttributeValue DataType, homogeneity fail-closed) lacks N1 locator. Material YES (DataType is H key).
O5 -- XML-bytes to AuthzForce Request parse fidelity unevidenced (whitespace/anyURI normalization, `(child.text or "")`). Material YES (value-identity load-bearing).
O6 -- Repaired bytes + route_a probe + projection absent from packet; blind checker cannot recompute request_bags(). Material YES for blind verifiability.
O7 -- Route-A exhaustiveness: no enumerated public-API list; MissingAttributeDetail IS partial resolved-context observation, unacknowledged. Material YES.
O8 -- Absent-MustBePresent-true conflated with empty bag in H_initial (key omitted); evaluation treats missing+MBP as Indeterminate, not empty. Material YES (H/omega linkage).

## Repair directions (evidence/representation only)
R1: narrow H to XML-side projection over RELEVANT_COORDINATES with completeness bound, or prove resolved identity.
R2: preserve empty categories explicitly; document IncludeInResult/sort/whitespace rules.
R3: exact Issuer-matching quote or split H key layers (raw vs designator-facing).
R4: cite Attribute DataType rule or normalize construction through one normalizer with diff log.
R5: AuthzForce parser locator (verbatim pass-through) or conditionalize claim on faithful parse.
R6: embed repaired bytes/canonical bytes + sha in packet; content-hash evidence.
R7: publish route-A method (API list, schema locator); scope route_a_unavailable to full-context observation; acknowledge StatusDetail partial observation.
R8: represent absent-MustBePresent-true distinctly from empty bag, or scope H to present-value bags with omega linkage.

## Falsifiers
Frozen lines for PIP-only addition; empty==absent equivalence; Issuer wildcard quote; effective-type precedence quote; verbatim parser pass-through locator; in-packet repaired bytes; enumerated no-getter API list + no-dump logging; missing-MBP empty-bag-with-flag semantics.
