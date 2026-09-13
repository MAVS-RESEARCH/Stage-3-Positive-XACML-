# NON_BLIND_HARDENING_REVIEW -- Wave-2 Atom depth sweep (developmental only)

## NEW OBJECTIONS
W2-A01 C14N-mask concedes byte deltas without PDP-equivalence proof. 3 lexical deltas (decl quotes, utf-8 case, attr order/spacing); INV-05 runs in-memory pre-serialization, never on re-parsed bytes; c14n method unexported. Cat D, MAJOR. Close: C14N spec + canonical-bytes diff on re-parsed files + AuthzForce parse-invariance proof for those lexical classes.
W2-A02 Token/import scan too coarse. Scanned set absent from report; os/lxml/sys admit dangerous members; etree.parse without hardening flags; namespace-blind matching permits spoof; deepcopy semantics unevidenced. Cat D, MAJOR. Close: published token/AST lists + hardening + call-graph + deepcopy note.
W2-A03 PDP-output consumption IS construction input (MissingAttributeDetail triple determines inserts; content-conditioned gates). "No authorization logic" undefined. Cat A, BLOCKING under strict definition. Close: definition scoping Decision-computation vs coordinate-forwarding + proof forwarding steers only via admitted channel.
W2-A04 Ordering record asserts without proof (no argv corpus/log excerpts/chronology/test pointer); refusal opt-in; staging-vs-evaluation blur. Cat B/D, MAJOR. Close: sealed argv/log corpus + universal-flag proof + staging/evaluation definition.
W2-A05 fail()/refuse() + stdout are content-conditioned decisions/flows (guards map content to outcomes; MBP/INV encode expectations; stdout leaks PDP content to logs). Cat A, MAJOR (minor if liveness-only proven). Close: trigger table + unreachability proof + liveness argument + non-interference statement.
W2-A06 Checkpoint pair bounds two transactions + asymmetric paths (in-place vs staged copy differ in PARENT_DIR/glob/file set). Cat C, MAJOR. Close: per-world atomicity + counting clarification + staged-identity proof.

## ACCEPTED WAVE-1 CLOSURES (narrow terms)
A-01 presence, A-02 existence, A-03 sharpness, A-04 false-identity fix, A-05 coverage, A-06 documentation, A-07 mapping existence; residuals move to W2-A01..A06.
