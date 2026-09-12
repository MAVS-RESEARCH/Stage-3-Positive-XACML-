"""Phase-1 semantic response comparison for PC-XACML-S3+.

Compares an actual PDP response against the frozen expected response by
canonical XACML semantics (Decision, StatusCode, MissingAttributeDetail
triple), ignoring whitespace and formatting. Writes a comparison record.

Step console lines use the [P1:cmp:NNN] tag, each marked by a
[P1-LOG-NNN] comment for Path.md citation.
"""

import json
import os
import sys

from lxml import etree


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P1-LOG-900] Fail-closed termination marker for every abort path.
    print("[P1:cmp:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def find_first(root, name):
    """Return the first descendant with the given local name or None."""
    for element in root.iter():
        if localname(element) == name:
            return element
    return None


def extract_semantics(path):
    """Extract (decision, status_code, missing_detail) from a response."""
    tree = etree.parse(path)
    root = tree.getroot()
    decision_node = find_first(root, "Decision")
    if decision_node is None or decision_node.text is None:
        fail("no Decision in " + path)
    decision = decision_node.text.strip()
    status_node = find_first(root, "StatusCode")
    status = status_node.get("Value") if status_node is not None else None
    detail_node = find_first(root, "MissingAttributeDetail")
    if detail_node is None:
        detail = None
    else:
        detail = {"AttributeId": detail_node.get("AttributeId"),
                  "Category": detail_node.get("Category"),
                  "DataType": detail_node.get("DataType")}
    return decision, status, detail


def main(argv):
    """Entry point: compare actual vs expected PDP responses."""
    # [P1-LOG-010] Step: start comparison, echo resolved arguments.
    print("[P1:cmp:010] start response comparison", flush=True)
    if len(argv) != 4:
        fail("usage: parse_response.py <actual.xml> <expected.xml> "
             "<out.json>")
    actual_path, expected_path, out_path = argv[1], argv[2], argv[3]
    print("[P1:cmp:012] actual=%s expected=%s"
          % (os.path.abspath(actual_path), os.path.abspath(expected_path)),
          flush=True)
    quarantined = any("target_" in os.path.basename(path).lower()
                      for path in (actual_path, expected_path))
    if not quarantined:
        # Content-bound allowlist (rename-evasion fix): pre-pass, any
        # file that is not byte-identical to a frozen original is
        # treated as quarantined. Frozen originals are the recorded
        # actual response and the fixture expected response.
        import hashlib as _hl
        repo_probe = os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".."))
        frozen = [os.path.join(repo_probe, "artifacts", "raw",
                               "original_response_actual.xml"),
                  os.path.join(repo_probe, "external", "authzforce",
                               "fixture", "response.xml")]
        allowed = set()
        for path in frozen:
            try:
                with open(path, "rb") as handle:
                    allowed.add(_hl.sha256(handle.read()).hexdigest())
            except OSError:
                continue
        for path in (actual_path, expected_path):
            try:
                with open(path, "rb") as handle:
                    digest = _hl.sha256(handle.read()).hexdigest()
            except OSError:
                digest = ""
            if digest not in allowed:
                quarantined = True
                break
    if quarantined:
        # [P1-LOG-014] Step: target-outcome gate (Amendment 007).
        # Quarantined target responses open only after a recorded
        # RUN_CONFORMANCE_PASSED verdict. Both argv positions are
        # gated (B02 fix); basename-substring match replaces the
        # prefix-only check (B01 partial). Rename-evasion by copying
        # quarantined bytes to a non-target_ name remains a known
        # limitation: full content-bound allowlist binds at launch
        # freeze via quarantined response hashes (see launch packet
        # quarantine manifest). No parser bypass exists short of that.
        repo_root = os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".."))
        gate_path = os.path.join(repo_root, "artifacts", "audits", "launch",
                                 "RUN_CONFORMANCE_PASS.json")
        try:
            with open(gate_path, encoding="utf-8") as handle:
                gate = json.load(handle)
        except (OSError, ValueError):
            gate = {}
        if gate.get("verdict") != "RUN_CONFORMANCE_PASSED":
            fail("target outcome quarantined until conformance passes")

    # [P1-LOG-020] Step: extract actual semantics.
    print("[P1:cmp:020] extracting actual semantics", flush=True)
    actual = extract_semantics(actual_path)
    print("[P1:cmp:022] actual decision=%s status=%s"
          % (actual[0], actual[1]), flush=True)

    # [P1-LOG-030] Step: extract expected semantics.
    print("[P1:cmp:030] extracting expected semantics", flush=True)
    expected = extract_semantics(expected_path)
    print("[P1:cmp:032] expected decision=%s status=%s"
          % (expected[0], expected[1]), flush=True)

    match = list(actual) == list(expected)
    # [P1-LOG-040] Step: write comparison record.
    print("[P1:cmp:040] semantic_match=%s" % match, flush=True)
    record = {"decision_actual": actual[0],
              "decision_expected": expected[0],
              "status_actual": actual[1],
              "status_expected": expected[1],
              "missing_detail_actual": actual[2],
              "missing_detail_expected": expected[2],
              "semantic_match": match}
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P1-LOG-050] Step: comparison complete.
    print("[P1:cmp:050] comparison complete", flush=True)
    if not match:
        fail("semantic mismatch between actual and expected responses")


if __name__ == "__main__":
    main(sys.argv)
