# PC-XACML-S3+: Source-Native Positive Stage-III Identification Experiment

**Document type:** Frozen implementation specification / preregistration blueprint  
**Target paper:** Perceptive Closure, post-D33 external-positive Stage-III validation  
**Experiment short name:** `PC-XACML-S3+`  
**Primary system:** OASIS XACML 3.0 + AuthzForce Core Community Edition 21.2.0  
**AuthzForce release tag:** `release-21.2.0`  
**Pinned AuthzForce commit:** `3cc0e988e1639da48184434cd5c918102ff5b499`  
**Primary fixture:** `StatusDetail.MissingAttributeDetail`  
**Experimental style:** deterministic, source-native, exact, non-statistical, fail-closed  
**Number of implementation phases:** 6  
**Core rule:** if the external system does not independently justify the Stage-III semantic anchors, the experiment MUST fail as `NATIVE_ANCHOR_INSUFFICIENT`; the implementation must never repair the result by choosing more favorable semantics after inspection.

---

# 0. Executive purpose

This experiment exists to answer one narrow reviewer-critical question:

> Can an independently engineered authorization system and its pre-existing governing specification/configuration naturally supply enough semantic information for Perceptive Closure (PC) to point-identify a nontrivial resource-freezing signature, without PC inventing the authorization-admission, certificate-representation, authority, or action/checkpoint boundaries after observing the result?

The experiment is **not** intended to establish prevalence, benchmark superiority, agent safety, causal effects, or a new authorization mechanism. It is a source-native positive witness for D33 Stage III.

The target scientific result is therefore:

```text
external standard + external policy/configuration + native request/response boundary
        |
        v
externally justified H, P_R, Lambda, Atom / successor semantics
        |
        v
mechanical PC touch extraction
        |
        v
singleton source-relative resource signature K_{Pi,Omega}
        |
        v
nontrivial exact all-freeze geometry
```

The intended contribution if successful is:

> A pre-existing standards-governed authorization implementation provides the semantic anchors needed for conditional PC identification; PC then derives resource touch and the resulting all-freeze signature mechanically rather than assigning the favorable resource label by hand.

The intended contribution if unsuccessful is also scientifically meaningful:

> Even this unusually explicit authorization standard/configuration does not fix the semantic interface required by Stage III, so PC correctly returns underidentification rather than manufacturing a positive witness.

**The experiment is only a success if the positive result survives the fail-closed criteria below.**

---

# 1. Why this system is chosen

## 1.1 System

Use:

- **OASIS XACML Version 3.0**, as the normative authorization semantics.
- **AuthzForce Core Community Edition 21.2.0**, as the independently engineered executable Policy Decision Point (PDP).
- AuthzForce's pre-existing conformance fixture:
  - `pdp-testutils/src/test/resources/conformance/others/StatusDetail.MissingAttributeDetail/`

This choice is locked before PC extraction or freeze evaluation.

## 1.2 Why XACML/AuthzForce is unusually suitable for Stage III

The system has four properties directly relevant to the remaining D33 reviewer attack:

1. **A normative authorization standard exists independently of PC.** XACML specifies request contexts, Policy Decision Point evaluation, context-handler behavior, attribute matching/retrieval, missing-attribute behavior, and authorization responses.
2. **The executable implementation is independent of PC.** AuthzForce implements XACML 3.0 and exposes a public PDP interface.
3. **A pre-existing fixture already expresses an incomplete authorization request.** The chosen fixture deliberately omits a policy-required subject attribute with `MustBePresent="true"` and expects `Indeterminate` with `MissingAttributeDetail`.
4. **The authorization-relevant representation is programmatically recoverable from a frozen policy.** The fixed `AttributeDesignator` set specifies the category/identifier/datatype coordinates that the PDP queries, so the certificate-visible request projection can be mechanically derived rather than manually labeled.

## 1.3 Why not use Polaris again

Polaris is already valuable as a **negative** source-identification case: its raw source dataflow does not uniquely select the E/R boundary. Reusing Polaris cannot answer the positive Stage-III externality attack.

## 1.4 Why not use PC-TAU

PC-TAU has a mechanically clean contract but PC supplied the governance counterfactual middleware. It therefore cannot by itself establish that an independently authored authorization specification naturally fixes the relevant semantic anchors.

## 1.5 Why not use a large multi-system survey

The current reviewer problem is not prevalence. It is existence of one convincing external positive Stage-III case. A multi-system survey would add selection, mapping, versioning, and interpretation attack surface without being necessary for the claim.

---

# 2. Frozen external sources

All source artifacts MUST be copied into a read-only `external/` directory and SHA-256 hashed before semantic extraction begins.

## 2.1 AuthzForce repository lock

Repository:

```text
https://github.com/authzforce/core
```

Pin:

```text
release tag: release-21.2.0
commit:      3cc0e988e1639da48184434cd5c918102ff5b499
```

Do not use `develop`, `main`, or a later release after Phase 1 begins.

## 2.2 Frozen fixture files

At the pinned commit, freeze exactly these files:

```text
pdp-testutils/src/test/resources/conformance/others/
  StatusDetail.MissingAttributeDetail/
    pdp.xml
    request.xml
    response.xml
    policies/
      policy.xml
```

Known upstream Git blob SHAs at the pinned release:

```text
pdp.xml      01a0adc080253afc2c523a0b8e58e8578e8275eb
request.xml  ff6582db3d9c2bd00ae87e69279c23057b14a47a
response.xml 835d483564a1c3ab052e0dbbd24c2258e5a5c295
policy.xml   698af364ba2db79534cc654765baaed4d1c8f867
```

Local SHA-256 hashes MUST additionally be recorded because Git blob hashes are not SHA-256 content hashes.

## 2.3 Relevant frozen fixture semantics

The original request contains:

- subject identifier: `Julius Hibbert`
- resource: `http://medico.com/record/patient/BartSimpson`
- action: `read`
- no value for the policy-required subject attribute:
  `urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute`

The frozen policy requires the missing attribute to equal:

```text
riddle me this
```

with:

```text
MustBePresent="true"
```

The frozen expected response is:

```text
Decision = Indeterminate
StatusCode = urn:oasis:names:tc:xacml:1.0:status:missing-attribute
MissingAttributeDetail.AttributeId =
  urn:oasis:names:tc:xacml:2.0:conformance-test:some-attribute
MissingAttributeDetail.Category =
  urn:oasis:names:tc:xacml:1.0:subject-category:access-subject
MissingAttributeDetail.DataType =
  http://www.w3.org/2001/XMLSchema#string
```

## 2.4 OASIS standard lock

Freeze a local copy of the OASIS XACML 3.0 core specification:

```text
https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html
```

At minimum, the anchor ledger must include locators for:

- XACML request context structure.
- `Attributes`, `Attribute`, `AttributeValue` semantics.
- `AttributeDesignator` matching by Category / AttributeId / DataType / Issuer as applicable.
- Section 7.3.5 attribute retrieval.
- `MustBePresent` missing-attribute semantics.
- PDP/context-handler/PEP request-response architecture.
- response decision/status semantics.

The normative HTML file must be hashed locally and retained in the release artifact.

## 2.5 Source classes

Every semantic assertion in the anchor ledger must be tagged as one of:

```text
N1 = normative external standard text
N2 = pinned external engine configuration/schema
N3 = pinned pre-existing external fixture/policy/request/expected response
N4 = pinned external implementation source, used only as execution corroboration
X  = experiment-authored orchestration or measurement convention
```

### Hard rule

`H`, `P_R`, `Lambda`, and `Atom` may not be justified solely by class `X`.

A Stage-III positive claim requires each of these semantic anchors to have at least one accepted `N1`, `N2`, or `N3` basis. `N4` can support but cannot rescue an otherwise unsupported semantic anchor.

---

# 3. Exact scientific question

Let `Omega_ext` denote the frozen external XACML standard, AuthzForce release/configuration, policy, original request, and expected response.

Let `Omega_exp` denote only the preregistered measurement wrapper:

- the two latent complete request worlds defined below;
- the unit-cost native-interface repair action;
- the freeze-mask order;
- the exact solver conventions;
- the deterministic recording format.

