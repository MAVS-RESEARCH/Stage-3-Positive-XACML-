"""Phase-6 audit-report assembler and verifier for PC-XACML-S3PLUS-v1.

Builds the machine-derived audit record (section values recomputed from
live artifact bytes — no hand-typed numbers) and verifies the sealed
`artifacts/audits/FINAL_AUDIT.md` binds the same values. Runs the
claim-string linter (spec 18.2 blocklist plus the Omega scope lock).

Modes: `--verify` (default) checks the sealed report; `--build OUT`
emits the deterministic machine record. Neither mode reruns the PDP,
recomputes semantics, opens quarantined Decisions beyond the sealed
opening record, or modifies frozen seals.

Step console lines use the [P6:report:NNN] tag, each marked by a
[P6-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import sys

REQUIRED_SECTIONS = (
    "External source provenance",
    "Original fixture",
    "Anchor-by-anchor",
    "Policy projection",
    "H-equivalence",
    "Blind-adjudication",
    "Native target decisions",
    "PC contract hash",
    "touch derivations",
    "Completion-space",
    "freeze values",
    "solver agreement",
    "Falsification",
    "limitations",
    "Allowed and forbidden",
)

BLOCKLIST = (
    "real systems naturally provide PC anchors",
    "Stage III works in the wild",
    "XACML validates the universal E/R/A ontology",
    "PC automatically extracts governance semantics",
    "we prove representation/evidence causality in XACML",
    "production authorization systems are PC-identifiable",
)

ALLOWED_PARAGRAPH = "We additionally audited a pre-existing XACML/AuthzForce"


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P6-LOG-900] Fail-closed termination marker for every abort path.
    print("[P6:report:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(repo_root, rel):
    """Load a JSON artifact relative to the repo root."""
    path = os.path.join(repo_root, *rel.split("/"))
    if not os.path.isfile(path):
        fail("missing required artifact: " + rel)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def derive_record(repo_root):
    """Recompute the machine audit record from live artifact bytes."""
    # [P6-LOG-020] Step: recompute values from artifacts (no hand numbers).
    print("[P6:report:020] deriving audit record from artifacts",
          flush=True)
    seal = load_json(repo_root, "artifacts/seal/FINAL_RESULT_LAUNCH.json")
    record = {
        "outcome": seal.get("outcome"),
        "decisions": dict(seal.get("decisions", {})),
        "derived_touch": seal.get("derived_touch"),
        "touch_sha256": sha256_file(os.path.join(
            repo_root, "artifacts", "contracts", "touch.json")),
        "contract_sha256": sha256_file(os.path.join(
            repo_root, "artifacts", "contracts",
            "pc_xacml_primary.contract.json")),
        "kappa": list(load_json(
            repo_root, "artifacts/freezes/K_table.json")["kappa"]),
        "k_table_sha256": sha256_file(os.path.join(
            repo_root, "artifacts", "freezes", "K_table.json")),
        "certificate_sha256": sha256_file(os.path.join(
            repo_root, "artifacts", "seal",
            "completion_space_certificate.json")),
        "identified_set_cardinality": load_json(
            repo_root,
            "artifacts/freezes/identified_set.json").get(
                "identified_set_cardinality"),
        "seal_sha256": sha256_file(os.path.join(
            repo_root, "artifacts/seal", "FINAL_RESULT_LAUNCH.json")),
        "manifest_sha256": sha256_file(os.path.join(
            repo_root, "MANIFEST.sha256")),
    }
    # [P6-LOG-022] Step: echo the derived outcome and signature.
    print("[P6:report:022] outcome=%s kappa=%s" % (
        record["outcome"], record["kappa"]), flush=True)
    return record


def lint_claims(text):
    """Enforce the claim gate; return a list of problems."""
    problems = []
    for section in REQUIRED_SECTIONS:
        if section.lower() not in text.lower():
            problems.append("missing section: " + section)
    for banned in BLOCKLIST:
        if banned in text:
            problems.append("forbidden claim present: " + banned)
    if ALLOWED_PARAGRAPH not in text:
        problems.append("allowed paragraph missing")
    return problems


def verify_report(repo_root):
    """Check the sealed report binds derived values; lint claims."""
    # [P6-LOG-030] Step: verify the sealed audit report.
    print("[P6:report:030] verifying sealed FINAL_AUDIT.md", flush=True)
    record = derive_record(repo_root)
    path = os.path.join(repo_root, "artifacts", "audits",
                        "FINAL_AUDIT.md")
    if not os.path.isfile(path):
        fail("sealed audit report missing")
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    problems = lint_claims(text)
    for key in ("outcome", "contract_sha256", "touch_sha256",
                "certificate_sha256", "seal_sha256"):
        if str(record[key]) not in text:
            problems.append("report does not bind " + key)
    if "POSITIVE_NATIVE_STAGE3" not in text:
        problems.append("report omits the sealed outcome")
    if problems:
        for item in problems:
            # [P6-LOG-032] Step: report one audit defect.
            print("[P6:report:FAIL] " + item, flush=True)
        sys.exit(1)
    # [P6-LOG-040] Step: audit verification complete.
    print("[P6:report:040] audit binds artifacts; claims green",
          flush=True)
    return record


def main(argv):
    """Entry point: --verify (default) or --build OUT."""
    # [P6-LOG-010] Step: start report assembly/verification.
    print("[P6:report:010] start audit report", flush=True)
    args = list(argv[1:])
    repo_root = os.path.abspath(args[0]) if args else os.getcwd()
    if "--build" in args:
        out = args[args.index("--build") + 1]
        record = derive_record(repo_root)
        with open(out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        # [P6-LOG-050] Step: machine record written.
        print("[P6:report:050] machine record written", flush=True)
    else:
        verify_report(repo_root)
    # [P6-LOG-060] Step: report step complete.
    print("[P6:report:060] report step complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
