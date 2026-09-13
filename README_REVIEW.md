# Reviewer Snapshot (Anonymized)

This branch (`anonymous`) is an anonymized reviewer snapshot prepared for
double-blind review. It is a sanitized staging copy of the canonical
final-positive scientific state. It is not the canonical repository history.

## Final scientific result (preserved)

- Experiment: `PC-XACML-S3PLUS-v1`
- Final result: `POSITIVE_NATIVE_STAGE3`
- Native outcomes: `Permit` (`x_permit`), `NotApplicable` (`x_nonpermit`)
- Touch: `{E}` (`q_supply_missing_attribute`)
- Freeze signature (K): `[1, INF, 1, 1, INF, INF, 1, INF]`
- Completion: `COMPLETE` (`free_k_relevant_fields = 0`)
- Identified-set cardinality: `1`
- Falsification battery: `13/13` boxes
  (5/5 corruptions, 4 semantic canaries, 3 perturbations,
  interface-change control, cost sweep, negative-world sweep,
  4 ablations, label injection, leakage audit, clean reproduction)
- Sealed native suite: `193 passed, 6 skipped` at seal
  (current working tree `200 passed, 6 skipped`; delta is post-seal
  verification tests only, no semantic change)
- External system: `OASIS XACML 3.0 + AuthzForce Core CE 21.2.0`
- External upstream commit: `3cc0e988e1639da48184434cd5c918102ff5b499`
  (third-party provenance, preserved verbatim)
- Launch: `PC-XACML-S3PLUS-v1-launch-003`
- Launch packet SHA256 (canonical): `8e23901d4643a42a4748af8894c0439f19f071f736d23225ea906aac97099ce6`
- Prompt SHA256 (canonical): `251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865`
- Registry SHA256 (canonical): `d7641f64ced4092a23e7e75dcb26f00f5fa274f27ca3171b2d39792e6fe7e44a`
- Conformance: `RUN_CONFORMANCE_PASSED`
- Target-execution evidence: `TARGET_EXECUTION_LOCK.json`
  (worlds `[x_nonpermit, x_permit]`), `TARGET_EXECUTION_AUTHORIZED.json`,
  `RUN_CONFORMANCE_PASS.json`, `completion_space_certificate.json`,
  `phase3_manifest.json`, `FINAL_RESULT_LAUNCH.json`
- Historical negatives preserved verbatim as separate seals:
  `FINAL_RESULT.json` (`CYCLE_001`, `NATIVE_ANCHOR_INSUFFICIENT`,
  `completed_executions = 0`, `freezes = NOT_COMPUTED`),
  `FINAL_RESULT_CYCLE_002.json` (`CYCLE_002`, same terminal negative),
  plus `CYCLE_001`/`CYCLE_002` material, `L01-03`/`L04-06` failed
  launch packets and all superseded hardening/rehearsal records.
  The old negative result is historical; the later `launch-003`
  positive seal is the final result. No failure record was removed,
  beautified, or relabeled.

Inspect without identity:

- `artifacts/seal/FINAL_RESULT_LAUNCH.json`
- `artifacts/seal/TARGET_EXECUTION_LOCK.json`
- `artifacts/audits/launch/RUN_CONFORMANCE_PASS.json`
- `artifacts/seal/completion_space_certificate.json`
- `artifacts/freezes/K_table.json`, `artifacts/freezes/identified_set.json`
- `artifacts/contracts/touch.json`
- `artifacts/seal/FINAL_RESULT.json`,
  `artifacts/seal/FINAL_RESULT_CYCLE_002.json` (historical negatives)

## What was omitted or redacted

- Author-controlled Git history (commits, authors, emails, chronology,
  messages) was intentionally omitted. This branch is an orphan snapshot
  with a single anonymous root commit; it has no parent relationship to
  the canonical history.
