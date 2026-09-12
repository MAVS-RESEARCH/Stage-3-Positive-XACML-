NON_BLIND_ADVERSARIAL_REVIEW — REHEARSAL_SWEEP_003_HOLDOUT — REVISION_001
Holdout falsifier 2 (capability). Contaminated, never blind. No taxonomy seen.

BREAK FOUND — deployed root-policy-set cardinality not pinned. pdp.xml loads by glob (StaticPolicyProvider, PARENT_DIR/*.xml); manifest pins element C14N + policy.xml bytes only; listing is observation not gate; staged-copy identity asserts byte-identity, not set-exclusivity; builder out_dir arbitrary (argv, makedirs, writes *.xml), no out_dir-vs-policies guard; invocation pins sites not values.
Counterexamples: extra Permit-all policy collapses world distinction; duplicate PolicyId vs ignoreOldVersions unpinned; non-policy xml breaks load. All frozen hashes still pass.
Self-pollution 1d: builder invoked with out_dir inside staged policies/ writes request_x_*.xml into the glob; second-world evaluation sees first-world build files; content hashes still verify (content, not path-exclusion).
Near-misses correctly pinned/inert: strictIssuer/xPath/verbosity/maxInteger/registries; env clock; IncludeInResult; attribute order/pretty-print; lax duplicates/empty env; unhashed impl bytes (supply-chain hypothetical, weaker).
Fix: freeze + enforce staged policies/ listing hash (count/names/bytes) as pre-eval gate; prove out_dir disjointness.
