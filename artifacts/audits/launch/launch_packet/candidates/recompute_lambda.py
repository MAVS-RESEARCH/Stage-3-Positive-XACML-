"""Independent Lambda pre_hash recomputation (Amendment 004).

Packet-only verification that a lambda_manifest.json pre_hash follows from
its own components+exclusions under the documented canonicalization, plus
optional file-backed constituent verification against a packet directory.

Usage:
  recompute_lambda.py --manifest <lambda_manifest.json>
  recompute_lambda.py --manifest <m> --packet-dir <FINAL_BLIND_PACKET>

Exit 0 iff composite recomputes AND every verifiable constituent matches.
Constituents whose bytes are absent (engine full sources in older packets)
are reported SKIP with method, never silently passed.

Step console lines use the [P2:rec:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import sys


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:rec:FAIL] " + message, flush=True)
    sys.exit(code)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_composite(manifest):
    """Serialize components+exclusions per the frozen canonicalization."""
    # [P2-LOG-010] Step: canonicalize per reconstruction spec.
    return json.dumps({"components": manifest["components"],
                       "exclusions": manifest["exclusions"]},
                      sort_keys=True, ensure_ascii=True,
                      separators=(", ", ": ")).encode("utf-8")


def main(argv=None):
    """Entry point: recompute and optionally verify constituents."""
    # [P2-LOG-020] Step: recompute Lambda pre_hash.
    print("[P2:rec:020] recomputing Lambda pre_hash", flush=True)
    parser = argparse.ArgumentParser(description="Recompute Lambda hash.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--packet-dir", default="")
    args = parser.parse_args(argv)
    with open(args.manifest, encoding="utf-8") as handle:
        manifest = json.load(handle)
    composite = canonical_composite(manifest)
    recomputed = hashlib.sha256(composite).hexdigest()
    print("[P2:rec:022] canonical bytes=%d recomputed=%s" % (
        len(composite), recomputed[:16]), flush=True)
    if recomputed != manifest.get("pre_hash"):
        fail("composite mismatch: manifest=%s recomputed=%s" % (
            manifest.get("pre_hash"), recomputed))
    if not args.packet_dir:
        print("[P2:rec:024] composite ok (no packet dir given)", flush=True)
        return
    problems, skips = [], []
    comps = manifest["components"]

    def check(label, actual, expected):
        """Record a constituent mismatch."""
        if actual != expected:
            problems.append(label)

    def packet(*parts):
        """Join a packet-relative path."""
        return os.path.join(args.packet_dir, *parts)

    def verify_bytes(label, rel, expected):
        """Verify a packet file hash or record SKIP."""
        path = packet(*rel.split("/"))
        if not os.path.isfile(path):
            skips.append(label + ": bytes absent in packet")
            return
        check(label, sha256_file(path), expected)

    verify_bytes("policy_bytes", "corpus/fixture/policies/policy.xml",
                 comps["policy_bytes"]["sha256"])
    excls = manifest["exclusions"]
    verify_bytes("resolved_defaults",
                 "candidates/resolved_effective.json",
                 excls["resolved_defaults"]["sha256"])
    listing = "candidates/policy_dir_listing.json"
    if os.path.isfile(packet(listing)):
        check("policy_location", sha256_file(packet(listing)),
              excls["policy_location"]["sha256"])
    else:
        skips.append("policy_location: listing absent in packet")
    for rel, entry in comps.get("engine_semantic_set", {}).get(
            "files", {}).items():
        digest = entry.get("sha256") if isinstance(entry, dict) else entry
        verify_bytes("engine:" + rel,
                     "candidates/engine_sources/" + rel, digest)
    if not comps.get("engine_semantic_set", {}).get("files"):
        skips.append("engine_semantic_set: no file list in manifest")
    provider_path = packet("corpus", "fixture", "pdp.xml")
    if os.path.isfile(provider_path):
        from lxml import etree

        def _local(element):
            """Strip namespace from a tag."""
            tag = element.tag
            if isinstance(tag, str) and tag.startswith("{"):
                return tag.split("}", 1)[1]
            return tag

        root = etree.parse(provider_path).getroot()
        blob = b"".join(etree.tostring(element, method="c14n",
                                       exclusive=True)
                        for element in root
                        if _local(element) == "policyProvider")
        check("provider_element",
              hashlib.sha256(blob).hexdigest(),
              comps["provider_element"]["sha256"])
    else:
        skips.append("provider_element: pdp.xml absent in packet")
    remap = {}
    remap_path = packet("candidates", "path_remap.json")
    if os.path.isfile(remap_path):
        try:
            with open(remap_path, encoding="utf-8") as handle:
                remap = json.load(handle).get("mappings", {})
        except ValueError:
            problems.append("path_remap_unparseable")
    else:
        skips.append("path_remap: no remap in packet (built-artifact "
                     "checks skipped)")
    if remap:
        for group in ("drivers", "jars", "poms"):
            for entry in comps.get("built_artifacts", {}).get(
                    group, []):
                if not isinstance(entry, dict):
                    continue
                rel = entry.get("path", "")
                target = remap.get(rel, "")
                if not target:
                    skips.append("built:%s: no remap entry" % rel)
                    continue
                path = packet(*target.split("/"))
                if not os.path.isfile(path):
                    skips.append("built:%s: bytes absent in packet"
                                 % rel)
                    continue
                check("built:" + rel, sha256_file(path),
                      entry.get("sha256"))
                if "bytes" in entry and os.path.getsize(path) != \
                        entry.get("bytes"):
                    problems.append("built-bytes:" + rel)
        dep_rel = remap.get("dependency_hashes.json",
                            "candidates/dependency_hashes.json")
        dep_path = packet(*dep_rel.split("/"))
        if not os.path.isfile(dep_path):
            skips.append("dependency_hashes: bytes absent in packet")
        else:
            with open(dep_path, encoding="utf-8") as handle:
                try:
                    dep_doc = json.load(handle)
                except ValueError:
                    dep_doc = None
            if not isinstance(dep_doc, dict) or \
                    not isinstance(dep_doc.get("entries"), list) or \
                    not dep_doc.get("entries"):
                problems.append("dependency_hashes malformed")
            else:
                check("dependency_content",
                      sha256_file(dep_path),
                      comps.get("dependency_content", {}).get("sha256"))
                if len(dep_doc.get("entries", [])) != \
                        comps.get("dependency_content", {}).get("count"):
                    problems.append("dependency_content count")
                for dep_entry in dep_doc.get("entries", []):
                    digest = dep_entry.get("sha256", "")
                    if not isinstance(digest, str) or len(digest) != 64 \
                            or any(char not in "0123456789abcdef"
                                   for char in digest):
                        problems.append("dependency_hash malformed")
                        break
    for problem in sorted(set(problems)):
        print("[P2:rec:032] MISMATCH %s" % problem, flush=True)
    for skip in skips:
        print("[P2:rec:034] SKIP %s" % skip, flush=True)
    if problems:
        fail("constituent mismatches: %s" % problems)
    print("[P2:rec:036] all verifiable constituents match", flush=True)


if __name__ == "__main__":
    main()
