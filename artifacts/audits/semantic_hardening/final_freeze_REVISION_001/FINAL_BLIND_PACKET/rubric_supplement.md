# Rubric supplement (procedure for evidence classes the base rubric omits)

1. Hash-only references are admissible ONLY with (a) the hashing method stated, (b) the input file list stated, and (c) the bytes present either in-packet or in the frozen repo at a pinned path. A bare hash with no method/inputs is not evidence.
2. Route-a/projection/builder gaps: check the packet manifest file list first; absence of a cited input fails the citing claim's blind verifiability (not necessarily its truth).
3. Locator resolution: stripped-text line numbers resolve ONLY via the verified locator map (evidence/locator_map_raw_html.json); raw-HTML numbers from any other numbering are unverified until re-checked.
4. Manifest check: recompute every listed file hash; corpus files must additionally match the frozen external seals.
5. Q/wrapper/adequacy handling: judge the construction rule against the builder bytes (now in-packet), the invocation flow record, and the input bindings -- never against counts alone.
6. Proponent verdict tokens (FIXED/VALID/PASS) inside candidates are claims, not evidence; judge the cited sources, not the tokens.
