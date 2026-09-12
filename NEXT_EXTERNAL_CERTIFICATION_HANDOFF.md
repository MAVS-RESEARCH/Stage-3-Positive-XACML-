# NEXT EXTERNAL CERTIFICATION HANDOFF (frozen inputs only)

Auditor IDs (fresh chairs, one isolated session each): AUD-C04, AUD-C05, AUD-C06.
Operative packet path: artifacts/audits/semantic_hardening/final_freeze/FINAL_BLIND_PACKET/
Operative packet SHA-256: 156e36d75627d2aa746026a9689e1d3f3f293b51b5104e16a60ea3f29bdc255e
Operative prompt path: prereg/final_certification_prompt.txt
Operative prompt SHA-256: 4ec4f9b6e21794f8068d225bf7b6825c8ab3f3a4ca1b43161fef504b08dcbdf3
Final schema: embedded in the prompt (verdict JSON shape lines 39-52: verdict_id, auditor_id, qualification COLD_MODEL_INDEPENDENT, per-anchor verdicts with locators, attestation_hash, verbatim declaration, prompt/packet hashes, isolation flags) plus a separate attestation text file.

## Cold-session instructions

1. Open a brand-new empty session per chair; never reuse a session across chairs.
2. Give the chair ONLY: the packet folder, the prompt file bytes, and the schema above. Nothing else.
3. Tell the chair its auditor ID and demand exactly two artifacts: the verdict JSON and the separate attestation text, with attestation_hash = sha256 of the attestation exact bytes.
4. Never mention other chairs, prior results, or any expectation about the outcome.

## Ingestion commands (operator runs after collecting outputs)

python src/audit/final_certification.py --repo-root . --ingest-final --auditor AUD-C04 --raw <chair-AUD-C04-raw-file> --attestation <chair-AUD-C04-attestation>
python src/audit/final_certification.py --repo-root . --ingest-final --auditor AUD-C05 --raw <chair-AUD-C05-raw-file> --attestation <chair-AUD-C05-attestation>
python src/audit/final_certification.py --repo-root . --ingest-final --auditor AUD-C06 --raw <chair-AUD-C06-raw-file> --attestation <chair-AUD-C06-attestation>
python src/audit/final_certification.py --repo-root . --assert-final-unlock

## Attestation and isolation requirements

Attestation names its auditor, is written in its own words, and is byte-distinct across chairs; verdict carries the verbatim non-exposure declaration and affirms fresh_context, no_prior_experiment_context, other_outputs_unavailable.

## Per-chair cold-session prompts (paste one per isolated session)

### AUD-C04

You are auditor `AUD-C04` for a final blind semantic certification.

You are operating in a brand-new isolated session. You have not seen and must not seek anything about this experiment beyond the supplied materials.

You are given ONLY:

1. the operative `FINAL_BLIND_PACKET/`;
2. the frozen `final_certification_prompt.txt`;
3. the final certification schema/output contract.

The frozen certification prompt is authoritative.

Judge:

- H
- P_R
- Lambda
- Atom

against the frozen packet only.

Do not attempt to help the experiment succeed.

Do not infer, reconstruct, seek, or speculate about:

- expected touch;
- expected K;
- freeze signature;
- expected classification;
- preferred result;
- publication claims;
- prior revisions;
- prior panels;
- prior developmental review.

Be adversarial toward unsupported mappings.

If materially relevant semantic freedom remains under the supplied certification criterion, return the appropriate non-FIXED status.

Do not resolve uncertainty toward FIXED merely because a mapping is reasonable or apparently intended.

Inspect frozen evidence rather than trusting experiment-authored summaries alone.

For Atom, apply the native-transaction versus experiment-authored staging/reconstruction distinction defined by the frozen prompt.

For Lambda, independently verify the capability boundary and packet-visible reconstruction rather than assuming manifests or composite hashes are complete.

Return exactly the artifacts required by the frozen prompt/schema.

Use:

auditor_id = `AUD-C04`

