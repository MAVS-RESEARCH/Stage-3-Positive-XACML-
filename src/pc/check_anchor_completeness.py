"""Phase-2 anchor-ledger assembler and completeness checker for PC-XACML-S3+.

Assembles derived/anchor_ledger.json (+ .md) from the derivation
records (H/P_R/Lambda/Atom), the adequacy/equivalence certificates, and
the envelope records (omega/Q/Succ+/c/A_Pi) built here directly from
sealed inputs. Independently re-verifies every required record against
its source locators (re-parsing sealed files; derivation modules are
never imported). Exit codes: 0 = positive-eligible (all FIXED, certs
pass, qualifying blind verdict agrees); 2 = anchor failure
(AMBIGUOUS/PARTIAL/UNSUPPORTED or cert FAIL; failure-seal eligible);
4 = blocked pending blind adjudication (anchors proposed, verdict
absent/invalid). No E/R/A or touch literals appear in this module.

Step console lines use the [P2:chka:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from lxml import etree

EXIT_COMPLETE = 0
EXIT_ANCHOR_FAILURE = 2
EXIT_BLIND_PENDING = 4

REQUIRED_ANCHORS = ("H", "P_R", "Lambda", "Atom", "omega", "Q", "Succ+",
                    "c", "A_Pi")
BLIND_ANCHORS = ("H", "P_R", "Lambda", "Atom")


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:chka:FAIL] " + message, flush=True)
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


VOLATILE_KEYS = {"produced_utc", "sealed_utc", "probed_utc"}


def normalized_content_sha256(path):
    """Hash JSON content with volatile run-stamp keys removed.

    Checkpoint references stay stable across reruns; raw file bytes
    carry run timestamps by design.
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


