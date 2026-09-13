"""Launch freeze for pre-execution certification (Amendment 007).

Builds artifacts/audits/launch/launch_packet/ = operative rev004 packet
bytes plus launch additions (registry, prompt, driver/jar/pom/invocation
sources, refreshed lineage/gate copies), seals LAUNCH_FREEZE.json with
code hashes, and verifies. Never touches frozen semantic history.

Commands (all --repo-root required): --build-launch-packet,
--verify-launch, --status.

Step console lines use the [P2:lfz:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone

LAUNCH_SUBDIR = os.path.join("artifacts", "audits", "launch")
REV_PACKET = os.path.join("artifacts", "audits", "semantic_hardening",
                          "final_freeze", "FINAL_BLIND_PACKET")
EXECUTION_CODE = [
    "src/xacml/run_authzforce.py",
    "src/xacml/PdpRunner.java",
    "src/xacml/build_repaired_requests.py",
    "src/xacml/parse_response.py",
    "src/pc/derive_Lambda.py",
    "src/audit/verify_deployment_set.py",
    "src/audit/recompute_lambda.py",
    "src/audit/conformance_verify_a.py",
    "src/audit/conformance_verify_b.py",
    "src/audit/launch_freeze.py",
    "src/audit/launch_certification.py",
]


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:lfz:FAIL] " + message, flush=True)
    sys.exit(code)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utcnow():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def launch_base(repo_root):
    """Return the launch base directory."""
    return os.path.join(repo_root, *LAUNCH_SUBDIR.split("/"))


def packet_dir(repo_root):
    """Return the launch packet directory."""
    return os.path.join(launch_base(repo_root), "launch_packet")


def copy_into(repo_root, src_rel, dst_rel):
    """Copy a repo file into the launch packet, creating parents."""
    src = os.path.join(repo_root, *src_rel.split("/"))
    dest = os.path.join(packet_dir(repo_root), *dst_rel.split("/"))
    if not os.path.isfile(src):
        fail("launch source missing: " + src_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(src, dest)


def cmd_build_packet(args):
    """Assemble the launch packet and seal the launch freeze."""
    # [P2-LOG-010] Step: build the launch packet.
    print("[P2:lfz:010] building launch packet", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    dest = packet_dir(repo_root)
    if os.path.isdir(dest):
        fail("launch packet exists; remove only via new launch revision "
             "procedure (never destroy silently)")
    clone = os.path.join(repo_root, "external", "authzforce-repo")
    try:
        head = __import__("subprocess").run(
            ["git", "-C", clone, "rev-parse", "HEAD"], capture_output=True,
            text=True, timeout=60).stdout.strip()
        dirty = __import__("subprocess").run(
            ["git", "-C", clone, "status", "--porcelain"],
            capture_output=True, text=True, timeout=60).stdout.strip()
    except OSError as exc:
        fail("clone provenance check failed: %s" % exc)
    with open(os.path.join(repo_root, "external", "MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    if head != manifest["authzforce"]["commit"] or dirty != "":
        fail("engine clone not pristine at launch freeze")
    if os.path.isfile(os.path.join(repo_root, "artifacts", "seal",
                                   "TARGET_EXECUTION_LOCK.json")):
        fail("execution lock sealed; launch freeze forbidden post-invocation")
    import glob as _glob
    if _glob.glob(os.path.join(repo_root, "artifacts", "raw",
                               "target_*_actual.xml")):
        fail("target outputs exist; launch freeze requires zero executions")
    panel = [part.strip() for part in args.panel_ids.split(",")
             if part.strip()]
    import sys as _sys
    _sys.path.insert(0, os.path.join(repo_root, "src", "audit"))
    import launch_certification as _lc
    if len(panel) != 3 or _lc.panel_of(panel[0]) != tuple(panel):
        fail("panel must be one canonical triple (e.g. AUD-L04,AUD-L05,"
             "AUD-L06)")
    rev_packet = os.path.join(repo_root, *REV_PACKET.split("/"))
    shutil.copytree(rev_packet, dest)
    static_additions = [
        ("src/xacml/PdpRunner.java", "candidates/invocation/PdpRunner.java"),
        ("src/xacml/run_authzforce.py",
         "candidates/invocation/run_authzforce.py"),
        ("scripts/run_phase1.ps1", "candidates/invocation/run_phase1.ps1"),
        ("scripts/run_phase1.sh", "candidates/invocation/run_phase1.sh"),
        ("scripts/run_phase2.ps1", "candidates/invocation/run_phase2.ps1"),
        ("scripts/run_phase2.sh", "candidates/invocation/run_phase2.sh"),
        ("src/audit/recompute_lambda.py",
         "candidates/recompute_lambda.py"),
        ("src/audit/verify_deployment_set.py",
         "candidates/verify_deployment_set.py"),
        ("src/audit/conformance_verify_a.py",
         "candidates/conformance_verify_a.py"),
        ("src/audit/conformance_verify_b.py",
         "candidates/conformance_verify_b.py"),
        ("src/pc/derive_Lambda.py",
         "candidates/derive_Lambda.py"),
        ("src/xacml/parse_response.py",
         "candidates/parse_response.py"),
        ("src/xacml/build_repaired_requests.py",
         "candidates/builder_source.py"),
        ("src/audit/launch_freeze.py",
         "candidates/launch_freeze.py"),
        ("src/audit/launch_certification.py",
         "candidates/launch_certification.py"),
        ("artifacts/audits/semantic_hardening/rounds/"
         "HARDENING_ROUND_007/evidence/dependency_hashes.json",
         "candidates/dependency_hashes.json"),
        ("prereg/execution_inputs.json", "candidates/execution_inputs.json"),
    ]
    for src_rel, dst_rel in static_additions:
        copy_into(repo_root, src_rel, dst_rel)
    for src_rel, dst_rel in (
            ("external/authzforce-repo/pom.xml",
             "candidates/built/poms/root-pom.xml"),
            ("external/authzforce-repo/pdp-engine/pom.xml",
             "candidates/built/poms/pdp-engine-pom.xml")):
        copy_into(repo_root, src_rel, dst_rel)
    jar_rels = [
        "pdp-engine/target/authzforce-ce-core-pdp-engine-21.2.0.jar",
        "pdp-io-xacml-json/target/"
        "authzforce-ce-core-pdp-io-xacml-json-21.2.0.jar",
        "pdp-testutils/target/"
        "authzforce-ce-core-pdp-testutils-21.2.0.jar",
        "pdp-testutils/src/test/resources.json/lib/Saxon-HE-9.8.0-15.jar",
    ]
    for rel in jar_rels:
        copy_into(repo_root, "external/authzforce-repo/" + rel,
                  "candidates/built/jars/" + rel.rsplit("/", 1)[-1])
    copy_into(repo_root, "artifacts/audits/launch/run_conformance_"
                         "obligations.json",
              "run_conformance_obligations.json")
    copy_into(repo_root, "artifacts/audits/launch/"
                         "launch_certification_prompt.txt",
              "launch_certification_prompt.txt")
    manifest_path = os.path.join(dest, "candidates",
                                     "lambda_manifest.json")
    with open(manifest_path, encoding="utf-8") as handle:
        staged_manifest = json.load(handle)
    prior_pre = staged_manifest.get("pre_hash", "")
    inv_map = {"src/xacml/PdpRunner.java":
               "candidates/invocation/PdpRunner.java",
               "src/xacml/run_authzforce.py":
               "candidates/invocation/run_authzforce.py"}
    for entry in staged_manifest["components"]["built_artifacts"][
            "drivers"]:
        staged_rel = inv_map.get(entry.get("path", ""))
        if not staged_rel:
            fail("manifest driver without staged bytes: %s"
                 % entry.get("path", "?"))
        staged_file = os.path.join(dest, *staged_rel.split("/"))
        if not os.path.isfile(staged_file):
            fail("staged driver bytes absent: " + staged_rel)
        entry["sha256"] = sha256_file(staged_file)
        entry["bytes"] = os.path.getsize(staged_file)
        entry["method"] = ("sha256 of staged packet bytes (launch "
                           "revision %s)" % args.launch_id)
    with open(os.path.join(dest, "candidates", "dependency_hashes.json"),
              encoding="utf-8") as handle:
        dep_doc = json.load(handle)
    dep_entries = dep_doc.get("entries", [])
    if not dep_entries:
        fail("dependency hashes empty; cannot bind transitive closure")
    dep_path = os.path.join(dest, "candidates", "dependency_hashes.json")
    staged_manifest["components"]["dependency_content"] = {
        "count": len(dep_entries),
        "method": ("sha256 of packet file "
                   "candidates/dependency_hashes.json "
                   "(offline mvn dependency:build-classpath, "
                   "includeScope=test; every listed jar hashed); "
                   "reproduce with sha256sum over that file"),
        "sha256": sha256_file(dep_path),
    }
    staged_manifest["builder_lineage"] = {
        "operative_builder": ("src/audit/hardening_evidence.py "
                              "cmd_lambda_manifest: per-constituent sha256 "
                              "over frozen bytes"),
        "historical_narrow_author": ("src/pc/derive_Lambda.py: Phase-2A "
                                     "6-field tuple (bb2c3c94 era); "
                                     "superseded for the operative set, "
                                     "retained for provenance"),
        "verifier": ("src/audit/recompute_lambda.py "
                     "canonical_composite over components+exclusions plus "
                     "packet file checks via candidates/path_remap.json"),
        "note": ("pre_hash reproduces EXACTLY via recompute canonical; "
                 "authorship history in pre_hash_lineage.json"),
    }
    remap = {
        "src/xacml/PdpRunner.java":
        "candidates/invocation/PdpRunner.java",
        "src/xacml/run_authzforce.py":
        "candidates/invocation/run_authzforce.py",
        "pdp-engine/target/authzforce-ce-core-pdp-engine-21.2.0.jar":
        "candidates/built/jars/authzforce-ce-core-pdp-engine-21.2.0.jar",
        "pdp-io-xacml-json/target/"
        "authzforce-ce-core-pdp-io-xacml-json-21.2.0.jar":
        "candidates/built/jars/"
        "authzforce-ce-core-pdp-io-xacml-json-21.2.0.jar",
        "pdp-testutils/target/"
        "authzforce-ce-core-pdp-testutils-21.2.0.jar":
        "candidates/built/jars/"
        "authzforce-ce-core-pdp-testutils-21.2.0.jar",
        "pdp-testutils/src/test/resources.json/lib/Saxon-HE-9.8.0-15.jar":
        "candidates/built/jars/Saxon-HE-9.8.0-15.jar",
        "pom.xml": "candidates/built/poms/root-pom.xml",
        "pdp-engine/pom.xml":
        "candidates/built/poms/pdp-engine-pom.xml",
        "dependency_hashes.json": "candidates/dependency_hashes.json",
    }
    with open(os.path.join(dest, "candidates", "path_remap.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump({"mappings": remap,
                   "note": "manifest repo-paths (clone- or repo-relative) "
                           "to launch-packet paths"}, handle, indent=2,
                  sort_keys=True)
        handle.write("\n")
    composite = json.dumps(
        {"components": staged_manifest["components"],
         "exclusions": staged_manifest["exclusions"]},
        sort_keys=True, ensure_ascii=True,
        separators=(", ", ": ")).encode("utf-8")
    staged_manifest["pre_hash"] = hashlib.sha256(composite).hexdigest()
    staged_manifest["refresh_note"] = (
        "Launch-revision %s: drivers rebound to staged packet bytes "
        "(prior %s preserved in lineage history); dependency_content "
        "added; composite recomputed." % (args.launch_id, prior_pre[:16]))
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(staged_manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:lfz:012] staged manifest refreshed pre=%s" % (
        staged_manifest["pre_hash"][:16]), flush=True)
    with open(os.path.join(dest, "candidates", "pre_hash_lineage.json"),
              encoding="utf-8") as handle:
        lineage = json.load(handle)
    operative = staged_manifest["pre_hash"]
    seen = {entry.get("pre_hash") for entry in
            lineage.get("history", [])}
    old_current = lineage.get("current", {})
    if old_current.get("pre_hash") not in (prior_pre, operative) and \
            old_current.get("pre_hash") not in seen:
        lineage.setdefault("history", []).append({
            "pre_hash": old_current.get("pre_hash", ""),
            "scope": old_current.get("scope", ""),
            "status": "HISTORICAL (stale current preserved "
                      "transparently at launch %s)" % args.launch_id,
        })
        seen.add(old_current.get("pre_hash"))
    if prior_pre not in seen and prior_pre != operative:
        lineage.setdefault("history", []).append({
            "pre_hash": prior_pre,
            "scope": "pre-refresh operative (superseded at launch %s; "
                     "value preserved)" % args.launch_id,
            "status": "HISTORICAL",
        })
    lineage["current"] = {
        "pre_hash": operative,
        "scope": "launch packet manifest (see lambda_manifest.json)",
    }
    with open(os.path.join(dest, "candidates", "pre_hash_lineage.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(lineage, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:lfz:012] static additions staged", flush=True)
    for tool_rel, staged_rel in (
            ("src/audit/recompute_lambda.py",
             "candidates/recompute_lambda.py"),
            ("src/audit/verify_deployment_set.py",
             "candidates/verify_deployment_set.py"),
            ("src/xacml/build_repaired_requests.py",
             "candidates/builder_source.py"),
            ("src/pc/derive_Lambda.py",
             "candidates/derive_Lambda.py"),
            ("src/xacml/parse_response.py",
             "candidates/parse_response.py"),
            ("src/xacml/run_authzforce.py",
             "candidates/invocation/run_authzforce.py"),
            ("src/xacml/PdpRunner.java",
             "candidates/invocation/PdpRunner.java"),
            ("src/audit/conformance_verify_a.py",
             "candidates/conformance_verify_a.py"),
            ("src/audit/conformance_verify_b.py",
             "candidates/conformance_verify_b.py"),
            ("src/audit/launch_freeze.py",
             "candidates/launch_freeze.py"),
            ("src/audit/launch_certification.py",
             "candidates/launch_certification.py")):
        live = sha256_file(os.path.join(repo_root, *tool_rel.split("/")))
        staged = sha256_file(os.path.join(
            dest, *staged_rel.split("/")))
        if live != staged:
            fail("packet tool copy drifted from live source: " + tool_rel)
    print("[P2:lfz:013] tool-copy currency verified", flush=True)
    manifest_entries = {}
    for base, _dirs, files in os.walk(dest):
        for name in files:
            if name in ("PACKET_MANIFEST.json", "PACKET_SHA256.txt"):
                continue
            path = os.path.join(base, name)
            key = os.path.relpath(path, dest).replace(os.sep, "/")
            manifest_entries[key] = sha256_file(path)
    manifest_json = json.dumps(
        {"packet_id": "PC-XACML-S3PLUS-v1-launch-packet-%s"
         % args.launch_id,
          "sealed_utc": utcnow(), "files": manifest_entries},
        indent=2, sort_keys=True)
    with open(os.path.join(dest, "PACKET_MANIFEST.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(manifest_json)
    packet_sha = hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()
    with open(os.path.join(dest, "PACKET_SHA256.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(packet_sha + "\n")
    print("[P2:lfz:014] launch packet sealed sha=%s" % packet_sha[:16],
          flush=True)
    prompt_path = os.path.join(launch_base(repo_root),
                               "launch_certification_prompt.txt")
    prompt_sha = sha256_file(prompt_path)
    registry_path = os.path.join(launch_base(repo_root),
                                 "run_conformance_obligations.json")
    registry_sha = sha256_file(registry_path)
    code = {rel: sha256_file(os.path.join(repo_root, *rel.split("/")))
            for rel in EXECUTION_CODE}
    try:
        import subprocess as _sp
        _head = _sp.run(["git", "-C", clone, "rev-parse", "HEAD"],
                        capture_output=True, text=True,
                        timeout=60).stdout.strip()
    except OSError:
        _head = ""
    env_binding = {"authzforce_commit": _head}
    try:
        with open(os.path.join(repo_root, "artifacts", "raw",
                               "environment.txt"), encoding="utf-8",
                  errors="replace") as handle:
            for line in handle.read().splitlines():
                if "openjdk version" in line or "Python" in line \
                        or line.startswith("CPython"):
                    env_binding.setdefault("toolchain", []).append(
                        line.strip())
                if len(env_binding.get("toolchain", [])) >= 4:
                    break
    except OSError:
        pass
    try:
        import importlib.metadata as _md
        env_binding["lxml"] = _md.version("lxml")
    except Exception:
        pass
    record = {
        "launch_id": "PC-XACML-S3PLUS-v1-launch-%s" % args.launch_id,
        "semantic_revision": 4,
        "frozen": True,
        "packet_sha256": packet_sha,
        "prompt_sha256": prompt_sha,
        "registry_sha256": registry_sha,
        "execution_code": code,
        "environment": env_binding,
        "panel": [part.strip() for part in
                  args.panel_ids.split(",") if part.strip()],
        "completed_executions": 0,
        "supersedes": args.supersedes,
        "frozen_utc": utcnow(),
    }
    with open(os.path.join(launch_base(repo_root), "LAUNCH_FREEZE.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("[P2:lfz:016] launch freeze sealed", flush=True)


def cmd_verify_launch(args):
    """Re-verify a sealed launch freeze against live bytes."""
    # [P2-LOG-020] Step: verify launch integrity.
    print("[P2:lfz:020] verifying launch integrity", flush=True)
    repo_root = os.path.abspath(args.repo_root)
    base = launch_base(repo_root)
    with open(os.path.join(base, "LAUNCH_FREEZE.json"),
              encoding="utf-8") as handle:
        record = json.load(handle)
    dest = packet_dir(repo_root)
    with open(os.path.join(dest, "PACKET_MANIFEST.json"),
              encoding="utf-8") as handle:
        manifest = json.load(handle)
    for key, digest in manifest.get("files", {}).items():
        with open(os.path.join(dest, *key.split("/")), "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        if actual != digest:
            fail("launch packet file drifted: " + key)
    manifest_json = json.dumps(
        {"packet_id": manifest.get("packet_id"),
         "sealed_utc": manifest.get("sealed_utc"),
         "files": manifest.get("files", {})},
        indent=2, sort_keys=True)
    with open(os.path.join(dest, "PACKET_SHA256.txt"),
              encoding="utf-8") as handle:
        aggregate = handle.read().strip()
    if hashlib.sha256(manifest_json.encode("utf-8")).hexdigest() \
            != aggregate:
        fail("launch packet aggregate mismatch")
    if aggregate != record.get("packet_sha256"):
        fail("launch packet differs from launch record")
    if sha256_file(os.path.join(base, "launch_certification_prompt.txt")) \
            != record.get("prompt_sha256"):
        fail("launch prompt drifted")
    if sha256_file(os.path.join(base, "run_conformance_obligations.json")) \
            != record.get("registry_sha256"):
        fail("registry drifted")
    for rel, digest in record.get("execution_code", {}).items():
        if sha256_file(os.path.join(repo_root, *rel.split("/"))) != digest:
            fail("execution code drifted: " + rel)
    live_files = set()
    for base_dir, _dirs, files in os.walk(dest):
        for name in files:
            if name in ("PACKET_MANIFEST.json", "PACKET_SHA256.txt"):
                continue
            live_files.add(os.path.relpath(
                os.path.join(base_dir, name), dest).replace(os.sep, "/"))
    if live_files != set(manifest.get("files", {})):
        fail("launch packet extra/missing files: %s" % sorted(
            live_files.symmetric_difference(set(manifest.get("files", {})))))
    with open(os.path.join(dest, "candidates", "lambda_manifest.json"),
              encoding="utf-8") as handle:
        staged_manifest = json.load(handle)
    composite = json.dumps(
        {"components": staged_manifest["components"],
         "exclusions": staged_manifest["exclusions"]},
        sort_keys=True, ensure_ascii=True,
        separators=(", ", ": ")).encode("utf-8")
    if hashlib.sha256(composite).hexdigest() != \
            staged_manifest.get("pre_hash"):
        fail("staged manifest composite does not recompute")
    inv_map = {"src/xacml/PdpRunner.java":
               "candidates/invocation/PdpRunner.java",
               "src/xacml/run_authzforce.py":
               "candidates/invocation/run_authzforce.py"}
    for entry in staged_manifest["components"]["built_artifacts"][
            "drivers"]:
        staged_rel = inv_map.get(entry.get("path", ""))
        if not staged_rel:
            fail("manifest driver without staged bytes: %s"
                 % entry.get("path", "?"))
        staged_file = os.path.join(dest, *staged_rel.split("/"))
        if sha256_file(staged_file) != entry.get("sha256") or \
                os.path.getsize(staged_file) != entry.get("bytes"):
            fail("staged manifest driver drifted from staged bytes: %s"
                 % entry.get("path", "?"))
    with open(os.path.join(dest, "candidates", "pre_hash_lineage.json"),
              encoding="utf-8") as handle:
        staged_lineage = json.load(handle)
    if staged_lineage.get("current", {}).get("pre_hash") != \
            staged_manifest.get("pre_hash"):
        fail("staged lineage current does not match staged operative")
    if os.path.isfile(os.path.join(repo_root, "artifacts", "seal",
                                   "TARGET_EXECUTION_LOCK.json")):
        fail("execution lock sealed; launch verify forbidden post-invocation")
    print("[P2:lfz:022] launch integrity confirmed", flush=True)


def judge_conformance(verdict_a_path, verdict_b_path, launch_base):
    """Compare dual-verifier outputs; seal exactly one outcome record."""
    # [P2-LOG-034] Step: judge conformance (mechanical, not semantic).
    print("[P2:lfz:034] judging conformance", flush=True)
    with open(verdict_a_path, encoding="utf-8") as handle:
        verdict_a = json.load(handle)
    with open(verdict_b_path, encoding="utf-8") as handle:
        verdict_b = json.load(handle)
    if verdict_a.get("verdicts") != verdict_b.get("verdicts"):
        outcome = "EXECUTION_CONFORMANCE_VERIFIER_MISMATCH"
    elif verdict_a.get("overall") != verdict_b.get("overall"):
        outcome = "EXECUTION_CONFORMANCE_VERIFIER_MISMATCH"
    elif set(verdict_a.get("verdicts", {})) != set(
            verdict_b.get("verdicts", {})):
        outcome = "EXECUTION_CONFORMANCE_VERIFIER_MISMATCH"
    else:
        try:
            with open(os.path.join(launch_base,
                                   "run_conformance_obligations.json"),
                      encoding="utf-8") as handle:
                expected_ids = sorted(
                    entry.get("obligation_id", "")
                    for entry in json.load(handle).get("obligations", []))
        except (OSError, ValueError, AttributeError):
            expected_ids = None
        if expected_ids is None:
            outcome = "EXECUTION_CONFORMANCE_UNVERIFIABLE"
        elif expected_ids and sorted(verdict_a.get("verdicts", {})) != \
                expected_ids:
            outcome = "EXECUTION_CONFORMANCE_UNVERIFIABLE"
        else:
            values = verdict_a.get("verdicts", {})
            if not values:
                outcome = "EXECUTION_CONFORMANCE_UNVERIFIABLE"
            elif all(value == "SATISFIED" for value in values.values()):
                outcome = "RUN_CONFORMANCE_PASSED"
            elif any(value == "FAILED" for value in values.values()):
                outcome = "EXECUTION_CONFORMANCE_FAIL"
            else:
                outcome = "EXECUTION_CONFORMANCE_UNVERIFIABLE"
    record = {"verdict": outcome, "judged_utc": utcnow(),
              "verdict_a_sha256": sha256_file(verdict_a_path),
              "verdict_b_sha256": sha256_file(verdict_b_path)}
    os.makedirs(launch_base, exist_ok=True)
    name = {"RUN_CONFORMANCE_PASSED": "RUN_CONFORMANCE_PASS.json"}.get(
        outcome, "RUN_CONFORMANCE_%s.json" % outcome)
    with open(os.path.join(launch_base, name), "w", encoding="utf-8",
               newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    if outcome != "RUN_CONFORMANCE_PASSED":
        stale = os.path.join(launch_base, "RUN_CONFORMANCE_PASS.json")
        try:
            if os.path.isfile(stale):
                os.remove(stale)
        except OSError:
            fail("cannot revoke stale conformance pass")
    print("[P2:lfz:036] conformance outcome=%s" % outcome, flush=True)
    return outcome


def cmd_status(args):
    """Print launch status."""
    """Print launch status."""
    # [P2-LOG-030] Step: report launch status.
    # [P2-LOG-030] Step: report launch status.
    repo_root = os.path.abspath(args.repo_root)
    base = launch_base(repo_root)
    record_path = os.path.join(base, "LAUNCH_FREEZE.json")
    if os.path.isfile(record_path):
        with open(record_path, encoding="utf-8") as handle:
            record = json.load(handle)
        print("[P2:lfz:032] launch frozen packet=%s panel=%s" % (
            record.get("packet_sha256", "")[:16],
            ",".join(record.get("panel", []))), flush=True)
    else:
        print("[P2:lfz:032] no launch freeze", flush=True)


def main(argv=None):
    """Entry point: dispatch launch-freeze operations."""
    # [P2-LOG-040] Step: dispatch launch mode.
    print("[P2:lfz:040] launch freeze invoked", flush=True)
    parser = argparse.ArgumentParser(description="Launch freeze.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--build-launch-packet", action="store_true")
    parser.add_argument("--verify-launch", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--launch-id", default="001")
    parser.add_argument("--panel-ids", default="AUD-L01,AUD-L02,AUD-L03")
    parser.add_argument("--supersedes", default="")
    args = parser.parse_args(argv)
    if args.build_launch_packet:
        cmd_build_packet(args)
    elif args.verify_launch:
        cmd_verify_launch(args)
    elif args.status:
        cmd_status(args)
    else:
        fail("no launch operation given")
    # [P2-LOG-042] Step: launch operation complete.
    print("[P2:lfz:042] launch operation complete", flush=True)


if __name__ == "__main__":
    main()
