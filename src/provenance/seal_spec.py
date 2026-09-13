"""Phase-1 authoritative spec seal for PC-XACML-S3+.

Copies the designated authoritative spec bytes to IMPLEMENTATION_SPEC.md,
records raw SHA-256, LF-normalized SHA-256, byte count, and line count in
external/MANIFEST.json, and writes prereg/prereg_sha256.txt over the sealed
prereg files plus the spec hashes. Heading agreement is never accepted as
identity; only these hashes are.

Step console lines use the [P1:seal:NNN] tag, each marked by a
[P1-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P1-LOG-900] Fail-closed termination marker for every abort path.
    print("[P1:seal:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_bytes(data):
    """Return the hex SHA-256 digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


def main(argv):
    """Entry point: copy, hash, and seal the authoritative spec."""
    # [P1-LOG-010] Step: start seal, echo resolved arguments.
    print("[P1:seal:010] start authoritative spec seal", flush=True)
    if len(argv) != 3:
        fail("usage: seal_spec.py <repo-root> <spec-source>")
    repo_root = os.path.abspath(argv[1])
    spec_source = os.path.abspath(argv[2])
    print("[P1:seal:012] repo-root=%s spec-source=%s"
          % (repo_root, spec_source), flush=True)
    if not os.path.isfile(spec_source):
        fail("spec source not found: " + spec_source)

    # [P1-LOG-020] Step: byte-exact copy to the authoritative path.
    print("[P1:seal:020] copying authoritative bytes", flush=True)
    dest = os.path.join(repo_root, "IMPLEMENTATION_SPEC.md")
    with open(spec_source, "rb") as handle:
        raw = handle.read()
    with open(dest, "wb") as handle:
        handle.write(raw)
    # [P1-LOG-022] Step: copy confirmation.
    print("[P1:seal:022] bytes=%d dest=IMPLEMENTATION_SPEC.md" % len(raw),
          flush=True)

    # [P1-LOG-030] Step: raw hash.
    print("[P1:seal:030] hashing raw bytes", flush=True)
    raw_sha = sha256_bytes(raw)
    print("[P1:seal:032] raw_sha256=%s" % raw_sha, flush=True)

    # [P1-LOG-040] Step: LF-normalized hash and counts.
    print("[P1:seal:040] hashing LF-normalized bytes", flush=True)
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    norm_sha = sha256_bytes(normalized)
    line_count = normalized.count(b"\n") + (0 if normalized.endswith(b"\n")
                                            else 1)
    print("[P1:seal:042] normalized_sha256=%s bytes=%d lines=%d"
          % (norm_sha, len(raw), line_count), flush=True)

    manifest_path = os.path.join(repo_root, "external", "MANIFEST.json")
    if not os.path.isfile(manifest_path):
        fail("external manifest missing; run lock_sources.py first")
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["implementation_spec"] = {
        "path": "IMPLEMENTATION_SPEC.md",
        "sha256_raw": raw_sha,
        "sha256_lf_normalized": norm_sha,
        "size_bytes": len(raw),
        "line_count": line_count,
        "normalization": "CRLF->LF",
        "sealed_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    derived_manifest = os.path.join(
        repo_root, "derived", "canonical_external_manifest.json")
    shutil.copyfile(manifest_path, derived_manifest)
    # [P1-LOG-050] Step: manifest update confirmation.
    print("[P1:seal:050] manifest updated with spec hashes", flush=True)

    # [P1-LOG-060] Step: seal the prereg directory hashes.
    print("[P1:seal:060] sealing prereg directory", flush=True)
    prereg_dir = os.path.join(repo_root, "prereg")
    seal_lines = []
    for name in sorted(os.listdir(prereg_dir)):
        if name == "prereg_sha256.txt":
            continue
        path = os.path.join(prereg_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            digest = sha256_bytes(handle.read())
        seal_lines.append("%s  %s\n" % (digest, name))
        # [P1-LOG-062] Step: per-file prereg hash confirmation.
        print("[P1:seal:062] %s %s" % (digest, name), flush=True)
    seal_lines.append("spec:sha256_raw=%s\n" % raw_sha)
    seal_lines.append("spec:sha256_lf_normalized=%s\n" % norm_sha)
    with open(os.path.join(prereg_dir, "prereg_sha256.txt"), "w",
              newline="\n") as handle:
        handle.writelines(seal_lines)

    # [P1-LOG-070] Step: seal complete.
    print("[P1:seal:070] spec seal complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
