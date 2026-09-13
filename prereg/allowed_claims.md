# Allowed manuscript claims (spec §18, verbatim ladder — claim wording locked to outcome)

## If outcome = POSITIVE_NATIVE_STAGE3 (§18.1)

> We additionally audited a pre-existing XACML/AuthzForce authorization fixture whose policy, request-context semantics, PDP configuration, and native request/response interface were fixed independently of PC. These external artifacts were sufficient to anchor the PC admission, policy-visible representation, authority/configuration, and atomic request boundary for the measured case. Without manual E/R/A action labels, PC mechanically derived a pure evidence-admission repair and a singleton nontrivial all-freeze signature. This is an external positive Stage-III witness, not a prevalence claim.

Stronger but still acceptable only if every audit passes:

> Unlike Polaris, whose raw repository semantics leave the E/R boundary underidentified, the XACML case contains an independently specified authorization interface sufficient for conditional PC point identification.

## Forbidden even on success (§18.2)

Do not write:

```text
"real systems naturally provide PC anchors"
"Stage III works in the wild"
"XACML validates the universal E/R/A ontology"
"PC automatically extracts governance semantics"
"we prove representation/evidence causality in XACML"
"production authorization systems are PC-identifiable"
```

## If outcome = NATIVE_ANCHOR_INSUFFICIENT (§18.3)

> A preregistered audit of XACML/AuthzForce did not justify all Stage-III anchors without additional analyst semantics; PC therefore retained underidentification rather than forcing a point estimate.

Do not call it a positive Stage-III experiment.
