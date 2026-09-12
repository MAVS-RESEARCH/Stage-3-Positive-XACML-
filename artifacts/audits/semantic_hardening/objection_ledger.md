# Objection ledger (PC-XACML-S3PLUS-v1-objections)

| id | round | anchor | cat | status | objection |
|---|---|---|---|---|---|
| H-01 | HARDENING_ROUND_000 | H | A | RESOLVED | Resolved PDP-visible request context may exceed raw request XML (handler MAY add attributes; environment values SHALL be supplied; conversion outside spec scope |
| H-02 | HARDENING_ROUND_000 | H | B | RESOLVED | Repaired request XML bytes absent from sealed packet; hash-only references cannot prove byte-identical-except-one-insertion or value identity through the handle |
| H-03 | HARDENING_ROUND_000 | H | A | RESOLVED | Issuer-or-null H keying conflicts with Issuer-absent wildcard matching: context Issuer variations the designator ignores would still distinguish H entries. |
| H-04 | HARDENING_ROUND_000 | H | C | RESOLVED | Canonicalization scope undetermined: empty environment element, IncludeInResult flags, and whitespace/order normalization allow source-consistent H variants. |
| P_R-01 | HARDENING_ROUND_000 | P_R | A | RESOLVED | Strict bag-identity is finer than Match-result equivalence (duplicates, extra non-matching values, Issuer pooling); sorted-multiset canonicalization is experime |
| P_R-02 | HARDENING_ROUND_000 | P_R | B | RESOLVED | Exclusivity (only these coordinates matter) depends on selector/Content/provider probes absent from the sealed packet. |
| L-01 | HARDENING_ROUND_000 | Lambda | C | RESOLVED | Capability boundary vague: narrow (policy+provider) vs broad (handler/normalization/environment/defaults) scopes both source-consistent; no extensional iff-rule |
| L-02 | HARDENING_ROUND_000 | Lambda | D | RESOLVED | Hash scope opaque: provider hash and preprocessor default-absent entries have no packet source files; hash derivation method absent. |
| L-03 | HARDENING_ROUND_000 | Lambda | C | RESOLVED | post_hash null makes the constant-Lambda equality criterion untestable pre-repair. |
| L-04 | HARDENING_ROUND_000 | Lambda | A | RESOLVED | Environment/time machinery (handler SHALL supply date/time; implicit PIP/defaults) may vary capability across repairs. |
| A-01 | HARDENING_ROUND_000 | Atom | B | RESOLVED | Wrapper evidence insufficient: repaired request bytes and builder source absent; hashes/counts cannot prove byte-identical-except-one-insertion. |
| A-02 | HARDENING_ROUND_000 | Atom | D | RESOLVED | No-authorization-logic claim unverifiable from packet: no AST/import scan artifacts, no invocation-flow record. |
| A-03 | HARDENING_ROUND_000 | Atom | C | RESOLVED | Construction rule is experiment-authored; native vs wrapper decomposition needs sharper external grounding. |
| G-01 | HARDENING_ROUND_000 | GLOBAL | B | RESOLVED | Packet completeness gaps: route_a probe, repaired requests, full projection, builder source referenced by records but absent as files. |
| G-02 | HARDENING_ROUND_000 | GLOBAL | E | RESOLVED | Seal/hash hygiene (EOL desync, config-dependent hashing) threatened reproducibility. |
| H-05 | HARDENING_ROUND_001 | H | D | RESOLVED | XML-bytes to AuthzForce Request parse fidelity unevidenced: whitespace/anyURI normalization and (child.text or '') ungrounded. |
| H-06 | HARDENING_ROUND_001 | H | B | RESOLVED | Route-A exhaustiveness gap: no enumerated public-API list; MissingAttributeDetail as partial resolved-context observation unacknowledged; route_a_unavailable ov |
| H-07 | HARDENING_ROUND_001 | H | C | RESOLVED | Absent-MustBePresent-true conflated with empty bag in H_initial (key omission); evaluation treats it as Indeterminate, not empty. |
| H-08 | HARDENING_ROUND_001 | H | C | RESOLVED | Empty environment Attributes container dropped from H_initial with no empty-vs-absent marker. |
| P_R-03 | HARDENING_ROUND_001 | P_R | D | RESOLVED | Error-vs-empty conflation: rule has no Indeterminate token though all designators are MustBePresent=true; P_R(missing,missing) undecided. |
| P_R-04 | HARDENING_ROUND_001 | P_R | B | RESOLVED | Glob expansion unbounded: ${PARENT_DIR}/policies/*.xml never resolved to a sealed file list; second policy file would widen designators silently. |
| P_R-05 | HARDENING_ROUND_001 | P_R | B | RESOLVED | Channel inventory lossy: obligations_advice/match_functions/rule_combining collected but unasserted; pdp check top-level names only. |
| P_R-06 | HARDENING_ROUND_001 | P_R | B | RESOLVED | 5-to-4 designator dedup (action-id x2) unexplained in evidence. |
| L-05 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Resolved-effective-config absent: XPath/std registries, strictIssuer, depths, cache, verbosity defaults uncaptured. |
| L-06 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | attribute_provider_set [] asserts disabled std-env default without schema/JAXB evidence; default is enabled. |
| L-07 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Preprocessor sentinel misses the true default adapter chain (default-lax + result postprocessor + flag wiring). |
| L-08 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Glob/PARENT_DIR binding, ordering, multi-root ambiguity, ignoreOldVersions unpinned. |
| L-09 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Version/build/extension identity absent (capability == code). |
| L-10 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Env override flags and evaluation timestamp source undetermined. |
| L-11 | HARDENING_ROUND_001 | Lambda | D | RESOLVED | post comparator design absent: null cannot be compared; no predicate, tolerance, or failure action. |
| A-04 | HARDENING_ROUND_001 | Atom | D | RESOLVED | Byte-identity claim false: pretty_print re-serialization changes declaration quotes, attribute order, empty-element style; builder c14n check masks these deltas |
| A-05 | HARDENING_ROUND_001 | Atom | D | RESOLVED | No-auth-logic scan incomplete: substring tokens miss eval/exec/__import__/getattr/compile/XSLT; os/sys/lxml permit file/exit/XML transforms; fail() branches are |
| A-06 | HARDENING_ROUND_001 | Atom | D | RESOLVED | Builder-to-PDP coupling unscanned (no Calls/transitive/call graph); response/policy consumption flow undocumented; no argv/log proving build preceded completed  |
| A-07 | HARDENING_ROUND_001 | Atom | B | RESOLVED | Construction rule underspecified vs code surplus (IncludeInResult, datatypes, append position, namespace derivation, MBP gate, INV asserts); no rule-phrase to c |
| G-03 | HARDENING_ROUND_001 | GLOBAL | B | RESOLVED | Stripped-text N1 locators unresolvable from packet bytes (raw HTML lines differ; index admits convenience-only). |
| G-04 | HARDENING_ROUND_001 | GLOBAL | D | RESOLVED | Rubric lacks procedures for hash-only evidence, route-a/projection/builder gaps, locator resolution, manifest check, Q/wrapper/adequacy handling. |
| G-05 | HARDENING_ROUND_001 | GLOBAL | E | RESOLVED | Proponent verdict tokens embedded as candidate bytes risk use as self-evidence. |
| G-06 | HARDENING_ROUND_001 | GLOBAL | E | RESOLVED | Repo-path references absent in packet layout; ledger-vs-derived hash drift unexplained. |
| G-07 | HARDENING_ROUND_001 | GLOBAL | C | RESOLVED | Cross-anchor consistency: handler triple-counted across H/Lambda/Atom; envelope/flags owned by none; Issuer jointly ungrounded; Lambda post==pre vs Atom pre/pos |
| G-08 | HARDENING_ROUND_001 | GLOBAL | C | RESOLVED | World labels+values disclose intended mapping via policy literal (naming-level hint, not numeric expectation). |
| R2H-01 | HARDENING_ROUND_001 | H | A | RESOLVED | Env-validation path: OPTIONAL helper validates present env values (syntax-error Indeterminate); census must cover repaired bytes and builder category pin. |
| R2H-02 | HARDENING_ROUND_001 | H | C | RESOLVED | Wall-clock latent state excluded from hash without pinned timestamp-source/UTC record. |
| R2H-03 | HARDENING_ROUND_001 | H | D | RESOLVED | (child.text or '') verbatim fiction vs N4 lexical parsing; empty/whitespace/multi-node/datatype-conflict cases unevidenced. |
| R2H-04 | HARDENING_ROUND_001 | H | B | RESOLVED | Content/repeated-Category dropped without census over all three request bytes. |
| R2H-05 | HARDENING_ROUND_001 | H | C | RESOLVED | Issuer '' vs absent census missing; N4 null-vs-'' handling uncited; strictIssuer flag outside hashed components. |
| R2H-06 | HARDENING_ROUND_001 | Lambda | D | RESOLVED | Manifest recorded-but-unhashed: resolved flags, dir listing, ignoreOldVersions, custom providers, std override. |
| R2H-07 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | PARENT_DIR path-dependence: absolute URI machine-dependent; glob ordering/multi-root unevidenced. |
| R2H-08 | HARDENING_ROUND_001 | Lambda | D | RESOLVED | Deferral promissory (no sealed comparator/abort demo); version under-pinned (no jar/xsd/extension/JVM pins). |
| R2A-01 | HARDENING_ROUND_001 | Atom | D | RESOLVED | C14N-mask concedes byte deltas without PDP-equivalence proof; INV-05 runs pre-serialization, never on re-parsed bytes. |
| R2A-02 | HARDENING_ROUND_001 | Atom | D | RESOLVED | Token/import scan too coarse: scanned set unpublished; os/sys/lxml admit dangerous members; parse flags absent; deepcopy semantics unevidenced. |
| R2A-03 | HARDENING_ROUND_001 | Atom | A | RESOLVED | PDP-output consumption IS construction input (Detail triple determines inserts); 'no authorization logic' undefined. |
| R2A-04 | HARDENING_ROUND_001 | Atom | B | RESOLVED | Ordering record asserts without argv/log corpus; refusal opt-in; staging-vs-evaluation blur. |
| R2A-05 | HARDENING_ROUND_001 | Atom | A | RESOLVED | fail()/refuse() + stdout are content-conditioned decisions/flows; MBP/INV gates encode expectations. |
| R2A-06 | HARDENING_ROUND_001 | Atom | C | RESOLVED | Checkpoint pair bounds two transactions + asymmetric fixture paths (in-place vs staged copy). |
| R2G-01 | HARDENING_ROUND_001 | P_R | B | RESOLVED | Match-vector P_R admits decision-based and world-indexed completions surviving the match table. |
| R2G-02 | HARDENING_ROUND_001 | P_R | A | RESOLVED | Indexed Indeterminate + Detail ordering: two missing-different histories equivalent under r1, distinct under indexed reading. |
| R2G-03 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Manifest excludes clock/build/interface that are capability; version at source not jar; timestamp excluded. |
| R2G-04 | HARDENING_ROUND_001 | Lambda | C | RESOLVED | Preprocessor/handler normalization excluded though defining bytes-to-bags fidelity. |
| R2G-05 | HARDENING_ROUND_001 | H | A | RESOLVED | Partial-multimap+side-lists vs total error-function; empty container as key vs list both fit r1. |
| R2G-06 | HARDENING_ROUND_001 | Atom | C | RESOLVED | Checkpoint placement/construction-inside-outside underdetermined; two-transaction interval may not close as one Atom. |
| R2G-07 | HARDENING_ROUND_001 | GLOBAL | C | RESOLVED | Boundary allocation triple-counts handler; envelope/flags/timestamps movable across H/Lambda/Atom preserving all censuses. |
| R2H-09 | HARDENING_ROUND_001 | H | D | RESOLVED | N4 text-to-bag conversion loop uncited; factory normalization for admitted shapes unevidenced. |
| R2H-10 | HARDENING_ROUND_001 | Lambda | D | RESOLVED | Manifest hashes descriptors not content: same triple plus rebuilt/mutated jar or wiring yields same pre_hash. |
| R2H-11 | HARDENING_ROUND_001 | Lambda | D | RESOLVED | Comparator demo records exit code only: no transcript of inputs, expected/actual hashes, stdout, or abort token. |
| R2A-07 | HARDENING_ROUND_001 | Atom | D | RESOLVED | C14N-equality is not PDP-equivalence: no N4/JAXB parse of written bytes; INV-05 runs pre-serialization. ADDITIONALLY (found by evidence tooling during ROUND_001 |
| R2A-08 | HARDENING_ROUND_001 | Atom | B | RESOLVED | Chronology proves vacuous precedence, not enforcement: no argv/log corpus; refusal opt-in; staging blur unresolved. |
| R2G-08 | HARDENING_ROUND_001 | GLOBAL | C | RESOLVED | Cost-reallocation alternative: wrapper as zero-cost envelope preparation re-partitions touch/K with identical Decisions. |
| R3-01 | HARDENING_ROUND_002 | H | D | RESOLVED | N4 text-to-bag conversion for admitted shapes unevidenced by census alone; engine parse proof required. |
| R3-02 | HARDENING_ROUND_002 | Lambda | D | RESOLVED | Manifest binds descriptor identity, not engine source content; same triple plus rebuilt jar yields same pre_hash. |
| R3-03 | HARDENING_ROUND_002 | Lambda | D | RESOLVED | Comparator demo records exit code only; transcript of inputs, expected/actual hashes, stdout, abort token required. |
| R3-04 | HARDENING_ROUND_002 | Atom | B | RESOLVED | Invocation-site map lacks script hashes/excerpts; refusal opt-in unproven universal; staging blur. |
| R3-05 | HARDENING_ROUND_002 | Atom | D | RESOLVED | Rule-to-code map omits surplus lines (IncludeInResult, namespace, append position, value DataType). |
| R3-06 | HARDENING_ROUND_002 | GLOBAL | C | RESOLVED | Cost-reallocation rejection lacks prereg paths/hashes. |
| R3-07 | HARDENING_ROUND_002 | Atom | D | RESOLVED | C14N-equality is not PDP-equivalence without engine parse of written bytes. |
| R3-08 | HARDENING_ROUND_002 | GLOBAL | C | RESOLVED | Match table world_rows disclose per-world Match outcomes (outcome-adjacent). |
| R3-09 | HARDENING_ROUND_002 | GLOBAL | E | RESOLVED | Cross-artifact hash references lack stated conventions and mechanical verification; backslash paths unhygienic. |
| R3-10 | HARDENING_ROUND_002 | GLOBAL | E | RESOLVED | Builder fix supersedes sealed request bytes; chain undocumented. |
| R3-11 | HARDENING_ROUND_002 | GLOBAL | D | RESOLVED | Envelope records overclaim (A_Pi N-class, omega locators, Q/Succ+/c scope). |
| R3-12 | HARDENING_ROUND_002 | Lambda | D | RESOLVED | Multiple pre_hash values floating (bb2c/0577/b679/cac0) without lineage record. |
| R3-13 | HARDENING_ROUND_002 | GLOBAL | E | RESOLVED | VOLATILE strip sets differ across modules; drift story in freeze_methodology inaccurate (timestamps are stripped). |
| R3-14 | HARDENING_ROUND_002 | Lambda | D | RESOLVED | Ledger Lambda binds superseded opaque hash; refs mode blind to ledger-to-manifest drift. |
| R3-15 | HARDENING_ROUND_002 | GLOBAL | D | RESOLVED | Envelope Q/Succ+/c/A_Pi/omega FIXED self-attested without mechanical cross-checks. |
| R3-16 | HARDENING_ROUND_002 | Atom | D | RESOLVED | builder_reaches_pdp import-root heuristic misses from-imports, method calls, getattr dispatch, os.system spawn. |
| R3-17 | HARDENING_ROUND_002 | GLOBAL | E | RESOLVED | C14N third hash kind unpinned/unverified; libxml2 scope excluded without record. |
| R3-18 | HARDENING_ROUND_002 | GLOBAL | D | RESOLVED | Empty-vs-null edge and argv value binding unproven (builder permits empty; census covers files only). |
| R3-19 | HARDENING_ROUND_002 | GLOBAL | E | RESOLVED | Nits bundle: repro_compare dead branch; supersession old-side pointers; lineage truncation honesty; newline semantics. |
| H3-01 | HARDENING_ROUND_003 | Lambda | E | RESOLVED | Deployed root-policy-set cardinality unpinned: extra *.xml under frozen glob changes authority with all hashes passing; builder accepts arbitrary out_dir (self- |
| H3-02 | HARDENING_ROUND_003 | GLOBAL | E | RESOLVED | In-packet builder cross-reference false: wrapper_evidence.builder_sha256 (live) != sha256(packet builder_source.py) (stale pre-guard copy). |
| P2D-01 | HARDENING_ROUND_004 | Lambda | E | RESOLVED | Deployment gate canon weaker than builder guard (trailing-space bypass); staged copies never verified pre-evaluation. |
| P2D-02 | HARDENING_ROUND_004 | GLOBAL | E | RESOLVED | No mechanical binding between built request world values and preregistered worlds. |
| P2D-03 | HARDENING_ROUND_004 | Lambda | E | RESOLVED | Lambda envelope not independently reconstructible: engine bytes/method absent, canonical form underspecified, capability set incomplete. |
| P2D-04 | HARDENING_ROUND_004 | GLOBAL | E | RESOLVED | Locator provenance unrecorded; staging evidence prose-only; freeze/panel machinery cannot span revisions. |
| P2D-05 | HARDENING_ROUND_005 | GLOBAL | E | RESOLVED | Wave-2 re-attack finds: recompute engine-dict mismatch; gate UNC/root-listing gaps; staged-root extras missed; C01-C03 reusable post-refreeze; freeze revision/v |
| P2D-06 | HARDENING_ROUND_006 | Lambda | E | RESOLVED | Runtime classpath composition (extension path, test-classes content, driver path) and staged TOCTOU window unpinned by any hash or gate. |

Full records (evidence, dispositions) live in the JSON ledger; this table is a finding aid only.
