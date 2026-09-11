"""Phase-2 P_R relation builder for PC-XACML-S3+.

Builds the extensional certificate-representation relation record from
the frozen, adequacy-certified policy projection: two admitted histories
are P_R-equivalent iff all frozen designator results are extensionally
equal under standard Category/AttributeId/DataType/Issuer-aware matching
semantics. The relation object itself is constant across the repair
action; only presented histories change. Requires the adequacy
certificate verdict PASS. Output: derived/pr_relation.json. No E/R/A or
touch literals appear anywhere in this module.

Step console lines use the [P2:derpr:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:derpr:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


VOLATILE_KEYS = {"produced_utc", "sealed_utc", "probed_utc"}


def normalized_content_sha256(path):
    """Hash JSON content with volatile run-stamp keys removed."""
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
    """Entry point: build the P_R relation record."""
    # [P2-LOG-010] Step: start P_R build, gate on adequacy verdict.
    print("[P2:derpr:010] start P_R relation build", flush=True)
    if len(argv) != 4:
        fail("usage: derive_PR.py <projection.json> <adequacy.json> "
             "<out>")
    projection_path, adequacy_path, out_path = argv[1], argv[2], argv[3]
    with open(adequacy_path, "r", encoding="utf-8") as handle:
        adequacy = json.load(handle)
    if adequacy.get("verdict") != "PASS":
        fail("adequacy certificate is not PASS; P_R stays AMBIGUOUS")
    print("[P2:derpr:012] adequacy PASS, proceeding", flush=True)

    with open(projection_path, "r", encoding="utf-8") as handle:
        projection = json.load(handle)
    designators = projection["designators"]
    # [P2-LOG-020] Step: freeze the designator coordinate set.
    print("[P2:derpr:020] freezing %d designator coordinates"
          % len(designators), flush=True)
    coordinates = sorted(set(
        (d["category"], d["attribute_id"], d["data_type"], d["issuer"])
        for d in designators))
    record = {
        "relation_id": "PC-XACML-S3PLUS-v1-PR",
        "rule": ("histories h1, h2 are P_R-equivalent iff for every "
                 "frozen designator coordinate "
                 "(Category, AttributeId, DataType, Issuer) the named "
                 "attribute bags compare equal as sorted typed multisets "
                 "under XACML matching semantics"),
        "designator_coordinates": [
            {"category": c, "attribute_id": i, "data_type": t,
             "issuer": u} for (c, i, t, u) in coordinates],
        "projection_sha256": normalized_content_sha256(projection_path),
        "adequacy_ref": "policy_adequacy_certificate.json",
        "adequacy_sha256": normalized_content_sha256(adequacy_path),
        "constant_across_repair": True,
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-030] Step: P_R build complete.
    print("[P2:derpr:030] P_R relation build complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
