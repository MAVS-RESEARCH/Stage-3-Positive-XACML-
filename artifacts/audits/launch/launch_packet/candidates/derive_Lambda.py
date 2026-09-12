"""Phase-2 Lambda (authority/admissibility) recorder for PC-XACML-S3+.

Canonicalizes the frozen authorization evaluation capability: root
policy identity, policy-provider configuration, enabled
attribute-provider set, request-preprocessor selection, and the admissible
native request interface. All components are read from the frozen
external configuration (never authored): provider/preprocessor facts are
extracted mechanically from pdp.xml child elements. Writes
derived/lambda_record.json with the pre-repair canonical hash and the
equality criterion the repair must satisfy (post == pre). No E/R/A or
touch literals appear anywhere in this module.

Step console lines use the [P2:derl:NNN] tag, each marked by a
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
    print("[P2:derl:FAIL] " + message, flush=True)
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


def sha256_bytes(data):
    """Return the hex SHA-256 digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


def main(argv):
    """Entry point: record the Lambda authority object."""
    # [P2-LOG-010] Step: start Lambda recording, echo arguments.
    print("[P2:derl:010] start Lambda recording", flush=True)
    if len(argv) != 5:
        fail("usage: derive_Lambda.py <pdp.xml> <policy.xml> "
             "<manifest.json> <out>")
    pdp_path, policy_path, manifest_path, out_path = (
        argv[1], argv[2], argv[3], argv[4])

    # [P2-LOG-020] Step: extract provider/preprocessor facts from pdp.xml.
    print("[P2:derl:020] extracting pdp.xml configuration facts", flush=True)
    try:
        pdp_root = etree.parse(pdp_path).getroot()
    except etree.XMLSyntaxError as exc:
        fail("pdp.xml syntax error: %s" % exc)
    children = [localname(e) for e in pdp_root]
    providers = [etree.tostring(e, method="c14n") for e in pdp_root
                 if localname(e) == "policyProvider"]
    attribute_providers = [localname(e) for e in pdp_root
                           if "ttributeProvider" in localname(e)]
    preprocessors = [localname(e) for e in pdp_root
                     if "reprocessor" in localname(e).lower()
                     or "Preprocessor" in localname(e)]
    print("[P2:derl:022] children=%s providers=%d attr_providers=%d "
          "preprocessors=%s" % (sorted(set(children)), len(providers),
                                len(attribute_providers), preprocessors),
          flush=True)

    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    sealed = manifest["authzforce"]["fixture_files"]
    live = {"pdp.xml": sha256_file(pdp_path),
            "policies/policy.xml": sha256_file(policy_path)}
    if (live["pdp.xml"] != sealed["pdp.xml"]["sha256"]
            or live["policies/policy.xml"]
            != sealed["policies/policy.xml"]["sha256"]):
        fail("authority artifacts differ from sealed manifest")
    # [P2-LOG-030] Step: sealed-identity confirmation.
    print("[P2:derl:030] authority artifacts match seal", flush=True)

    components = {
        "root_policy_sha256": live["policies/policy.xml"],
        "pdp_xml_sha256": live["pdp.xml"],
        "policy_provider_sha256": sha256_bytes(b"".join(providers)),
        "attribute_provider_set": attribute_providers,
        "request_preprocessor": (preprocessors if preprocessors
                                 else ["default-absent-in-pdp.xml"]),
        "native_request_interface": ("XACML request/response transaction "
                                     "(N1 data-flow)"),
    }
    canonical = json.dumps(components, sort_keys=True).encode("utf-8")
    record = {
        "lambda_id": "PC-XACML-S3PLUS-v1-Lambda",
        "components": components,
        "pre_hash": sha256_bytes(canonical),
        "post_hash": None,
        "equality_criterion": ("post_hash == pre_hash after "
                               "q_supply_missing_attribute; any "
                               "extensional change invalidates the "
                               "constant-Lambda design"),
        "produced_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-040] Step: Lambda recording complete.
    print("[P2:derl:040] Lambda pre_hash=%s" % record["pre_hash"],
          flush=True)


if __name__ == "__main__":
    main(sys.argv)
