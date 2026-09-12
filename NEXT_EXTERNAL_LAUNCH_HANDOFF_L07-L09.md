# NEXT EXTERNAL LAUNCH HANDOFF — LAUNCH REVISION 003, FRESH PANEL AUD-L07/08/09 (frozen inputs only)

Supersedes: L04–06 handoff (launch-002, panel AUD-L04/05/06: 0/3 valid ingest;
merits Lambda 2×PARTIAL + 1×FIXED with 3×IMPROPER_DEFERRAL from L06 on
dep-sha opacity, path remap, recompute subset, event-log/cp producers;
preserved as `artifacts/audits/launch/launch_packet_rev002/` +
`LAUNCH_FREEZE_rev002.json`; INVALID records retained under
`artifacts/audits/launch_certification/`). Do NOT reuse AUD-L01–L06.

Auditor IDs (fresh chairs, one isolated session each): AUD-L07, AUD-L08, AUD-L09.
Operative launch packet path: artifacts/audits/launch/launch_packet/
Operative launch packet SHA-256: 8e23901d4643a42a4748af8894c0439f19f071f736d23225ea906aac97099ce6
Operative prompt path: artifacts/audits/launch/launch_certification_prompt.txt
Operative prompt SHA-256: 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865
Operative registry path: artifacts/audits/launch/run_conformance_obligations.json
Operative registry SHA-256: d7641f64ced4092a23e7e75dcb26f00f5fa274f27ca3171b2d39792e6fe7e44a
Launch freeze record: artifacts/audits/launch/LAUNCH_FREEZE.json
(launch-003, supersedes launch-002; staged Lambda pre_hash
194fcbbecc398f718d4b172133db3825f40648f73d62e31d1fae658bd50f4ed3)
Protocol: PROTOCOL_AMENDMENT_007.md (§§0–19 operative).

What changed vs launch-002 (operator context, NOT chair material — chairs
judge launch-003 only, prior panel outputs must NOT be shown): dependency
binding is now sha256 of the staged file (reproduce with sha256sum);
frozen path_remap.json maps manifest paths to packet paths; recompute
verifies drivers/jars/poms/deps via remap; staged manifest carries
builder_lineage; run_authzforce emits a JSONL chronology (names+utc+
request-sha, zero response bytes); verify_deployment_set has a frozen
--hash-cp mode; RC-ATOM-ORDER/RC-DEPS-CONSISTENT/RC-REQUEST point at the
real producers with invocation-instant scoping.

Verdict schema: embedded in the prompt (verdict JSON: verdict_id, auditor_id,
qualification COLD_MODEL_INDEPENDENT, per-anchor verdicts H/P_R/Lambda/Atom
with locators, per-obligation deferrals LEGITIMATELY_DEFERRED /
IMPROPER_DEFERRAL / UNSUPPORTED, attestation_hash, verbatim declaration,
prompt/packet hashes, isolation flags) plus a separate attestation text file.
Attestation MUST name its auditor ID AND quote the packet SHA-256 AND the
prompt SHA-256 above (revision binding; attestations without both hashes are
INVALID and will be refused at ingest). Attestation must name NO other
auditor ID (cross-reads are INVALID).

## Cold-session instructions

1. Open a brand-new empty session per chair; never reuse a session across chairs.
2. Give the chair ONLY: the launch packet folder, the prompt file bytes, the
   registry file bytes, and the schema above. Nothing else. Never show prior
   panel outputs, reassessment records, or this handoff's history paragraph.
3. Tell the chair its auditor ID and demand exactly two artifacts: the verdict
   JSON and the separate attestation text, with attestation_hash = sha256 of
   the attestation EXACT bytes. Collect chair FILES directly (never retype or
   reformat — past transcription corrupted two attestation hashes).
4. Never mention other chairs, prior results, CYCLE_001/CYCLE_002, expected
   touch/K/classification, manuscript claims, or any expectation about the outcome.

## Ingestion commands (operator runs after collecting outputs)

python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L07 --raw <chair-AUD-L07-raw-file> --attestation <chair-AUD-L07-attestation>
python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L08 --raw <chair-AUD-L08-raw-file> --attestation <chair-AUD-L08-attestation>
python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L09 --raw <chair-AUD-L09-raw-file> --attestation <chair-AUD-L09-attestation>
python src/audit/launch_certification.py --repo-root . --assert-launch-unlock

Unlock requires unanimous FIXED on all four anchors AND unanimous
LEGITIMATELY_DEFERRED on all six obligations (no majority, no fourth chair).
Any IMPROPER_DEFERRAL blocks launch. Do NOT manufacture verdicts in-session.

## Per-chair cold-session prompts (paste one per isolated session)

### AUD-L07

You are auditor `AUD-L07` for a pre-execution launch certification.

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
share no context with other certifiers, name no other auditor, and MUST quote
packet SHA-256
8e23901d4643a42a4748af8894c0439f19f071f736d23225ea906aac97099ce6 and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.

### AUD-L08

You are auditor `AUD-L08` for a pre-execution launch certification.

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
share no context with other certifiers, name no other auditor, and MUST quote
packet SHA-256
8e23901d4643a42a4748af8894c0439f19f071f736d23225ea906aac97099ce6 and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.

### AUD-L09

You are auditor `AUD-L09` for a pre-execution launch certification.

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
share no context with other certifiers, name no other auditor, and MUST quote
packet SHA-256
8e23901d4643a42a4748af8894c0439f19f071f736d23225ea906aac97099ce6 and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.