Define:

```text
Omega_star = Omega_ext union Omega_exp
```

The experiment asks:

```text
Does Omega_star fix the PC semantic interface sufficiently that
|K_{Pi,Omega_star}| = 1,
with a nontrivial all-freeze signature,
without manual E/R/A action labels?
```

This decomposition is mandatory in reporting. Do not imply the external system supplied the experimental cost normalization or the two-world finite measurement wrapper. The positive externality claim is specifically about the **semantic authorization anchors and native intervention boundary**.

---

# 4. Preregistered PC instance

## 4.1 Latent worlds

Use exactly two latent worlds.

```text
x_permit:
  some-attribute = "riddle me this"

x_nonpermit:
  some-attribute = "not-riddle-me-this"
```

No third world may be added after observing PDP output.

The only difference between worlds is the true value of the missing subject attribute. Subject identity, resource, action, policy, PDP configuration, request schema, and every other request field remain fixed.

## 4.2 Target functional

The sealed target functional is **the exact XACML decision returned by the frozen PDP/policy on a complete request containing the world's missing-attribute value**.

Preregistered expected target classes:

```text
A_Pi(x_permit)    = Permit
A_Pi(x_nonpermit) = NotApplicable
```

If AuthzForce 21.2.0 does not return these two distinct decisions on the completed requests, the experiment MUST stop at `TARGET_REPRODUCTION_FAIL`. Do not redefine the target classes after observing output.

Do not collapse the target to a hand-authored safety label unless a new experiment version is preregistered.

## 4.3 Initial checkpoint

`S0` is the authorization state after the frozen original request has produced the frozen missing-attribute response.

The initial observation includes:

```text
Decision = Indeterminate
StatusCode = missing-attribute
MissingAttributeDetail =
  (AttributeId, Category, DataType)
```

The initial state is PC-open because the represented fiber contains `x_permit` and `x_nonpermit`, whose sealed target decisions differ.

Important: the current XACML `Indeterminate` response is **not itself** the PC target label. PC closure is defined by homogeneity of the sealed target functional over compatible latent worlds.

## 4.4 Native repair action

Exactly one repair action is permitted in the primary instance:

```text
q_supply_missing_attribute
```

Semantics:

1. Use the `MissingAttributeDetail` identifier/category/datatype already emitted by the external PDP.
2. Construct one new valid XACML Request by copying the original request exactly and adding one subject `Attribute` with the world-specific value.
3. Submit that request to the same frozen AuthzForce PDP, policy, configuration, and release.
4. Record the returned XACML response as the action outcome.

The action MUST NOT:

- modify the XACML policy;
- modify `pdp.xml`;
- enable a new attribute provider;
- change the request preprocessor;
- change subject/resource/action identifiers;
- alter resource/action semantics;
- add any other evidence;
- alter the engine;
- inject PC-specific middleware into the PDP;
- modify authorization authority or permission rules.

The action boundary is one native PEP-style request submission / PDP response cycle. The orchestration layer may construct the standard request but may not perform authorization logic.

## 4.5 Action cost

Set:

```text
c(q_supply_missing_attribute) = 1
```

This is an experiment-authored normalization, not an external XACML semantic fact.

The primary scientific classification is structural under an E freeze, so it must be invariant to replacing the unit cost with any finite strictly positive scalar. Phase 5 tests this explicitly.

## 4.6 Positive-support successors

The action has two source-valid semantic successors:

```text
S_permit    under x_permit
S_nonpermit under x_nonpermit
```

The exact external PDP response determines the terminal label in each successor.

No stochastic probability distribution is required. PC uses positive-support worst-branch evaluation; both worlds are included as possible support.

## 4.7 Controller observation

At `S0`, the controller observes only the frozen missing-attribute XACML response.

At terminal checkpoints, it observes the returned XACML decision and status.

The controller is not given the latent world label directly.

## 4.8 Authority coordinate

`Lambda` is held extensionally constant across the primary instance.

The frozen authority/admissibility environment consists of:

- the pinned `pdp.xml`;
- the pinned root/static policy provider configuration;
- the pinned policy set;
- the fixed native XACML request interface;
- no experiment-added dynamic authority escalation;
- no experiment-added PIP/attribute-provider capability.

Therefore no primary action should touch `A` unless the mechanical extractor detects an actual extensional change to the authority/admissibility object. If such a change is detected, the predicted signature is invalid and must be investigated rather than relabeled away.

---

# 5. External-to-PC semantic anchor definitions

The purpose of Phase 2 is to determine whether these mappings are actually justified by external semantics. The definitions below are **candidate derivation rules** that must pass the source-provenance gate; they are not self-certifying merely because this specification writes them down.

## 5.1 `H`: normalized authorization-admitted history

For this experiment, define `H(s)` as the canonicalized logical XACML request-context attribute multimap available to the PDP at the relevant evaluation checkpoint after context-handler population and before policy tests consume it.

Canonical entry key:

```text
(Category, AttributeId, DataType, Issuer-or-null)
```

Canonical value:

```text
sorted bag of typed AttributeValue values
```

Exclude:

- raw XML whitespace;
- attribute ordering where XACML semantics treat order as irrelevant;
- file paths;
- Java object identities;
- parser-local state;
- logging metadata;
- PC harness state.

Initial `H(S0)` contains the subject-id, resource-id, and action-id present in the original request and does **not** contain the missing `some-attribute` value.

After `q_supply_missing_attribute`, the corresponding successor history includes that typed attribute/value.

### Anchor acceptance condition

The XACML standard and frozen request-processing semantics must support treating the PDP request-context attributes as authorization-admitted information. If this mapping requires an ungrounded analyst convention, mark `H = AMBIGUOUS` and fail the positive Stage-III gate.

## 5.2 `P_R`: certificate-representation equivalence

For this experiment, derive `P_R` mechanically from the **frozen policy's authorization-visible attribute projection**.

Procedure:

1. Parse every `AttributeDesignator` reachable from the frozen policy.
2. Canonicalize each designator by:
   - Category;
   - AttributeId;
   - DataType;
   - Issuer semantics;
   - `MustBePresent`.
3. For a source-valid admitted history `h`, evaluate the named attribute bags that the XACML standard says the PDP obtains for these designators.
4. Define two histories as `P_R`-equivalent iff all policy-relevant designator results are extensionally equal under the standard matching semantics.

The relation is a **function of the frozen policy and XACML evaluation semantics**, not a manual PC partition.

In the primary instance, `P_R` itself is expected to remain extensionally unchanged across `q_supply_missing_attribute`; the histories presented to that fixed relation change because `H` changes.

### Anchor acceptance condition

The extractor must be able to derive the complete designator projection directly from the pinned policy, with no handwritten list of authorization-relevant attributes. If a human must manually decide which policy inputs count as certificate-visible, mark `P_R = AMBIGUOUS` and fail the positive Stage-III gate.

## 5.3 `Lambda`: authority/admissibility object

Define `Lambda(s)` extensionally as the frozen authorization evaluation capability relevant to the measured interface:

```text
(root policy identity,
 policy-provider configuration,
 enabled attribute-provider configuration,
 request-preprocessor identity,
 admissible native request interface)
```

The exact serialization should use canonical hashes of the relevant external configuration artifacts, not mutable object addresses.

`Lambda` is expected to be constant before and after the primary repair action.

### Anchor acceptance condition

The experiment must show that all authority/admissibility components included here are fixed by external configuration/standard semantics, and that no hidden experiment-side authority change is required to submit the completed request. If this cannot be justified, mark `Lambda = AMBIGUOUS` and fail the positive Stage-III gate.

## 5.4 `Atom`: source-exposed action/checkpoint boundary

The primary action boundary is one externally meaningful XACML request/response transaction:

```text
PEP-style request submission -> PDP evaluation -> XACML response
```

The internal implementation may contain many Java calls, but they are not independent controller actions in this experiment.

The experiment does **not** claim invariance to splitting this native interaction into a different exposed action algebra.

### Anchor acceptance condition

The XACML architecture must independently support request/response as an authorization interface boundary. If the action boundary exists only because the PC harness invented an arbitrary internal cut, mark `Atom = AMBIGUOUS` and fail.

