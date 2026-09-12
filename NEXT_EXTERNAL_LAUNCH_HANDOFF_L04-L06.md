# NEXT EXTERNAL LAUNCH HANDOFF — LAUNCH REVISION 002, FRESH PANEL AUD-L04/05/06 (frozen inputs only)

Supersedes: `NEXT_EXTERNAL_LAUNCH_HANDOFF.md` (launch-001, panel AUD-L01/02/03:
0/3 valid ingest; merits Lambda 3×PARTIAL on packet-internal driver/pom gaps;
preserved as `artifacts/audits/launch/launch_packet_rev001/` +
`LAUNCH_FREEZE_rev001.json`; INVALID records retained under
`artifacts/audits/launch_certification/`). Do NOT reuse AUD-L01/02/03.

Auditor IDs (fresh chairs, one isolated session each): AUD-L04, AUD-L05, AUD-L06.
Operative launch packet path: artifacts/audits/launch/launch_packet/
Operative launch packet SHA-256: a75ee3b0506de98ea34d925d92c0240d001d685f6be8ed206d3f13787f1e1777
Operative prompt path: artifacts/audits/launch/launch_certification_prompt.txt
Operative prompt SHA-256: 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865
Operative registry path: artifacts/audits/launch/run_conformance_obligations.json
Operative registry SHA-256: 12a46820dca3434a6d993d6801c52e4df24d02602e6391a263df03e98910a837
Launch freeze record: artifacts/audits/launch/LAUNCH_FREEZE.json
(launch-002, supersedes launch-001; staged Lambda pre_hash
5ecdd192cc606fcc1fdc901c8390c31ba22ec20935f39f1522c6d7867bae1dbd)
Protocol: PROTOCOL_AMENDMENT_007.md (§§0–19 operative).

What changed vs launch-001 (chairs judge launch-002 only; history below is
operator context, NOT chair material): packet manifest drivers rebound to
staged bytes with recomputed composite; root + pdp-engine poms under distinct
names; 145-jar transitive dependency content hashes staged and bound;
derive_Lambda/parse_response/launcher sources staged with 11-copy currency
gate; freeze code pinned in execution_code. Prior panel outputs must NOT be
shown to this panel.

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
   the attestation exact bytes. Collect chair files directly (never retype).
4. Never mention other chairs, prior results, CYCLE_001/CYCLE_002, expected
   touch/K/classification, manuscript claims, or any expectation about the outcome.

## Ingestion commands (operator runs after collecting outputs)

python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L04 --raw <chair-AUD-L04-raw-file> --attestation <chair-AUD-L04-attestation>
python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L05 --raw <chair-AUD-L05-raw-file> --attestation <chair-AUD-L05-attestation>
python src/audit/launch_certification.py --repo-root . --ingest-launch --auditor AUD-L06 --raw <chair-AUD-L06-raw-file> --attestation <chair-AUD-L06-attestation>
python src/audit/launch_certification.py --repo-root . --assert-launch-unlock

Unlock requires unanimous FIXED on all four anchors AND unanimous
LEGITIMATELY_DEFERRED on all six obligations (no majority, no fourth chair).
Any IMPROPER_DEFERRAL blocks launch. Do NOT manufacture verdicts in-session.

## Per-chair cold-session prompts (paste one per isolated session)

### AUD-L04

You are auditor `AUD-L04` for a pre-execution launch certification.

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
a75ee3b0506de98ea34d925d92c0240d001d685f6be8ed206d3f13787f1e1777 and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.

### AUD-L05

You are auditor `AUD-L05` for a pre-execution launch certification.

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
a75ee3b0506de98ea34d925d92c0240d001d685f6be8ed206d3f13787f1e1777 and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.

### AUD-L06

You are auditor `AUD-L06` for a pre-execution launch certification.

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
a75ee3b0506de98ea34d925d92c0240d001d685f6be8ed206d3f13787f1e1777 and prompt
SHA-256 251f7e5875b243a24d0fe95b3252ecfdf08e06f97fbc254e0ed45ea3cb4c7865.
