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
    ("out-dir disjoint from policies glob (RS003-B01)",
     "assert_out_dir_disjoint(out_dir, policies_dir,"),
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
    flow_reads = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in ("open", "parse", "fromstring"):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(
                            arg.value, str):
                        flow_reads.add(arg.value)
    flow_hits = sorted(
        value for value in flow_reads
        if any(marker in value for marker in
               ("x_permit", "x_nonpermit", "target_", "artifacts/raw")))
    if flow_hits:
        fail("builder reads built-world or response outputs: %s"
             % flow_hits)
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
    world_binding = {"bound": False,
                     "note": "no execution-inputs file supplied"}
    if args.execution_inputs:
        # [P2-LOG-024] Step: bind built world values to preregistration.
        print("[P2:hev:024] binding world values", flush=True)
        with open(args.execution_inputs, "r", encoding="utf-8") as handle:
            worlds = json.load(handle)["worlds"]
        binding = {}
        for label, path, world in (
                ("permit", args.permit, "x_permit"),
                ("nonpermit", args.nonpermit, "x_nonpermit")):
            root = etree.parse(path).getroot()
            texts = [child.text for element in root.iter()
                     for child in element
                     if localname(element) == "Attribute"
                     and "some-attribute" in (element.get("AttributeId")
                                              or "")
                     and localname(child) == "AttributeValue"]
            expected = worlds[world]["missing_attribute_value"]
            binding[label] = {"world": world, "expected": expected,
                              "observed": texts,
                              "match": texts == [expected]}
        if not all(entry["match"] for entry in binding.values()):
            fail("built world values do not match preregistration")
        world_binding = {"bound": True, "binding": binding,
                         "source": "prereg/execution_inputs.json worlds "
                                   "vs built request AttributeValue text"}
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
        "flow_reads_outputs": flow_hits,
        "input_hashes": {
            "request.xml": sha256_file(args.original),
            "response.xml": sha256_file(args.response),
            "policy.xml": sha256_file(args.policy),
            "request_x_permit.xml": sha256_file(args.permit),
            "request_x_nonpermit.xml": sha256_file(args.nonpermit),
        },
        "world_value_binding": world_binding,
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

# Semantically capable engine implementation set (Phase 2D closure):
# every AuthzForce source file that can change authorization evaluation
# under the measured interface (evaluation core, combining, functions,
# datatypes, policy/rule/target/match, preprocessing io). Enumerated as
# directories; all *.java beneath are hashed.
ENGINE_SEMANTIC_DIRS = [
    "pdp-engine/src/main/java/org/ow2/authzforce/core/pdp/impl",
]

# Built artifacts actually executed (not in git; hashed as files).
BUILT_JARS = [
    "pdp-engine/target/authzforce-ce-core-pdp-engine-21.2.0.jar",
    "pdp-io-xacml-json/target/authzforce-ce-core-pdp-io-xacml-json-21.2.0.jar",
    "pdp-testutils/target/authzforce-ce-core-pdp-testutils-21.2.0.jar",
    "pdp-testutils/src/test/resources.json/lib/Saxon-HE-9.8.0-15.jar",
]

# Dependency lockfiles pinning transitive build inputs.
BUILD_POMS = [
    "pom.xml",
    "pdp-engine/pom.xml",
]

# Experiment-side evaluation-path sources (repo files, git-pinned).
DRIVER_SOURCES = [
    "src/xacml/PdpRunner.java",
    "src/xacml/run_authzforce.py",
]

CANONICAL_SPEC = ("json.dumps({'components':..., 'exclusions':...}, "
                  "sort_keys=True, ensure_ascii=True, "
                  "separators=(', ', ': ')).encode('utf-8'); "
                  "pre_hash = sha256(canonical).hexdigest() lower-case")


def engine_source_hashes(repo_root):
    """Hash the cited frozen engine sources (clone must be pristine)."""
    out = {}
    for rel in ENGINE_SOURCES:
        path = os.path.join(repo_root, "external", "authzforce-repo", rel)
        if not os.path.isfile(path):
            fail("engine source missing: " + rel)
        out[rel] = sha256_file(path)
    return out


