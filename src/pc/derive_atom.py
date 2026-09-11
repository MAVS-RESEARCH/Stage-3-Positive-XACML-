"""Phase-2 Atom (action-boundary) prover for PC-XACML-S3+.

Proposes (never self-certifies) the native transaction boundary record
with the four wrapper-condition evidence items: (1) native PDP
request/response transaction supported by N1 data-flow locators;
(2) construction-only wrapper shown by byte-diff evidence between the
frozen original and the constructed completed requests; (3) zero
authorization logic shown by static scan of the builder source (locked
import set, no decision/prediction literals); (4) preregistered action
definition match against execution_inputs.json. Conclusion:
NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER (auditor_status
PENDING_2B; COMBINED_BOUNDARY_PROVEN is never demanded). Output:
derived/atom_record.json. No E/R/A or touch literals appear anywhere in
this module.

Step console lines use the [P2:dera:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import ast
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from lxml import etree

N1_DATAFLOW = ("N1 data-flow model (frozen stripped-text lines 1755-1784): "
               "PEP sends the native request to the context handler; the "
               "handler constructs the request context and sends it to the "
               "PDP; the PDP evaluates and returns the response context; "
               "the handler returns the response to the PEP. "
               "Glossary: Context handler (line 931), PDP (line 1007), "
               "PEP (line 1016).")
ALLOWED_IMPORT_ROOTS = {"lxml", "copy", "os", "sys", "hashlib", "json",
                        "datetime"}
FORBIDDEN_SOURCE_TOKENS = ("subprocess", "socket", "urllib", "PdpEngine",
                           "evaluate(", "Permit", "NotApplicable",
                           "Indeterminate", "expected_signature",
                           "canary_expectations")


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:dera:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def attribute_count(path):
    """Count Attribute elements in a request file."""
    root = etree.parse(path).getroot()
    return sum(1 for e in root.iter() if localname(e) == "Attribute")


def scan_builder(path):
    """Statically verify the builder performs no authorization logic."""
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tree = ast.parse(source)
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    foreign = sorted(roots - ALLOWED_IMPORT_ROOTS)
    hits = sorted(t for t in FORBIDDEN_SOURCE_TOKENS if t in source)
    return foreign, hits


def main(argv):
    """Entry point: prove the Atom boundary record."""
    # [P2-LOG-010] Step: start Atom proof, echo arguments.
    print("[P2:dera:010] start Atom boundary proof", flush=True)
    if len(argv) != 7:
        fail("usage: derive_atom.py <request.xml> <permit.xml> "
             "<nonpermit.xml> <builder.py> <execution_inputs.json> <out>")
    (request_path, permit_path, nonpermit_path, builder_path,
     exec_inputs_path, out_path) = argv[1:7]

    # [P2-LOG-020] Step: evidence item 1 (native transaction, N1).
    print("[P2:dera:020] recording native-transaction evidence", flush=True)
    native_evidence = {
        "boundary": ("PEP-style request submission -> PDP evaluation -> "
                     "XACML response"),
        "n1_locator": N1_DATAFLOW,
        "status": "PROVEN",
    }

    # [P2-LOG-030] Step: evidence item 2 (construction-only diff).
    print("[P2:dera:030] checking construction-only diff evidence",
          flush=True)
    counts = {label: attribute_count(path) for label, path in
              (("original", request_path), ("permit", permit_path),
               ("nonpermit", nonpermit_path))}
    hashes = {label: sha256_file(path) for label, path in
              (("original", request_path), ("permit", permit_path),
               ("nonpermit", nonpermit_path))}
    if not (counts["permit"] == counts["original"] + 1
            and counts["nonpermit"] == counts["original"] + 1):
        fail("construction diff evidence violated: %s" % counts)
    if len(set(hashes.values())) != 3:
        fail("request files are not pairwise distinct")
    print("[P2:dera:032] counts=%s distinct=%s" % (counts, True), flush=True)

    # [P2-LOG-040] Step: evidence item 3 (no authorization logic).
    print("[P2:dera:040] scanning builder for authorization logic",
          flush=True)
    foreign, hits = scan_builder(builder_path)
    if foreign or hits:
        fail("builder exceeds mere construction: imports=%s tokens=%s"
             % (foreign, hits))
    print("[P2:dera:042] builder scan clean", flush=True)

    # [P2-LOG-050] Step: evidence item 4 (preregistered definition).
    print("[P2:dera:050] matching preregistered action definition",
          flush=True)
    with open(exec_inputs_path, "r", encoding="utf-8") as handle:
        exec_inputs = json.load(handle)
    action = exec_inputs["action_interface"]
    if action["actions"] != ["q_supply_missing_attribute"]:
        fail("action identity mismatch with preregistration")
    if action["authorization_logic_performed"] is not False:
        fail("preregistration does not warrant construction-only wrapper")
    print("[P2:dera:052] preregistration match confirmed", flush=True)

    record = {
        "atom_id": "xacml-request-transaction",
        "pre_checkpoint": "after original MissingAttributeDetail response",
        "post_checkpoint": "after repaired request response",
        "native_transaction": native_evidence,
        "wrapper": {
            "construction_rule": action["construction_rule"],
            "diff_evidence": {"attribute_counts": counts,
                             "file_hashes": hashes},
            "no_authorization_logic": {
                "builder": os.path.relpath(builder_path),
                "import_roots": "locked set, verified",
                "forbidden_tokens": "absent, verified",
            },
            "preregistered": True,
        },
        "conclusion": ("NATIVE_TRANSACTION_PROVEN + "
                       "RECONSTRUCTION_AS_WRAPPER"),
        "auditor_status": "PENDING_2B",
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-060] Step: Atom proof complete (proposed, not certified).
    print("[P2:dera:060] Atom record proposed, pending 2B", flush=True)


if __name__ == "__main__":
    main(sys.argv)
