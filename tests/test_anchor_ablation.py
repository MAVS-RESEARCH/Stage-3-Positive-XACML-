"""Phase-5 ablation tests (C04-C08, controls 5.10-5.11).

Each single-anchor deletion must kill POSITIVE_NATIVE_STAGE3 eligibility;
planted manual labels must trip the static audit.
"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "audit"))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "pc"))

AUDITS = os.path.join(REPO_ROOT, "artifacts", "audits")


def load_json(path):
    """Load a JSON document."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_ablations_refuse_positive():
    """C04-C07: H/P_R/Lambda/Atom ablation each refuses positive."""
    # [P5-LOG-T50] Test step: assert ablation refusals.
    print("[P5:test:ablate:050] anchor ablations", flush=True)
    mapping = {"H": "ablation_H.json",
               "P_R": "ablation_P_R.json",
               "Lambda": "ablation_Lambda.json",
               "Atom": "ablation_Atom.json"}
    for anchor, fname in mapping.items():
        path = os.path.join(AUDITS, fname)
        assert os.path.isfile(path), anchor
        doc = load_json(path)
        assert doc["control"] == "5.10", anchor
        assert doc["ablated_anchor"] == anchor
        assert doc["checker_exit"] != 0, anchor
        assert doc["refuses_positive"] is True, anchor
        assert doc["pass"] is True, anchor


def test_ablation_end_to_end_checker():
    """Checker refuses an ablated ledger in an isolated copy."""
    # [P5-LOG-T52] Test step: isolated ablation re-check.
    print("[P5:test:ablate:052] isolated ablation", flush=True)
    import shutil
    import tempfile
    import check_anchor_completeness as checker
    fake_root = tempfile.mkdtemp(prefix="pc-ablate-test-")
    try:
        shutil.copytree(os.path.join(REPO_ROOT, "derived"),
                        os.path.join(fake_root, "derived"))
        os.makedirs(os.path.join(fake_root, "external", "authzforce",
                                 "fixture"), exist_ok=True)
        shutil.copyfile(os.path.join(REPO_ROOT, "external",
                                     "MANIFEST.json"),
                        os.path.join(fake_root, "external",
                                     "MANIFEST.json"))
        shutil.copyfile(os.path.join(REPO_ROOT, "external", "authzforce",
                                     "fixture", "response.xml"),
                        os.path.join(fake_root, "external", "authzforce",
                                     "fixture", "response.xml"))
        os.makedirs(os.path.join(fake_root, "prereg"), exist_ok=True)
        shutil.copyfile(os.path.join(REPO_ROOT, "prereg",
                                     "execution_inputs.json"),
                        os.path.join(fake_root, "prereg",
                                     "execution_inputs.json"))
        os.makedirs(os.path.join(fake_root, "artifacts", "raw"),
                    exist_ok=True)
        shutil.copyfile(os.path.join(REPO_ROOT, "artifacts", "raw",
                                     "original_response_actual.xml"),
                        os.path.join(fake_root, "artifacts", "raw",
                                     "original_response_actual.xml"))
        os.remove(os.path.join(fake_root, "derived", "atom_record.json"))
        try:
            checker.main(["check_anchor_completeness.py", fake_root,
                          os.path.join(fake_root, "derived")])
            code = 0
        except SystemExit as exc:
            code = exc.code
        assert code != 0, code
    finally:
        shutil.rmtree(fake_root, ignore_errors=True)


def test_label_injection_detected():
    """C08: planted action-specific preassignment trips the audit."""
    # [P5-LOG-T54] Test step: assert injection detection.
    print("[P5:test:ablate:054] label injection", flush=True)
    path = os.path.join(AUDITS, "label_injection.json")
    assert os.path.isfile(path)
    doc = load_json(path)
    assert doc["control"] == "5.11"
    assert doc["detected"] is True
    assert doc["pass"] is True
    # Independent re-check via the scanner on a fresh temp payload.
    import tempfile
    import check_no_manual_labels as scanner
    tmp = tempfile.mkdtemp(prefix="pc-label-test-")
    try:
        evil = os.path.join(tmp, "evil.py")
        with open(evil, "w", encoding="utf-8", newline="\n") as h:
            h.write("X=" + chr(34) + "q_supply"
                    + "_missing_attribute" + chr(34) + "\n")
            h.write("Y=[" + chr(34) + "E" + chr(34) + "]\n")
            # Combined on one line to trip the detector:
            h.write("MAP={" + chr(34) + "q_supply_missing_attribute"
                    + chr(34) + ": [" + chr(34) + "E" + chr(34)
                    + "]}\n")
        problems = scanner._check_src_file(evil, "src/pc/evil2.py")
        assert len(problems) > 0, problems
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
