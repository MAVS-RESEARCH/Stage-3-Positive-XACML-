"""Locator-table tests (Amendment 004).

The verified section table rebuilds deterministically from frozen HTML
bytes; all 13 sections resolve with token-verified quotes; method and
source encoding recorded. No PDP, no expected results.
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))

import hardening_evidence as hev  # noqa: E402


class _ns:
    """Minimal argparse-namespace stand-in."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_locator_table_resolves(tmp_path):
    """All 13 sections resolve against frozen HTML bytes."""
    # [P2-LOG-L10] Test step: assert locator table resolution.
    print("[P2:test:locator:010] locator table", flush=True)
    out = str(tmp_path / "locator_verified_table.json")
    hev.cmd_locator_table(_ns(
        html=os.path.join(REPO_ROOT, "external", "xacml",
                          "xacml-3.0-core-spec-cos01-en.html"),
        repo_root=REPO_ROOT, out=out))
    with open(out, encoding="utf-8") as handle:
        doc = json.load(handle)
    assert len(doc["sections"]) == 13
    assert all(entry["quote_verified"]
               for entry in doc["sections"].values())
    assert doc["html_sha256"] == (
        "8da7d21f72d1813d1f6db0620ee6840ff0687da69cce8bdf075d5ecad592eefb")


def test_locator_table_deterministic(tmp_path):
    """Two builds are byte-identical modulo produced_utc."""
    # [P2-LOG-L12] Test step: assert locator determinism.
    print("[P2:test:locator:012] locator determinism", flush=True)
    outs = [str(tmp_path / ("t%d.json" % index)) for index in (0, 1)]
    for out in outs:
        hev.cmd_locator_table(_ns(
            html=os.path.join(REPO_ROOT, "external", "xacml",
                              "xacml-3.0-core-spec-cos01-en.html"),
            repo_root=REPO_ROOT, out=out))
    docs = []
    for out in outs:
        with open(out, encoding="utf-8") as handle:
            doc = json.load(handle)
        doc.pop("produced_utc", None)
        docs.append(doc)
    assert docs[0] == docs[1]
