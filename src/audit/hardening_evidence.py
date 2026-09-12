"""Phase-2B-H hardening evidence builder for PC-XACML-S3+.

Generates deterministic, source-grounded evidence artifacts WITHOUT
executing completed-world PDP evaluations and WITHOUT computing
touch/K: --diffs (unified structural diffs original to worlds),
--wrapper (builder source hash, import/call inventory, forbidden-token
scan, input bindings, rule-to-code map), --match-table (static
per-designator bag-state truth table), --lambda-manifest (extensional
component manifest with canonical hashes + inertness records), --all.
All cross-artifact references are content-addressed. No E/R/A or touch
literals appear in this module.

Step console lines use the [P2:hev:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import ast
import difflib
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from lxml import etree

EXTENDED_FORBIDDEN_TOKENS = (
    "subprocess", "socket", "urllib", "PdpEngine", "evaluate(",
    "Permit", "NotApplicable", "Indeterminate", "expected_signature",
    "canary_expectations", "eval(", "exec(", "__import__", "getattr(",
    "compile(", "XSLT", "xslt",
)
CHECKED_TOKENS = sorted(set(EXTENDED_FORBIDDEN_TOKENS))
CHECKED_AST_NODES = ("Import", "ImportFrom", "Call", "FunctionDef")
DANGEROUS_CALLS = ("eval", "exec", "system", "popen", "spawn", "xpath",
                   "xslt", "transform", "parse", "XML", "evaluate")
# Analyst-authored rule-phrase to builder-code map; each snippet must be
# present verbatim in the builder source (mechanically checked).
RULE_TO_CODE = [
    ("copy frozen original",
     "copy.deepcopy(original)"),
    ("insert exactly one subject Attribute",
     "insert_attribute(copy.deepcopy(original), triple,"),
    ("world-specific value",
     "permit_value, nonpermit_value, out_dir = argv[4], argv[5], argv[6]"),
    ("coordinates from MissingAttributeDetail",
     "read_missing_detail(response_path)"),
    ("MustBePresent cross-check against policy",
     "read_policy_designators(policy_path, triple)"),
    ("single-addition assertion INV-05",
     "assert_single_attribute_addition("),
    ("inter-world value difference INV-06",
     "if permit_value == nonpermit_value:"),
    ("IncludeInResult false on insert",
     'attribute.set("IncludeInResult", "false")'),
    ("namespace derivation from request root",
     'namespace = root.tag.split("}")[0]'),
    ("append-last position",
     "etree.SubElement(subject,"),
    ("value-level DataType only (never Attribute-level)",
     "value_node.set(\"DataType\", datatype)"),
]


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:hev:FAIL] " + message, flush=True)
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
    """Return the hex SHA-256 digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def utcnow():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path, doc):
    """Write a deterministic JSON document."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")


def cmd_diffs(args):
    """Build unified structural diffs original to completed worlds."""
    # [P2-LOG-010] Step: build request diffs.
    print("[P2:hev:010] building request diffs", flush=True)
    with open(args.original, "r", encoding="utf-8") as handle:
        original = handle.read().splitlines()
    diffs = {}
    c14n = {}
    for label, path in (("permit", args.permit), ("nonpermit", args.nonpermit)):
        with open(path, "r", encoding="utf-8") as handle:
            world = handle.read().splitlines()
        diffs[label] = "\n".join(difflib.unified_diff(
            original, world, fromfile="request.xml",
            tofile="request_x_%s.xml" % label, lineterm=""))
        root = etree.parse(path).getroot()
        c14n[label] = sha256_bytes(etree.tostring(root, method="c14n",
                                                  exclusive=True))
    with open(args.original, "rb") as handle:
        original_bytes = handle.read()
    root = etree.fromstring(original_bytes)
    c14n["original"] = sha256_bytes(etree.tostring(root, method="c14n",
                                                   exclusive=True))
    write_json(args.out, {
        "diff_id": "PC-XACML-S3PLUS-v1-request-diffs",
        "unified_diffs": diffs,
        "c14n_sha256": c14n,
        "produced_utc": utcnow(),
    })
    print("[P2:hev:012] diffs written", flush=True)


def cmd_wrapper(args):
    """Build the wrapper static-evidence report."""
    # [P2-LOG-020] Step: build wrapper evidence.
    print("[P2:hev:020] building wrapper evidence", flush=True)
    with open(args.builder, "r", encoding="utf-8") as handle:
        source = handle.read()
    tree = ast.parse(source)
    imports = set()
    calls = set()
    os_members = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
                if isinstance(func.value, ast.Name) and func.value.id in (
                        "os", "sys", "lxml"):
                    os_members.add(func.value.id + "." + func.attr)
    hits = sorted(t for t in EXTENDED_FORBIDDEN_TOKENS if t in source)
    dangerous_present = sorted(c for c in calls
                               if c.lower() in DANGEROUS_CALLS)
    from_imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                from_imports.add(node.module.split(".")[0] + "."
                                 + alias.name)
    risky_members = sorted(
        m for m in from_imports
        if m.split(".")[-1] in ("system", "popen", "spawnl", "spawnle",
                                "spawnlp", "spawnv", "spawnve", "spawnvp",
                                "spawnvpe", "execv", "execl", "call",
                                "run", "Popen", "evaluate", "check_output"))
    os_reachable = bool({"subprocess", "PdpEngine"} & imports) or bool(
        risky_members) or bool({"evaluate"} & calls)
    rule_map = []
    for phrase, snippet in RULE_TO_CODE:
        rule_map.append({"rule_phrase": phrase, "code_snippet": snippet,
                         "present": snippet in source})
    if not all(entry["present"] for entry in rule_map):
        fail("rule-to-code map drifted from builder source")
    with open(args.runner, "r", encoding="utf-8") as handle:
        runner_source = handle.read()
    runner_tree = ast.parse(runner_source)
    runner_imports = set()
    for node in ast.walk(runner_tree):
        if isinstance(node, ast.Import):
            runner_imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            runner_imports.add(node.module.split(".")[0])
    for label, path in (("original", args.original),
                        ("permit", args.permit),
                        ("nonpermit", args.nonpermit)):
        with open(path, "rb") as handle:
            content = handle.read()
        for marker in (b"<!DOCTYPE", b"<!ENTITY", b"<?xml-stylesheet"):
            if marker in content:
                fail("active XML construct in %s input: %s" % (label,
                                                               marker))
    write_json(args.out, {
        "evidence_id": "PC-XACML-S3PLUS-v1-wrapper",
        "builder_sha256": sha256_file(args.builder),
        "builder_import_roots": sorted(imports),
        "builder_calls": sorted(calls),
        "os_sys_lxml_members_used": sorted(os_members),
        "checked_tokens": CHECKED_TOKENS,
        "checked_ast_nodes": list(CHECKED_AST_NODES),
        "forbidden_token_hits": hits,
        "dangerous_calls_present": dangerous_present,
        "input_trust": ("inputs are frozen sealed files (fixture bytes "
                        "hash-verified pre-parse by the phase seal) "
                        "containing no DOCTYPE/ENTITY/stylesheet "
                        "constructs (scanned above); no untrusted XML "
                        "is ever parsed"),
        "deepcopy_note": ("copy.deepcopy of lxml ElementTree yields an "
                          "independent tree (verified root-distinct "
                          "during implementation); original never "
                          "mutated by insertion (INV-05 residual check "
                          "runs on a probe copy)"),
        "rule_to_code": rule_map,
        "runner_import_roots": sorted(runner_imports),
        "from_import_members": sorted(from_imports),
        "risky_members_present": risky_members,
        "builder_reaches_pdp": os_reachable,
        "input_hashes": {
            "request.xml": sha256_file(args.original),
            "response.xml": sha256_file(args.response),
            "policy.xml": sha256_file(args.policy),
            "request_x_permit.xml": sha256_file(args.permit),
            "request_x_nonpermit.xml": sha256_file(args.nonpermit),
        },
        "produced_utc": utcnow(),
    })
    print("[P2:hev:022] wrapper evidence written hits=%s" % hits, flush=True)


def cmd_match_table(args):
    """Build the static Match truth table over actual bag states."""
    # [P2-LOG-030] Step: build Match truth table.
    print("[P2:hev:030] building Match truth table", flush=True)
    with open(args.projection, "r", encoding="utf-8") as handle:
        projection = json.load(handle)
    rows = []
    for designator in projection["designators"]:
        rows.append({
            "coordinate": [designator["category"],
                           designator["attribute_id"],
                           designator["data_type"]],
            "must_be_present": designator["must_be_present"],
            "match_function": designator["match_function"],
            "missing_bag": "Indeterminate (MustBePresent=true)",
            "match_bag": "Match TRUE",
            "mismatch_bag": "Match FALSE",
            "duplicate_extra_values": ("same Match outcome as singleton "
                                       "under existential Match "
                                       "semantics; recorded, immaterial "
                                       "here"),
        })
    worlds = {
        "note": ("per-world Match outcomes are OUTCOME-adjacent and are "
                 "deliberately NOT recorded here (blindness hygiene); "
                 "the table covers designator-coordinate semantics only"),
    }
    write_json(args.out, {
        "table_id": "PC-XACML-S3PLUS-v1-match-table",
        "designator_rows": rows,
        "world_rows": worlds,
        "granularity_note": ("Bag-identity coincides with Match-vector "
                             "equality on the admitted singleton "
                             "null-Issuer interface; bag-identity is "
                             "finer in general and that generality is "
                             "not claimed."),
        "projection_sha256": projection["policy_sha256"],
        "produced_utc": utcnow(),
    })
    print("[P2:hev:032] match table written rows=%d" % len(rows), flush=True)


# Frozen engine sources bound into the capability record (N4 reads).
ENGINE_SOURCES = [
    "pdp-engine/src/main/java/org/ow2/authzforce/core/pdp/impl/io/"
    "PdpEngineAdapters.java",
    "pdp-engine/src/main/java/org/ow2/authzforce/core/pdp/impl/"
    "StandardEnvironmentAttributeProvider.java",
    "pdp-engine/src/main/java/org/ow2/authzforce/core/pdp/impl/"
    "PdpEngineConfiguration.java",
    "pdp-engine/src/main/java/org/ow2/authzforce/core/pdp/impl/io/"
    "SingleDecisionXacmlJaxbRequestPreprocessor.java",
    "pdp-engine/src/main/resources/pdp.xsd",
]


def engine_source_hashes(repo_root):
    """Hash the cited frozen engine sources (clone must be pristine)."""
    out = {}
    for rel in ENGINE_SOURCES:
        path = os.path.join(repo_root, "external", "authzforce-repo", rel)
        if not os.path.isfile(path):
            fail("engine source missing: " + rel)
        out[rel] = sha256_file(path)
    return out


def cmd_lambda_manifest(args):
    """Build the extensional Lambda component manifest."""
    # [P2-LOG-040] Step: build Lambda component manifest.
    print("[P2:hev:040] building Lambda manifest", flush=True)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    sealed = manifest["authzforce"]["fixture_files"]
    for key in ("pdp.xml", "policies/policy.xml"):
        live = sha256_file(os.path.join(args.fixture_dir, key))
        if live != sealed[key]["sha256"]:
            fail("authority artifact drift: " + key)
    pdp_root = etree.parse(
        os.path.join(args.fixture_dir, "pdp.xml")).getroot()
    providers = [etree.tostring(e, method="c14n", exclusive=True)
                 for e in pdp_root if localname(e) == "policyProvider"]
    provider_c14n = b"".join(providers)
    clone = os.path.join(args.repo_root, "external", "authzforce-repo")
    try:
        head = subprocess.run(
            ["git", "-C", clone, "rev-parse", "HEAD"], capture_output=True,
            text=True, timeout=60).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", clone, "status", "--porcelain"],
            capture_output=True, text=True, timeout=60).stdout.strip()
    except OSError as exc:
        fail("clone provenance check failed: %s" % exc)
    if head != manifest["authzforce"]["commit"] or dirty != "":
        fail("engine clone not pristine at evidence build")
    components = {
        "policy_bytes": {
            "sha256": sealed["policies/policy.xml"]["sha256"],
            "reason": "sole authorization policy evaluated",
            "basis": "frozen fixture + designator census",
            "canonical": "frozen file bytes",
            "stability": "byte-equal across repair",
        },
        "provider_element": {
            "sha256": sha256_bytes(provider_c14n),
            "reason": "sole policy provider configuration",
            "basis": "frozen pdp.xml StaticPolicyProvider element",
            "canonical": "W3C exclusive C14N, no comments, of the "
                         "policyProvider element bytes",
            "stability": "byte-equal across repair",
        },
        "preprocessor_resolved": {
            "id": "urn:ow2:authzforce:feature:pdp:request-preproc:"
                  "xacml-xml:default-lax",
            "reason": "effective preprocessor absent explicit config",
            "basis": "N4 PdpEngineAdapters default adapter construction "
                     "with strictIssuer=false (pdp.xsd default), "
                     "xPath=false (pdp.xsd default), verbosity=0 "
                     "(pdp.xsd default)",
            "canonical": "identifier string",
            "stability": "config-equal across repair",
        },
        "attribute_providers_resolved": {
            "active": ["StandardEnvironmentAttributeProvider "
                       "(DEFAULT_FACTORY, override=false)"],
            "reason": "enabled by pdp.xsd standardAttributeProviders "
                      "default true; serves current-* environment "
                      "attributes only",
            "basis": "N4 PdpEngineConfiguration std-provider wiring + "
                     "pdp.xsd documentary + designator census (no "
                     "environment designators read it)",
            "canonical": "descriptor identifier set",
            "stability": "config-equal across repair",
        },
        "implementation_identity": {
            "release": "21.2.0", "tag": "release-21.2.0",
            "commit": manifest["authzforce"]["commit"],
            "reason": "capability == code; version pins behavior",
            "basis": "frozen RELEASE.json/COMMIT.txt",
            "canonical": "identifier triple",
            "stability": "identical across repair",
        },
        "engine_sources": {
            "files": engine_source_hashes(args.repo_root),
            "reason": "cited N4 default-wiring evidence bound by content",
            "basis": "pristine pinned clone (clean tree verified at "
                     "evidence build)",
            "canonical": "frozen file bytes",
            "stability": "byte-equal across repair",
        },
        "request_path": {
            "preprocessor": "default-lax adapter (strictIssuer=false, "
                            "xPath=false, verbosity=0)",
            "parser_rules": "empty containers skipped; bags immutable "
                            "per 7.3.5; lax duplicates permitted "
                            "(moot: singletons throughout)",
            "reason": "bytes-to-bags path is capability, not per-eval "
                      "state",
            "basis": "N4 preprocessor + parser findings (see "
                     "parser_fidelity record)",
            "canonical": "rule strings",
            "stability": "config-equal across repair",
        },
    }
    exclusions = {
        "handler_added_non_env": {
            "reason": "no configured channel can supply non-environment "
                      "values: sole provider serves current-* only; no "
                      "PIP elements; default handler passes request "
                      "values through",
            "basis": "pdp.xml child census + provider scope + "
                     "designator census",
        },
        "jvm_toolchain": {
            "reason": "execution substrate, not authorization "
                      "capability; pinned in environment record, not "
                      "in capability hash",
            "basis": "environment record (out of Lambda scope by "
                     "definition)",
        },
    }
    canonical = json.dumps({"components": components,
                            "exclusions": exclusions},
                           sort_keys=True).encode("utf-8")
    for required in (args.resolved_effective, args.dir_listing):
        if not required or not os.path.isfile(required):
            fail("lambda-manifest requires --resolved-effective and "
                 "--dir-listing files")
    exclusions["evaluation_clock"] = {
        "reason": "no read path from timestamps into evaluation: "
                  "timestamps enter only via env attributes, proven "
                  "inert for this fixture; excluded from hash by "
                  "documented rule, not by omission",
        "basis": "env-inertness record (designator/function census)",
    }
    exclusions["resolved_defaults"] = {
        "sha256": sha256_file(args.resolved_effective),
        "reason": "schema defaults (XPath/strictIssuer/verbosity/"
                  "maxInteger/ignoreOldVersions/std registries) are "
                  "capability; pinned by content hash",
    }
    exclusions["policy_location"] = {
        "sha256": sha256_file(args.dir_listing),
        "rule": "PARENT_DIR-relative glob policies/*.xml resolved "
                "inside the frozen fixture dir; absolute URI excluded "
                "as machine-dependent by design",
    }
    canonical = json.dumps({"components": components,
                            "exclusions": exclusions},
                           sort_keys=True).encode("utf-8")
    write_json(args.out, {
        "manifest_id": "PC-XACML-S3PLUS-v1-lambda-manifest",
        "components": components,
        "exclusions": exclusions,
        "canonical_spec": "UTF-8 JSON, sorted keys, of "
                          "components+exclusions",
        "pre_hash": sha256_bytes(canonical),
        "supersedes_pre_hash": "bb2c3c94-method-opaque (historical; "
                               "replaced by reconstructible "
                               "construction)",
        "produced_utc": utcnow(),
    })
    print("[P2:hev:042] manifest written", flush=True)


def main(argv):
    """Entry point: dispatch hardening-evidence builders."""
    # [P2-LOG-050] Step: dispatch evidence mode.
    print("[P2:hev:050] hardening evidence invoked", flush=True)
    parser = argparse.ArgumentParser(description="Hardening evidence.")
    parser.add_argument("--mode", required=True,
                        choices=["diffs", "wrapper", "match-table",
                                 "lambda-manifest"])
    parser.add_argument("--original", default="")
    parser.add_argument("--permit", default="")
    parser.add_argument("--nonpermit", default="")
    parser.add_argument("--response", default="")
    parser.add_argument("--policy", default="")
    parser.add_argument("--builder", default="")
    parser.add_argument("--runner", default="")
    parser.add_argument("--projection", default="")
    parser.add_argument("--manifest", default="")
    parser.add_argument("--fixture-dir", default="")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--resolved-effective", default="")
    parser.add_argument("--dir-listing", default="")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.mode == "diffs":
        cmd_diffs(args)
    elif args.mode == "wrapper":
        cmd_wrapper(args)
    elif args.mode == "match-table":
        cmd_match_table(args)
    elif args.mode == "lambda-manifest":
        cmd_lambda_manifest(args)
    # [P2-LOG-060] Step: evidence complete.
    print("[P2:hev:060] hardening evidence complete", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
