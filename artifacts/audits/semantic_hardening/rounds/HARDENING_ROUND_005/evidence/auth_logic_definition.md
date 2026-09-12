# Authorization logic: definition for this experiment

"Authorization logic" means computation that determines, selects, or
steers an authorization DECISION (Permit/Deny/NotApplicable/
Indeterminate or its inputs beyond the admitted single-attribute
channel).

"Coordinate forwarding" means copying the missing-attribute
(Category, AttributeId, DataType) named by the frozen native
MissingAttributeDetail into the request constructor. Forwarding is
gated by MustBePresent cross-checks against the frozen policy.

The builder performs coordinate forwarding only: its outputs differ
from the frozen original solely by the admitted single-attribute
insertion (proven by unified diffs + residual C14N equality). It
cannot steer any Decision except through that channel, whose
authorization effect is exactly what P_R exclusivity governs. Liveness
guards (fail/exit on malformed frozen inputs) are unreachable on
admitted inputs and decide nothing.