## 5.5 Target classes

`A_Pi` is derived from the frozen PDP/policy evaluation on the complete request worlds. It is not a hand-labeled success variable.

## 5.6 Outcomes and successors

The semantic outcome classes are canonical XACML response classes:

```text
Decision
StatusCode
relevant StatusDetail / MissingAttributeDetail where present
```

Internal log text and stack traces are not semantic outcome classes.

---

# 6. Mechanical touch derivation

Touch MUST be computed from pre/post extensional objects exactly as D33 defines it.

Pseudocode:

```python
def derive_touch(pre, successors):
    touch = set()
    for post in successors:
        if canonical_H(post) != canonical_H(pre):
            touch.add("E")
        if canonical_PR(post) != canonical_PR(pre):
            touch.add("R")
        if canonical_Lambda(post) != canonical_Lambda(pre):
            touch.add("A")
    return touch
```

## 6.1 Forbidden implementation pattern

No input file may contain:

```json
{"touch": ["E"]}
```

or equivalent manual resource labels.

The only stored touch label may be an **output** of the mechanical derivation procedure.

## 6.2 Preregistered touch prediction

The expected primary result is:

```text
T(q_supply_missing_attribute) = {E}
```

because:

- admitted request history changes;
- the frozen policy-derived representation relation does not change;
- the authority/admissibility configuration does not change.

If the mechanical derivation yields `{E,R}`, `{E,A}`, `{R}`, or any other touch set, do not overwrite it. The result must be traced back to the anchor definitions and either accepted or classified as an anchor/implementation failure.

---

# 7. Preregistered exact PC prediction

Use the freeze bit order already used in the D33/PC-TAU paper:

```text
F000 = freeze none
F100 = freeze E
F010 = freeze R
F001 = freeze A
F110 = freeze E+R
F101 = freeze E+A
F011 = freeze R+A
F111 = freeze E+R+A
```

Under the primary predicted pure-E action and unit cost:

```text
K_Pi = [1, INF, 1, 1, INF, INF, 1, INF]
```

Interpretation:

```text
unrestricted:        one native evidence-admission repair closes
E freeze:            no proper closer remains
R freeze:            native evidence repair remains
A freeze:            native evidence repair remains
E+R freeze:          no proper closer
E+A freeze:          no proper closer
R+A freeze:          native evidence repair remains
E+R+A freeze:        no proper closer
```

This is a **structural E-touch-dependence** witness relative to the declared native request interface.

## 7.1 Why sole-action structure is acceptable here

This experiment is not intended to demonstrate nondegenerate substitution geometry. PC-TAU already performs that role with a pure-R optimum and finite fallback.

The sole purpose of `PC-XACML-S3+` is to demonstrate **source-native positive Stage-III semantic identification** in an independently specified authorization system. Therefore a one-repair-action structural signature is acceptable and should not be oversold as a geometry-diversity result.

---

# 8. Outcome taxonomy

Exactly one top-level outcome must be emitted.

```text
POSITIVE_NATIVE_STAGE3
NATIVE_ANCHOR_INSUFFICIENT
SOURCE_REPRODUCTION_FAIL
TARGET_REPRODUCTION_FAIL
TOUCH_DERIVATION_MISMATCH
SOLVER_MISMATCH
NONTRIVIALITY_FAIL
INDEPENDENT_REPRODUCTION_FAIL
```

## 8.1 `POSITIVE_NATIVE_STAGE3`

May be emitted only if all of the following hold:

1. Pinned external fixture reproduces.
2. Completed-world PDP decisions reproduce the preregistered distinct target classes.
3. `H`, `P_R`, `Lambda`, and `Atom` each pass the external-anchor provenance gate.
4. No E/R/A labels are manually supplied to the PC compiler.
5. Mechanical touch is uniquely derived.
6. All eight freezes are solved exactly.
7. `|K_{Pi,Omega_star}| = 1` under the declared complete interface.
8. The signature is nontrivial: at least one freeze differs from F000 or is infinite.
9. Independent recomputation agrees on touch and all eight coordinates.
10. Phase-5 falsification tests pass.

No partial credit should be reported as a Stage-III positive result.

---

# 9. Repository layout

Create a fresh repository named, for example:

```text
PC-XACML-StageIII
```

Required layout:

```text
PC-XACML-StageIII/
├── README.md
├── LICENSE
├── IMPLEMENTATION_SPEC.md
├── CHANGELOG.md
├── pyproject.toml
├── requirements-lock.txt
├── .gitignore
├── prereg/
│   ├── experiment.yaml
│   ├── expected_signature.json
│   ├── allowed_claims.md
│   └── prereg_sha256.txt
├── external/
│   ├── MANIFEST.json
│   ├── xacml/
│   │   ├── xacml-3.0-core-spec-cos01-en.html
│   │   └── SHA256SUMS
│   └── authzforce/
│       ├── RELEASE.json
│       ├── COMMIT.txt
│       ├── fixture/
│       │   ├── pdp.xml
│       │   ├── request.xml
│       │   ├── response.xml
│       │   └── policies/
│       │       └── policy.xml
│       └── SHA256SUMS
├── derived/
│   ├── requests/
│   │   ├── request_x_permit.xml
│   │   └── request_x_nonpermit.xml
│   ├── policy_projection.json
│   ├── anchor_ledger.json
│   ├── anchor_ledger.md
│   └── canonical_external_manifest.json
├── src/
│   ├── provenance/
│   │   ├── lock_sources.py
│   │   └── verify_sources.py
│   ├── xacml/
│   │   ├── canonicalize_request.py
│   │   ├── parse_policy.py
│   │   ├── build_repaired_requests.py
│   │   ├── run_authzforce.py
│   │   └── parse_response.py
│   ├── pc/
│   │   ├── models.py
│   │   ├── derive_H.py
│   │   ├── derive_PR.py
│   │   ├── derive_Lambda.py
│   │   ├── derive_atom.py
│   │   ├── derive_touch.py
│   │   ├── compile_contract.py
│   │   └── solve_freezes.py
│   ├── audit/
│   │   ├── independent_touch.py
│   │   ├── independent_solver.py
│   │   ├── check_no_manual_labels.py
│   │   ├── check_anchor_completeness.py
│   │   └── build_audit_report.py
│   └── cli.py
├── schemas/
│   ├── anchor_ledger.schema.json
│   ├── contract.schema.json
│   ├── freeze_row.schema.json
│   └── final_result.schema.json
├── tests/
│   ├── test_source_hashes.py
│   ├── test_original_fixture.py
│   ├── test_completed_world_decisions.py
│   ├── test_policy_projection.py
│   ├── test_anchor_completeness.py
│   ├── test_no_manual_touch_labels.py
│   ├── test_touch_derivation.py
│   ├── test_all_freezes.py
│   ├── test_cost_robustness.py
│   ├── test_interface_preserving_mutations.py
│   ├── test_anchor_ablation.py
│   ├── test_parser_corruptions.py
│   └── test_clean_reproduction.py
├── artifacts/
│   ├── raw/
│   ├── contracts/
│   ├── freezes/
│   ├── audits/
│   ├── logs/
│   └── seal/
└── scripts/
    ├── run_phase1.sh
    ├── run_phase2.sh
    ├── run_phase3.sh
    ├── run_phase4.sh
    ├── run_phase5.sh
    ├── run_phase6.sh
    └── reproduce_all.sh
```

---

# 10. Canonical data schemas

## 10.1 `prereg/experiment.yaml`

Minimum fields:

```yaml
experiment_id: PC-XACML-S3PLUS-v1
paper_target: Perceptive Closure D33+
system:
  standard: OASIS XACML 3.0
  implementation: AuthzForce Core CE
  release: 21.2.0
  tag: release-21.2.0
  commit: 3cc0e988e1639da48184434cd5c918102ff5b499
fixture:
  name: StatusDetail.MissingAttributeDetail
worlds:
  x_permit:
    some_attribute: "riddle me this"
    expected_decision: Permit
  x_nonpermit:
    some_attribute: "not-riddle-me-this"
    expected_decision: NotApplicable
action_interface:
  actions:
    - q_supply_missing_attribute
  unit_cost: 1
freeze_order:
  - F000
  - F100
  - F010
  - F001
  - F110
  - F101
  - F011
  - F111
expected_touch:
  q_supply_missing_attribute: [E]
expected_K:
  - 1
  - INF
  - 1
  - 1
  - INF
  - INF
  - 1
  - INF
abort_on_anchor_ambiguity: true
allow_manual_touch_labels: false
allow_policy_modification: false
allow_engine_modification: false
allow_dynamic_authority_change: false
```

