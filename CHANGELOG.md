# CHANGELOG

All notable changes to this experiment package. Post-preregistration changes to worlds, target, action interface, cost, anchor definitions, freeze order, expected signature, or success criteria require a new experiment version (`PC-XACML-S3PLUS-v2`, ...), not an unmarked patch.

## [Unreleased] — Phase 1 (planning)

- 2026-09-11: Repository created (`LICENSE` only).
- 2026-09-11: Added `WorkPlan.md` (6-phase plan) and `Path.md` (implementation trail). Docs bootstrap; no code, no execution results.
- 2026-09-11: WorkPlan audit hardening rounds 1–6 applied (spec-hash identity protocol, Phase 2B blinded adjudication, H-equivalence proof, P_R adequacy certificate, proven-Atom rule, completion-space closure certificate, sealed canary expectations, `execution_inputs.json` split, completed-execution ordering, environment pin, failure-seal path). Planning changes only; no prereg artifact existed yet, so no experiment-version change.

## [Phase 1] — 2026-09-11 — SOURCE LOCK AND NATIVE REPRODUCTION: PASS

- Locked AuthzForce `release-21.2.0` at `3cc0e988e1639da48184434cd5c918102ff5b499` (HEAD verified, tree clean); 4/4 fixture blob SHAs match; local SHA-256 manifest written.
- Froze OASIS XACML 3.0 core HTML (1257025 bytes; dynamic server content observed across retrievals, frozen copy authoritative).
- Sealed authoritative `IMPLEMENTATION_SPEC.md` (raw + LF-normalized SHA-256) and `prereg/` hashes.
- Built pinned PDP modules from source (Maven, JDK 21); compiled `PdpRunner` driver.
- Constructed both completed requests (INV-05/INV-06 asserted, unexecuted).
- Original fixture reproduces natively: Indeterminate/missing-attribute, semantic match.
- 11/11 Phase-1 tests pass; 10/10 gate boxes PASS. Bugs found by stress testing and fixed: destructive INV-05 assertion, manifest `verified_head` gap, prereg-hash test parser bug (see `Path.md` §4).
- Instantiation note: primary environment is the Windows 11 host + PowerShell (`run_phase1.ps1` authoritative, `.sh` twin); WSL2 was unavailable. No scientific content affected.

## [Phase 2] - 2026-09-11 - 2A COMPLETE, 2B PACKET SEALED, ADJUDICATION PENDING (BLOCKED, not failed)

- 2A extraction complete: 5-designator projection (canary exact), adequacy PASS (no selectors/XPath/references/providers), route (a) unavailable by javap probe + sequencing guard, route (b) equivalence VALID (4 rows), H x3, P_R relation, Lambda pre-hash, Atom NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER (pending 2B), ledger 9/9 FIXED with four PENDING_2B.
- Blind packet sealed (20 files, redaction-clean, corpus byte-identical); no qualifying human verdict exists, so `--assert-unlock` refuses (exit 4), the target audit stays locked, and zero completed-world PDP evaluations occurred.
- Content-addressed cross-artifact references (timestamps excluded from reference hashes); reproduce mode verifies derivations + ledger + packet (all match).
- Bugs found and fixed: DataType read from Attribute instead of AttributeValue (None coordinates), destructive-test path in synthetic verdict dirs, packet manifest backslash keys, adequacy manifest ordering, scanner false-positive methodology (verified via Python, not PowerShell matching).
- Status: BLOCKED_PENDING_ADJUDICATION. Unblocks on delivery of a qualifying independent blind verdict (AUD-XXX, never shown the expectations) via `--seal-verdict`, then rerun unlocks the target audit.
