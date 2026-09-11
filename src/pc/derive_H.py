"""Phase-2 H derivation for PC-XACML-S3+.

Builds the normalized authorization-admitted history objects
(H_initial, H_permit, H_nonpermit) as canonical multimaps keyed by
(Category, AttributeId, DataType, Issuer-or-null) with sorted typed
value bags. H is computed over the proven-equivalent source: derivation
refuses to run unless derived/h_equivalence_proof.json carries verdict
VALID. No E/R/A/touch literals appear anywhere in this module.

Step console lines use the [P2:derh:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from lxml import etree


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:derh:FAIL] " + message, flush=True)
    sys.exit(1)


def localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def canonical_h(request_path):
    """Build the canonical history multimap for one request file.

    Effective datatype follows XACML 3.0: Attribute/@DataType when
    present, else the (single, asserted uniform) AttributeValue datatype.
    """
    root = etree.parse(request_path).getroot()
    entries = []
    for container in root.iter():
        if localname(container) != "Attributes":
            continue
        category = container.get("Category")
        for attribute in container:
            if localname(attribute) != "Attribute":
                continue
            values = sorted(
                (child.text or "") for child in attribute
                if localname(child) == "AttributeValue")
            child_types = set(
                child.get("DataType") for child in attribute
                if localname(child) == "AttributeValue")
            declared = attribute.get("DataType")
            if declared is not None:
                effective = declared
            elif len(child_types) == 1:
                effective = child_types.pop()
            else:
                fail("ambiguous effective datatype in %s attribute %s"
                     % (request_path, attribute.get("AttributeId")))
            entries.append({
                "category": category,
                "attribute_id": attribute.get("AttributeId"),
                "data_type": effective,
                "issuer": attribute.get("Issuer"),
                "values": values,
            })
    entries.sort(key=lambda e: (e["category"] or "", e["attribute_id"] or "",
                                e["data_type"] or "", e["issuer"] or ""))
    return entries


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


VOLATILE_KEYS = {"produced_utc", "sealed_utc", "probed_utc"}


def normalized_content_sha256(path):
    """Hash JSON content with volatile run-stamp keys removed.

    Content-addressed cross-artifact reference: stable across reruns,
    unlike filesystem paths or timestamped file bytes.
    """
    with open(path, "r", encoding="utf-8") as handle:
        doc = json.load(handle)

    def strip(obj):
        if isinstance(obj, dict):
            return {k: strip(v) for k, v in obj.items()
                    if k not in VOLATILE_KEYS}
        if isinstance(obj, list):
            return [strip(v) for v in obj]
        return obj

    canonical = json.dumps(strip(doc), sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def main(argv):
    """Entry point: derive the three H objects."""
    # [P2-LOG-010] Step: start H derivation, gate on the proof verdict.
    print("[P2:derh:010] start H derivation", flush=True)
    if len(argv) != 7:
        fail("usage: derive_H.py <request.xml> <permit.xml> "
             "<nonpermit.xml> <h_equivalence_proof.json> <out-dir> "
             "<provenance-out>")
    (request_path, permit_path, nonpermit_path, proof_path,
     out_dir, provenance_path) = argv[1:7]
    with open(proof_path, "r", encoding="utf-8") as handle:
        proof = json.load(handle)
    if proof.get("verdict") != "VALID":
        fail("equivalence proof verdict is not VALID; H stays AMBIGUOUS")
    print("[P2:derh:012] equivalence proof VALID, proceeding", flush=True)

    os.makedirs(out_dir, exist_ok=True)
    written = {}
    # [P2-LOG-020] Step: derive H for the three checkpoints.
    print("[P2:derh:020] deriving H_initial/H_permit/H_nonpermit",
          flush=True)
    jobs = (("H_initial", request_path, "S0"),
            ("H_permit", permit_path, "S_permit"),
            ("H_nonpermit", nonpermit_path, "S_nonpermit"))
    for name, path, checkpoint in jobs:
        entries = canonical_h(path)
        record = {
            "history_id": "PC-XACML-S3PLUS-v1-%s" % name,
            "checkpoint": checkpoint,
            "source": {"request_file": os.path.relpath(path),
                       "sha256": sha256_file(path)},
            "proof": {"ref": "h_equivalence_proof.json",
                      "sha256": normalized_content_sha256(proof_path),
                      "verdict": "VALID"},
            "attributes": entries,
            "produced_utc": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
        }
        out_path = os.path.join(out_dir, "%s.json" % name)
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written[name] = normalized_content_sha256(out_path)
        # [P2-LOG-022] Step: per-checkpoint derivation confirmation.
        print("[P2:derh:022] wrote %s entries=%d"
              % (name, len(entries)), flush=True)

    provenance = {
        "provenance_id": "PC-XACML-S3PLUS-v1-H",
        "h_files": written,
        "proof": {"ref": "h_equivalence_proof.json",
                  "sha256": normalized_content_sha256(proof_path),
                  "verdict": "VALID"},
        "derivation_module": "src/pc/derive_H.py",
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(provenance_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(provenance, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P2-LOG-024] Step: H provenance record written.
    print("[P2:derh:024] provenance written", flush=True)

    # [P2-LOG-030] Step: H derivation complete.
    print("[P2:derh:030] H derivation complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