This file must be committed and hashed before Phase 3 implementation is run.

## 10.2 Anchor ledger record

Each semantic anchor record must contain:

```json
{
  "anchor_id": "H.request_context",
  "pc_field": "H",
  "extensional_definition": "...",
  "source_class": ["N1", "N3"],
  "source_documents": [
    {
      "id": "xacml-core",
      "locator": "section ...",
      "artifact_sha256": "..."
    }
  ],
  "derivation_module": "src/pc/derive_H.py",
  "manual_semantic_choice_required": false,
  "ambiguity_status": "FIXED",
  "auditor_status": "PASS"
}
```

Permitted `ambiguity_status` values:

```text
FIXED
PARTIAL
AMBIGUOUS
UNSUPPORTED
```

Only `FIXED` is allowed for the Stage-III positive anchor set.

## 10.3 Contract JSON

At minimum:

```json
{
  "contract_id": "pc-xacml-s3plus-primary",
  "worlds": ["x_permit", "x_nonpermit"],
  "initial_checkpoint": "S0",
  "target": {
    "x_permit": "Permit",
    "x_nonpermit": "NotApplicable"
  },
  "H": {},
  "PR": {},
  "Lambda": {},
  "omega": {},
  "actions": {},
  "successors": {},
  "costs": {},
  "atomicity": {},
  "provenance": {}
}
```

No resource-touch field is allowed in the input contract schema. Touch is a derived output artifact.

## 10.4 Freeze row

```json
{
  "freeze": "F100",
  "frozen_resources": ["E"],
  "removed_actions": ["q_supply_missing_attribute"],
  "surviving_actions": [],
  "proper_closer_exists": false,
  "kappa": "INF",
  "solver": "primary",
  "contract_sha256": "..."
}
```

---

# 11. Six-phase implementation plan

# PHASE 1 - External source lock and native reproduction

## Goal

Prove that the experiment starts from a stable, independently authored authorization artifact that can be reproduced before PC touches it.

## 1.1 Create clean repository

Initialize the experiment repository and commit this specification as `IMPLEMENTATION_SPEC.md`.

The first commit must contain no PC result generated from AuthzForce execution.

## 1.2 Clone and pin AuthzForce

Recommended sequence:

```bash
git clone https://github.com/authzforce/core.git external/authzforce-repo
cd external/authzforce-repo
git checkout 3cc0e988e1639da48184434cd5c918102ff5b499
git rev-parse HEAD
git status --porcelain
```

Required checks:

```text
HEAD == 3cc0e988e1639da48184434cd5c918102ff5b499
working tree == clean
```

Copy only the frozen fixture files into `external/authzforce/fixture/` and record both Git blob SHA and local SHA-256.

Do not edit the copied originals.

## 1.3 Freeze XACML standard

Download the normative XACML 3.0 specification into `external/xacml/`.

Record:

- source URL;
- retrieval timestamp;
- local SHA-256;
- title/version;
- all sections later used for semantic anchoring.

## 1.4 Record environment

Required runtime:

```text
JDK: 17 LTS or later, primary run pinned to one exact installed build
AuthzForce: 21.2.0
OS: record exact OS/build
Python: pin exact minor version used by PC harness
XML parser: lock package/version
```

Create:

```text
artifacts/raw/environment.txt
```

containing at least:

```bash
java -version
python --version
git --version
```

and dependency lock output.

Do not silently upgrade any dependency after the preregistration seal.

## 1.5 Reproduce the original fixture

Execute the pinned AuthzForce PDP on the frozen original `request.xml` with the frozen `pdp.xml` and policy.

Expected semantic output:

```text
Decision = Indeterminate
StatusCode = missing-attribute
MissingAttributeDetail = expected AttributeId/Category/DataType
```

Comparison is semantic XML comparison, not whitespace-sensitive byte comparison.

Store:

```text
artifacts/raw/original_response_actual.xml
artifacts/raw/original_response_expected.xml
artifacts/raw/original_response_comparison.json
```

## 1.6 Build the two completed requests

Use a deterministic script to copy the original request and add exactly one missing subject attribute.

Positive world value:

```text
riddle me this
```

Negative world value:

```text
not-riddle-me-this
```

The script must insert the value into the exact Category / AttributeId / DataType named by the frozen `MissingAttributeDetail` and frozen policy.

Do not hardcode a different category.

## 1.7 Preregistration seal

Before Phase 2 semantic extraction begins, create:

```text
prereg/experiment.yaml
prereg/expected_signature.json
prereg/allowed_claims.md
prereg/prereg_sha256.txt
```

`allowed_claims.md` must contain the exact claim ladder in Section 18 below.

Commit these files.

## Phase-1 gate

PASS only if:

```text
[ ] AuthzForce exact release commit pinned
[ ] source tree clean
[ ] four fixture artifacts match recorded upstream blobs
[ ] local SHA-256 manifest created
[ ] XACML standard frozen and hashed
[ ] original missing-attribute fixture reproduces semantically
[ ] completed requests built deterministically
[ ] preregistration files committed and hashed
```

Failure outcome:

```text
SOURCE_REPRODUCTION_FAIL
```

Do not continue to a Stage-III claim if this gate fails.

---

# PHASE 2 - Source-native semantic anchor audit

## Goal

Determine whether the external system actually fixes the PC semantic anchors required by Stage III **before** resource touch or K is computed.

This is the most important phase of the experiment.

## 2.1 Build the anchor ledger without resource labels

Create records for:

```text
H
P_R
Lambda
Atom
omega
Q
Succ+
c
A_Pi
terminal/open semantics
```

Do not include `E`, `R`, `A`, `touch`, `Delta`, or expected freeze results in the extraction code.

The anchor audit is about **semantics**, not desired PC classification.

## 2.2 H audit

Required demonstration:

- the XACML standard specifies the request context / attribute bag exposed to PDP evaluation;
- the initial request objectively lacks the required `some-attribute`;
- the completed request objectively contains it;
- canonicalization discards only semantically irrelevant syntax.

Produce:

```text
derived/H_initial.json
derived/H_permit.json
derived/H_nonpermit.json
artifacts/audits/H_provenance.json
```

## 2.3 P_R audit

Implement a policy parser that mechanically extracts all authorization-visible `AttributeDesignator`s reachable from `policy.xml`.

For each designator record:

```text
RuleId / path
Category
AttributeId
DataType
Issuer
MustBePresent
Match function context
```

Generate:

```text
derived/policy_projection.json
```

Then construct the extensional relation rule from this frozen projection.

Required canary:

The extractor must find the missing `some-attribute` designator with:

```text
Category = access-subject
AttributeId = ...:some-attribute
DataType = xsd:string
MustBePresent = true
```

If it does not, stop.

## 2.4 Lambda audit

Canonicalize the externally fixed authorization capability/configuration.

At minimum hash and record:

```text
pdp.xml
policy.xml
policy-provider configuration
request-preprocessor selection/default
attribute-provider set
```

Verify that `q_supply_missing_attribute` does not require changing these artifacts.

The pre/post `Lambda` hash must therefore be identical.

If an additional provider, policy, role, capability, or permission must be enabled to make the repaired request evaluate, the primary experiment does not satisfy the preregistered constant-Lambda design.

## 2.5 Atomicity audit

Document the externally meaningful request/response boundary using the XACML architecture.

The action is one standard request transaction. Internal Java methods are not source-exposed PC actions.

Record:

```text
atom_id: xacml-request-transaction
pre_checkpoint: after original MissingAttributeDetail response
post_checkpoint: after repaired request response
decomposable_in_primary_interface: false
```

