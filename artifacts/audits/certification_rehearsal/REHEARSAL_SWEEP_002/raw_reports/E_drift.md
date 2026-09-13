NON_BLIND_ADVERSARIAL_REVIEW — REHEARSAL_SWEEP_002 — REVISION_001
Panel E drift hunt (frozen packets vs live tree at <AUTHOR_REPO_COMMIT_018>). Contaminated, never blind. No prior sweep seen.

1. Builder hash: live has guard lines, frozen copy lacks them (033c84fd vs 1fb45c57); wrapper_evidence current, packet copy stale. Provenance bookkeeping only; bytes evaluated identical.
2. Rule-to-code: live 11 entries incl. value-level DataType; blind atom had counts-only; FINAL points at fresh wrapper evidence. Evidence strength only.
3. Schema fix: blind proof/H/atom/manifest reference old invalid bytes; live proof/H/ledger reference new valid bytes, bags identical. Legality only.
4. H checkpoints: blind ledger/files old shas + backslash paths; live new shas + slashes; VOLATILE 3-vs-4 unified live. Bookkeeping only.
5. Proof hashes: content differs only input_hashes + timestamps; rows/verdict/route identical.
6. Manifests: blind 20-file candidate set superseded by FINAL 50-file set; corpus hashes identical. Coverage bookkeeping.
7. Phase scripts bind execution_inputs values live; packets contain no scripts; values identical. Input-trust binding only.
8. Ledger envelope cross-checks + volatile unification + refs mode live; blind ledger bare. Anchors stay FIXED; FINAL ledger matches live. Promotion bookkeeping.
Conclusion: 8 drift states, all provenance/bookkeeping, no bag/verdict/status change. Only intra-REVISION_001 inconsistency needing a freeze note: FINAL builder_source.py trails live while wrapper_evidence.json is current.
