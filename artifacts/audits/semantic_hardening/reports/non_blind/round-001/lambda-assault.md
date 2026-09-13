# NON_BLIND_HARDENING_REVIEW -- Lambda assault, Wave 1, HARDENING_ROUND_001 input
# Role: Lambda / capability-configuration boundary. Developmental only.
# Key contribution: exact AuthzForce source paths for default wiring.

## Per-component DEV verdicts
policy bytes WEAK (raw sha only, no canonical form/PARENT_DIR binding); provider element bytes FAIL (c14n bytes never stored); preprocessor selection FAIL (sentinel, misses real default io/PdpEngineAdapters.java:242-250 default-lax + BaseXacmlJaxbResultPostprocessor); attribute-provider set FAIL ([] contradicts likely std-env default; PdpEngineConfiguration.java:369-392 adds StandardEnvironmentAttributeProvider.DEFAULT_FACTORY if enabled; schema default unseen); native interface FAIL (free text); version/build identity ABSENT (no pom lock/git SHA/jar hash/pdp.xsd); environment/time UNPROVEN (StandardEnvironmentAttributeProvider.java helper validates env consistency -> Indeterminate; overrideEvalCtxFromTimestamp wall-clock injection; timestamp source unpinned); handler/config defaults ABSENT (enableXPath, standard registries, strictAttributeIssuerMatch:461/510-511, depths, cache, verbosity); glob/PARENT_DIR BINDING ABSENT (CoreStaticPolicyProvider.java:176-256, getCandidateRootPolicy:765-826, ignoreOldVersions, DefaultEnvironmentProperties.java:81-103, PdpEngineConfiguration.java:735-748); post null + prose criterion FAIL.

## Objections 1-9 (anchor=Lambda)
1. pre_hash input includes opaque sentinel + unstored c14n bytes; recomputation requires re-running code. (E/D)
2. provider c14n bytes/method unstated; comment/attr-order changes undetectable in principle. (D/E)
3. preprocessor sentinel misses true default adapter chain. (B/C)
4. empty provider set asserts disabled default without schema/JAXB evidence. (C)
5. env/time inertness unproven (override flags, timestamp source, env-bearing-request errors). (B)
6. resolved-effective-config absent (all JAXB defaults/registries). (C/D)
7. glob expansion/PARENT_DIR/ordering/multi-root ambiguity unpinned. (C)
8. version/build/extension identity absent (capability == code). (C)
9. post null + prose criterion, no comparator/tolerance/failure action. (A/F)

## Repair design (evidence/representation only)
component_manifest.json per component {reason, source (file+line or code path), canonical_spec, sha256, stability_criterion} + exclusions with inertness locators; publish provider_c14n bytes + method spec, pdp_resolved_effective.json, policy_dir_listing.json, version_lock.json, preprocessor_resolved.json; recompute pre_hash over canonical manifest bytes with spec in packet; env_inertness_certificate (designator/function census + override flag + H-world locators).

## Falsifiers
Per-objection packet-internal deterministic recomputation from stored canonical bytes without opaque re-execution or external checkout.