This is not a claim that another system exposing additional operations must have the same K.

## 2.6 Target audit

Run the completed requests through the frozen external PDP.

Expected:

```text
x_permit    -> Permit
x_nonpermit -> NotApplicable
```

If either result differs, emit `TARGET_REPRODUCTION_FAIL` and stop the primary positive claim.

## 2.7 Semantic completeness checker

Implement `check_anchor_completeness.py` with explicit required fields.

A positive gate requires:

```text
H      = FIXED
P_R    = FIXED
Lambda = FIXED
Atom   = FIXED
omega  = FIXED
Q      = FIXED
Succ+  = FIXED
A_Pi   = FIXED
```

`c` may be experiment-authored because it is explicitly a measurement normalization; it must be frozen and sensitivity-tested.

## 2.8 Ambiguity rule

If any semantic anchor depends on a statement of the form:

```text
"we choose to regard X as admitted here"
"we choose to call this certificate-visible"
"we choose this function boundary as the intervention boundary"
```

without an external N1/N2/N3 justification, the anchor is not fixed.

Set:

```text
ambiguity_status = AMBIGUOUS
```

and the experiment's top-level outcome becomes:

```text
NATIVE_ANCHOR_INSUFFICIENT
```

**Do not proceed by sealing the analyst's preferred completion and calling that source-native Stage III.**

## Phase-2 gate

PASS only if:

```text
[ ] H has external provenance
[ ] P_R derived mechanically from frozen policy/standard
[ ] Lambda externally fixed and unchanged by repair
[ ] Atom justified by native protocol boundary
[ ] target decisions reproduced
[ ] no resource labels used during anchor construction
[ ] all required anchor records marked FIXED
[ ] anchor ledger independently checked against source locators
```

If this gate fails, preserve the result as a negative identification finding and stop the positive experiment.

---

# PHASE 3 - Mechanical PC contract compilation

## Goal

Compile the externally anchored semantics into the D33 PC contract **without manual touch labels**.

## 3.1 Contract compiler

Implement:

```text
src/pc/compile_contract.py
```

Inputs:

```text
external manifest
anchor ledger
canonical original request
canonical completed requests
parsed external PDP responses
preregistered world set
preregistered cost normalization
```

Output:

```text
artifacts/contracts/pc_xacml_primary.contract.json
```

## 3.2 Required state graph

Primary graph:

```text
             x_permit outcome
          /------------------> S_permit [closed]
S0 -- q_supply_missing_attribute
          \------------------> S_nonpermit [closed]
             x_nonpermit outcome
```

There are no other repair actions in the primary declared interface.

## 3.3 Closure verification

The compiler must compute:

```text
A_Pi(x_permit) != A_Pi(x_nonpermit)
```

Therefore `S0` is open.

For each terminal successor, the represented fiber must contain one target-homogeneous class, so the terminal is closed.

The terminal classification must be derived from contract/world compatibility and target decisions, not simply copied from a field named `closed=true`.

## 3.4 Mechanical touch

Run only after the contract is serialized and hashed.

Output:

```text
artifacts/contracts/touch.json
```

Expected:

```json
{
  "q_supply_missing_attribute": ["E"]
}
```

but this expected value must never be an input to the derivation.

## 3.5 No-manual-label static audit

`check_no_manual_labels.py` must scan:

```text
prereg/
derived/
src/
artifacts/contracts/input*
```

and reject any precomputed/manual touch assignment except the preregistered expected-output file.

The expected-output file must be excluded from all execution imports and dependency graphs.

## 3.6 Independent touch implementation

Write a second implementation:

```text
src/audit/independent_touch.py
```

Constraints:

- do not import `derive_touch.py`;
- do not import helper functions that perform equality checks for it;
- independently canonicalize the three pre/post objects;
- compare output to primary touch derivation.

Agreement required exactly.

## 3.7 Contract seal

After compilation, write:

```text
contract_sha256
touch_sha256
anchor_ledger_sha256
external_manifest_sha256
```

into:

```text
artifacts/seal/phase3_manifest.json
```

## Phase-3 gate

PASS only if:

```text
[ ] complete contract compiles
[ ] S0 is open for the preregistered reason
[ ] both successor states are closed
[ ] touch is mechanically derived
[ ] primary and independent touch implementations agree
[ ] no manual touch labels feed execution
[ ] contract and provenance hashes sealed
```

Failure outcome:

```text
TOUCH_DERIVATION_MISMATCH
```

if disagreement is about resource derivation; otherwise classify according to the earlier source/anchor failure.

---

# PHASE 4 - Exact all-freeze evaluation

## Goal

Compute the complete eight-coordinate resource-freezing signature exactly and verify it with an independent solver.

## 4.1 Freeze implementation

The freeze evaluator must follow D33 literally:

For freeze set `S`, remove every source-exposed atomic action `q` satisfying:

```text
T(q) intersection S != empty
```

A freeze may not edit the interior of `q_supply_missing_attribute`.

A freeze may not fabricate a partial subaction.

## 4.2 Exact primary solver

Because the graph is finite and tiny, use exhaustive exact search, not sampling.

For each freeze row record:

```text
freeze mask
frozen resources
removed actions
surviving actions
reachable checkpoints
proper closer exists
worst positive-support branch cost
kappa
terminal target classes
```

Store one file per freeze plus a consolidated table.

## 4.3 Preregistered expected table

| Freeze | Frozen resources | Expected q availability | Expected kappa |
|---|---|---:|---:|
| F000 | none | yes | 1 |
| F100 | E | no | INF |
| F010 | R | yes | 1 |
| F001 | A | yes | 1 |
| F110 | E,R | no | INF |
| F101 | E,A | no | INF |
| F011 | R,A | yes | 1 |
| F111 | E,R,A | no | INF |

Expected:

```text
K_Pi = [1, INF, 1, 1, INF, INF, 1, INF]
```

## 4.4 Independent solver

Implement a second solver that does not import the primary search code.

Given the graph is small, the independent solver should enumerate all surviving finite policy trees directly.

The two solvers must agree on:

- available action set;
- existence/nonexistence of proper closer;
- exact finite cost;
- all eight coordinates.

## 4.5 Singleton identification record

Write:

```text
artifacts/freezes/identified_set.json
```

with:

```json
{
  "identified_set_cardinality": 1,
  "signature": [1, "INF", 1, 1, "INF", "INF", 1, "INF"],
  "basis": "all required Stage-III semantic anchors fixed by accepted external provenance plus preregistered measurement wrapper"
}
```

If the anchor audit retained multiple admissible semantic completions, this file must not claim cardinality one.

## 4.6 Nontriviality gate

Nontriviality is satisfied iff:

```text
exists freeze F != F000 such that kappa_F != kappa_F000
```

The preregistered expectation satisfies this through every freeze containing E.

## Phase-4 gate

PASS only if:

```text
[ ] all eight masks evaluated
[ ] no partial-action fabrication
[ ] primary and independent solvers agree
[ ] observed signature matches preregistered signature OR mismatch is reported honestly
[ ] singleton claim consistent with Phase-2 anchor gate
[ ] nontriviality criterion satisfied
```

If solvers disagree:

```text
SOLVER_MISMATCH
```

If signature is trivial:

```text
NONTRIVIALITY_FAIL
```

---

# PHASE 5 - Falsification, sensitivity, and anti-circularity audit

## Goal

Try to break the positive Stage-III interpretation before the result is allowed into the manuscript.

This phase is mandatory even if the primary signature matches exactly.

## 5.1 Source-hash corruption test

Mutate one byte in each frozen external artifact in a temporary test copy.

The source verifier must fail closed.

Required: 4/4 fixture corruptions detected plus XACML-spec corruption detected.

## 5.2 Missing-attribute canary

Temporary negative-control variant only:

- remove or change the `MustBePresent="true"` property;
- verify the original expected missing-attribute behavior no longer matches the frozen external source claim.

This variant is **not** part of the primary K measurement. It only checks that the harness is actually sensitive to the governing policy semantics.

## 5.3 Wrong-category canary

Construct a temporary repaired request that inserts the correct string under the wrong XACML Category.