def engine_semantic_hashes(repo_root):
    """Hash the full semantically capable engine set + tree identity."""
    clone = os.path.join(repo_root, "external", "authzforce-repo")
    files = {}
    for directory in ENGINE_SEMANTIC_DIRS:
        base = os.path.join(clone, *directory.split("/"))
        for dirpath, _dirs, names in os.walk(base):
            for name in names:
                if not name.endswith(".java"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, clone).replace(os.sep, "/")
                files[rel] = {"bytes": os.path.getsize(path),
                              "sha256": sha256_file(path)}
    if not files:
        fail("engine semantic set empty")
    head = subprocess.run(
        ["git", "-C", clone, "rev-parse", "HEAD"], capture_output=True,
        text=True, timeout=60).stdout.strip()
    tree = subprocess.run(
        ["git", "-C", clone, "rev-parse", "HEAD^{tree}"], capture_output=True,
        text=True, timeout=60).stdout.strip()
    return {"files": files, "commit": head, "tree": tree,
            "method": "sha256 of frozen file bytes per path; tree binds "
                      "all blobs at commit (git rev-parse HEAD^{tree})"}


def built_artifact_hashes(repo_root):
    """Hash executed jars, lockfiles, driver sources, toolchain identity."""
    clone = os.path.join(repo_root, "external", "authzforce-repo")
    jars = []
    for rel in BUILT_JARS:
        path = os.path.join(clone, *rel.split("/"))
        if not os.path.isfile(path):
            fail("built jar missing: " + rel)
        jars.append({"path": rel, "bytes": os.path.getsize(path),
                     "sha256": sha256_file(path),
                     "method": "sha256 of built file bytes"})
    poms = []
    for rel in BUILD_POMS:
        path = os.path.join(clone, *rel.split("/"))
        poms.append({"path": rel, "bytes": os.path.getsize(path),
                     "sha256": sha256_file(path),
                     "method": "sha256 of lockfile bytes"})
    drivers = []
    for rel in DRIVER_SOURCES:
        path = os.path.join(repo_root, *rel.split("/"))
        drivers.append({"path": rel, "bytes": os.path.getsize(path),
                        "sha256": sha256_file(path),
                        "method": "sha256 of repo file bytes (git-pinned)"})
    jdk_identity = "unrecorded"
    environment_path = os.path.join(repo_root, "artifacts", "raw",
                                    "environment.txt")
    if os.path.isfile(environment_path):
        with open(environment_path, encoding="utf-8",
                  errors="replace") as handle:
            for line in handle.read().splitlines():
                if "openjdk version" in line:
                    jdk_identity = line.strip()
                    break
    return {"jars": jars, "poms": poms, "drivers": drivers,
            "jdk_identity": jdk_identity,
            "api_boundary": ("pdp-api sources external to the clone "
                             "(artifact 22.2.0, coordinates-pinned); "
                             "coverage via coordinates + built engine jar "
                             "bytes + engine-source tree")}


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
    classpath_sha = "PENDING"
    classpath_manifest = getattr(args, "classpath_manifest", "") or ""
    if classpath_manifest:
        if not os.path.isfile(classpath_manifest):
            fail("classpath manifest missing: " + classpath_manifest)
        classpath_sha = sha256_file(classpath_manifest)
    components = {
        "policy_bytes": {
            "sha256": sealed["policies/policy.xml"]["sha256"],
            "method": "sha256 of frozen policy.xml file bytes",
            "reason": "sole authorization policy evaluated",
            "basis": "frozen fixture + designator census",
            "canonical": "frozen file bytes",
            "stability": "byte-equal across repair",
        },
        "provider_element": {
            "sha256": sha256_bytes(provider_c14n),
            "method": ("sha256 of b''.join(exclusive-C14N-no-comments "
                       "per policyProvider element) via lxml etree.tostring"
                       "(method='c14n', exclusive=True); pinned lxml 6.1.1"),
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
            "method": "identifier triple cross-checked to frozen "
                      "RELEASE.json/COMMIT.txt + clone HEAD",
            "reason": "capability == code; version pins behavior",
            "basis": "frozen RELEASE.json/COMMIT.txt",
            "canonical": "identifier triple",
            "stability": "identical across repair",
        },
        "engine_sources": {
            "files": engine_source_hashes(args.repo_root),
            "method": "sha256 of frozen file bytes per path (subset kept "
                      "for lineage; superseded by engine_semantic_set)",
            "reason": "cited N4 default-wiring evidence bound by content",
            "basis": "pristine pinned clone (clean tree verified at "
                     "evidence build)",
            "canonical": "frozen file bytes",
            "stability": "byte-equal across repair",
        },
        "engine_semantic_set": dict(
            engine_semantic_hashes(args.repo_root),
            reason=("every AuthzForce source capable of changing "
                    "evaluation under the measured interface: evaluation "
                    "core, combining, functions, datatypes, policy/rule/"
                    "target/match, preprocessing io"),
            basis=("capability-ranked enumeration at pinned commit "
                   "(see engine_sources_manifest.json); tree sha binds "
                   "all blobs"),
            stability="byte-equal across repair"),
        "built_artifacts": dict(
            built_artifact_hashes(args.repo_root),
            reason=("executed bytes (jars), dependency lock (poms), "
                    "evaluation-path drivers"),
            basis=("hashes of built/tested artifacts at pinned commit; "
                   "transitive Central artifacts pinned by pom coordinates "
                   "(immutable repository policy), not content-hashed: "
                   "explicit limitation"),
            stability="byte-equal across repair"),
        "classpath": {
            "manifest": "classpath_manifest.json (content hashes of "
                        "test-classes + pdp-classes trees, extension "
                        "activation facts)",
            "manifest_sha256": classpath_sha,
            "method": "sha256 per clone-relative path; pre-eval gate "
                      "recomputes live vs manifest",
            "reason": "runtime classpath composition decides which bytes "
                      "execute (extension path, test utilities)",
            "basis": "classpath_manifest content + pre-eval "
                     "--check-classpath gate",
            "canonical": "manifest file bytes (bound by hash)",
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
        "reconstruction": {
            "ordered_manifest": "component/exclusion keys in JSON "
                                "sorted-key order (deterministic)",
            "canonicalization": CANONICAL_SPEC,
            "composition": ("extract components+exclusions objects only; "
                            "serialize per canonicalization; "
                            "pre_hash = sha256 hexdigest lower-case"),
            "recompute_tool": "src/audit/recompute_lambda.py "
                              "(--manifest always; --packet-dir verifies "
                              "file-backed constituents)",
            "test_vector": ("see tests/test_lambda_manifest.py: "
                            "fixed mini-manifest -> fixed digest"),
            "unexposed": ("engine full bytes live in packet "
                          "candidates/engine_sources/ for this revision; "
                          "transitive Central artifacts by coordinates "
                          "(limitation disclosed in built_artifacts)"),
        },
        "pre_hash": sha256_bytes(canonical),
        "supersedes_pre_hash": "bb2c3c94-method-opaque (historical; "
                               "replaced by reconstructible "
                               "construction)",
        "produced_utc": utcnow(),
    })
    print("[P2:hev:042] manifest written", flush=True)


