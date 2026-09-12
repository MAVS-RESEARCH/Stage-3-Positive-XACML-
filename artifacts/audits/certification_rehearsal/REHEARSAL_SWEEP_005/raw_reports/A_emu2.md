NON_BLIND_CERTIFIER_EMULATION — REHEARSAL_SWEEP_005 — REVISION_002
Emulator 2 (Lambda/Atom staging). Contaminated, never blind. No prior sweep seen.

Seals confirm (prompt/packet/freeze/manifest + corpus fixture hashes all match).
1. Builder currency CONFIRM: live == packet == evidence f732a08a.
2. Listing accuracy CONFIRM: live single policy.xml 3630 bytes matches; repaired hashes match; no pollution.
3. Guard pre/post-create CONFIRM (lines 42-56, 221, 265); 12/12 phrases; disjoint live.
4. Disjointness CONFIRM live + pre-eval gates in run scripts; residual gate-to-PDP window noted.
Remaining: (a) cardinality TOCTOU (extra xml passes content hashes; deferral rechecks pre_hash not glob); (b) argv policy_path trust (frozen scripts pass fixture policy); (c) staging asymmetry (original uses fixture in place).
Lambda=PARTIAL (constancy/cardinality closure needs (a)(b) + gate source in packet). Atom=PARTIAL (inherits staging; live clean, wrapper reviewable; blind FIXED overstates).
