# NON_BLIND_HARDENING_REVIEW -- Wave-6 hunt sweep (developmental only)
# Full record of new material findings (all accepted as genuine; see R3-13..R3-19).

O-1 Canonicalization spec inconsistent: VOLATILE set 3 (check_anchor_completeness) vs 4 (repro_compare DROP/VOLATILE incl. checkpoint_sha256) vs HASHING_CONVENTIONS (4 keys) vs freeze_methodology ledger-drift note (claims timestamped-file drift, but normalized hashing strips timestamps so reruns are stable). Latent divergence; freeze seals two canonical forms as one. MEDIUM.
O-2 Ledger Lambda binds superseded opaque hash (bb2c in derived/anchor_ledger.json + derived/lambda_record.json) while operative is manifest pre_hash; refs mode never checks ledger-to-manifest binding. HIGH -- convergence would seal a ledger pointing at a superseded value.
O-3 Envelope Q/Succ+/c/A_Pi (+omega triple) self-attested FIXED, mechanically unchecked: omega fixture_response_sha256 taken from manifest without hashing live bytes; Q/c/A_Pi values copied from execution_inputs without integrity check; observed_triple parsed without binding to hashed response.xml; only envelope.response hash verified in refs. HIGH.
O-4 builder_reaches_pdp is a 3-token import-root heuristic: misses from-X imports of dangerous members, method calls without imports, __import__/getattr dispatch, os.system PDP spawn. MEDIUM.
O-5 Exclusive-C14N is a third hash kind: unpinned libxml2, unverified by refs mode; lxml==6.1.1 pin exists but excluded from scope; manifest deliberately excludes absolute PARENT_DIR URI making same-hash-across-paths vacuous for hermeticity. MEDIUM.
O-6 Empty-string vs null inconsistency + argv gap: builder permits "" coordinates; envelope rejects ""; census covers files only, never argv values; builder None-vs-"" conflation. (Split-verdict framing overblown; argv binding genuinely missing.)
O-7 Nits: repro_compare dead branch; supersession old_bytes pointer; pre_hash_lineage truncations; *-text vs MANIFEST CRLF note vs builder newline-insensitive substring checks.

Ledger spot-checks (4 refs resolve), scope as stated. No further new material objections beyond O-1..O-7.