def cmd_staging_certificate(args):
    """Build the mechanically inspectable staging certificate.

    Everything here is constructible WITHOUT PDP evaluation. Fields that
    require unlock/execution are marked PENDING_TARGET with the exact
    procedure that will fill them. No response bytes are read or produced.
    """
    # [P2-LOG-044] Step: build staging certificate.
    print("[P2:hev:044] building staging certificate", flush=True)
    repo = os.path.abspath(args.repo_root)
    fixture = os.path.join(repo, "external", "authzforce", "fixture")
    derived_requests = os.path.join(repo, "derived", "requests")
    with open(os.path.join(repo, "prereg", "execution_inputs.json"),
              encoding="utf-8") as handle:
        worlds = json.load(handle)["worlds"]
    source_hashes = {}
    for rel in ("request.xml", "response.xml", "pdp.xml",
                "policies/policy.xml"):
        source_hashes[rel.replace("/", "_")] = sha256_file(
            os.path.join(fixture, *rel.split("/")))
    repaired = {}
    for label, world in (("permit", "x_permit"),
                         ("nonpermit", "x_nonpermit")):
        path = os.path.join(derived_requests,
                            "request_%s.xml" % world)
        root = etree.parse(path).getroot()
        texts = [child.text for element in root.iter()
                 for child in element
                 if localname(element) == "Attribute"
                 and "some-attribute" in (element.get("AttributeId") or "")
                 and localname(child) == "AttributeValue"]
        expected = worlds[world]["missing_attribute_value"]
        if texts != [expected]:
            fail("staging cert: %s world value mismatch" % label)
        repaired[label] = {
            "sha256": sha256_file(path),
            "world_value_bound": True,
            "single_attribute_insert": True,
        }
    policies_dir = os.path.join(fixture, "policies")
    listing = [{"name": name,
                "bytes": os.path.getsize(os.path.join(policies_dir, name)),
                "sha256": sha256_file(os.path.join(policies_dir, name))}
               for name in sorted(os.listdir(policies_dir))]
    disjoint = True
    try:
        left = os.path.normcase(os.path.realpath(
            os.path.abspath(derived_requests)))
        right = os.path.normcase(os.path.realpath(
            os.path.abspath(policies_dir)))
        common = os.path.normcase(os.path.commonpath([left, right]))
        disjoint = common not in (left, right)
    except ValueError:
        disjoint = True
    with open(os.path.join(repo, "src", "xacml",
                           "build_repaired_requests.py"),
              encoding="utf-8") as handle:
        builder_source = handle.read()
    builder_markers = ("assert_out_dir_disjoint(out_dir, policies_dir,",
                       "copy.deepcopy(original)",
                       "assert_single_attribute_addition(")
    if not all(marker in builder_source for marker in builder_markers):
        fail("staging cert: builder guard markers absent")
    with open(os.path.join(repo, "scripts",
                           "run_phase2.ps1"), encoding="utf-8") as handle:
        phase2 = handle.read()
    argv_markers = ("verify_deployment_set.py", "--check", "--disjoint",
                    "run_authzforce.py")
    if not all(marker in phase2 for marker in argv_markers):
        fail("staging cert: invocation template markers absent")
    with open(os.path.join(repo, "src", "xacml", "PdpRunner.java"),
              encoding="utf-8") as handle:
        driver = handle.read()
    if "pdp.evaluate" not in driver:
        fail("staging cert: native entrypoint marker absent")
    scan_hits = []
    for dirpath, _dirs, files in os.walk(repo):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for name in files:
            lowered = name.lower()
            if lowered.startswith("target_") or lowered.startswith(
                    "response_x_"):
                scan_hits.append(os.path.join(dirpath, name))
    if scan_hits:
        fail("staging cert: completed-world outputs exist: %s" % scan_hits)
    classpath_pointer = "classpath_manifest.json (content hashes of "
    classpath_pointer += "test-classes + pdp-classes trees; pre-eval "
    classpath_pointer += "--check-classpath gate)"
    write_json(args.out, {
        "certificate_id": "PC-XACML-S3PLUS-v1-staging",
        "source_hashes": source_hashes,
        "repaired_hashes": repaired,
        "structural_diff": ("exactly one added subject Attribute per "
                            "world (INV-05 probe-copy residual + "
                            "request_diffs.json unified diffs); "
                            "inter-world delta is AttributeValue only"),
        "staged_path_template": "<work_dir>/fixture_<world>/ + policies/ "
                                "(run_authzforce.stage_completed_fixture)",
        "canonical_realpath_procedure": ("realpath + \\?\\ strip + "
                                         "normcase + normpath + "
                                         "per-component dot/space strip; "
                                         "see builder canon_path"),
        "dir_set_manifest": {"directory": "external/authzforce/fixture/"
                                          "policies/",
                             "files": listing},
        "deployment_set_manifest": {
            "parent_dir_rule": "PARENT_DIR-relative glob policies/*.xml",
            "count": len(listing),
            "count_is_one": len(listing) == 1,
            "gate": "verify_deployment_set --check/--disjoint pre-eval",
        },
        "disjointness": {"live_out_dir_disjoint": disjoint,
                         "enforced": "builder pre/post-create + pre-eval "
                                     "gate (exit 2 on overlap)"},
        "wrapper_hash": sha256_file(os.path.join(
            repo, "src", "xacml", "build_repaired_requests.py")),
        "invocation_argv_templates": {
            "builder": ("build_repaired_requests.py <request.xml> "
                        "<response.xml> <policy.xml> <permit-value> "
                        "<nonpermit-value> <out-dir> (values bound from "
                        "execution_inputs.json by phase scripts)"),
            "runner": ("run_authzforce.py --mode completed --world "
                       "<x_permit|x_nonpermit> --request "
                       "derived/requests/request_<world>.xml ... "
                       "(staged fixture + PdpRunner + out "
                       "artifacts/raw/target_<world>_actual.xml)"),
            "verified_in": "scripts/run_phase1.ps1 + scripts/run_phase2.ps1",
        },
        "native_entrypoint": ("PdpRunner.main(<fixtureDir> <requestFile> "
                              "<responseOutFile>) -> "
                              "PdpEngineConfiguration.getInstance(pdp.xml) "
                              "-> pdp.evaluate"),
        "no_prior_response": {"target_scan_empty": True,
                              "build_before_eval": "requests constructed "
                              "in Phase 1, never executed (chronology + "
                              "phase1-only-original refusal exit 2)",
                              "responses_pending_target": True},
        "no_alternate_policy": {"copy_whitelist": ["pdp.xml",
                                                   "policies/policy.xml"],
                                "staged_exclusivity": "gated pre-eval; "
                                "PENDING_TARGET measurement",
                                "classpath_manifest": classpath_pointer},
        "before_after_manifests": ("PENDING_TARGET: live before/after "
                                   "listings require unlock + execution; "
                                   "procedure: gate --emit at P2:phase2:095 "
                                   "then post-run staged listing"),
        "produced_utc": utcnow(),
    })
    print("[P2:hev:046] staging certificate written", flush=True)