Expected: it must not be treated as satisfying the frozen designator merely because the literal value is present somewhere in XML.

This tests that H/P_R canonicalization respects external XACML attribute identity rather than naive string presence.

## 5.4 Wrong-datatype canary

Insert the correct literal under an incompatible datatype.

Expected: parser/PDP behavior must reflect XACML datatype semantics; the harness must not silently coerce it into the expected attribute bag.

## 5.5 Policy-projection canary

Inject an unrelated extra attribute into a temporary request.

Expected:

- H may record the admitted extra fact if semantically present;
- the fixed policy-derived `P_R` must not change merely because an authorization-irrelevant XML field appears, unless the frozen policy actually references it.

This tests the difference between admitted information and authorization-visible representation.

## 5.6 Interface-preserving XML perturbations

Create semantically equivalent temporary inputs via:

- whitespace changes;
- element formatting changes permitted by the parser/schema;
- order permutations that are semantically irrelevant under the canonicalization rule;
- file renaming/path relocation while contents/config references are updated without changing the external semantic interface.

Expected:

```text
H extensional form unchanged where semantics unchanged
P_R unchanged
Lambda unchanged
T unchanged
K unchanged
```

Do not include any transformation that changes the source-exposed action algebra.

## 5.7 Interface-changing negative control

Create one explicitly labeled `OUT_OF_SCOPE_INTERFACE_CHANGE` variant in which the experiment harness splits the primary action into two independently exposed controller actions, e.g.:

```text
q_construct_attribute
q_submit_request
```

Do **not** use this variant to claim Theorem-3 invariance.

The purpose is to verify that the audit system recognizes the action algebra has changed and refuses to compare K as though this were an interface-preserving refactor.

Expected audit verdict:

```text
INTERFACE_CHANGED
THEOREM3_INVARIANCE_NOT_APPLICABLE
```

This directly prevents the paper from repeating the atomicity overclaim attacked against D33.

## 5.8 Cost sensitivity

Recompute with temporary costs:

```text
c(q) = 0.5
c(q) = 2
c(q) = 10
```

Expected:

- unrestricted and non-E-frozen finite kappa changes to the selected cost;
- every E-containing freeze remains `INF`;
- structural E-touch dependence classification is invariant.

Report this only as a robustness check on the unit-cost normalization.

## 5.9 Negative-world sensitivity

Before execution, preregister at least two additional nonmatching strings for test-only sensitivity, e.g.:

```text
wrong-answer-1
wrong-answer-2
```

They must not replace the primary `x_nonpermit` value.

Expected: each remains in the nonmatching target class under the frozen policy, preserving the open initial fiber and structural E-touch classification.

## 5.10 Anchor-ablation tests

Systematically delete one accepted anchor record at a time from a temporary copy of the anchor ledger:

```text
remove H provenance
remove P_R provenance
remove Lambda provenance
remove Atom provenance
```

Expected: `check_anchor_completeness.py` refuses `POSITIVE_NATIVE_STAGE3` each time.

This demonstrates that the positive claim is conditioned on the declared anchors rather than silently defaulting missing semantics.

## 5.11 No-manual-label mutation test

Insert a forbidden manual touch label in a temporary fixture.

Expected: static audit fails.

## 5.12 Result-leakage audit

Generate a dependency graph showing that:

```text
expected_signature.json
```

is never imported/read by:

```text
anchor extraction
contract compilation
touch derivation
freeze solver
```

The expected signature may only be read by the final comparison/reporting stage.

## 5.13 Independent clean reproduction

From a fresh checkout / clean environment:

1. verify external hashes;
2. rebuild derived completed requests;
3. rerun native PDP outputs;
4. rebuild anchor-derived canonical objects;
5. recompile PC contract;
6. derive touch independently;
7. solve all eight freezes;
8. reproduce final result JSON.

The final result JSON must be byte-identical after canonical key ordering, except for explicitly excluded run metadata such as timestamps/absolute paths.

## Phase-5 gate

PASS only if:

```text
[ ] all source corruptions detected
[ ] missing-attribute canary behaves as expected
[ ] wrong-category canary detected
[ ] wrong-datatype canary detected/handled correctly
[ ] irrelevant-attribute test respects H vs P_R distinction
[ ] interface-preserving perturbations preserve signature
[ ] interface-changing variant is explicitly rejected from T3 invariance
[ ] cost sensitivity preserves structural classification
[ ] negative-world sensitivity preserves target distinction
[ ] every anchor ablation kills positive Stage-III eligibility
[ ] manual touch-label injection detected
[ ] expected-result leakage audit passes
[ ] clean reproduction matches
```

Failure outcome:

```text
INDEPENDENT_REPRODUCTION_FAIL
```

or the more specific earlier failure category.

---

# PHASE 6 - Seal, independent audit package, and manuscript-ready report

## Goal

Freeze a tamper-evident result package whose claims cannot silently exceed what the experiment established.

## 6.1 Final result object

Create:

```text
artifacts/seal/FINAL_RESULT.json
```

Required fields:

```json
{
  "experiment_id": "PC-XACML-S3PLUS-v1",
  "outcome": "POSITIVE_NATIVE_STAGE3",
  "external_system": "OASIS XACML 3.0 + AuthzForce Core CE 21.2.0",
  "authzforce_commit": "3cc0e988e1639da48184434cd5c918102ff5b499",
  "fixture": "StatusDetail.MissingAttributeDetail",
  "anchor_status": {
    "H": "FIXED",
    "PR": "FIXED",
    "Lambda": "FIXED",
    "Atom": "FIXED"
  },
  "derived_touch": {
    "q_supply_missing_attribute": ["E"]
  },
  "K": [1, "INF", 1, 1, "INF", "INF", 1, "INF"],
  "identified_set_cardinality": 1,
  "primary_classification": "STRUCTURAL_E_TOUCH_DEPENDENCE",
  "manual_touch_labels_used": false,
  "native_policy_modified": false,
  "native_engine_modified": false,
  "claim_scope": "source-native positive Stage-III specification witness; not prevalence or production-safety evidence"
}
```

Do not force these values if the observed experiment differs. The builder must populate from observed artifacts.

## 6.2 Final manifest

Create `MANIFEST.sha256` over every final artifact that matters for reproduction.

Include:

- external source copies;
- preregistration;
- anchor ledger;
- derived requests;
- native PDP outputs;
- contract;
- touch output;
- freeze rows;
- test results;
- audit report;
- source code;
- dependency lock.

## 6.3 Mutation log

`CHANGELOG.md` must record every change after the preregistration commit.

Any change to:

```text
worlds
target
action interface
cost
anchor definition
freeze order
expected signature
success criteria
```

requires a new experiment version, not an unmarked patch.

## 6.4 Independent audit report

Generate:

```text
artifacts/audits/FINAL_AUDIT.md
```

Required sections:

1. external source provenance;
2. original fixture reproduction;
3. anchor-by-anchor provenance table;
4. policy projection;
5. native target decisions;
6. PC contract hash;
7. primary and independent touch derivations;
8. all eight freeze values;
9. independent solver agreement;
10. falsification tests;
11. source/action-interface limitations;
12. allowed and forbidden claims.

## 6.5 Release bundle

Produce one deterministic release archive:

```text
PC-XACML-S3PLUS-v1.tar.gz
```

plus:

```text
PC-XACML-S3PLUS-v1.sha256
```

The archive must not include local secrets, API keys, usernames, unrelated files, or mutable caches.

## 6.6 Manuscript integration rule

Do not edit the paper until `FINAL_RESULT.json` is sealed.

If the outcome is `POSITIVE_NATIVE_STAGE3`, the paper may add one concise external-positive paragraph/table row.

If the outcome is `NATIVE_ANCHOR_INSUFFICIENT`, the paper must not convert the case into a point-identified contract-relative result and call it natural Stage III.

## Phase-6 gate

PASS only if:

```text
[ ] final outcome generated from artifacts
[ ] final manifest complete
[ ] all tests pass
[ ] audit report generated
[ ] release archive reproducible
[ ] allowed claims exactly match outcome
[ ] no post-hoc semantic edits
```

---

# 12. Required source-to-anchor table

