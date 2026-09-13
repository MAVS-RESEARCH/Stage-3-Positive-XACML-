"""Deployment-set gate for the frozen policies glob (RS003-B01).

Proves the deployed policies/ set is exactly {policy.xml} at measurement
and proves a builder output directory sits outside the policies glob
(self-pollution refusal). Fail-closed: any mismatch exits nonzero.

Commands (all --repo-root required):
--emit --fixture-dir X --out Y
--check --fixture-dir X --listing Y  (exit 1 on mismatch)
--disjoint --out-dir X --policies-dir Y  (exit 2 on overlap)

Step console lines use the [P2:gate:NNN] tag, each marked by a
[P2-LOG-NNN] comment for Path.md citation.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone


def fail(message, code=1):
    """Emit a fail-closed error line and exit nonzero."""
    # [P2-LOG-900] Fail-closed termination marker for every abort path.
    print("[P2:gate:FAIL] " + message, flush=True)
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


def live_listing(fixture_policies_dir):
    """List every entry in the policies dir, sorted by name.

    Every regular file (hidden files included via os.listdir) is
    recorded as {"name", "bytes", "sha256"}. Subdirectories are
    recorded as {"name", "type": "dir"} and fail check mode.
    """
    # [P2-LOG-010] Step: measure the live policies directory.
    directory = os.path.abspath(fixture_policies_dir)
    entries = []
    for name in os.listdir(directory):
        full = os.path.join(directory, name)
        if os.path.isdir(full):
            entries.append({"name": name, "type": "dir"})
        elif os.path.isfile(full):
            entries.append({"name": name, "bytes": os.path.getsize(full),
                            "sha256": sha256_file(full)})
        else:
            entries.append({"name": name, "type": "other"})
    entries.sort(key=lambda entry: entry["name"])
    return {"directory": directory, "files": entries}


def check(live, expected_listing_doc):
    """Compare live listing vs expected doc; return problem list."""
    # [P2-LOG-020] Step: enforce single-file set equality + hashes.
    problems = []
    expected_files = (expected_listing_doc.get("files")
                      if isinstance(expected_listing_doc, dict) else None)
    if not isinstance(expected_files, list):
        return ["expected-missing-files"]
    if len(expected_files) != 1:
        problems.append("count!=1: expected has %d files"
                        % len(expected_files))
    live_files = live.get("files", []) if isinstance(live, dict) else []
    for entry in live_files:
        if entry.get("type") in ("dir", "other"):
            problems.append("subdir:%s" % ascii_safe(entry.get("name",
                                                               "?")))
    live_map = {e["name"]: e for e in live_files
                if isinstance(e, dict) and "sha256" in e and "name" in e}
    expected_map = {e["name"]: e for e in expected_files
                    if isinstance(e, dict) and "name" in e}
    if set(live_map) != set(expected_map):
        problems.append("name-set-mismatch: live=%s expected=%s"
                        % (ascii_safe(sorted(live_map)),
                           ascii_safe(sorted(expected_map))))
    if len(live_map) != 1:
        problems.append("count!=1: live has %d files" % len(live_map))
    for name in set(live_map) & set(expected_map):
        got, want = live_map[name], expected_map[name]
        if got.get("bytes") != want.get("bytes") or \
                got.get("sha256") != want.get("sha256"):
            problems.append("modified:%s" % ascii_safe(name))
    return problems


def staged_root_ok(staged_dir):
    """Require the staged root to hold exactly pdp.xml + policies/."""
    # [P2-LOG-058] Step: enforce staged-root exclusivity.
    try:
        names = sorted(os.listdir(staged_dir))
    except OSError:
        return ["staged root unreadable"]
    if names != ["pdp.xml", "policies"]:
        return ["staged root not exclusive: %s" % ascii_safe(names)]
    return []


def ascii_safe(value):
    """Render a value with non-ASCII replaced (console-safe)."""
    return str(value).encode("ascii", errors="replace").decode("ascii")


def canon_path(path):
    """Canonicalize a path for alias-resistant containment checks."""
    resolved = os.path.realpath(path)
    if resolved.startswith('\\\\?\\UNC\\'):
        resolved = '\\' + resolved[8:]
    elif resolved.startswith('\\\\?\\'):
        resolved = resolved[4:]
    resolved = os.path.normcase(os.path.normpath(resolved))
    parts = [part.rstrip('. ') for part in resolved.split(os.sep)]
    return os.sep.join(parts)


def is_unc(path):
    """Detect UNC spellings that realpath may not normalize."""
    lowered = os.path.normcase(path)
    return lowered.startswith('\\\\') and not lowered.startswith('\\\\?\\')


def disjoint(out_dir, policies_dir):
    """Return True iff neither dir contains the other (fail-closed)."""
    # [P2-LOG-030] Step: resolve both dirs and prove neither nests.
    # Same canon as the builder guard: realpath + \\?\ strip + normcase +
    # normpath + per-component dot/space strip, fail-closed on ambiguity.
    # UNC spellings fail closed: commonpath cannot prove disjointness
    # across roots that may alias one device.
    if is_unc(out_dir) or is_unc(policies_dir):
        return False
    left = canon_path(os.path.abspath(out_dir))
    right = canon_path(os.path.abspath(policies_dir))
    try:
        common = os.path.normcase(os.path.commonpath([left, right]))
    except ValueError:
        return True
    if common == left or common == right:
        return False
    return True


def main(argv=None):
    """Entry point: dispatch deployment-set gate operations."""
    # [P2-LOG-070] Step: dispatch gate mode.
    print("[P2:gate:070] deployment-set gate invoked", flush=True)
    parser = argparse.ArgumentParser(description="Deployment-set gate.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-staged", action="store_true")
    parser.add_argument("--disjoint", action="store_true")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--fixture-dir", default="")
    parser.add_argument("--staged-dir", default="")
    parser.add_argument("--listing", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--policies-dir", default="")
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)
    if args.emit:
        # [P2-LOG-040] Step: emit a live listing document.
        print("[P2:gate:040] emitting listing", flush=True)
        if not args.fixture_dir or not args.out:
            fail("--emit needs --fixture-dir --out")
        live = live_listing(args.fixture_dir)
        doc = {"directory": live["directory"], "emitted_utc": utcnow(),
               "files": live["files"]}
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, indent=2, sort_keys=True)
            handle.write("\n")
        # [P2-LOG-042] Step: emit complete.
        print("[P2:gate:042] emitted files=%d" % len(live["files"]),
              flush=True)
    elif args.check:
        # [P2-LOG-050] Step: fail-closed check of live set vs listing.
        print("[P2:gate:050] checking deployment set", flush=True)
        if not args.fixture_dir or not args.listing:
            fail("--check needs --fixture-dir --listing")
        with open(args.listing, encoding="utf-8") as handle:
            expected = json.load(handle)
        problems = check(live_listing(args.fixture_dir), expected)
        if problems:
            fail("deployment-set mismatch: %s" % problems, code=1)
        # [P2-LOG-052] Step: deployment set matches.
        print("[P2:gate:052] deployment set ok", flush=True)
    elif args.check_staged:
        # [P2-LOG-054] Step: staged-copy equality pre-evaluation.
        print("[P2:gate:054] checking staged fixture copy", flush=True)
        if not args.staged_dir or not args.fixture_dir:
            fail("--check-staged needs --staged-dir --fixture-dir")
        for rel in ("pdp.xml", os.path.join("policies", "policy.xml")):
            frozen = os.path.join(args.fixture_dir, rel)
            staged = os.path.join(args.staged_dir, rel)
            if not os.path.isfile(staged):
                fail("staged copy missing: " + rel)
            if sha256_file(staged) != sha256_file(frozen):
                fail("staged copy drifted: " + rel)
        for problem in staged_root_ok(args.staged_dir):
            fail(problem)
        names = sorted(os.listdir(os.path.join(args.staged_dir,
                                               "policies")))
        if names != ["policy.xml"]:
            fail("staged policy set not exclusive: %s"
                 % ascii_safe(names))
        # [P2-LOG-056] Step: staged copy verified.
        print("[P2:gate:056] staged copy ok", flush=True)
    elif args.disjoint:
        # [P2-LOG-060] Step: fail-closed overlap check for builder out_dir.
        print("[P2:gate:060] checking disjointness", flush=True)
        if not args.out_dir or not args.policies_dir:
            fail("--disjoint needs --out-dir --policies-dir")
        if not disjoint(args.out_dir, args.policies_dir):
            fail("out_dir overlaps policies_dir", code=2)
        # [P2-LOG-062] Step: disjointness proved.
        print("[P2:gate:062] disjoint ok", flush=True)
    else:
        fail("no gate operation given")
    # [P2-LOG-072] Step: gate operation complete.
    print("[P2:gate:072] gate operation complete", flush=True)


if __name__ == "__main__":
    main()
