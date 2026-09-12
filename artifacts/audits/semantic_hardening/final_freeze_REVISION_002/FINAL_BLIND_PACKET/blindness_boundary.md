# Blindness boundary: inputs vs outcomes

World labels and world values (`x_permit` = "riddle me this") are
measurement INPUTS: the compiler cannot construct completed requests
without them, and they appear in `execution_inputs.json` by design.
An adjudicator who reads the frozen policy can infer which world the
policy favors. That inference is accepted and declared here.

Blindness constrains OUTCOME knowledge, never input knowledge: no
adjudicator input may contain expected touch, expected K/freeze
signature, expected classification, desired verdict, target-world
decisions, or manuscript claims. The packet, prompt, and schemas are
scanned for exactly these classes (see leakage machinery), not for
world values.

Therefore world-value visibility is NOT a blinding defect, and its
observation in any review is recorded but does not support any
anchor verdict in either direction.

Addendum (Wave-2): the MissingAttributeDetail feedback channel (native
response names the missing coordinate later used for construction) is
likewise native authorization behavior available to any PEP, not
leakage: the measured intervention openly uses it, and the blindness
constraint covers outcome decisions (never observed: 0 executions),
not the native request/response evidence both worlds share.
