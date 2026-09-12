NON_BLIND_ADVERSARIAL_REVIEW — REHEARSAL_SWEEP_001 — REVISION_001
Panel B packet/provenance/locator specialist. Contaminated, never blind.

Passes: forward-slash paths; repaired bytes match live; live inputs match wrapper hashes; corpus bytes match manifest; 50-file manifest with blob+sha.

O1 packet-verify path stale: repro_compare packet_verify hardcodes blind_anchor_packet, not the freeze packet.
O2 refs gap: refs_verify never opens freeze-packet candidates; packet-internal refs stated not mechanically checked.
O3 locator path contradiction: supplement requires evidence/locator_map_raw_html.json; packet carries candidates/locator_map.json per locator_index_final.
O4 locator map method: heading-presence method unnamed, no sha/inputs in-packet; stripped-lines only, no raw-HTML offsets.
O5 volatile/normalization: DROP/VOLATILE 4 keys vs methodology ledger-only note; created/sealed/retrieved/produced stamps uncovered; packet_verify exact-SHA brittle.
O6 hash-only refs: policy_location/resolved_defaults equal packet file hashes not directory/derivation bytes; canonical spec without worked bytes; n4 manifest zero hashes.
