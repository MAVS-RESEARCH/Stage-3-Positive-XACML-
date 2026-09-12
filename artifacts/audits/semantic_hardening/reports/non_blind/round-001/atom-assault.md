# NON_BLIND_HARDENING_REVIEW -- Atom assault, Wave 1, HARDENING_ROUND_001 input
# Role: Atom / native transaction + wrapper boundary. Developmental only.

## DEV verdicts
NATIVE PART DEV-ACCEPT (narrow): PEP->handler->PDP->response with N1 locators externally specified, separable. WRAPPER PART DEV-INSUFFICIENT: counts+hashes only, no bytes/diff/source-hash/AST/call-order evidence; rule underspecified vs code.

## Objections (anchor=Atom)
1. Counts+hashes cannot prove single-Attribute addition (namespace/ordering/whitespace/CombinedDecision could change). Verified +1 Attribute logically by reading the three files, but packet stores no bytes/diff; derive_atom checks counts+distinctness only, never residual equality. Category C. BLOCKING.
2. "Byte-identical copy" is FALSE: decl quotes, Request attr order, self-closing style differ (pretty_print re-serialization); builder's own c14n check masks these deltas and is not exported. Category C. BLOCKING.
3. No-auth-logic claim is verdict-strings-only: no builder SHA, import list, hit list, AST/call inventory in packet. Substring scan misses eval/exec/__import__/getattr/compile/XSLT; os/sys/lxml permit file/exit/XML transforms; fail() branches are content-conditioned denial. Category D. BLOCKING.
4. Builder-to-PDP coupling unscanned (no Calls/transitive-deps/call-graph); no argv/log proving build preceded completed runs; ordering flag exists in code but uncited in packet. Category D/F. MAJOR.
5. Builder CONSUMES native PDP MissingAttributeDetail output (triple=read_missing_detail) + policy cross-check; rule text omits this flow; no response/policy/argv binding in packet. Category B/F. MAJOR.
6. Rule underspecified vs code surplus (IncludeInResult=false, AttributeValue DataType, append-last, namespace derivation, MBP gate, INV asserts, shorthand Category vs full URI). No rule-phrase->code-line map. Category E. MAJOR.

## Repairs (evidence/representation only)
Embed: repaired bytes (or unified byte diff + c14n diff) with decl/attr-order/whitespace disposition; exported INV-05 boolean + c14n hashes; original/permit/nonpermit/c14n sha fields. Embed: builder sha256, actual import_roots, full Call inventory via ast.walk, empty foreign/hits, AST dump hash; coupling statement + run logs showing no completed run before build. Embed: response/policy sha + build argv + order log; amend rule copy to state MissingAttributeDetail+MBP sourcing with line pointers. Embed: rule-phrase->code-lines table + execution_inputs hash + builder hash.

## Falsifiers
In-packet bytes/diffs + residual-equality proof; byte-diff with zero non-insert deltas (or amended rule allowing re-serialization deltas with c14n proof); embedded source hash + complete import/call inventory + empty hits; call-graph + logs proving builder never invokes evaluation and completed runs post-date builds; hashed input bindings + corrected rule copy; line-level rule-to-code map with no surplus semantics.
