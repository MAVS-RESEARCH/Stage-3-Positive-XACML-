"""Shared XACML request canonicalizer for PC-XACML-S3+ Phase 2.

Single canonicalization path for H/P_R/Lambda consumers: parses a
request file with the locked parser and returns exclusive-C14N bytes plus
the parsed tree. Drops nothing semantically: whitespace-only text nodes
are insignificant under XACML request semantics; ordering and formatting
are normalized by C14N.

Step console lines use the [P2:canon:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import os
import sys

from lxml import etree


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:canon:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def canonicalize_file(path):
    """Parse a request file and return (tree, c14n_bytes)."""
    # [P2-LOG-010] Step: parse and canonicalize one request file.
    print("[P2:canon:010] canonicalizing %s" % os.path.abspath(path),
          flush=True)
    if not os.path.isfile(path):
        fail("request file missing: " + path)
    try:
        tree = etree.parse(path)
    except etree.XMLSyntaxError as exc:
        fail("request XML syntax error in %s: %s" % (path, exc))
    root = tree.getroot()
    if localname(root) != "Request":
        fail("root element is not Request in " + path)
    data = etree.tostring(root, method="c14n", exclusive=True)
    print("[P2:canon:012] c14n bytes=%d" % len(data), flush=True)
    return tree, data


def main(argv):
    """Entry point: canonicalize files listed on the command line."""
    # [P2-LOG-020] Step: canonicalize CLI-provided files.
    print("[P2:canon:020] canonicalizer invoked", flush=True)
    if len(argv) < 2:
        fail("usage: canonicalize_request.py <request.xml> [...]")
    for path in argv[1:]:
        canonicalize_file(path)
    # [P2-LOG-030] Step: canonicalizer complete.
    print("[P2:canon:030] canonicalizer complete files=%d" % (len(argv) - 1),
          flush=True)


if __name__ == "__main__":
    main(sys.argv)
