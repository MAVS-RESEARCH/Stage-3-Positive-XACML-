"""Phase-4 independent freeze solver for PC-XACML-S3+.

Second implementation of the exact all-freeze evaluation over the same
contract plus mechanically derived touch map (plus the freeze order
from the sealed non-outcome inputs). It never imports the primary
search code; it enumerates surviving finite policy trees directly as
ordered sequences with itertools.product (no sampling) and prices each
tree by its worst positive-support branch. Agreement with the primary
solver is required on the available set, closer existence, exact finite
cost, and all eight coordinates.

Step console lines use the [P4:indsolve:NNN] tag, each marked by a
[P4-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import itertools
import json
import os
import sys
from datetime import datetime, timezone


def abort(msg):
    """Emit a fail-closed error line and exit nonzero."""
    # [P4-LOG-900] Fail-closed termination marker for every abort path.
    print("[P4:indsolve:FAIL] " + msg, flush=True)
    sys.exit(1)


def digest_file(path):
    """Return the hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_doc(path):
    """Read a JSON document, failing closed on absence."""
    if not os.path.isfile(path):
        abort("missing required artifact: " + path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def now_utc():
    """Return the current UTC time in seal format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def frozen_set_for_label(label):
    """Derive the frozen resource set from a freeze label.

    The label form is F plus three binary digits in E,R,A order, so
    the set is decoded positionally rather than looked up.
    """
    if (len(label) != 4 or label[0] != "F"
            or any(ch not in "01" for ch in label[1:])):
        abort("malformed freeze label: " + str(label))
    bits = label[1:]
    symbols = ("E", "R", "A")
    return sorted(sym for sym, bit in zip(symbols, bits) if bit == "1")


def collect_declared_ids(contract_doc, touch_doc):
    """Determine the declared identifier universe from contract+touch.

    Reads only identifier keys (never interiors). Cross-checks the
    touch, successor, and cost maps for unknown entries and requires a
    cost entry per identifier. Returns the sorted identifier list.
    """
    raw_actions = contract_doc.get("actions", {})
    if isinstance(raw_actions, dict):
        universe = sorted(raw_actions.keys())
    elif isinstance(raw_actions, list):
        universe = []
        for item in raw_actions:
            if isinstance(item, str):
                universe.append(item)
            elif isinstance(item, dict):
                found = None
                for cand in ("name", "action_id", "id"):
                    if isinstance(item.get(cand), str):
                        found = item[cand]
                        break
                if found is None:
                    abort("unrecognized action entry shape")
                universe.append(found)
            else:
                abort("unrecognized action entry shape")
        universe = sorted(universe)
    else:
        abort("contract actions field has unrecognized shape")
    if not universe:
        merged = set()
        for fld in ("successors", "costs", "atomicity"):
            grp = contract_doc.get(fld, {})
            if isinstance(grp, dict):
                merged.update(grp.keys())
        if isinstance(touch_doc, dict):
            merged.update(touch_doc.keys())
        universe = sorted(merged)
    if not universe:
        abort("no actions declared in contract")
    # Agreement uses checkpoint-aware successor references: the compiled
    # table nests action maps under checkpoint keys, while minimal
    # fixtures key actions directly. Gather referenced ids either way.
    referenced = set()
    tree = contract_doc.get("successors", {})
    if isinstance(tree, dict):
        for top, sub in tree.items():
            if top in universe and isinstance(sub, (dict, list, str)):
                referenced.add(top)
            if isinstance(sub, dict):
                for nested in sub.keys():
                    if nested in universe:
                        referenced.add(nested)
    if isinstance(raw_actions, dict):
        for ident, detail in raw_actions.items():
            if isinstance(detail, dict) and isinstance(
                    detail.get("successors"), list):
                referenced.add(ident)
    for origin, mapping in (("touch", touch_doc),
                            ("costs", contract_doc.get("costs", {}))):
        if isinstance(mapping, dict):
            unknown = sorted(set(mapping.keys()) - set(universe))
            if unknown:
                abort("unknown identifiers in %s: %s" % (origin, unknown))
    stray = sorted(referenced - set(universe))
    if stray:
        abort("unknown identifiers in successors: %s" % stray)
    price = contract_doc.get("costs", {})
    if isinstance(price, dict):
        absent = sorted(set(universe) - set(price.keys()))
        if absent:
            abort("actions missing cost entries: %s" % absent)
    if len(set(universe)) != len(universe):
        abort("duplicate action identifiers")
    for ident in universe:
        if not isinstance(ident, str) or not ident:
            abort("non-string action identifier")
    return universe


def checkpoints_for_identifier(contract_doc, ident):
    """Normalize the checkpoint list for one identifier.

    Understands the compiled checkpoint-nested layout, the minimal
    direct layout, and the actions-table list fallback.
    """
    slot = None
    group = contract_doc.get("successors", {})
    if isinstance(group, dict) and ident in group:
        slot = group[ident]
    elif isinstance(group, dict):
        for _mark, inner in group.items():
            if isinstance(inner, dict) and ident in inner:
                slot = inner[ident]
                break
    if slot is None:
        acts = contract_doc.get("actions", {})
        if isinstance(acts, dict) and ident in acts:
            detail = acts[ident]
            if isinstance(detail, dict) and "successors" in detail:
                slot = detail["successors"]
    if slot is None:
        abort("missing successor entry for action")
    if isinstance(slot, dict):
        vals = list(slot.values())
    elif isinstance(slot, list):
        vals = slot
    elif isinstance(slot, str):
        vals = [slot]
    else:
        abort("unrecognized successor entry shape")
    uniq = sorted(set(v for v in vals if isinstance(v, str) and v))
    if not uniq:
        abort("empty successor list")
    return uniq


def world_map_for_identifier(contract_doc, ident):
    """Return the world->checkpoint map for one identifier, if mapped."""
    group = contract_doc.get("successors", {})
    cands = []
    if isinstance(group, dict) and ident in group:
        cands.append(group.get(ident, {}))
    if isinstance(group, dict):
        for _mark, inner in group.items():
            if isinstance(inner, dict) and ident in inner:
                cands.append(inner[ident])
    for slot in cands:
        if isinstance(slot, dict) and all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in slot.items()):
            return dict(slot)
    return None


def price_for_identifier(contract_doc, ident):
    """Return the numeric price for one identifier."""
    book = contract_doc.get("costs", {})
    amt = book.get(ident)
    if amt is None:
        acts = contract_doc.get("actions", {})
        if isinstance(acts, dict) and ident in acts:
            detail = acts[ident]
            if isinstance(detail, dict):
                amt = detail.get("cost", detail.get("unit_cost"))
    if isinstance(amt, bool) or not isinstance(amt, (int, float)):
        abort("non-numeric cost entry")
    if not (amt > 0):
        abort("non-positive cost entry")
    return amt


def closed_by_checkpoint(contract_doc):
    """Infer the closed flag per checkpoint from contract evidence.

    Prefers an explicit checkpoints table (open/closed flags) when
    present; otherwise the start point is open exactly when the target
    map is heterogeneous, and each listed terminal is treated as a
    closed singleton fiber per the compiler fiber rule.
    """
    start = contract_doc.get("initial_checkpoint", "S0")
    aims = contract_doc.get("target", {})
    if not isinstance(aims, dict) or len(aims) < 2:
        abort("contract target map missing or too small")
    if len(set(str(v) for v in aims.values())) <= 1:
        abort("initial checkpoint is not open (targets homogeneous)")
    table = contract_doc.get("checkpoints", None)
    flags = {}
    if isinstance(table, dict):
        for name, info in table.items():
            if isinstance(info, dict):
                if "closed" in info:
                    flags[name] = (info["closed"] is True)
                elif "open" in info:
                    flags[name] = (info["open"] is False)
                else:
                    flags[name] = (name != start)
            elif isinstance(info, bool):
                flags[name] = info
            else:
                flags[name] = (name != start)
        flags.setdefault(start, False)
        for ident in collect_declared_ids(contract_doc, {}):
            for cp in checkpoints_for_identifier(contract_doc, ident):
                flags.setdefault(cp, (cp != start))
    else:
        flags[start] = False
        for ident in collect_declared_ids(contract_doc, {}):
            for cp in checkpoints_for_identifier(contract_doc, ident):
                flags.setdefault(cp, True)
    return flags


def identifier_closes(contract_doc, flags, ident):
    """Test whether one identifier alone closes the start point."""
    return all(flags.get(cp, False)
               for cp in checkpoints_for_identifier(contract_doc, ident))


def sequence_closes(contract_doc, flags, seq):
    """Test whether an ordered identifier sequence closes the point."""
    # A sequence closes iff its distinct member set holds at least one
    # individually closing identifier (one native repair step already
    # reaches closed terminals; longer sequences add no further
    # reachability but are enumerated to prove exhaustiveness).
    seen = set()
    for ident in seq:
        if ident in seen:
            continue
        seen.add(ident)
        if identifier_closes(contract_doc, flags, ident):
            return True
    return False


def assess_freeze(contract_doc, touch_norm, flags, universe,
                  label, frozen_list, contract_digest):
    """Assess one freeze by enumerating ordered surviving trees."""
    frozen_s = set(frozen_list)
    gone = sorted(ident for ident in universe
                  if set(touch_norm.get(ident, [])) & frozen_s)
    left = sorted(set(universe) - set(gone))
    if sorted(gone + left) != sorted(universe):
        abort("freeze partition violated identifier conservation")
    for ident in gone + left:
        if ident not in universe:
            abort("freeze fabricated an unknown identifier")
    # Direct enumeration of all surviving finite policy trees as
    # ordered sequences via itertools.product (lengths 1..N, tiny
    # graph so the full cross product is trivially enumerable).
    cheapest = None
    cheapest_seq = None
    if left:
        ranked = sorted(left)
        for depth in range(1, len(ranked) + 1):
            for seq in itertools.product(ranked, repeat=depth):
                if not sequence_closes(contract_doc, flags, seq):
                    continue
                distinct = sorted(set(seq))
                total = max(price_for_identifier(contract_doc, ident)
                            for ident in distinct)
                if cheapest is None or total < cheapest:
                    cheapest = total
                    cheapest_seq = distinct
    exists = cheapest_seq is not None
    if exists:
        if isinstance(cheapest, float) and cheapest.is_integer():
            cheapest = int(cheapest)
        kappa_val = cheapest
        worst_val = cheapest
    else:
        kappa_val = "INF"
        worst_val = "INF"
    start = contract_doc.get("initial_checkpoint", "S0")
    reached = sorted(set([start] + [
        cp for ident in left
        for cp in checkpoints_for_identifier(contract_doc, ident)
    ]))
    aims = contract_doc.get("target", {})
    term_classes = {}
    for ident in left:
        wmap = world_map_for_identifier(contract_doc, ident)
        if wmap:
            for world, cp in wmap.items():
                if world in aims:
                    term_classes[cp] = aims[world]
    if not term_classes:
        for ident in left:
            for cp in checkpoints_for_identifier(contract_doc, ident):
                if cp not in term_classes:
                    term_classes[cp] = None
        term_classes = {k: v for k, v in term_classes.items()
                        if v is not None}
        if not term_classes:
            term_classes = dict(sorted(
                (cp, None) for cp in reached if cp != start))
    # Silence unused-variable lint for the witness combo detail.
    _witness = cheapest_seq
    return {
        "freeze": label,
        "frozen_resources": sorted(frozen_list),
        "removed_actions": gone,
        "surviving_actions": left,
        "reachable_checkpoints": reached,
        "proper_closer_exists": exists,
        "worst_branch_cost": worst_val,
        "kappa": kappa_val,
        "terminal_target_classes": dict(sorted(term_classes.items())),
        "solver": "independent",
        "contract_sha256": contract_digest,
    }


def main(argv):
    """Entry point: solve all eight freezes independently."""
    # [P4-LOG-010] Step: start independent solve, echo arguments.
    print("[P4:indsolve:010] start independent freeze evaluation",
          flush=True)
    if len(argv) != 5:
        abort("usage: independent_solver.py <contract> <touch> "
              "<execution_inputs> <out_dir>")
    contract_p, touch_p, inputs_p, dest = argv[1:5]
    # [P4-LOG-012] Step: echo the resolved contract path.
    print("[P4:indsolve:012] contract=%s" % os.path.abspath(contract_p),
          flush=True)
    contract_doc = read_doc(contract_p)
    touch_raw = read_doc(touch_p)
    inputs_doc = read_doc(inputs_p)
    if not isinstance(touch_raw, dict):
        abort("touch map must be an object")
    touch_norm = {}
    for key, val in touch_raw.items():
        if isinstance(val, list):
            touch_norm[key] = sorted(set(str(v) for v in val))
        elif isinstance(val, str):
            touch_norm[key] = [str(val)]
        else:
            abort("unrecognized touch entry shape")
        for sym in touch_norm[key]:
            if sym not in ("E", "R", "A"):
                abort("unknown resource symbol")
    # [P4-LOG-020] Step: resolve freeze order from the sealed inputs.
    print("[P4:indsolve:020] resolving freeze order", flush=True)
    seq = inputs_doc.get("freeze_order", [])
    if (not isinstance(seq, list) or len(seq) != 8
            or set(seq) != {"F000", "F100", "F010", "F001",
                            "F110", "F101", "F011", "F111"}):
        abort("freeze order must list all eight masks once")
    universe = collect_declared_ids(contract_doc, touch_norm)
    flags = closed_by_checkpoint(contract_doc)
    digest = digest_file(contract_p)
    # [P4-LOG-022] Step: echo action count and freeze order.
    print("[P4:indsolve:022] actions=%d order=%s" % (len(universe), seq),
          flush=True)
    # [P4-LOG-030] Step: assess each mask via direct tree enumeration.
    print("[P4:indsolve:030] assessing eight freezes", flush=True)
    rows = []
    for label in seq:
        frozen_list = frozen_set_for_label(label)
        row = assess_freeze(contract_doc, touch_norm, flags, universe,
                            label, frozen_list, digest)
        rows.append(row)
        # [P4-LOG-032] Step: per-freeze outcome line.
        print("[P4:indsolve:032] %s frozen=%s surviving=%d kappa=%s"
              % (label, frozen_list, len(row["surviving_actions"]),
                 row["kappa"]), flush=True)
    os.makedirs(dest, exist_ok=True)
    for row in rows:
        dest_p = os.path.join(dest, "%s.json" % row["freeze"])
        with open(dest_p, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(row, handle, indent=2, sort_keys=True)
            handle.write("\n")
    vec = [row["kappa"] for row in rows]
    nontriv_flag = any(v != vec[0] for v in vec[1:])
    summary = {
        "experiment_id": "PC-XACML-S3PLUS-v1",
        "contract_id": contract_doc.get("contract_id", ""),
        "contract_sha256": digest,
        "freeze_order": seq,
        "kappa": vec,
        "nontrivial": nontriv_flag,
        "solver": "independent",
        "produced_utc": now_utc(),
    }
    with open(os.path.join(dest, "K_table.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P4-LOG-040] Step: consolidated table written, report summary.
    print("[P4:indsolve:040] K_table=%s nontrivial=%s"
          % (vec, nontriv_flag), flush=True)
    # [P4-LOG-050] Step: independent solve complete.
    print("[P4:indsolve:050] independent freeze evaluation complete",
          flush=True)


if __name__ == "__main__":
    main(sys.argv)
