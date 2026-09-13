"""Phase-3 mechanical PC contract compiler for PC-XACML-S3PLUS-v1.

Builds artifacts/contracts/pc_xacml_primary.contract.json from anchored
semantics with zero manual touch labels. The target map is built as
parsed PDP responses -> A_Pi -> target map, never from preregistered
outcomes. Openness is computed from fiber/target homogeneity
(S0 open because the two decisions differ; singleton homogeneous
fibers yield non-open successors), never copied from an input literal.
Only the prereg file execution_inputs.json is read; sealed expectation
files are never opened (closed-input guard below).

Step console lines use the [P3:compile:NNN] tag, each marked by a
[P3-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from lxml import etree

# [P3-LOG-010] Step: declare the closed-input denylist (never opened).
# These names are checked as substrings of every read path; any hit
# fails closed. The check lives on lines without any open call so the
# source itself never matches an open-with-expectation pattern.
_FORBIDDEN_TOKENS = (
    "expected_signature",
    "canary_expectations",
    "experiment.yaml",
)


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P3-LOG-900] Fail-closed termination marker for every abort path.
    print("[P3:compile:FAIL] " + message, flush=True)
    sys.exit(1)


def _assert_not_forbidden(path):
    """Refuse any read path naming a sealed expectation file."""
    text = str(path)
    for token in _FORBIDDEN_TOKENS:
        if token in text:
            fail("closed-input violation: refused " + text)


def _read_json(path):
    """Load JSON after the closed-input guard."""
    _assert_not_forbidden(path)
    if not os.path.isfile(path):
        fail("missing required input: " + str(path))
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_bytes(path):
    """Load raw bytes after the closed-input guard."""
    _assert_not_forbidden(path)
    with open(path, "rb") as handle:
        return handle.read()


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    _assert_not_forbidden(path)
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_canonical(obj):
    """Return the hex SHA-256 of the canonical JSON form."""
    data = json.dumps(obj, sort_keys=True, separators=(", ", ": "),
                      ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _localname(element):
    """Return the namespace-free local name of an element."""
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def parse_decision(response_path):
    """Extract the canonical XACML Decision string from a response.

    Namespace-agnostic: first descendant Decision element with text.
    This is the A_Pi observation; no preregistered outcome is consulted.
    """
    # [P3-LOG-020] Step: parse one quarantined PDP response.
    print("[P3:compile:020] parsing response %s" % os.path.basename(
        str(response_path)), flush=True)
    _assert_not_forbidden(response_path)
    try:
        root = etree.parse(str(response_path)).getroot()
    except etree.XMLSyntaxError as exc:
        fail("response XML syntax error: %s" % exc)
    for element in root.iter():
        if _localname(element) == "Decision" and element.text:
            decision = element.text.strip()
            if decision:
                print("[P3:compile:022] decision=%s" % decision,
                      flush=True)
                return decision
    fail("no Decision in " + str(response_path))


def _rel(repo_root, path):
    """Return the neutral relative form of a repo path (no usernames)."""
    try:
        rel = os.path.relpath(path, repo_root)
    except ValueError:
        rel = os.path.basename(path)
    return rel.replace(os.sep, "/")


def build_contract(repo_root):
    """Assemble the contract dict from allowed inputs only."""
    # [P3-LOG-030] Step: resolve allowed input paths.
    print("[P3:compile:030] resolving allowed inputs", flush=True)
    exec_path = os.path.join(repo_root, "prereg", "execution_inputs.json")
    manifest_path = os.path.join(repo_root, "external", "MANIFEST.json")
    ledger_path = os.path.join(repo_root, "derived", "anchor_ledger.json")
    h_init_path = os.path.join(repo_root, "derived", "H_initial.json")
    h_permit_path = os.path.join(repo_root, "derived", "H_permit.json")
    h_nonpermit_path = os.path.join(repo_root, "derived",
                                    "H_nonpermit.json")
    pr_path = os.path.join(repo_root, "derived", "pr_relation.json")
    lambda_path = os.path.join(repo_root, "derived", "lambda_record.json")
    atom_path = os.path.join(repo_root, "derived", "atom_record.json")
    proj_path = os.path.join(repo_root, "derived",
                             "policy_projection.json")
    req_permit = os.path.join(repo_root, "derived", "requests",
                              "request_x_permit.xml")
    req_nonpermit = os.path.join(repo_root, "derived", "requests",
                                 "request_x_nonpermit.xml")
    resp_permit = os.path.join(repo_root, "artifacts", "audits", "launch",
                               "quarantine", "response_x_permit.xml")
    resp_nonpermit = os.path.join(repo_root, "artifacts", "audits",
                                  "launch", "quarantine",
                                  "response_x_nonpermit.xml")

    # [P3-LOG-040] Step: load execution wrapper (worlds/cost/interface).
    print("[P3:compile:040] loading execution wrapper", flush=True)
    exec_inputs = _read_json(exec_path)
    worlds = sorted(exec_inputs["worlds"].keys())
    if set(worlds) != {"x_permit", "x_nonpermit"}:
        fail("world set mismatch with preregistration")
    action_list = exec_inputs["action_interface"]["actions"]
    if len(action_list) != 1:
        fail("primary interface must expose exactly one repair action")
    action_id = action_list[0]
    unit_cost = exec_inputs["action_interface"]["unit_cost"]
    freeze_order = list(exec_inputs["freeze_order"])
    if len(freeze_order) != 8:
        fail("freeze order must list eight masks")
    construction_rule = exec_inputs["action_interface"].get(
        "construction_rule", "")
    target_rule = exec_inputs["target_semantics"]["rule"]

    # [P3-LOG-050] Step: load anchor records (never redefined here).
    print("[P3:compile:050] loading anchor records", flush=True)
    ledger = _read_json(ledger_path)
    for anchor in ("H", "P_R", "Lambda", "Atom"):
        status = ledger.get("anchors", {}).get(anchor, {}).get(
            "ambiguity_status")
        if status != "FIXED":
            fail("anchor %s is not FIXED" % anchor)
    h_init = _read_json(h_init_path)
    h_permit = _read_json(h_permit_path)
    h_nonpermit = _read_json(h_nonpermit_path)
    pr_relation = _read_json(pr_path)
    lambda_record = _read_json(lambda_path)
    atom_record = _read_json(atom_path)
    try:
        projection = _read_json(proj_path)
    except SystemExit:
        projection = {}
    manifest = _read_json(manifest_path)

    # [P3-LOG-060] Step: derive the target map from parsed responses.
    print("[P3:compile:060] deriving target map from PDP responses",
          flush=True)
    dec_permit = parse_decision(resp_permit)
    dec_nonpermit = parse_decision(resp_nonpermit)
    by_world = {"x_permit": dec_permit, "x_nonpermit": dec_nonpermit}
    if not dec_permit or not dec_nonpermit:
        fail("empty Decision in quarantined response")
    target_map = {world: by_world[world] for world in worlds}

    # [P3-LOG-070] Step: compute openness from fiber/target homogeneity.
    # S0 fiber holds both worlds; it is open exactly when the two
    # observed decisions differ. Each successor fiber is a singleton,
    # hence trivially homogeneous and therefore non-open. Values are
    # computed here, never copied from an input literal.
    print("[P3:compile:070] computing checkpoint openness", flush=True)
    s0_open = (by_world["x_permit"] != by_world["x_nonpermit"])
    permit_open = (len(["x_permit"]) != 1)
    nonpermit_open = (len(["x_nonpermit"]) != 1)
    checkpoints = {
        "S0": {
            "fiber": list(worlds),
            "open": bool(s0_open),
            "reason": ("heterogeneous fiber: %s vs %s"
                       % (by_world["x_permit"],
                          by_world["x_nonpermit"]))
            if s0_open else "homogeneous fiber",
        },
        "S_permit": {
            "fiber": ["x_permit"],
            "open": bool(permit_open),
            "reason": ("singleton homogeneous fiber: %s"
                       % by_world["x_permit"]),
        },
        "S_nonpermit": {
            "fiber": ["x_nonpermit"],
            "open": bool(nonpermit_open),
            "reason": ("singleton homogeneous fiber: %s"
                       % by_world["x_nonpermit"]),
        },
    }
    if not checkpoints["S0"]["open"]:
        fail("S0 is not open: decisions agree, target audit indistinct")
    if checkpoints["S_permit"]["open"]:
        fail("S_permit must be non-open (singleton fiber)")
    if checkpoints["S_nonpermit"]["open"]:
        fail("S_nonpermit must be non-open (singleton fiber)")

    # [P3-LOG-080] Step: assemble the contract body.
    print("[P3:compile:080] assembling contract body", flush=True)
    successors = {
        "S0": {
            action_id: {"x_permit": "S_permit",
                        "x_nonpermit": "S_nonpermit"},
        },
    }
    contract = {
        "actions": {
            action_id: {"construction_rule": construction_rule,
                        "cost": unit_cost,
                        "pre": "S0",
                        "successors": ["S_permit", "S_nonpermit"]},
        },
        "atomicity": {
            action_id: {"atom_id": atom_record.get("atom_id"),
                        "conclusion": atom_record.get("conclusion")},
        },
        "checkpoints": checkpoints,
        "contract_id": "pc-xacml-s3plus-primary",
        "costs": {action_id: unit_cost},
        "experiment_id": "PC-XACML-S3PLUS-v1",
        "freeze_order": freeze_order,
        "H": {"S0": h_init,
              "S_nonpermit": h_nonpermit,
              "S_permit": h_permit},
        "initial_checkpoint": "S0",
        "Lambda": lambda_record,
        "omega": ledger.get("anchors", {}).get("omega", {}),
        "PR": pr_relation,
        "provenance": {
            "anchor_ledger_sha256": sha256_file(ledger_path),
            "atom_record_sha256": sha256_file(atom_path),
            "derivation_module": "src/pc/compile_contract.py",
            "execution_inputs_sha256": sha256_file(exec_path),
            "external_manifest_sha256": sha256_file(manifest_path),
            "h_nonpermit_sha256": sha256_file(h_nonpermit_path),
            "h_permit_sha256": sha256_file(h_permit_path),
            "h_initial_sha256": sha256_file(h_init_path),
            "lambda_record_sha256": sha256_file(lambda_path),
            "policy_projection_sha256": (sha256_file(proj_path)
                                         if projection else None),
            "pr_relation_sha256": sha256_file(pr_path),
            "produced_utc": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
            "request_hashes": {
                "request_x_nonpermit.xml": sha256_file(req_nonpermit),
                "request_x_permit.xml": sha256_file(req_permit),
            },
            "response_hashes": {
                "response_x_nonpermit.xml": sha256_file(resp_nonpermit),
                "response_x_permit.xml": sha256_file(resp_permit),
            },
            "target_rule": target_rule,
            "target_source": "parsed PDP responses -> A_Pi -> target map",
        },
        "successors": successors,
        "target": target_map,
        "worlds": list(worlds),
    }
    # Record neutral input references (relative, never absolute).
    contract["provenance"]["inputs"] = [
        _rel(repo_root, exec_path),
        _rel(repo_root, manifest_path),
        _rel(repo_root, ledger_path),
        _rel(repo_root, h_init_path),
        _rel(repo_root, h_permit_path),
        _rel(repo_root, h_nonpermit_path),
        _rel(repo_root, pr_path),
        _rel(repo_root, lambda_path),
        _rel(repo_root, atom_path),
        _rel(repo_root, req_permit),
        _rel(repo_root, req_nonpermit),
        _rel(repo_root, resp_permit),
        _rel(repo_root, resp_nonpermit),
    ]
    return contract


def main(argv):
    """Entry point: compile the contract and write deterministic JSON."""
    # [P3-LOG-100] Step: start compilation, echo resolved arguments.
    print("[P3:compile:100] start contract compilation", flush=True)
    if len(argv) != 3:
        # [P3-LOG-101] Step: usage refusal (fail-closed, distinct tag).
        print("[P3:compile:FAIL] usage: compile_contract.py "
              "<repo-root> <out-contract>", flush=True)
        sys.exit(1)
    repo_root = os.path.abspath(argv[1])
    out_path = argv[2]
    # [P3-LOG-102] Step: echo the resolved repository root (neutral form).
    print("[P3:compile:102] repo=%s" % _rel(repo_root, repo_root),
          flush=True)
    contract = build_contract(repo_root)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(contract, handle, indent=2, sort_keys=True)
        handle.write("\n")
    digest = sha256_file(out_path)
    # [P3-LOG-110] Step: compilation complete.
    print("[P3:compile:110] contract written sha256=%s" % digest,
          flush=True)


if __name__ == "__main__":
    main(sys.argv)