- Author-controlled identity in tracked content was redacted with stable
  placeholders:
  - author repository URLs and owner references
    (`<AUTHOR_REPOSITORY>`, `<AUTHOR_ORG>`);
  - local filesystem users and paths
    (`<USER_HOME>`, `<LOCAL_PATH>`, `<WORKSPACE>`, `<REPO>`);
  - author-repository Git commit and object identifiers
    (`<AUTHOR_REPO_COMMIT_001>` …,
     `<AUTHOR_GIT_OBJECT_001>` …), applied consistently in chronological
    order to preserve chronology and logical relationships;
  - copyright holder names (review copy only):
    `Copyright (c) 2026 Anonymous Authors` (license terms unchanged);
  - schema `$id` authority redacted to `https://anonymous.invalid/…`
    (path suffixes preserved);
  - local timezone indicators reduced to UTC where scientifically
    unnecessary.
- Archive packaging for anonymity:
  `PC-XACML-S3PLUS-v1.tar.gz` and its two `.sha256` sidecars are omitted
  from this snapshot by design. The compressed archive would embed
  canonical bytes containing identity (license/copyright, clone URLs)
  even though its file metadata is deterministic. All constituent files
  are present individually in this snapshot and are covered by
  `REVIEW_SHA256SUMS.txt`. Original archive hashes remain authoritative
  in the canonical branch.
- No author names, emails, usernames, organizations, personal domains,
  local paths, or canonical commit/object identifiers remain in tracked
  content (verified by scan; see `ANONYMIZATION_REPORT.json`).

## What was preserved

- Scientific results, including the final positive witness and all
  negative results, failed panels (`M01-03`, `C01-03`, `C04-06`,
  `L01-03`, `L04-06` plus procedural `L08` invalid attempts), failed
  launches, null outcomes, metrics, freeze geometry, costs, policy
  semantics, worlds, requests, semantic anchors, frozen
  producer/verifier structure, experiment IDs, external versions, and
  falsification outcomes, are unchanged in meaning.
- External upstream provenance is preserved verbatim:
  - upstream AuthzForce release (`21.2.0`) and commit pin
    (`3cc0e988e1639da48184434cd5c918102ff5b499`);
  - upstream fixture blob identifiers and content hashes;
  - OASIS XACML standard references;
  - third-party toolchain versions and platform facts where
    scientifically relevant (Maven, Java, `lxml`, `pytest`).
- Third-party source copies (engine sources, specification text) are
  byte-identical; generic example paths (e.g. `/home/foo`,
  `file:///path/to`) are upstream documentation examples and were
  preserved.
- Amendment history, measured values, policies, requests, worlds, costs,
  semantic-interface definitions, and the negative chronology were not
  altered to obtain positivity. No experiment was rerun to recreate
  evidence.

## Review hashes versus original seals

Sanitization changes bytes. Original experiment seals therefore cannot
authenticate the sanitized reviewer bytes.

- `REVIEW_SHA256SUMS.txt` authenticates the final anonymized reviewer
  bytes only. It is not a claim about canonical bytes. Never relabel a
  review hash as an original seal.
- Original canonical seals are preserved as historical provenance where
  still truthful about canonical bytes:
  - launch packet `8e23901d…`, prompt `251f7e58…`, registry `d7641f64…`
    remain in `FINAL_RESULT_LAUNCH.json` and launch-freeze records;
  - AuthzForce upstream commit `3cc0e988…` remains verbatim everywhere;
  - freeze/contract/touch/certificate hashes in
    `FINAL_RESULT_LAUNCH.json` still match live review bytes for all
    scientific files (no scientific file was altered).
- Where sanitization broke a live consistency binding required for
  reproduction, the binding was recomputed over sanitized bytes and
  explicitly marked as a review value:
  - amendment seal `amendment_sha256` recomputed over anonymized
    `PROTOCOL_AMENDMENT_001.md` (was
    `47c803a41177ddfb885e60a4ead3f3ed8b65a010977922862cc993a440be1be8`,
    now `dad4260000c197944676f0e68c2c3a8b76f431fe93c0d44a27d7a85990972338`);
    author commit and blob identifiers aliased;
    `review_snapshot: true` added with `review_note`;
  - live launch-packet (`launch_packet`, `launch-003`)
    `dependency_content.sha256` recomputed (was
    `bac1eae93f099ec85af41aaf0f3725ca674fd035cd65c835356741e98af41c56`,
    now `b7ee4fb81a07960e0d09b2a73d1f124a5cbd63ec652c544597a81836ea53621d`),
    `pre_hash` recomputed (was
    `194fcbbecc398f718d4b172133db3825f40648f73d62e31d1fae658bd50f4ed3`,
    now `5d602e07db597fdcd6f181014f41558c0a32df3c287dc7bc72f7c0c7806ec55b`),
    `PACKET_MANIFEST.json` entries recomputed,
    `PACKET_SHA256.txt` recomputed (was `8e23901d…`, now
    `c282a29e06e039a868c8ee1630525f2afc581aa5f4d4a95369e857d9a3c9bda3`),
    and `pre_hash_lineage.json` current `pre_hash` recomputed; each JSON
    file carries `review_snapshot: true` and a `review_note`.
    Historical launch packets (`rev001`, `rev002`) and hardening-round
    evidence were left with canonical hashes as historical seals even
    though review bytes differ by path redaction only; no test checks
    those historical bindings live.