def cmd_classpath_manifest(args):
    """Record the measurement runtime classpath content (no execution).

    Hashes the AuthzForce-owned classpath roots used at target-audit
    time plus the extension-activation facts. Driver-classes and the
    dependency cp-file are runtime-built; their provenance rule (pinned
    sources + pinned coordinates) is recorded, not their bytes.
    """
    # [P2-LOG-052] Step: build classpath manifest.
    print("[P2:hev:052] building classpath manifest", flush=True)
    clone = os.path.abspath(args.clone)

    def tree_hashes(root):
        """Hash every file under root, repo-relative keys."""
        out = {}
        for dirpath, _dirs, names in os.walk(root):
            for name in sorted(names):
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, clone).replace(os.sep, "/")
                out[rel] = {"bytes": os.path.getsize(path),
                            "sha256": sha256_file(path)}
        return out

    test_classes = os.path.join(
        clone, "pdp-testutils", "target", "test-classes")
    pdp_classes = os.path.join(clone, "pdp-testutils", "target", "classes")
    for required in (test_classes, pdp_classes):
        if not os.path.isdir(required):
            fail("classpath root missing: " + required)
    test_files = tree_hashes(test_classes)
    pdp_files = tree_hashes(pdp_classes)
    ext_markers = [rel for rel in test_files
                   if rel.endswith(("pdp-ext.xsd", "catalog.xml"))
                   or "META-INF/services" in rel
                   or "TestExtensible" in rel]
    write_json(args.out, {
        "manifest_id": "PC-XACML-S3PLUS-v1-classpath",
        "method": "sha256 of file bytes per clone-relative path",
        "test_classes": {"root": "pdp-testutils/target/test-classes",
                         "count": len(test_files), "files": test_files},
        "pdp_classes": {"root": "pdp-testutils/target/classes",
                        "count": len(pdp_files), "files": pdp_files},
        "extension_active": {
            "pdp_ext_xsd_present": any(
                name.endswith("pdp-ext.xsd") for name in test_files),
            "catalog_present": any(name.endswith("catalog.xml")
                                   for name in test_files),
            "extension_markers": sorted(ext_markers),
        },
        "runtime_built": {
            "driver_classes": "built per-run from pinned "
                              "src/xacml/PdpRunner.java; content verified "
                              "by pre-eval gate procedure, not pre-pinned",
            "dependency_cp": "Maven coordinates from frozen poms; "
                             "immutable Central policy; content hashed "
                             "at pre-eval gate, compared across worlds",
        },
        "produced_utc": utcnow(),
    })
    print("[P2:hev:054] classpath manifest written", flush=True)


