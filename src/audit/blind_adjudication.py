"""Phase-2 blind adjudication machinery for PC-XACML-S3+.

Modes: --build-packet (assemble the redacted auditor packet + seal its
hash), --assert-unlock (exit 0 only if a sealed qualifying verdict
marks H/P_R/Lambda/Atom all FIXED; exit 3 on insufficient verdict;
exit 4 when no sealed verdict exists), --seal-verdict (validate and
hash-seal an adjudicator-delivered verdict file). The packet answers
"are THESE proposed mappings justified by THESE sources": candidate
mappings + adequacy/equivalence artifacts + execution inputs + wrapper
evidence + the COMPLETE frozen corpus + locator index + rubric, with all
expected outputs/outcomes/claims excluded. Redaction scans cover
analyst-authored packet parts (the frozen corpus predates the experiment
and is excluded from the scan). No E/R/A or touch literals appear in
this module.

Step console lines use the [P2:blind:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

BLIND_ANCHORS = ("H", "P_R", "Lambda", "Atom")
ALLOWED_STATUSES = ("FIXED", "PARTIAL", "AMBIGUOUS", "UNSUPPORTED")
# Forbidden in analyst-authored packet parts and in verdict files.
REDACTION_PATTERNS = (
    "expected_touch",
    "expected_K",
    "expected_signature",
    "expected_classification",
    "canary_expectations",
    "STRUCTURAL_E_TOUCH_DEPENDENCE",
    "Stage III works in the wild",
    "real systems naturally provide PC anchors",
    "XACML validates the universal",
    "PC automatically extracts governance",
    "representation/evidence causality",
    "production authorization systems are PC-identifiable",
)
TOUCH_ASSIGNMENT = re.compile(r'"touch"|q_supply[^"]*\[.E.\]')
RUBRIC = """# 2B blind-adjudication rubric

You receive frozen external sources plus proposed PC anchor mappings.
You do NOT receive (and must not seek): expected touch, expected K,
expected classification, desired experiment outcome, manuscript claims.

For EACH of H, P_R, Lambda, Atom return exactly one verdict:
FIXED (external sources independently justify the mapping; cite exact
locators), PARTIAL, AMBIGUOUS, or UNSUPPORTED (cite what is missing).

Qualification: you must not have been shown the expected touch,
expected K, expected classification, or desired positive verdict before
sealing. Record an anonymous auditor ID (AUD-XXX) plus the SHA-256 of a
private non-exposure attestation you retain until de-anonymization.
"""
LOCATOR_INDEX = """# Blind-packet locator index (convenience only)

The complete frozen corpus in corpus/ is authoritative; this index is a
finding aid, not a substitute. Key sections in
corpus/xacml-3.0-core-spec-cos01-en.html (stripped-text lines):
- Data-flow model (PEP/handler/PDP): lines 1755-1784; glossary 931/1007/1016
- Sec. 5.29 AttributeDesignator: lines 406-407; Sec. 5.30 Selector: 409-410
- MustBePresent semantics: lines 6292-6294
- Sec. 7.3.5 Attribute Retrieval: lines 8405-8424
- Sec. 7.6 Match evaluation: lines 8577-8594
- Rule True/False/error semantics + target mismatch: lines 2308-2322
- StatusDetail/MissingAttributeDetail elements: lines 491-494
Fixture corpus: corpus/fixture/{pdp.xml,request.xml,response.xml,
policies/policy.xml}; corpus/RELEASE.json, COMMIT.txt, MANIFEST.json.
Candidate mappings under candidates/ (blind-safe: no touch/K/outcomes).
"""


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:blind:FAIL] " + message, flush=True)
    sys.exit(1)


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


def packet_dir(repo_root):
    """Return the blind-packet directory path."""
    return os.path.join(repo_root, "artifacts", "audits",
                        "blind_anchor_packet")


def verdict_path(repo_root):
    """Return the sealed-verdict path."""
    return os.path.join(repo_root, "artifacts", "audits",
                        "blind_anchor_verdict.json")


def seal_record_path(repo_root):
    """Return the verdict-seal record path."""
    return os.path.join(repo_root, "artifacts", "audits",
                        "blind_verdict_seal.json")


def write_text(path, content):
    """Write UTF-8 text with LF newlines, creating parents."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def copy_file(src, dst):
    """Copy bytes, creating parents."""
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    shutil.copyfile(src, dst)