The implementation must fill a table with exact section/file locators. The following is the required structure, not permission to skip source review.

| PC object | External basis that must be demonstrated | Primary source class | Failure if absent |
|---|---|---|---|
| `H` | XACML request-context/attribute-bag semantics at PDP evaluation | N1 + N3 | `NATIVE_ANCHOR_INSUFFICIENT` |
| `P_R` | policy-visible attribute projection mechanically derived from frozen `AttributeDesignator`s and matching rules | N1 + N3 | `NATIVE_ANCHOR_INSUFFICIENT` |
| `Lambda` | fixed policy/provider/preprocessor/native request capability | N1/N2/N3 | `NATIVE_ANCHOR_INSUFFICIENT` |
| `Atom` | native XACML request/response interaction boundary | N1 | `NATIVE_ANCHOR_INSUFFICIENT` |
| `omega` | native XACML responses and `MissingAttributeDetail` | N1 + N3 | contract incomplete |
| `Q` | preregistered native request submission operation | N1 + X wrapper | contract incomplete |
| `Succ+` | completed request worlds and native PDP responses | N3 + X wrapper | contract incomplete |
| `A_Pi` | exact complete-request PDP decision under frozen policy | N3 execution | `TARGET_REPRODUCTION_FAIL` |
| `c` | unit action cost normalization | X | allowed if frozen |

---

# 13. Threat model against experiment validity

The implementation must explicitly defend against the following failure modes.

## T1. Post-hoc boundary selection

**Threat:** inspect results, then choose an H/P_R boundary that makes q pure E.

**Defense:** external-anchor ledger is frozen before touch derivation; ambiguous anchors fail closed.

## T2. Manual resource labeling

**Threat:** encode `q -> E` directly.

**Defense:** no touch field in contract input; static scan; independent derivation.

## T3. PC middleware creates the semantics

**Threat:** experiment appears external but PC-specific middleware changes authorization meaning.

**Defense:** native policy and PDP are immutable; wrapper only constructs and submits standard XACML requests.

## T4. Cost cherry-picking

**Threat:** choose cost 1 to make geometry look meaningful.

**Defense:** main result is structural; cost sensitivity over multiple finite values must preserve classification.

## T5. Hidden authority change

**Threat:** the repaired request works only because some privilege/provider/configuration changed.

**Defense:** canonical `Lambda` hash and external config artifacts are identical pre/post.

## T6. Representation-by-string-presence

**Threat:** parser equates any appearance of the value with authorization visibility.

**Defense:** P_R derived from Category/AttributeId/DataType/Issuer-aware policy designators; wrong-category and wrong-datatype canaries.

## T7. Atomicity laundering

**Threat:** internal split/merge refactor is called Theorem-3-equivalent.

**Defense:** native request transaction is the declared interface; interface-changing variants are tagged out of scope.

## T8. Expected-result leakage

**Threat:** expected K influences compiler or solver.

**Defense:** dependency audit; expected file accessible only to final comparison stage.

## T9. Version drift

**Threat:** source changes mid-experiment.

**Defense:** pinned commit + local hashes + source verification before every phase.

## T10. Target relabeling

**Threat:** PDP returns unexpected decisions, then target classes are redefined to recover closure.

**Defense:** expected Permit/NotApplicable targets preregistered; mismatch aborts.

---

# 14. Test matrix

Minimum mandatory tests:

| ID | Test | Expected |
|---|---|---|
| S01 | pinned AuthzForce commit | exact SHA match |
| S02 | frozen fixture blobs | exact upstream blob matches |
| S03 | local source hashes | all pass |
| N01 | original request | Indeterminate/missing-attribute |
| N02 | x_permit completed request | Permit |
| N03 | x_nonpermit completed request | NotApplicable |
| A01 | H external anchor | FIXED |
| A02 | P_R external anchor | FIXED |
| A03 | Lambda external anchor | FIXED |
| A04 | Atom external anchor | FIXED |
| P01 | missing designator extracted | exact Category/Id/DataType/MBP |
| T01 | primary touch | `{E}` |
| T02 | independent touch | exact agreement |
| F000 | no freeze | 1 |
| F100 | E freeze | INF |
| F010 | R freeze | 1 |
| F001 | A freeze | 1 |
| F110 | E+R freeze | INF |
| F101 | E+A freeze | INF |
| F011 | R+A freeze | 1 |
| F111 | E+R+A freeze | INF |
| C01 | wrong category | does not satisfy designator |
| C02 | wrong datatype | rejected/handled per XACML semantics |
| C03 | irrelevant extra attribute | no manual P_R expansion |
| C04 | H anchor removed | positive gate fails |
| C05 | P_R anchor removed | positive gate fails |
| C06 | Lambda anchor removed | positive gate fails |
| C07 | Atom anchor removed | positive gate fails |
| C08 | manual touch injected | audit fails |
| C09 | source byte corruption | hash check fails |
| R01 | XML formatting perturbation | same semantic result |
| R02 | interface-changing split | marked out-of-scope |
| R03 | cost 0.5 | same structural class |
| R04 | cost 2 | same structural class |
| R05 | cost 10 | same structural class |
| R06 | clean full rerun | canonical result identical |

No mandatory test may be deleted after the preregistration seal without creating a new experiment version.

---

# 15. Implementation invariants

The following conditions must be asserted in code and documentation.

```text
INV-01 external policy bytes never change
INV-02 external pdp.xml bytes never change
INV-03 original request bytes never change
INV-04 original expected response bytes never change
INV-05 repaired requests differ from original only by the single declared Attribute addition
INV-06 world requests differ from each other only in that AttributeValue
INV-07 policy projection is parser-derived, never handwritten
INV-08 H canonicalization is independent of expected K
INV-09 P_R construction is independent of expected K
INV-10 Lambda construction is independent of expected K
INV-11 touch is derived only from extensional pre/post comparisons
INV-12 freezes only remove source-exposed actions
INV-13 freeze code never edits action internals
INV-14 target classes come from external PDP execution
INV-15 expected_signature is never imported by computation modules
INV-16 every artifact carries input hashes/provenance
INV-17 source drift fails closed
INV-18 anchor ambiguity fails closed
INV-19 solver disagreement fails closed
INV-20 manuscript claim generation occurs only after final seal
```

---

# 16. Exact analysis plan

There are no statistical tests, confidence intervals, p-values, bootstraps, or population estimates in the primary experiment.

The analysis is deterministic:

1. reproduce external authorization semantics;
2. audit external anchor completeness;
3. mechanically compile a complete PC contract;
4. derive resource touch;
5. evaluate all eight freezes exactly;
6. independently recompute;
7. run falsification/sensitivity controls;
8. seal one categorical outcome.

The primary numerical object is:

```text
K_Pi
```

The primary identification object is:

```text
|K_{Pi,Omega_star}|
```

The primary success criterion is:

```text
|K_{Pi,Omega_star}| = 1
AND K_Pi is nontrivial
AND H/P_R/Lambda/Atom are externally anchored
AND touch is mechanically derived
```

---

# 17. Interpretation rules

## 17.1 What success means

Success means:

> In this independently authored standards-based authorization case, external governing semantics were sufficiently explicit to fix the PC admission/representation/authority/intervention interface used by the measurement, allowing mechanical resource-touch extraction and point identification of a nontrivial all-freeze signature.

## 17.2 What success does not mean

It does **not** mean:

- XACML is universally PC-complete.
- AuthzForce deployments usually exhibit this signature.
- PC can infer semantics from arbitrary source code.
- the `E/R/A` factorization is universal.
- every authorization implementation exposes the same action algebra.
- the unit cost is a real-world economic cost.
- the single external case establishes prevalence.
- the structural E result is a causal decomposition of evidence's internal contribution.
- XACML proves PC's theorems.
- PC improves AuthzForce authorization decisions.
- this experiment replaces the PC-TAU finite-substitution evidence.

## 17.3 What failure means

If the external anchors are insufficient, that does not falsify Stage III. It shows this particular natural specification does not satisfy the sufficient conditions needed for point identification.

The failed case may be reported as an additional natural underidentification example only if scientifically useful; it must not be converted into a positive result by analyst-chosen completion.