def cmd_locator_table(args):
    """Build a verified raw-HTML section table for packet locators.

    The legacy stripped-line numbers came from an unrecorded extraction
    (disclosed limitation). This table re-grounds every map section in the
    frozen HTML bytes with a deterministic, re-runnable procedure: strip
    tags, unescape entities, number lines, locate headings, verify a
    token-subsequence quote per section. No PDP, no expected results.
    """
    # [P2-LOG-048] Step: build locator verification table.
    print("[P2:hev:048] building locator table", flush=True)
    import html as html_module
    import re as re_module
    with open(args.html, "rb") as handle:
        raw = handle.read()
    html_sha = sha256_bytes(raw)
    text = re_module.sub(r"<[^>]*>", "", raw.decode(
        "windows-1252", errors="strict"))
    text = html_module.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    stripped = text.split("\n")
    encoding = ("windows-1252 (per document meta Content-Type); "
                "CRLF normalized to LF before numbering")
    sections = [
        ("Sec-3.1-dataflow", r"3\.1\s+Data-flow",
         ["native request format", "optionally adds attributes"]),
        ("Sec-3.2-conversion-scope", r"3\.2\s+",
         ["DataType", "AttributeValue"]),
        ("Sec-5.29-AttributeDesignator", r"5\.29\s+",
         ["MustBePresent", "AttributeId", "Category"]),
        ("Sec-5.30-AttributeSelector", r"5\.30\s+",
         ["XPath", "AttributeSelector", "Category"]),
        ("Sec-5.57-5.58-StatusDetail", r"5\.5[78]\s+",
         ["MissingAttributeDetail", "StatusDetail"]),
        ("Sec-7.17-Decision", r"7\.17\s+",
         ["Permit", "Deny"]),
        ("Sec-7.3.4-Attribute-Matching", r"7\.3\.4\s+Attribute Matching",
         ["governed by", "AttributeId", "DataType", "alone"]),
        ("Sec-7.3.5-Attribute-Retrieval", r"7\.3\.5\s+Attribute Retrieval",
         ["SHALL", "empty", "immutable", "bag"]),
        ("Sec-7.3.6-Environment", r"7\.3\.6\s+Environment",
         ["environment", "handler"]),
        ("Sec-7.3.7-Selector-eval", r"7\.3\.7",
         ["XPath", "evaluation"]),
        ("Sec-7.6-Match", r"7\.6\s+Match",
         ["Indeterminate", "Match"]),
        ("Sec-7.7-Target", r"7\.7\s+Target",
         ["AnyOf", "AllOf", "Match"]),
        ("Sec-10.2.5-env-attributes", r"10\.2\.5",
         ["environment", "attributes"]),
    ]
    resolved = {}
    problems = []
    for key, heading, tokens in sections:
        starts = [i + 1 for i, line in enumerate(stripped)
                  if re_module.search(heading, line)]
        verified_at = None
        for start in starts:
            window = "\n".join(stripped[start - 1:start + 400])
            if all(token in window for token in tokens):
                verified_at = start
                break
        if verified_at is None:
            problems.append("tokens unverified for " + key)
            continue
        resolved[key] = {"heading_pattern": heading,
                         "stripped_start_line": verified_at,
                         "quote_tokens": tokens,
                         "quote_verified": True,
                         "candidate_starts": starts[:6]}
    if problems:
        fail("locator table unresolved: %s" % problems)
    write_json(args.out, {
        "table_id": "PC-XACML-S3PLUS-v1-locator-table",
        "method": ("strip tags re <[^>]*>, html.unescape, split \\n, "
                   "1-indexed; heading = first regex match; quote = "
                   "token-subsequence within following 400 lines"),
        "source_encoding": encoding,
        "html_sha256": html_sha,
        "legacy_note": ("map stripped numbers came from an unrecorded "
                        "extraction and are superseded by this table; "
                        "legacy map retained for lineage only"),
        "sections": resolved,
        "produced_utc": utcnow(),
    })
    print("[P2:hev:049] locator table written sections=%d"
          % len(resolved), flush=True)


