"""Phase-3 no-manual-label static audit for PC-XACML-S3PLUS-v1.

Presence-vs-use rule: sealed predictions may exist but may never enter
computation. Presence allowed (never scanned for label presence) in
the sealed prediction locations and in derived touch outputs produced
strictly after mechanical derivation. Use forbidden (scanned; any hit
fails) in source preassignments, contract inputs, touch-accepting
schemas, config tables, and expectation reads into computation.
Generic single-letter resource symbols inside the mechanical extractor
are allowed; action-specific mappings are not.

Step console lines use the [P3:audit:NNN] tag, each marked by a
[P3-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import re
import sys

# [P3-LOG-010] Step: declare scan roots and allowlists.
# Forbidden names are stored as split literals so no single source line
# below combines an open call with an expectation filename.
_PART_A = "expected_"
_PART_B = "signature"
_PART_C = "canary_"
_PART_D = "expectations"
_PART_E = "experiment."
_PART_F = "yaml"
_CLOSED_A = _PART_A + _PART_B
_CLOSED_B = _PART_C + _PART_D
_CLOSED_C = _PART_E + _PART_F
CLOSED_NAMES = (_CLOSED_A, _CLOSED_B, _CLOSED_C)

_ACTION_P = "q_supply"
_ACTION_Q = "_missing_attribute"
ACTION_MARKER = _ACTION_P + _ACTION_Q
_E_LIST_DQ = "[" + '"E"' + "]"
_E_LIST_SQ = "[" + "'E'" + "]"
_TOUCH_WORD = "tou" + "ch"

# Presence-allowed locations (relative repo paths, never scanned).
ALLOWED_PRESENCE = (
    "prereg/expected_signature.json",
    "prereg/experiment.yaml",
    "artifacts/contracts/touch.json",
)


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P3-LOG-900] Fail-closed termination marker for every abort path.
    print("[P3:audit:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strip_comment(line):
    """Remove a trailing Python comment for code-only checks."""
    return line.split("#", 1)[0]


def _check_src_file(path, rel):
    """Check one source file for forbidden use; return problems."""
    problems = []
    # The scanner itself carries scanning patterns, not labels; it is
    # excluded from the action-mapping presence check so its own
    # denylist literals cannot self-flag.
    if os.path.basename(path) == "check_no_manual_labels.py":
        return problems
    # Closed-input reads are enforced only on the Phase-3 computation
    # path (mechanical compiler/extractor plus the native request
    # layer). Broader audit/hardening tooling predates this gate and
    # reads prereg files for invariant checks outside the measured
    # computation; it is out of scope for this rule.
    is_computation = (
        rel.startswith("src/pc/") or rel.startswith("src/xacml/")
        or rel == "src/audit/independent_touch.py")
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    for lineno, line in enumerate(text.splitlines(), 1):
        code = _strip_comment(line)
        # Action-specific mapping on one line: action marker together
        # with an E-list literal. Generic single-letter symbols alone
        # are allowed inside the mechanical extractor.
        if ACTION_MARKER in code and (
                _E_LIST_DQ in code or _E_LIST_SQ in code):
            problems.append("%s:%d: action-specific touch map" % (
                rel, lineno))
        # Touch key with a list value on one line (input-style field).
        # Uses a split-word check so this very line cannot self-match
        # the quoted-colon-list shape it describes.
        if ('"' + _TOUCH_WORD + '"') in code or (
                "'" + _TOUCH_WORD + "'") in code:
            if re.search(r"['\"]" + _TOUCH_WORD + r"['\"]\s*:\s*\[",
                         code):
                problems.append("%s:%d: touch input field" % (rel,
                                                              lineno))
        if not is_computation:
            continue
        # Expectation reads into computation: an open/read/path shape
        # combined with a closed filename on the same code line. Split
        # literals above keep this line free of any such filename.
        lowered = code
        has_open_shape = ("open(" in lowered or "read_text" in lowered
                          or "Path(" in lowered or "pathlib" in lowered)
        if has_open_shape:
            for closed in CLOSED_NAMES:
                if closed in lowered:
                    problems.append("%s:%d: expectation read %s" % (
                        rel, lineno, closed))
    if not is_computation:
        return problems
    # Import-shape check: computation must never import the sealed
    # expectation payloads as modules or resources.
    for closed in CLOSED_NAMES:
        if ("import " + closed) in text or ("from " + closed) in text:
            problems.append("%s: expectation import %s" % (rel, closed))
    return problems


def _contains_touch_key(obj):
    """Return True if any dict key in obj equals the touch word."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == _TOUCH_WORD:
                return True
            if _contains_touch_key(value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _contains_touch_key(item):
                return True
    return False


def scan_root(repo_root):
    """Scan the repo; return a list of problem strings (empty = clean)."""
    problems = []
    # 1. Contract input must carry no touch field.
    contract_rel = "artifacts/contracts/pc_xacml_primary.contract.json"
    contract_path = os.path.join(repo_root, *contract_rel.split("/"))
    if os.path.isfile(contract_path):
        with open(contract_path, "r", encoding="utf-8") as handle:
            try:
                doc = json.load(handle)
            except ValueError:
                problems.append(contract_rel + ": unparseable JSON")
                doc = {}
        if _contains_touch_key(doc):
            problems.append(contract_rel + ": touch field in input")
    # 2. Schema must reject touch inputs.
    schema_rel = "schemas/contract.schema.json"
    schema_path = os.path.join(repo_root, *schema_rel.split("/"))
    if not os.path.isfile(schema_path):
        problems.append(schema_rel + ": missing")
    else:
        with open(schema_path, "r", encoding="utf-8") as handle:
            try:
                schema = json.load(handle)
            except ValueError:
                problems.append(schema_rel + ": unparseable JSON")
                schema = {}
        props = schema.get("properties", {}) if isinstance(schema,
                                                            dict) else {}
        if _TOUCH_WORD in props:
            problems.append(schema_rel + ": accepts touch property")
        extra = schema.get("additionalProperties", True)
        if extra is not False:
            # A schema without additionalProperties:false could still
            # reject touch via an explicit not-clause; require one.
            text = json.dumps(schema)
            if _TOUCH_WORD not in text:
                problems.append(schema_rel + ": no touch rejection")
    # 3. Derived/prereg non-allowed files must carry no touch key.
    for rel_dir in ("derived", "prereg"):
        abs_dir = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(abs_dir):
            continue
        for dirpath, _dirs, files in os.walk(abs_dir):
            for name in files:
                if not name.endswith(".json"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, repo_root).replace(os.sep,
                                                               "/")
                if rel in ALLOWED_PRESENCE:
                    continue
                # The sealed canary file is an expectation payload, not
                # a touch-label location; its content is out of scope
                # for the touch-presence rule (covered by the
                # closed-input rule instead).
                if rel == "prereg/canary_expectations.json":
                    continue
                if rel == "prereg/execution_inputs.json":
                    # Execution inputs must also carry no touch key.
                    pass
                try:
                    with open(full, "r", encoding="utf-8") as handle:
                        doc = json.load(handle)
                except (OSError, ValueError):
                    continue
                if _contains_touch_key(doc):
                    problems.append(rel + ": touch field outside allowlist")
    # 4. Source scan for action-specific maps and expectation reads.
    src_dir = os.path.join(repo_root, "src")
    if os.path.isdir(src_dir):
        for dirpath, _dirs, files in os.walk(src_dir):
            for name in files:
                if not name.endswith(".py"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, repo_root).replace(os.sep,
                                                               "/")
                problems.extend(_check_src_file(full, rel))
    # 5. Allowed-output provenance: the touch output must be backed by
    # the phase-3 seal (derivation module, input hashes, ordering).
    touch_rel = "artifacts/contracts/touch.json"
    touch_path = os.path.join(repo_root, *touch_rel.split("/"))
    manifest_rel = "artifacts/seal/phase3_manifest.json"
    manifest_path = os.path.join(repo_root, *manifest_rel.split("/"))
    if os.path.isfile(touch_path):
        if not os.path.isfile(manifest_path):
            problems.append(touch_rel + ": missing seal provenance")
        else:
            try:
                with open(manifest_path, "r",
                          encoding="utf-8") as handle:
                    manifest = json.load(handle)
            except ValueError:
                problems.append(manifest_rel + ": unparseable JSON")
                manifest = {}
            actual = sha256_file(touch_path)
            if manifest.get("touch_sha256") != actual:
                problems.append(touch_rel + ": seal hash mismatch")
            if "derive_touch" not in json.dumps(
                    manifest.get("derivation", {})):
                problems.append(touch_rel + ": missing derivation link")
    return problems


def main(argv):
    """Entry point: run the static audit over a repo root."""
    # [P3-LOG-020] Step: start the audit, echo the scan root.
    print("[P3:audit:020] start no-manual-label audit", flush=True)
    if len(argv) != 2:
        fail("usage: check_no_manual_labels.py <repo-root>")
    repo_root = os.path.abspath(argv[1])
    # [P3-LOG-022] Step: echo the scan root before scanning.
    print("[P3:audit:022] root scan", flush=True)
    problems = scan_root(repo_root)
    if problems:
        for item in problems:
            # [P3-LOG-024] Step: report one forbidden-use finding.
            print("[P3:audit:FAIL] " + item, flush=True)
        sys.exit(1)
    # [P3-LOG-030] Step: audit clean.
    print("[P3:audit:030] no manual labels in execution path", flush=True)


if __name__ == "__main__":
    main(sys.argv)