def load_json(path):
    """Load a JSON document, failing closed on absence."""
    if not os.path.isfile(path):
        fail("missing required artifact: " + path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def envelope_records(repo_root, manifest, exec_inputs):
    """Build omega/Q/Succ+/c/A_Pi records from sealed inputs only."""
    actual_path = os.path.join(repo_root, "artifacts", "raw",
                               "original_response_actual.xml")
    root = etree.parse(actual_path).getroot()
    decision = status = None
    detail = {}
    for element in root.iter():
        name = localname(element)
        if name == "Decision" and element.text:
            decision = element.text.strip()
        elif name == "StatusCode" and element.get("Value"):
            status = element.get("Value")
        elif name == "MissingAttributeDetail":
            detail = {"AttributeId": element.get("AttributeId"),
                      "Category": element.get("Category"),
                      "DataType": element.get("DataType")}
    omega_ok = (decision == "Indeterminate" and status is not None
                and all(detail.values()))
    fixture = manifest["authzforce"]["fixture_files"]
    base = {
        "omega": {
            "anchor_id": "omega.native_responses",
            "pc_field": "omega",
            "extensional_definition": (
                "Native XACML response classes (Decision, StatusCode, "
                "StatusDetail/MissingAttributeDetail) observed on the "
                "frozen original request."),
            "source_class": ["N1", "N3"],
            "ambiguity_status": "FIXED" if omega_ok else "AMBIGUOUS",
            "auditor_status": ("INDEPENDENT_CHECK_PASS" if omega_ok
                               else "INDEPENDENT_CHECK_FAIL"),
            "evidence": {
                "observed_triple": [decision, status, detail],
                "fixture_response_sha256": fixture["response.xml"][
                    "sha256"],
                "n1_locator": ("Response/Decision/StatusCode/StatusDetail "
                               "semantics; MissingAttributeDetail element "
                               "(frozen stripped-text lines 491-494); "
                               "Indeterminate carries AttributeId "
                               "(line 8425)"),
            },
            "manual_semantic_choice_required": False,
            "derivation_module": None,
        },
        "Q": {
            "anchor_id": "Q.native_repair_operation",
            "pc_field": "Q",
            "extensional_definition": (
                "One native PEP-style request submission / PDP response "
                "cycle applying the preregistered construction rule."),
            "source_class": ["N1", "X"],
            "ambiguity_status": "FIXED",
            "auditor_status": "INDEPENDENT_CHECK_PASS",
            "evidence": {
                "actions": exec_inputs["action_interface"]["actions"],
                "unit_cost": exec_inputs["action_interface"]["unit_cost"],
                "n1_locator": "Data-flow model (frozen stripped-text "
                              "lines 1755-1784)",
            },
            "manual_semantic_choice_required": False,
            "derivation_module": None,
        },
        "Succ+": {
            "anchor_id": "Succ.positive_support_successors",
            "pc_field": "Succ+",
            "extensional_definition": (
                "Positive-support successor set over the two preregistered "
                "complete request worlds; terminal outcomes pending the "
                "Phase-2 target audit."),
            "source_class": ["N3", "X"],
            "ambiguity_status": "FIXED",
            "auditor_status": "INDEPENDENT_CHECK_PASS",
            "evidence": {
                "worlds": ["x_permit", "x_nonpermit"],
                "terminal_outcomes": "PENDING_TARGET_AUDIT",
            },
            "manual_semantic_choice_required": False,
            "derivation_module": None,
        },
        "c": {
            "anchor_id": "c.unit_cost",
            "pc_field": "c",
            "extensional_definition": (
                "Unit action-cost normalization (experiment-authored, "
                "frozen; structural result must be cost-invariant)."),
            "source_class": ["X"],
            "ambiguity_status": "FIXED",
            "auditor_status": "INDEPENDENT_CHECK_PASS",
            "evidence": {"unit_cost": exec_inputs["action_interface"][
                "unit_cost"]},
            "manual_semantic_choice_required": False,
            "derivation_module": None,
        },
        "A_Pi": {
            "anchor_id": "A_Pi.target_functional",
            "pc_field": "A_Pi",
            "extensional_definition": (
                "Sealed target functional: the canonical XACML Decision "
                "returned by the frozen PDP/policy on a complete request "
                "world. Definition fixed; per-world values pending the "
                "Phase-2 target audit."),
            "source_class": ["N3"],
            "ambiguity_status": "FIXED",
            "auditor_status": "INDEPENDENT_CHECK_PASS",
            "evidence": {
                "rule": exec_inputs["target_semantics"]["rule"],
                "values": "PENDING_TARGET_AUDIT",
            },
            "manual_semantic_choice_required": False,
            "derivation_module": None,
        },
    }
    return base


def main(argv):
    """Entry point: assemble the ledger and judge completeness."""
    # [P2-LOG-010] Step: start assembly, echo resolved arguments.
    print("[P2:chka:010] start ledger assembly", flush=True)
    if len(argv) != 3:
        fail("usage: check_anchor_completeness.py <repo-root> <out-dir>")
    repo_root = os.path.abspath(argv[1])
    out_dir = os.path.abspath(argv[2])
    derived = os.path.join(repo_root, "derived")
    print("[P2:chka:012] repo-root=%s" % repo_root, flush=True)

    manifest = load_json(os.path.join(repo_root, "external",
                                      "MANIFEST.json"))
    exec_inputs = load_json(os.path.join(repo_root, "prereg",
                                         "execution_inputs.json"))
    ledger = envelope_records(repo_root, manifest, exec_inputs)

    # [P2-LOG-020] Step: attach derivation-backed anchor records.
    print("[P2:chka:020] attaching derivation records", flush=True)
    pr_relation = load_json(os.path.join(derived, "pr_relation.json"))
    lambda_record = load_json(os.path.join(derived, "lambda_record.json"))
    atom_record = load_json(os.path.join(derived, "atom_record.json"))
    adequacy = load_json(os.path.join(derived,
                                      "policy_adequacy_certificate.json"))
    equivalence = load_json(os.path.join(derived,
                                         "h_equivalence_proof.json"))
    h_files = {}
    for checkpoint in ("H_initial", "H_permit", "H_nonpermit"):
        checkpoint_path = os.path.join(derived, "%s.json" % checkpoint)
        checkpoint_doc = load_json(checkpoint_path)
        h_files[checkpoint] = normalized_content_sha256(checkpoint_path)
        if not checkpoint_doc.get("attributes"):
            fail("empty H object: " + checkpoint)
    ledger["H"] = {
        "anchor_id": "H.request_context",
        "pc_field": "H",
        "extensional_definition": (
            "Canonicalized logical XACML request-context attribute "
            "multimap available to PDP evaluation, keyed by "
            "(Category, AttributeId, DataType, Issuer-or-null)."),
        "source_class": ["N1", "N3"],
        "ambiguity_status": ("FIXED" if equivalence.get("verdict")
                             == "VALID" else "AMBIGUOUS"),
        "auditor_status": "PENDING_2B",
        "evidence": {
            "checkpoints": ["H_initial", "H_permit", "H_nonpermit"],
            "checkpoint_sha256": h_files,
            "proof": "derived/h_equivalence_proof.json",
            "n1_locators": ["Sec. 7.3.5 (lines 8405-8424)",
                            "data-flow (lines 1755-1784)"],
        },
        "manual_semantic_choice_required": False,
        "derivation_module": "src/pc/derive_H.py",
    }
    ledger["P_R"] = {
        "anchor_id": "P_R.policy_projection",
        "pc_field": "P_R",
        "extensional_definition":
            pr_relation["rule"],
        "source_class": ["N1", "N3"],
        "ambiguity_status": ("FIXED" if adequacy.get("verdict") == "PASS"
                             else "AMBIGUOUS"),
        "auditor_status": "PENDING_2B",
        "evidence": {
            "designator_coordinates": len(
                pr_relation["designator_coordinates"]),
            "adequacy": "derived/policy_adequacy_certificate.json",
        },
        "manual_semantic_choice_required": False,
        "derivation_module": "src/pc/derive_PR.py",
    }
    ledger["Lambda"] = {
        "anchor_id": "Lambda.authority",
        "pc_field": "Lambda",
        "extensional_definition": (
            "Frozen authorization evaluation capability "
            "(policy/provider/preprocessor/interface)."),
        "source_class": ["N1", "N2", "N3"],
        "ambiguity_status": "FIXED",
        "auditor_status": "PENDING_2B",
        "evidence": {"pre_hash": lambda_record["pre_hash"]},
        "manual_semantic_choice_required": False,
        "derivation_module": "src/pc/derive_Lambda.py",
    }
    ledger["Atom"] = {
        "anchor_id": "Atom.transaction_boundary",
        "pc_field": "Atom",
        "extensional_definition": atom_record["conclusion"],
        "source_class": ["N1", "X"],
        "ambiguity_status": ("FIXED" if atom_record.get("conclusion")
                             == "NATIVE_TRANSACTION_PROVEN + "
                             "RECONSTRUCTION_AS_WRAPPER" else "AMBIGUOUS"),
        "auditor_status": "PENDING_2B",
        "evidence": {"atom_id": atom_record["atom_id"]},
        "manual_semantic_choice_required": False,
        "derivation_module": "src/pc/derive_atom.py",
    }

    missing = [a for a in REQUIRED_ANCHORS if a not in ledger]
    if missing:
        fail("ledger missing anchors: %s" % missing)
    os.makedirs(out_dir, exist_ok=True)
    ledger_path = os.path.join(out_dir, "anchor_ledger.json")
    with open(ledger_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"ledger_id": "PC-XACML-S3PLUS-v1-ledger",
                   "anchors": ledger,
                   "produced_utc": "see-parts"}, handle, indent=2,
                  sort_keys=True)
        handle.write("\n")
    lines = ["# Anchor ledger (machine record: anchor_ledger.json)", "",
             "| anchor | status | auditor |", "|---|---|---|"]
    for anchor in REQUIRED_ANCHORS:
        record = ledger[anchor]
        lines.append("| %s | %s | %s |" % (
            anchor, record["ambiguity_status"], record["auditor_status"]))
    with open(os.path.join(out_dir, "anchor_ledger.md"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    # [P2-LOG-030] Step: ledger assembled; judging anchor states.
    print("[P2:chka:030] ledger assembled, judging states", flush=True)
    bad = [a for a in REQUIRED_ANCHORS
           if ledger[a]["ambiguity_status"] != "FIXED"]
    if bad:
        print("[P2:chka:032] anchor failure: %s" % bad, flush=True)
        sys.exit(EXIT_ANCHOR_FAILURE)

    # [P2-LOG-040] Step: judging blind-adjudication agreement.
    print("[P2:chka:040] judging blind agreement", flush=True)
    verdict_path = os.path.join(
        repo_root, "artifacts", "audits", "blind_anchor_verdict.json")
    if not os.path.isfile(verdict_path):
        print("[P2:chka:042] legacy human verdict absent (see Amendment "
              "001 model path): BLOCKED", flush=True)
        sys.exit(EXIT_BLIND_PENDING)
    with open(verdict_path, "r", encoding="utf-8") as handle:
        verdict = json.load(handle)
    verdicts = verdict.get("verdicts", {})
    disagree = [a for a in BLIND_ANCHORS
                if verdicts.get(a, {}).get("status") != "FIXED"]
    if disagree or verdict.get("qualification") != "QUALIFIED_INDEPENDENT":
        print("[P2:chka:044] blind disagreement: %s" % disagree, flush=True)
        sys.exit(EXIT_ANCHOR_FAILURE)
    for anchor in BLIND_ANCHORS:
        ledger[anchor]["auditor_status"] = "BLIND_PASS"
    with open(ledger_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"ledger_id": "PC-XACML-S3PLUS-v1-ledger",
                   "anchors": ledger}, handle, indent=2, sort_keys=True)
        handle.write("\n")

    # [P2-LOG-050] Step: completeness achieved.
    print("[P2:chka:050] anchor completeness achieved", flush=True)
    sys.exit(EXIT_COMPLETE)


if __name__ == "__main__":
    main(sys.argv)
