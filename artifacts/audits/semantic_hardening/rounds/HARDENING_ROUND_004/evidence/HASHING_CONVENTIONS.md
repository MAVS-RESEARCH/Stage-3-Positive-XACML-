# Hashing conventions (normative for cross-artifact references)

## Volatile-key set (single, used everywhere)

`{produced_utc, sealed_utc, probed_utc, checkpoint_sha256}`. The same
set applies in derivation modules, the ledger checker, and the
reproduce comparator. Timestamps carry zero evidential weight by
construction: they are run records only. Event ordering across runs is
established by the git commit sequence and seal records, never by file
clocks (unpinned system clock; backdating undetectable and therefore
unrelied-upon).

## Hash kinds

1. `raw-sha256:<hex>` -- SHA-256 over exact file bytes. Used for frozen
   external artifacts and committed run outputs.
2. `normalized-json-sha256:<hex>` -- SHA-256 over canonical JSON
   (`sort_keys=True`, default separators, UTF-8, ASCII-only content,
   no floats) after removing volatile keys. Used for cross-references
   between derived/provenance JSON files.
3. `c14n-sha256:<hex>` -- SHA-256 over W3C exclusive C14N bytes (no
   comments) produced by pinned lxml 6.1.1 (libxml2 as bundled; see
   toolchain exclusion below). Used for XML element/subtree identity
   (provider element, request documents). Recomputable by parsing the
   cited file and serializing with the stated method.

## Text-scan rule

Substring/scanner checks read text with universal newlines, so they
are newline-insensitive by construction. Hashes always cover raw
bytes, so CRLF/LF differences change digests honestly. The two
mechanisms never substitute for each other.

## Toolchain exclusion

`jvm_toolchain` and `xml_toolchain` (lxml spec above; stdlib difflib
for text diffs) are pinned in the environment record and excluded from
capability hashes with explicit reason (execution substrate, not
authorization capability). Absolute PARENT_DIR URIs are likewise
excluded as machine-dependent; hermeticity rests on the relative
layout rule plus the single-file listing, both hashed.

A reference is verifiable iff recomputation by the stated method over
the stated file yields the stated digest (see `scripts/repro_compare.py`
refs mode, which covers H/proof, checkpoints, PR refs, ledger-md,
lambda pre_hash, wrapper inputs, engine sources, match/envelope refs).