---

# 18. Allowed manuscript claims

## 18.1 If outcome = `POSITIVE_NATIVE_STAGE3`

Allowed wording:

> We additionally audited a pre-existing XACML/AuthzForce authorization fixture whose policy, request-context semantics, PDP configuration, and native request/response interface were fixed independently of PC. These external artifacts were sufficient to anchor the PC admission, policy-visible representation, authority/configuration, and atomic request boundary for the measured case. Without manual E/R/A action labels, PC mechanically derived a pure evidence-admission repair and a singleton nontrivial all-freeze signature. This is an external positive Stage-III witness, not a prevalence claim.

Stronger but still acceptable only if every audit passes:

> Unlike Polaris, whose raw repository semantics leave the E/R boundary underidentified, the XACML case contains an independently specified authorization interface sufficient for conditional PC point identification.

## 18.2 Forbidden even on success

Do not write:

```text
"real systems naturally provide PC anchors"
"Stage III works in the wild"
"XACML validates the universal E/R/A ontology"
"PC automatically extracts governance semantics"
"we prove representation/evidence causality in XACML"
"production authorization systems are PC-identifiable"
```

## 18.3 If outcome = `NATIVE_ANCHOR_INSUFFICIENT`

Allowed wording:

> A preregistered audit of XACML/AuthzForce did not justify all Stage-III anchors without additional analyst semantics; PC therefore retained underidentification rather than forcing a point estimate.

Do not call it a positive Stage-III experiment.

---

# 19. Recommended paper role if successful

This experiment should occupy **very little main-paper space**.

Its job is only to answer:

> Does a non-PC governing specification ever naturally supply enough semantic structure for Stage III?

Recommended empirical composition after success:

```text
DS-CF
  -> motivating semantic repair

Polaris
  -> natural negative source-identification case

XACML/AuthzForce S3+
  -> natural/externally specified positive conditional-identification case

PC-TAU Exact
  -> controlled nondegenerate finite substitution + geometry diversity

LLM1
  -> trained-agent fallback realizability
```

This creates a clean negative/positive external pair:

```text
Polaris: external source insufficient -> retain identified set
XACML:   external governing semantics sufficient -> point identify
```

That pairing is the scientific value of this experiment.

---

# 20. Recommended implementation order within each phase

Each phase must follow:

```text
SOURCE CHECK
   -> DERIVE
      -> ASSERT
         -> SAVE RAW OUTPUT
            -> INDEPENDENT CHECK
               -> GATE
                  -> COMMIT
```

Do not combine multiple phases into one opaque script during development.

Final reproduction may use `scripts/reproduce_all.sh`, but phase-specific raw artifacts must remain available.

---

# 21. Logging requirements

Every execution record must contain:

```text
experiment_id
phase
UTC timestamp
Git commit of experiment repository
AuthzForce pinned commit
external manifest hash
preregistration hash
contract hash if available
command invoked
exit code
stdout hash
stderr hash
output artifact hashes
```

Logs must never overwrite prior logs. Use deterministic run IDs plus append-only indexing.

---

# 22. AI-assistance policy

AI tools may assist with boilerplate coding, test generation, debugging, or prose, but may not silently choose the semantic anchor that makes the expected PC result succeed.

Rules:

1. every accepted anchor must cite external source evidence;
2. AI suggestions are treated as analyst suggestions, not external authority;
3. any AI-assisted change to an anchor after Phase-2 seal requires a new experiment version or an explicit mutation record;
4. expected-result files must not be provided to an AI agent whose task is to infer the anchors unless the interaction is explicitly labeled adversarial review rather than primary extraction;
5. the final audit must state where AI tools were used.

---

# 23. Stop conditions

Immediately stop the positive experiment if any of the following occurs:

```text
STOP-01 pinned external source cannot be reproduced
STOP-02 completed target decisions are not distinct as preregistered
STOP-03 H lacks external semantic justification
STOP-04 P_R requires a manually selected authorization-visible partition
STOP-05 Lambda changes during the repair or cannot be externally fixed
STOP-06 native atomic request boundary cannot be justified
STOP-07 mechanical touch depends on manual E/R/A labels
STOP-08 primary/independent touch disagree
STOP-09 primary/independent solvers disagree
STOP-10 source drift occurs after seal
STOP-11 result requires changing the frozen policy/configuration
STOP-12 positive claim requires redefining target after execution
```

A stop is a scientific result, not permission to improvise a new completion.

---

# 24. Completion checklist

## Source and preregistration

- [ ] AuthzForce 21.2.0 pinned at exact commit.
- [ ] Four external fixture files copied without modification.
- [ ] Git blob SHAs recorded.
- [ ] Local SHA-256 hashes recorded.
- [ ] OASIS XACML 3.0 spec copied and hashed.
- [ ] environment versions locked.
- [ ] original fixture reproduced.
- [ ] experiment.yaml sealed.
- [ ] expected signature sealed.

## External semantic anchors

- [ ] H provenance passes.
- [ ] P_R provenance passes.
- [ ] Lambda provenance passes.
- [ ] Atom provenance passes.
- [ ] policy projection mechanically generated.
- [ ] no manual certificate partition list.
- [ ] no manual resource-touch labels.
- [ ] completed target decisions reproduce.

## PC compilation

- [ ] complete contract serialized.
- [ ] initial state open.
- [ ] both world successors closed.
- [ ] touch derived mechanically.
- [ ] independent touch agrees.

## Exact geometry

- [ ] eight freeze rows generated.
- [ ] primary exact solver complete.
- [ ] independent exact solver complete.
- [ ] all coordinates agree.
- [ ] identified set cardinality justified.
- [ ] nontriviality gate passes.

## Falsification

- [ ] source corruptions detected.
- [ ] missing-attribute canary passes.
- [ ] wrong-category canary passes.
- [ ] wrong-datatype canary passes.
- [ ] irrelevant-attribute projection test passes.
- [ ] interface-preserving mutations preserve signature.
- [ ] interface-changing split correctly rejected from invariance claim.
- [ ] cost sensitivity passes.
- [ ] anchor ablations kill positive eligibility.
- [ ] manual touch injection detected.
- [ ] expected-result leakage check passes.
- [ ] clean reproduction passes.

## Seal

- [ ] FINAL_RESULT.json generated from observed artifacts.
- [ ] FINAL_AUDIT.md generated.
- [ ] MANIFEST.sha256 complete.
- [ ] deterministic archive created.
- [ ] claim wording matches outcome.
- [ ] no post-hoc semantic edits.

---

# 25. Final success definition

The experiment is complete only when the following statement is either proven by the artifact package or explicitly rejected by the experiment's own gates:

```text
For the pinned OASIS XACML 3.0 / AuthzForce 21.2.0
StatusDetail.MissingAttributeDetail authorization case,
the independently authored governing semantics fix the PC semantic
anchors and native intervention boundary sufficiently to derive resource
touch mechanically and point-identify a nontrivial all-freeze closure
signature, without manually choosing E/R/A labels after observing the
result.
```

Preregistered positive prediction:

```text
T(q_supply_missing_attribute) = {E}
K_Pi = [1, INF, 1, 1, INF, INF, 1, INF]
|K_{Pi,Omega_star}| = 1
classification = structural E-touch dependence
```

The experiment must be allowed to contradict this prediction.

That fail-open-to-evidence / fail-closed-to-claims asymmetry is the entire point of the design.

---

# 26. External references to freeze in the artifact package

1. OASIS, **eXtensible Access Control Markup Language (XACML) Version 3.0**. Normative core specification.  
   `https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html`

2. AuthzForce Core Community Edition repository.  
   `https://github.com/authzforce/core`

3. AuthzForce Core release `21.2.0`, tag `release-21.2.0`, pinned commit `3cc0e988e1639da48184434cd5c918102ff5b499`.

4. Frozen AuthzForce fixture at the pinned commit:  
   `pdp-testutils/src/test/resources/conformance/others/StatusDetail.MissingAttributeDetail/`

The final release package should contain immutable local copies/hashes so reproducing the experiment does not depend on future network content remaining unchanged.