- `MANIFEST.sha256` is preserved verbatim as a canonical seal even
  though review bytes differ for anonymized files. `REVIEW_SHA256SUMS.txt`
  is the live integrity binding for review bytes. The drift is exactly
  the anonymized/review-recomputed set; all scientific files
  (contracts, freezes, seals, policies, requests, worlds, costs,
  anchors, certificates, falsification artifacts) still match
  `MANIFEST.sha256` (see `ANONYMIZATION_REPORT.json` non-regression).
- Historical records that attest to canonical bytes (freeze records,
  verdicts, lineage history entries, prior-work notes) were left
  verbatim where they do not contain identity, even though their
  recorded hashes refer to canonical bytes rather than review bytes.
  This preserves negative evidence and chronology exactly.
- A minimal review-aware branch in the amendment gate
  (`src/audit/model_adjudication.py`) and its test
  (`tests/test_model_adjudication.py::test_18_amendment_chronology`)
  skips the `merge-base --is-ancestor` check when the seal carries a
  review alias (other seal bindings remain enforced). See code comments
  referencing this file. No scientific gate was weakened; canonical
  history checks remain intact in the canonical branch.

Canonical identity, history, and original seals remain authoritative in
the canonical branch and will be restored after double-blind review.

## Reproduction

Primary environment is recorded in `artifacts/raw/environment.txt`.
Phase scripts: `scripts/run_phase<N>.ps1` (authoritative on the pinned
Windows host) with POSIX twins `run_phase<N>.sh`. Full replay:
`scripts/reproduce_all.sh` / `reproduce_all.ps1` (uses `--reproduce`
modes; sealed human-judgment artifacts verified by hash, never
regenerated).

To inspect the final result without running the native experiment:

- read `artifacts/seal/FINAL_RESULT_LAUNCH.json` and verify
  `outcome`, `decisions`, `derived_touch`, `K`,
  `identified_set_cardinality`, `external_system`,
  `authzforce_commit`, and hash bindings against live files;
- read `artifacts/seal/completion_space_certificate.json`
  (`verdict: COMPLETE`);
- read `artifacts/freezes/K_table.json` and
  `artifacts/freezes/identified_set.json`;
- read `artifacts/audits/FINAL_AUDIT.md` (15 sections) for the
  per-condition record, including `13/13` falsification.

Do not rerun the native experiment to recreate evidence. Tests verify
copied artifacts; they do not regenerate seals.

Expected review-suite result in this snapshot: `200 passed, 6 skipped`
(206 collected) in the canonical working tree; in this anonymized snapshot
the suite reports `197 passed, 7 skipped, 2 failed` (206 collected) where
the two failures are (a) one pre-existing environment-only failure
requiring the git-ignored upstream clone (`external/authzforce-repo`,
absent from any snapshot by design; also fails on a clean canonical
checkout without that ignored directory), and (b) one expected
review-artifact drift failure in `test_manifest_and_archive` because
`MANIFEST.sha256` is the canonical seal while review bytes differ exactly
in the anonymized set (all scientific files still match). No
sanitization-related scientific failure remains. See
`ANONYMIZATION_REPORT.json` for exact recorded counts from the review run.

## Provenance of this snapshot

- Orphan branch with one anonymous root commit:
  author and committer `Anonymous Authors`,
  non-identifying noreply address, UTC timestamps.
- Commit message is exactly `Anonymous reviewer snapshot`.
- No tags, submodules, or LFS storage associated with this snapshot.
