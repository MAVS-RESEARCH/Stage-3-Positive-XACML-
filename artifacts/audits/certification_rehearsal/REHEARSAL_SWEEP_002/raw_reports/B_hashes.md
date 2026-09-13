NON_BLIND_ADVERSARIAL_REVIEW — REHEARSAL_SWEEP_002 — REVISION_001
Panel B hash recomputation (all digests recomputed from live bytes). Contaminated, never blind. No prior sweep seen.

(a) Corpus fixtures PASS: request 8c733c46, response f78d839f, pdp 2c3ceab0, policy 8475166c, HTML 8da7d21f — match packet corpus manifest + live external manifest + wrapper input hashes; upstream blob SHAs verified via clone ls-tree.
(b) Repaired requests PASS: permit 3f8eedb7 and nonpermit b4077e77 match live derived files + wrapper hashes + H source hashes. Nonmaterial: filename mapping implicit.
(c) Lambda pre_hash PASS content (3e8cf8ff recomputes under sorted-keys JSON): NONMATERIAL method gap (separators/ensure_ascii undocumented; compact forms differ).
(d) PACKET_MANIFEST PASS: all 48 entries match packet file bytes.
(e) Anchor checkpoints PASS: H_initial fa9e4079, H_permit a5c98a5d, H_nonpermit f7c38508 match normalized recomputation.
(f) MATERIAL CONTENT MISMATCH (1): wrapper_evidence builder_sha256 033c84fd != sha256(packet builder_source.py) 1fb45c57. Claimed hash equals LIVE builder (guard lines added post-freeze); packet ships stale copy; manifest self-consistent on stale bytes; all 11 rule_to_code snippets still present. Provenance/identity claim broken; semantics unaffected.
