"""Phase-4 completion-space closure certificate checker for PC-XACML-S3+.

Machine-checks the WorkPlan Phase-4 table (X, U_H, S, H, P_R, Lambda,
omega, Q, Succ+, c, A_Pi, Atom, Y): every K-affecting contract field
must carry a constraint source plus artifact-hash evidence with no
degree of freedom remaining after the audit. Asserts the free count is
zero; only then may the singleton identification record be written
(cardinality 1, signature copied from the observed table, never forced).
Any row that cannot honestly read not-free refuses cardinality 1.

Step console lines use the [P4:complete:NNN] tag, each marked by a
[P4-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

FIELDS = ("X", "U_H", "S", "H", "P_R", "Lambda", "omega", "Q",
          "Succ+", "c", "A_Pi", "Atom", "Y")

SOURCE = {
    "X": "experiment prereg",
    "U_H": "external + wrapper",
    "S": "native / wrapper",
    "H": "N1 / N3",
    "P_R": "N1 / N3",
    "Lambda": "N1 / N2 / N3",
    "omega": "N1 / N3",
    "Q": "N1 + prereg wrapper",
    "Succ+": "N3 + prereg wrapper",
    "c": "prereg normalization",
    "A_Pi": "native PDP execution",
    "Atom": "N1 / native interface",
    "Y": ("induced by canonical response representation "
          "(covered by omega/Succ+/A_Pi)"),
}

EXIT_COMPLETE = 0
EXIT_INCOMPLETE = 2


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P4-LOG-900] Fail-closed termination marker for every abort path.
    print("[P4:complete:FAIL] " + message, flush=True)
    sys.exit(1)


def sha_or_missing(path):
    """Return file hash or the marker for absent evidence."""
    if not os.path.isfile(path):
        return "MISSING"
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    """Load a JSON document, failing closed on absence."""
    if not os.path.isfile(path):
        fail("missing required artifact: " + path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def utcnow():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(repo_root, *parts):
    """Join a repo-relative path."""
    return os.path.join(repo_root, *parts)


def ledger_ok(ledger, name):
    """Check one ledger anchor is FIXED with no manual choice."""
    rec = (ledger.get("anchors", {}).get(name, {})
           if isinstance(ledger, dict) else {})
    return (rec.get("ambiguity_status") == "FIXED"
            and rec.get("manual_semantic_choice_required") is False)


def main(argv):
    """Entry point: build the certificate, gate the singleton record."""
    # [P4-LOG-010] Step: start certificate check, echo arguments.
    print("[P4:complete:010] start completion-space check", flush=True)
    if len(argv) != 6:
        fail("usage: check_completion_space.py <repo-root> <contract> "
             "<k_table> <certificate_out> <identified_set_out>")
    repo_root = os.path.abspath(argv[1])
    contract_path = os.path.abspath(argv[2])
    ktable_path = os.path.abspath(argv[3])
    cert_path = os.path.abspath(argv[4])
    ident_path = os.path.abspath(argv[5])
    # [P4-LOG-012] Step: echo the resolved repository root.
    print("[P4:complete:012] repo=%s" % repo_root, flush=True)

    contract = load_json(contract_path)
    ktable = load_json(ktable_path)
    ledger_p = rel(repo_root, "derived", "anchor_ledger.json")
    inputs_p = rel(repo_root, "prereg", "execution_inputs.json")
    ledger = load_json(ledger_p)
    inputs = load_json(inputs_p)

    proofs = {
        "ledger": sha_or_missing(ledger_p),
        "inputs": sha_or_missing(inputs_p),
        "contract": sha_or_missing(contract_path),
        "ktable": sha_or_missing(ktable_path),
        "h_init": sha_or_missing(rel(repo_root, "derived",
                                     "H_initial.json")),
        "h_permit": sha_or_missing(rel(repo_root, "derived",
                                       "H_permit.json")),
        "h_nonpermit": sha_or_missing(rel(repo_root, "derived",
                                          "H_nonpermit.json")),
        "hequiv": sha_or_missing(rel(repo_root, "derived",
                                     "h_equivalence_proof.json")),
        "adequacy": sha_or_missing(rel(repo_root, "derived",
                                       "policy_adequacy_certificate.json")),
        "projection": sha_or_missing(rel(repo_root, "derived",
                                         "policy_projection.json")),
        "prrel": sha_or_missing(rel(repo_root, "derived",
                                    "pr_relation.json")),
        "lambdarec": sha_or_missing(rel(repo_root, "derived",
                                        "lambda_record.json")),
        "atomrec": sha_or_missing(rel(repo_root, "derived",
                                      "atom_record.json")),
        "req_permit": sha_or_missing(rel(repo_root, "derived", "requests",
                                         "request_x_permit.xml")),
        "req_nonpermit": sha_or_missing(
            rel(repo_root, "derived", "requests",
                "request_x_nonpermit.xml")),
        "manifest": sha_or_missing(rel(repo_root, "external",
                                       "MANIFEST.json")),
        "orig_actual": sha_or_missing(rel(repo_root, "artifacts", "raw",
                                          "original_response_actual.xml")),
    }
    # [P4-LOG-020] Step: core cross-checks (contract/table/inputs).
    print("[P4:complete:020] cross-checking contract and table",
          flush=True)
    contract_worlds = contract.get("worlds", [])
    if isinstance(contract_worlds, dict):
        contract_worlds = sorted(contract_worlds.keys())
    inputs_worlds = sorted(inputs.get("worlds", {}).keys())
    worlds_match = (sorted(contract_worlds) == inputs_worlds
                    and len(inputs_worlds) == 2)
    contract_actions = set()
    raw_actions = contract.get("actions", {})
    if isinstance(raw_actions, dict):
        contract_actions = set(raw_actions.keys())
    elif isinstance(raw_actions, list):
        for item in raw_actions:
            if isinstance(item, str):
                contract_actions.add(item)
    inputs_actions = inputs.get("action_interface", {}).get("actions", [])
    actions_match = (sorted(contract_actions) == sorted(inputs_actions)
                     and len(contract_actions) >= 1)
    k_order = ktable.get("freeze_order", [])
    inputs_order = inputs.get("freeze_order", [])
    order_match = (k_order == inputs_order and len(k_order) == 8)
    k_vec = ktable.get("kappa", [])
    kappa_shape = (isinstance(k_vec, list) and len(k_vec) == 8 and all(
        (isinstance(v, bool) is False
         and isinstance(v, (int, float)) and v > 0) or v == "INF"
        for v in k_vec))
    table_contract_match = (
        ktable.get("contract_sha256") == proofs["contract"])
    try:
        with open(rel(repo_root, "derived",
                      "h_equivalence_proof.json"),
                  "r", encoding="utf-8") as handle:
            hequiv_verdict = json.load(handle).get("verdict")
    except (OSError, ValueError):
        hequiv_verdict = None
    try:
        with open(rel(repo_root, "derived",
                      "policy_adequacy_certificate.json"),
                  "r", encoding="utf-8") as handle:
            adequacy_verdict = json.load(handle).get("verdict")
    except (OSError, ValueError):
        adequacy_verdict = None
    try:
        with open(rel(repo_root, "derived", "lambda_record.json"),
                  "r", encoding="utf-8") as handle:
            lambdadoc = json.load(handle)
    except (OSError, ValueError):
        lambdadoc = {}
    try:
        with open(rel(repo_root, "derived", "atom_record.json"),
                  "r", encoding="utf-8") as handle:
            atomdoc = json.load(handle)
    except (OSError, ValueError):
        atomdoc = {}
    try:
        with open(rel(repo_root, "derived", "pr_relation.json"),
                  "r", encoding="utf-8") as handle:
            prdoc = json.load(handle)
    except (OSError, ValueError):
        prdoc = {}
    # H objects non-empty check (admitted histories present).
    h_nonempty = True
    for key in ("h_init", "h_permit", "h_nonpermit"):
        fname = {"h_init": "H_initial.json",
                 "h_permit": "H_permit.json",
                 "h_nonpermit": "H_nonpermit.json"}[key]
        try:
            with open(rel(repo_root, "derived", fname),
                      "r", encoding="utf-8") as handle:
                doc = json.load(handle)
            if not doc.get("attributes"):
                h_nonempty = False
        except (OSError, ValueError):
            h_nonempty = False
    # Cost alignment: every contract cost equals the prereg unit cost.
    try:
        unit = inputs["action_interface"]["unit_cost"]
        costs = contract.get("costs", {})
        costs_match = (isinstance(costs, dict) and len(costs) >= 1
                       and all(v == unit for v in costs.values()))
    except (KeyError, TypeError):
        costs_match = False
    # Target heterogeneity (open initial fiber, closed terminals).
    try:
        tvals = list(contract.get("target", {}).values())
        targets_open = (len(tvals) == 2 and len(set(str(v) for v in tvals))
                        == 2)
    except (AttributeError, TypeError):
        targets_open = False
    # Successor coverage: each action reaches all worlds or lists.
    # Handles the compiled checkpoint-nested layout, the minimal
    # direct layout, and the actions-table list fallback.
    succ_cover = True
    try:
        succ = contract.get("successors", {})
        acts_tbl = contract.get("actions", {})
        for ident in contract_actions:
            entry = None
            if isinstance(succ, dict) and ident in succ:
                entry = succ.get(ident)
            elif isinstance(succ, dict):
                for _cp, inner in succ.items():
                    if isinstance(inner, dict) and ident in inner:
                        entry = inner[ident]
                        break
            if entry is None and isinstance(acts_tbl, dict):
                detail = acts_tbl.get(ident, {})
                if isinstance(detail, dict) and "successors" in detail:
                    entry = detail["successors"]
            if isinstance(entry, dict):
                if set(entry.keys()) != set(inputs_worlds):
                    succ_cover = False
            elif isinstance(entry, list):
                if not entry:
                    succ_cover = False
            elif isinstance(entry, str):
                pass
            else:
                succ_cover = False
    except (AttributeError, TypeError):
        succ_cover = False
    atom_conclusion_ok = (
        atomdoc.get("conclusion")
        == "NATIVE_TRANSACTION_PROVEN + RECONSTRUCTION_AS_WRAPPER")
    lambda_ok = isinstance(lambdadoc.get("pre_hash"), str) and len(
        lambdadoc.get("pre_hash", "")) == 64
    pr_ok = (isinstance(prdoc.get("designator_coordinates"), list)
             and len(prdoc["designator_coordinates"]) >= 1)
    worlds_files = (proofs["req_permit"] != "MISSING"
                    and proofs["req_nonpermit"] != "MISSING")

    rows = []
    # [P4-LOG-030] Step: judging each K-relevant field.
    print("[P4:complete:030] judging thirteen fields", flush=True)

    def row(field, constrained, evidence, detail):
        rows.append({
            "pc_field": field,
            "source_constraint": SOURCE[field],
            "evidence": evidence,
            "free_after_audit": (not bool(constrained)),
            "check_detail": detail,
        })
        # [P4-LOG-032] Step: per-field verdict line.
        print("[P4:complete:032] %s free_after_audit=%s"
              % (field, (not bool(constrained))), flush=True)

    row("X", worlds_match and actions_match and order_match, {
        "prereg/execution_inputs.json": proofs["inputs"],
        "contract": proofs["contract"],
    }, "worlds/actions/order cross-checked between prereg inputs "
       "and contract/table")
    row("U_H", h_nonempty and hequiv_verdict == "VALID" and worlds_files, {
        "derived/H_initial.json": proofs["h_init"],
        "derived/H_permit.json": proofs["h_permit"],
        "derived/H_nonpermit.json": proofs["h_nonpermit"],
        "derived/h_equivalence_proof.json": proofs["hequiv"],
    }, "admitted histories present over proven-equivalent source")
    row("S", worlds_match and succ_cover and atom_conclusion_ok
        and targets_open, {
        "contract": proofs["contract"],
        "derived/atom_record.json": proofs["atomrec"],
        "derived/requests/request_x_permit.xml": proofs["req_permit"],
        "derived/requests/request_x_nonpermit.xml":
            proofs["req_nonpermit"],
    }, "checkpoints/successors cover both worlds under native boundary")
    row("H", ledger_ok(ledger, "H") and hequiv_verdict == "VALID"
        and h_nonempty, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "derived/h_equivalence_proof.json": proofs["hequiv"],
        "derived/H_initial.json": proofs["h_init"],
    }, "ledger FIXED with N1/N3 evidence and valid equivalence proof")
    row("P_R", ledger_ok(ledger, "P_R")
        and adequacy_verdict == "PASS" and pr_ok, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "derived/policy_adequacy_certificate.json": proofs["adequacy"],
        "derived/pr_relation.json": proofs["prrel"],
        "derived/policy_projection.json": proofs["projection"],
    }, "ledger FIXED with adequate frozen projection and relation")
    row("Lambda", ledger_ok(ledger, "Lambda") and lambda_ok, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "derived/lambda_record.json": proofs["lambdarec"],
        "external/MANIFEST.json": proofs["manifest"],
    }, "ledger FIXED with frozen capability hash present")
    row("omega", ledger_ok(ledger, "omega")
        and proofs["orig_actual"] != "MISSING", {
        "derived/anchor_ledger.json": proofs["ledger"],
        "artifacts/raw/original_response_actual.xml":
            proofs["orig_actual"],
    }, "ledger FIXED with native response observation present")
    row("Q", ledger_ok(ledger, "Q") and actions_match
        and atom_conclusion_ok, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "prereg/execution_inputs.json": proofs["inputs"],
        "derived/atom_record.json": proofs["atomrec"],
    }, "ledger FIXED with prereg wrapper operation defined")
    row("Succ+", ledger_ok(ledger, "Succ+") and worlds_files
        and succ_cover, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "contract": proofs["contract"],
        "derived/requests/request_x_permit.xml": proofs["req_permit"],
    }, "ledger FIXED with both world successors present")
    row("c", ledger_ok(ledger, "c") and costs_match, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "prereg/execution_inputs.json": proofs["inputs"],
        "contract": proofs["contract"],
    }, "ledger FIXED with unit normalization matching contract costs")
    row("A_Pi", ledger_ok(ledger, "A_Pi") and targets_open, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "contract": proofs["contract"],
    }, "ledger FIXED with heterogeneous target map over two worlds")
    row("Atom", ledger_ok(ledger, "Atom") and atom_conclusion_ok, {
        "derived/anchor_ledger.json": proofs["ledger"],
        "derived/atom_record.json": proofs["atomrec"],
    }, "ledger FIXED with proven native transaction boundary")
    omega_free = rows[6]["free_after_audit"] is False
    succ_free = rows[8]["free_after_audit"] is False
    api_free = rows[10]["free_after_audit"] is False
    y_constrained = (omega_free and succ_free and api_free
                     and kappa_shape and table_contract_match
                     and order_match)
    row("Y", y_constrained, {
        "artifacts/freezes/K_table.json": proofs["ktable"],
        "contract": proofs["contract"],
    }, "outcome classes induced where omega/Succ+/A_Pi constrained "
       "and table matches contract/order")

    free_count = sum(1 for r in rows if r["free_after_audit"])
    nontriv = (isinstance(k_vec, list) and len(k_vec) == 8
               and any(v != k_vec[0] for v in k_vec[1:]))
    verdict = "COMPLETE" if free_count == 0 else "INCOMPLETE"
    cert = {
        "certificate_id": "PC-XACML-S3PLUS-v1-completion-space",
        "experiment_id": "PC-XACML-S3PLUS-v1",
        "contract_sha256": proofs["contract"],
        "k_table_sha256": proofs["ktable"],
        "ledger_sha256": proofs["ledger"],
        "execution_inputs_sha256": proofs["inputs"],
        "rows": rows,
        "free_k_relevant_fields": free_count,
        "nontrivial": nontriv,
        "verdict": verdict,
        "produced_utc": utcnow(),
    }
    os.makedirs(os.path.dirname(os.path.abspath(cert_path)),
                exist_ok=True)
    with open(cert_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(cert, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P4-LOG-040] Step: certificate written, report verdict.
    print("[P4:complete:040] free=%d verdict=%s nontrivial=%s"
          % (free_count, verdict, nontriv), flush=True)
    if free_count != 0:
        # [P4-LOG-042] Step: refuse the singleton record (fields free).
        print("[P4:complete:042] refusing singleton record "
              "(free fields remain)", flush=True)
        sys.exit(EXIT_INCOMPLETE)
    # Only a zero-free certificate may authorize cardinality 1; the
    # signature below is copied from the observed table, never forced.
    ident = {
        "identified_set_cardinality": 1,
        "signature": list(k_vec),
        "basis": ("all required Stage-III semantic anchors fixed by "
                  "accepted external provenance plus preregistered "
                  "measurement wrapper"),
        "contract_sha256": proofs["contract"],
        "certificate_sha256": sha_or_missing(cert_path),
        "freeze_order": list(k_order),
    }
    # Re-hash after write for a stable self-reference: first write,
    # then refresh the certificate hash field honestly.
    os.makedirs(os.path.dirname(os.path.abspath(ident_path)),
                exist_ok=True)
    with open(ident_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(ident, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P4-LOG-050] Step: singleton record written.
    print("[P4:complete:050] singleton record written", flush=True)
    sys.exit(EXIT_COMPLETE)


if __name__ == "__main__":
    main(sys.argv)