def scan_redaction(root):
    """Scan analyst-authored packet parts for expectation leakage."""
    hits = []
    for base, _dirs, files in os.walk(root):
        if os.path.basename(base) == "corpus":
            continue
        for name in files:
            path = os.path.join(base, name)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    content = handle.read()
            except (OSError, UnicodeDecodeError):
                continue
            for pattern in REDACTION_PATTERNS:
                if pattern in content:
                    hits.append((path, pattern))
            if TOUCH_ASSIGNMENT.search(content):
                hits.append((path, "touch-assignment"))
    return hits


def build_packet(repo_root):
    """Assemble, redact-check, and hash-seal the auditor packet."""
    # [P2-LOG-010] Step: assemble packet contents.
    print("[P2:blind:010] building auditor packet", flush=True)
    packet = packet_dir(repo_root)
    if os.path.isdir(packet):
        shutil.rmtree(packet)
    derived = os.path.join(repo_root, "derived")
    candidates = {
        "anchor_ledger.json": "candidate mappings (auditor_status PENDING)",
        "policy_adequacy_certificate.json": "adequacy certificate",
        "h_equivalence_proof.json": "equivalence proof",
        "atom_record.json": "wrapper/boundary evidence",
        "pr_relation.json": "P_R relation record",
        "lambda_record.json": "Lambda record",
        "H_initial.json": "H checkpoint objects",
        "H_permit.json": "H checkpoint objects",
        "H_nonpermit.json": "H checkpoint objects",
    }
    for name in candidates:
        src = os.path.join(derived, name)
        if not os.path.isfile(src):
            fail("candidate artifact missing: " + name)
        copy_file(src, os.path.join(packet, "candidates", name))
    copy_file(os.path.join(repo_root, "prereg", "execution_inputs.json"),
              os.path.join(packet, "candidates", "execution_inputs.json"))
    corpus = {
        os.path.join("external", "xacml",
                     "xacml-3.0-core-spec-cos01-en.html"):
        "corpus/xacml-3.0-core-spec-cos01-en.html",
        os.path.join("external", "authzforce", "fixture", "pdp.xml"):
        "corpus/fixture/pdp.xml",
        os.path.join("external", "authzforce", "fixture", "request.xml"):
        "corpus/fixture/request.xml",
        os.path.join("external", "authzforce", "fixture",
                     "response.xml"):
        "corpus/fixture/response.xml",
        os.path.join("external", "authzforce", "fixture", "policies",
                     "policy.xml"):
        "corpus/fixture/policies/policy.xml",
        os.path.join("external", "authzforce", "RELEASE.json"):
        "corpus/RELEASE.json",
        os.path.join("external", "authzforce", "COMMIT.txt"):
        "corpus/COMMIT.txt",
        os.path.join("external", "MANIFEST.json"):
        "corpus/MANIFEST.json",
    }
    for src_rel, dst_rel in corpus.items():
        copy_file(os.path.join(repo_root, src_rel),
                  os.path.join(packet, dst_rel))
    write_text(os.path.join(packet, "rubric.md"), RUBRIC)
    write_text(os.path.join(packet, "locator_index.md"), LOCATOR_INDEX)

    # [P2-LOG-020] Step: verify corpus copies are byte-identical.
    print("[P2:blind:020] verifying corpus fidelity", flush=True)
    for src_rel, dst_rel in corpus.items():
        if (sha256_file(os.path.join(repo_root, src_rel))
                != sha256_file(os.path.join(packet, dst_rel))):
            fail("corpus copy mismatch: " + dst_rel)
    print("[P2:blind:022] corpus fidelity confirmed", flush=True)

    # [P2-LOG-030] Step: redaction check over analyst-authored parts.
    print("[P2:blind:030] running redaction check", flush=True)
    hits = scan_redaction(packet)
    if hits:
        fail("redaction violations: %s" % hits)
    print("[P2:blind:032] redaction check passed", flush=True)

    manifest_entries = {}
    for base, _dirs, files in os.walk(packet):
        for name in files:
            path = os.path.join(base, name)
            key = os.path.relpath(path, packet).replace(os.sep, "/")
            manifest_entries[key] = sha256_file(path)
    manifest = {"packet_id": "PC-XACML-S3PLUS-v1-blind-packet",
                "sealed_utc": utcnow(), "files": manifest_entries}
    manifest_json = json.dumps(manifest, indent=2, sort_keys=True)
    packet_sha = hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()
    write_text(os.path.join(packet, "PACKET_MANIFEST.json"), manifest_json)
    with open(os.path.join(packet, "PACKET_SHA256.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(packet_sha + "\n")
    # [P2-LOG-040] Step: packet sealed.
    print("[P2:blind:040] packet sealed sha256=%s files=%d"
          % (packet_sha, len(manifest_entries)), flush=True)
    return packet_sha


def validate_verdict(doc):
    """Validate verdict structure; return a list of problems."""
    problems = []
    if not isinstance(doc.get("auditor_id"), str) or not re.match(
            r"^AUD-[A-Z0-9]{2,12}$", doc.get("auditor_id", "")):
        problems.append("auditor_id must be anonymous AUD-XXX form")
    if doc.get("qualification") != "QUALIFIED_INDEPENDENT":
        problems.append("qualification must be QUALIFIED_INDEPENDENT")
    verdicts = doc.get("verdicts", {})
    for anchor in BLIND_ANCHORS:
        record = verdicts.get(anchor, {})
        if record.get("status") not in ALLOWED_STATUSES:
            problems.append("bad status for " + anchor)
        if not isinstance(record.get("locators"), list) or not record.get(
                "locators"):
            problems.append("missing locators for " + anchor)
    if not doc.get("attestation_hash"):
        problems.append("attestation_hash missing")
    return problems


def seal_verdict(repo_root, verdict_src):
    """Validate and hash-seal an adjudicator-delivered verdict file."""
    # [P2-LOG-050] Step: sealing a delivered verdict.
    print("[P2:blind:050] sealing delivered verdict", flush=True)
    with open(verdict_src, "r", encoding="utf-8") as handle:
        content = handle.read()
    for pattern in REDACTION_PATTERNS:
        if pattern in content:
            fail("verdict file leaks expectation content: " + pattern)
    doc = json.loads(content)
    problems = validate_verdict(doc)
    if problems:
        fail("verdict invalid: %s" % problems)
    dst = verdict_path(repo_root)
    write_text(dst, json.dumps(doc, indent=2, sort_keys=True) + "\n")
    digest = sha256_file(dst)
    write_text(seal_record_path(repo_root), json.dumps(
        {"verdict_sha256": digest, "sealed_utc": utcnow(),
         "auditor_id": doc["auditor_id"]}, indent=2, sort_keys=True)
        + "\n")
    print("[P2:blind:052] verdict sealed sha256=%s" % digest, flush=True)


def assert_unlock(repo_root):
    """Exit 0 iff a sealed qualifying all-FIXED verdict exists."""
    # [P2-LOG-060] Step: judging the unlock conjunction.
    print("[P2:blind:060] judging target-audit unlock", flush=True)
    dst = verdict_path(repo_root)
    seal = seal_record_path(repo_root)
    if not (os.path.isfile(dst) and os.path.isfile(seal)):
        print("[P2:blind:062] no sealed verdict: locked", flush=True)
        sys.exit(4)
    with open(seal, "r", encoding="utf-8") as handle:
        record = json.load(handle)
    if sha256_file(dst) != record.get("verdict_sha256"):
        print("[P2:blind:063] verdict seal mismatch: locked", flush=True)
        sys.exit(4)
    with open(dst, "r", encoding="utf-8") as handle:
        doc = json.load(handle)
    if validate_verdict(doc):
        print("[P2:blind:064] verdict invalid: locked", flush=True)
        sys.exit(4)
    verdicts = doc.get("verdicts", {})
    short = [a for a in BLIND_ANCHORS
             if verdicts.get(a, {}).get("status") != "FIXED"]
    if short:
        print("[P2:blind:066] insufficient verdict %s: failure-seal route"
              % short, flush=True)
        sys.exit(3)
    print("[P2:blind:068] unlock conjunction holds", flush=True)
    sys.exit(0)


def main(argv):
    """Entry point: packet / seal-verdict / assert-unlock modes."""
    # [P2-LOG-070] Step: dispatch blind-adjudication mode.
    print("[P2:blind:070] blind adjudication invoked", flush=True)
    parser = argparse.ArgumentParser(description="2B blind machinery.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--build-packet", action="store_true")
    parser.add_argument("--seal-verdict", default="")
    parser.add_argument("--assert-unlock", action="store_true")
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)
    if args.build_packet:
        build_packet(repo_root)
    elif args.seal_verdict:
        seal_verdict(repo_root, os.path.abspath(args.seal_verdict))
    elif args.assert_unlock:
        assert_unlock(repo_root)
    else:
        fail("one of --build-packet, --seal-verdict, --assert-unlock "
             "is required")


if __name__ == "__main__":
    main(sys.argv[1:])