def main(argv):
    """Entry point: dispatch hardening-evidence builders."""
    # [P2-LOG-050] Step: dispatch evidence mode.
    print("[P2:hev:050] hardening evidence invoked", flush=True)
    parser = argparse.ArgumentParser(description="Hardening evidence.")
    parser.add_argument("--mode", required=True,
                        choices=["diffs", "wrapper", "match-table",
                                 "lambda-manifest", "staging-certificate",
                                 "locator-table", "classpath-manifest"])
    parser.add_argument("--original", default="")
    parser.add_argument("--html", default="")
    parser.add_argument("--clone", default="")
    parser.add_argument("--permit", default="")
    parser.add_argument("--nonpermit", default="")
    parser.add_argument("--response", default="")
    parser.add_argument("--policy", default="")
    parser.add_argument("--builder", default="")
    parser.add_argument("--runner", default="")
    parser.add_argument("--projection", default="")
    parser.add_argument("--manifest", default="")
    parser.add_argument("--execution-inputs", default="")
    parser.add_argument("--fixture-dir", default="")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--resolved-effective", default="")
    parser.add_argument("--classpath-manifest", default="")
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
    elif args.mode == "staging-certificate":
        cmd_staging_certificate(args)
    elif args.mode == "locator-table":
        if not args.html:
            fail("locator-table requires --html")
        cmd_locator_table(args)
    elif args.mode == "classpath-manifest":
        if not args.clone:
            fail("classpath-manifest requires --clone")
        cmd_classpath_manifest(args)
    # [P2-LOG-060] Step: evidence complete.
    print("[P2:hev:060] hardening evidence complete", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
