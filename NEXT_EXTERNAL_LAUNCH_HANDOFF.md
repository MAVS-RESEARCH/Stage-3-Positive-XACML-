# NEXT EXTERNAL LAUNCH HANDOFF — AMENDMENT 007 PRE-EXECUTION CERTIFICATION (frozen inputs only)

Auditor IDs (fresh chairs, one isolated session each): AUD-L01, AUD-L02, AUD-L03.
Operative launch packet path: artifacts/audits/launch/launch_packet/
Operative launch packet SHA-256: db661dd74a37bec4586fce0ae329263b63ab679908fd1336a69eefa904e92a8d
Operative prompt path: artifacts/audits/launch/launch_certification_prompt.txt
Operative prompt SHA-256: 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865
Operative registry path: artifacts/audits/launch/run_conformance_obligations.json
Operative registry SHA-256: 12a46820dca3434a6d993d6801c52e4df24d02602e6391a263df03e98910a837
Launch freeze record: artifacts/audits/launch/LAUNCH_FREEZE.json
Protocol: PROTOCOL_AMENDMENT_007.md (§§0–19 operative).

Verdict schema: embedded in the prompt (verdict JSON: verdict_id, auditor_id,
qualification COLD_MODEL_INDEPENDENT, per-anchor verdicts H/P_R/Lambda/Atom
with locators, per-obligation deferrals LEGITIMATELY_DEFERRED /
IMPROPER_DEFERRAL / UNSUPPORTED, attestation_hash, verbatim declaration,
prompt/packet hashes, isolation flags) plus a separate attestation text file.
Attestation MUST name its auditor ID AND quote the packet SHA-256 AND the
prompt SHA-256 above (revision binding; attestations without both hashes are
INVALID and will be refused at ingest).

## Cold-session instructions

1. Open a brand-new empty session per chair; never reuse a session across chairs.
2. Give the chair ONLY: the launch packet folder, the prompt file bytes, the
   registry file bytes, and the schema above. Nothing else.
3. Tell the chair its auditor ID and demand exactly two artifacts: the verdict
   JSON and the separate attestation text, with attestation_hash = sha256 of
   the attestation exact bytes.
4. Never mention other chairs, prior results, CYCLE_001/CYCLE_002, expected
   touch/K/classification, manuscript claims, or any expectation about the outcome.

## Ingestion commands (operator runs after collecting outputs)

python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L01 --raw <chair-AUD-L01-raw-file> --attestation <chair-AUD-L01-attestation>
python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L02 --raw <chair-AUD-L02-raw-file> --attestation <chair-AUD-L02-attestation>
python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L03 --raw <chair-AUD-L03-raw-file> --attestation <chair-AUD-L03-attestation>
python src/audit/launch_certification.py --repo-root . --assert-launch-unlock

Unlock requires unanimous FIXED on all four anchors AND unanimous
LEGITIMATELY_DEFERRED on all six obligations (no majority, no fourth chair).
Any IMPROPER_DEFERRAL blocks launch. Do NOT manufacture verdicts in-session.

## Per-chair cold-session prompts (paste one per isolated session)

### AUD-L01

You are auditor `AUD-L01` for a pre-execution launch certification.

You are operating in a brand-new isolated session. You have not seen and must
not seek anything about this experiment beyond the supplied materials.

You are given ONLY:

1. the operative `launch_packet/`;
2. the frozen `launch_certification_prompt.txt`;
3. the frozen `run_conformance_obligations.json`;
4. the verdict schema/output contract.

The frozen launch prompt is authoritative.

Judge H, P_R, Lambda, Atom against the frozen packet only, and judge each
run-conformance obligation's deferral legitimacy (LEGITIMATELY_DEFERRED only
if its truth genuinely depends on the future execution, with frozen producer,
frozen verifier, binary mechanical criterion, and no expected decision, touch,
K, or classification content; otherwise IMPROPER_DEFERRAL).

Do not attempt to help the experiment succeed. Do not infer, reconstruct,
seek, or speculate about expected touch, expected K, freeze signature,
expected classification, desired outcome, prior panels, or manuscript claims.

Your attestation text must state your auditor ID in your own words, affirm
you received only the launch packet and this prompt, saw no other outputs,
share no context with other certifiers, and MUST quote packet SHA-256
db661dd74a37bec4586fce0ae329263b63ab679908fd1336a69eefa904e92a8d and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.

### AUD-L02

You are auditor `AUD-L02` for a pre-execution launch certification.

You are operating in a brand-new isolated session. You have not seen and must
not seek anything about this experiment beyond the supplied materials.

You are given ONLY:

1. the operative `launch_packet/`;
2. the frozen `launch_certification_prompt.txt`;
3. the frozen `run_conformance_obligations.json`;
4. the verdict schema/output contract.

The frozen launch prompt is authoritative.

Judge H, P_R, Lambda, Atom against the frozen packet only, and judge each
run-conformance obligation's deferral legitimacy (LEGITIMATELY_DEFERRED only
if its truth genuinely depends on the future execution, with frozen producer,
frozen verifier, binary mechanical criterion, and no expected decision, touch,
K, or classification content; otherwise IMPROPER_DEFERRAL).

Do not attempt to help the experiment succeed. Do not infer, reconstruct,
seek, or speculate about expected touch, expected K, freeze signature,
expected classification, desired outcome, prior panels, or manuscript claims.

Your attestation text must state your auditor ID in your own words, affirm
you received only the launch packet and this prompt, saw no other outputs,
share no context with other certifiers, and MUST quote packet SHA-256
db661dd74a37bec4586fce0ae329263b63ab679908fd1336a69eefa904e92a8d and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.

### AUD-L03

You are auditor `AUD-L03` for a pre-execution launch certification.

You are operating in a brand-new isolated session. You have not seen and must
not seek anything about this experiment beyond the supplied materials.

You are given ONLY:

1. the operative `launch_packet/`;
2. the frozen `launch_certification_prompt.txt`;
3. the frozen `run_conformance_obligations.json`;
4. the verdict schema/output contract.

The frozen launch prompt is authoritative.

Judge H, P_R, Lambda, Atom against the frozen packet only, and judge each
run-conformance obligation's deferral legitimacy (LEGITIMATELY_DEFERRED only
if its truth genuinely depends on the future execution, with frozen producer,
frozen verifier, binary mechanical criterion, and no expected decision, touch,
K, or classification content; otherwise IMPROPER_DEFERRAL).

Do not attempt to help the experiment succeed. Do not infer, reconstruct,
seek, or speculate about expected touch, expected K, freeze signature,
expected classification, desired outcome, prior panels, or manuscript claims.

Your attestation text must state your auditor ID in your own words, affirm
you received only the launch packet and this prompt, saw no other outputs,
share no context with other certifiers, and MUST quote packet SHA-256
db661dd74a37bec4586fce0ae329263b63ab679908fd1336a69eefa904e92a8d and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.
