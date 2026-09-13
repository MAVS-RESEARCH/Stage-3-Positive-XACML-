# PATH ALIASES CORRIGENDUM (packet revision 003)

Two pre-revision-003 records use stale paths. The bytes are identical;
only the names below resolve inside the final blind packet.

| Stale reference | Operative packet path |
|---|---|
| `evidence/locator_map_raw_html.json` (rubric_supplement R3) | `candidates/locator_map.json` (per `locator_index_final.md`) |
| `evidence/*.json` pointers (atom_record evidence_pointers, h_r1/pr_r1 basis) | `candidates/<same basename>` |
| `HARDENING_ROUND_001/evidence/*` (ledger basis strings) | `candidates/*` in-packet; round evidence retained in repo |

`locator_verified_table.json` supersedes stripped-line provenance: legacy
stripped numbers came from an unrecorded extraction (disclosed); the table
re-grounds all 13 sections in frozen HTML bytes with a re-runnable method.