prompt_sha256 = `4ec4f9b6e21794f8068d225bf7b6825c8ab3f3a4ca1b43161fef504b08dcbdf3`

packet_sha256 = `156e36d75627d2aa746026a9689e1d3f3f293b51b5104e16a60ea3f29bdc255e`

The attestation hash must be the SHA-256 of the exact separate attestation artifact bytes.

No commentary outside the required artifacts.

Your role is certification, not collaboration.

### AUD-C05

You are auditor `AUD-C05` for a final blind semantic certification.

You are operating in a brand-new isolated session. You have not seen and must not seek anything about this experiment beyond the supplied materials.

You are given ONLY:

1. the operative `FINAL_BLIND_PACKET/`;
2. the frozen `final_certification_prompt.txt`;
3. the final certification schema/output contract.

The frozen certification prompt is authoritative.

Judge:

- H
- P_R
- Lambda
- Atom

against the frozen packet only.

Do not attempt to help the experiment succeed.

Do not infer, reconstruct, seek, or speculate about:

- expected touch;
- expected K;
- freeze signature;
- expected classification;
- preferred result;
- publication claims;
- prior revisions;
- prior panels;
- prior developmental review.

Be adversarial toward unsupported mappings.

If materially relevant semantic freedom remains under the supplied certification criterion, return the appropriate non-FIXED status.

Do not resolve uncertainty toward FIXED merely because a mapping is reasonable or apparently intended.

Inspect frozen evidence rather than trusting experiment-authored summaries alone.

For Atom, apply the native-transaction versus experiment-authored staging/reconstruction distinction defined by the frozen prompt.

For Lambda, independently verify the capability boundary and packet-visible reconstruction rather than assuming manifests or composite hashes are complete.

Return exactly the artifacts required by the frozen prompt/schema.

Use:

auditor_id = `AUD-C05`

prompt_sha256 = `4ec4f9b6e21794f8068d225bf7b6825c8ab3f3a4ca1b43161fef504b08dcbdf3`

packet_sha256 = `156e36d75627d2aa746026a9689e1d3f3f293b51b5104e16a60ea3f29bdc255e`

The attestation hash must be the SHA-256 of the exact separate attestation artifact bytes.

No commentary outside the required artifacts.

Your role is certification, not collaboration.

### AUD-C06

You are auditor `AUD-C06` for a final blind semantic certification.

You are operating in a brand-new isolated session. You have not seen and must not seek anything about this experiment beyond the supplied materials.

You are given ONLY:

1. the operative `FINAL_BLIND_PACKET/`;
2. the frozen `final_certification_prompt.txt`;
3. the final certification schema/output contract.

The frozen certification prompt is authoritative.

Judge:

- H
- P_R
- Lambda
- Atom

against the frozen packet only.

Do not attempt to help the experiment succeed.

Do not infer, reconstruct, seek, or speculate about:

- expected touch;
- expected K;
- freeze signature;
- expected classification;
- preferred result;
- publication claims;
- prior revisions;
- prior panels;
- prior developmental review.

Be adversarial toward unsupported mappings.

If materially relevant semantic freedom remains under the supplied certification criterion, return the appropriate non-FIXED status.

Do not resolve uncertainty toward FIXED merely because a mapping is reasonable or apparently intended.

Inspect frozen evidence rather than trusting experiment-authored summaries alone.

For Atom, apply the native-transaction versus experiment-authored staging/reconstruction distinction defined by the frozen prompt.

For Lambda, independently verify the capability boundary and packet-visible reconstruction rather than assuming manifests or composite hashes are complete.

Return exactly the artifacts required by the frozen prompt/schema.

Use:

auditor_id = `AUD-C06`

prompt_sha256 = `4ec4f9b6e21794f8068d225bf7b6825c8ab3f3a4ca1b43161fef504b08dcbdf3`

packet_sha256 = `156e36d75627d2aa746026a9689e1d3f3f293b51b5104e16a60ea3f29bdc255e`

The attestation hash must be the SHA-256 of the exact separate attestation artifact bytes.

No commentary outside the required artifacts.

Your role is certification, not collaboration.

