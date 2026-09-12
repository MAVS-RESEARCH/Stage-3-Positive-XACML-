# NON_BLIND_HARDENING_REVIEW -- Wave-6 verify sweep (developmental only)
# Full record of per-fix verification (fix = ROUND_002 evidence for Wave-4 items).

(a) PASS -- parse_proof_bags.txt shows all three worlds with exact expected bags: original 3 bags (no some-attribute), permit/nonpermit 4 bags each, correct values riddle me this / not-riddle-me-this, correct datatypes (string/anyURI), null Issuers throughout.
(b) PASS (internal) -- lambda_manifest.json engine_sources lists exactly the 5 ENGINE_SOURCES; canonical_spec components+exclusions matches builder construction; lineage scope consistent. Live-byte correspondence asserted via pristine-clone check (not re-hashed here).
(c) PASS (weak) -- comparator_demo.json contains mutated/pristine input sha256, expected_pre_hash, exit 1, stdout tail, abort_token TOUCH_DERIVATION_MISMATCH, fail_closed true. Residual: no command/argv, no comparator version, no timestamp.
(d) PASS -- invocation_record.json sites resolve: run_phase1.ps1:125 --mode original --phase1-only-original, run_phase2.ps1:242 --mode completed, gate ~217-233; refusal wiring verified (refuse() exit 2 + flag). Record omits scripts/ prefix but sites real.
(e) PASS -- wrapper_evidence.json rule_to_code has 11 phrases, all present:true (spot-checked copy.deepcopy(original), argv values, value_node.set(DataType,datatype)); generator fails on drift.
(f) FAIL -- R3-06 disposition claims grounding but rejected_alternatives.json cost entry contains only bare names (execution_inputs + experiment.yaml, immutable): no repo paths, no hashes/identifiers, no sweep procedure. Bare-name mention is not grounded citation.
(g) PASS -- match_table.json has designator-coordinate rows only; world_rows is hygiene note only, no per-world Match/Decision outcomes.
(h) MIXED/FAIL -- supersession new side PASS (new hashes verified byte-identical to live repaired files; reason coherent; old 7e28c8c3/f5c3b09f acknowledged as ROUND_000 history). Lineage FAIL: disposition claims lineage bb2c->0577->b679->cac0 recorded but pre_hash_lineage.json lists only bb2c + current; intermediates absent.
(i) PASS -- anchor_ledger.json: A_Pi source_class [N3,X]; omega locator with verified raw-HTML map; Q/Succ+/c scope notes present.
