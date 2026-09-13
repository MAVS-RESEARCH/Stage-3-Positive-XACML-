"""One-off R3 seeder for Wave-6-driven items (not part of the harness)."""
import json

PATH = ('artifacts/audits/semantic_hardening/objection_ledger.json')
ledger = json.load(open(PATH, encoding='utf-8'))


def ob(oid, anchor, cat, text, locators, materiality):
    return {
        "objection_id": oid,
        "round_id": "HARDENING_ROUND_002",
        "anchor": anchor,
        "originating_reviewer": "Wave-6 sweep (NON_BLIND developmental)",
        "historical_verdict": None,
        "objection": text,
        "locators": locators,
        "category": cat,
        "materiality": materiality,
        "resolution_status": "OPEN",
        "proposed_resolution": None,
        "files_changed": [],
        "source_grounding_evidence": None,
        "external_semantics_changed": False,
        "downstream_result_info_used": False,
        "independent_recheck": None,
        "final_disposition": "OPEN",
    }


news = [
    ob("R3-13", "GLOBAL", "E",
       "VOLATILE strip sets differ across modules; drift story in "
       "freeze_methodology inaccurate (timestamps are stripped).",
       ["checker VOLATILE_KEYS", "repro_compare DROP",
        "freeze_methodology ledger-drift"],
       "Material: latent divergence in canonical forms."),
    ob("R3-14", "Lambda", "D",
       "Ledger Lambda binds superseded opaque hash; refs mode blind to "
       "ledger-to-manifest drift.",
       ["derived/anchor_ledger Lambda evidence", "lambda_manifest"],
       "Material: operative pointer stale."),
    ob("R3-15", "GLOBAL", "D",
       "Envelope Q/Succ+/c/A_Pi/omega FIXED self-attested without "
       "mechanical cross-checks.",
       ["checker envelope_records"], "Material: gate honesty."),
    ob("R3-16", "Atom", "D",
       "builder_reaches_pdp import-root heuristic misses from-imports, "
       "method calls, getattr dispatch, os.system spawn.",
       ["hardening_evidence reachability predicate"],
       "Material: no-reach proof strength."),
    ob("R3-17", "GLOBAL", "E",
       "C14N third hash kind unpinned/unverified; libxml2 scope "
       "excluded without record.",
       ["HASHING_CONVENTIONS", "manifest exclusions"],
       "Material: C14N digest trust."),
    ob("R3-18", "GLOBAL", "D",
       "Empty-vs-null edge and argv value binding unproven (builder "
       "permits empty; census covers files only).",
       ["builder guards", "phase scripts"],
       "Material: input edge + binding."),
    ob("R3-19", "GLOBAL", "E",
       "Nits bundle: repro_compare dead branch; supersession old-side "
       "pointers; lineage truncation honesty; newline semantics.",
       ["repro_compare", "supersession", "pre_hash_lineage",
        "newline handling"],
       "Material: minor hygiene with one honesty fix."),
]
ids = set(o["objection_id"] for o in ledger["objections"])
for entry in news:
    assert entry["objection_id"] not in ids, entry["objection_id"]
    ids.add(entry["objection_id"])
    ledger["objections"].append(entry)
with open(PATH, "w", encoding="utf-8", newline="\n") as handle:
    json.dump(ledger, handle, indent=2, sort_keys=True)
    handle.write("\n")
print('seeded=%d total=%d' % (len(news), len(ledger["objections"])))
