NON_BLIND_CERTIFIER_EMULATION — REHEARSAL_SWEEP_004 — REVISION_002
Emulator 2 (Atom/staging). Contaminated, never blind. No prior sweep seen.

Byte verifications PASS: packet builder copy == live bytes (f732a08a, 278 lines); evidence hash == packet file; all manifest/input/corpus/listing hashes match live; listing count==1 accurate.
Listing count==1 enforced in gate check() (count/name-set/subdir/modified refusals), not in doc.
Disjointness enforced pre-create + post-create in builder + independent gate exit-2; live derived/requests disjoint; stage_completed_fixture never writes into policies/.
Remaining: (a) caller-supplied policy_path redefines policies_dir (trust in frozen scripts); (b) TOCTOU swap in same-process window; (c) manual operator copy (caught by --check). None material here.
Atom verdict: FIXED-emulation (native emission proven; wrapper byte-evidenced; counting definitional per blindness boundary; staging gated).
