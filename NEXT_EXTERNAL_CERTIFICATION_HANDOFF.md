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
