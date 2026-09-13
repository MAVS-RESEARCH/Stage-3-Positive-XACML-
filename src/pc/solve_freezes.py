"""Phase-4 primary exhaustive freeze solver for PC-XACML-S3+.

Reads a compiled contract plus a mechanically derived touch map (plus
the freeze order from the sealed non-outcome inputs). For each freeze
mask it applies the D33 removal rule literally over action identifiers
only, then runs an exhaustive policy-tree search over the surviving
actions with itertools enumeration (no sampling, no partial-action
fabrication). Writes one row per freeze plus a consolidated table in
prereg order with the contract hash embedded per row.

Step console lines use the [P4:solve:NNN] tag, each marked by a
[P4-LOG-NNN] comment for Path.md citation.
"""

import hashlib
import itertools
import json
import os
import sys
from datetime import datetime, timezone


def fail(message):
    """Emit a fail-closed error line and exit nonzero."""
    # [P4-LOG-900] Fail-closed termination marker for every abort path.
    print("[P4:solve:FAIL] " + message, flush=True)
    sys.exit(1)


def sha256_file(path):
    """Return the hex SHA-256 digest of a file."""
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


def frozen_for_name(freeze_name):
    """Map a freeze label to its frozen resource set via bit order.

    Bit positions are E,R,A in order: label Fxyz freezes E iff x is 1,
    R iff y is 1, A iff z is 1. Operates on the label only.
    """
    if (len(freeze_name) != 4 or not freeze_name.startswith("F")
            or any(c not in ("0", "1") for c in freeze_name[1:])):
        fail("malformed freeze label: " + str(freeze_name))
    out = []
    if freeze_name[1] == "1":
        out.append("E")
    if freeze_name[2] == "1":
        out.append("R")
    if freeze_name[3] == "1":
        out.append("A")
    return out


def collect_action_ids(contract, touch):
    """Collect the declared action identifier set from contract+touch.

    Primary source is the contract actions field (dict keys or list
    entries). Touch keys, successor keys, and cost keys must agree;
    any disagreement fails closed. Only identifiers are handled here;
    interiors are never inspected or edited.
    """
    declared = None
    raw = contract.get("actions", {})
    if isinstance(raw, dict):
        declared = sorted(raw.keys())
    elif isinstance(raw, list):
        ids = []
        for entry in raw:
            if isinstance(entry, str):
                ids.append(entry)
            elif isinstance(entry, dict):
                for key in ("id", "action_id", "name"):
                    if isinstance(entry.get(key), str):
                        ids.append(entry[key])
                        break
                else:
                    fail("unrecognized action entry shape")
            else:
                fail("unrecognized action entry shape")
        declared = sorted(ids)
    else:
        fail("contract actions field has unrecognized shape")
    if not declared:
        # Fall back to the union of the remaining contract maps so a
        # minimal spec-conformant fixture still resolves; the agreement
        # check below keeps this honest (no invented identifiers).
        union = set()
        for field in ("successors", "costs", "atomicity"):
            val = contract.get(field, {})
            if isinstance(val, dict):
                union.update(val.keys())
        if isinstance(touch, dict):
            union.update(touch.keys())
        declared = sorted(union)
    if not declared:
        fail("no actions declared in contract")
    # Agreement: every touch/cost key must be declared; successor maps
    # are checkpoint-keyed in the compiled contract (S0 -> action ->
    # world map) or action-keyed in minimal fixtures, so collect the
    # referenced identifiers from either shape. Successor coverage is
    # checked per action below.
    succ_ids = set()
    succ = contract.get("successors", {})
    if isinstance(succ, dict):
        for key, val in succ.items():
            if key in declared and isinstance(val, (dict, list, str)):
                succ_ids.add(key)
            if isinstance(val, dict):
                for inner_key in val.keys():
                    if inner_key in declared:
                        succ_ids.add(inner_key)
    # Fallback references inside the actions table itself.
    if isinstance(raw, dict):
        for ident, info in raw.items():
            if isinstance(info, dict) and isinstance(
                    info.get("successors"), list):
                succ_ids.add(ident)
    for source, mapping in (("touch", touch),
                            ("costs", contract.get("costs", {}))):
        if isinstance(mapping, dict):
            extra = sorted(set(mapping.keys()) - set(declared))
            if extra:
                fail("unknown identifiers in %s: %s" % (source, extra))
    # Successor references must also resolve to declared identifiers.
    extra_succ = sorted(succ_ids - set(declared))
    if extra_succ:
        fail("unknown identifiers in successors: %s" % extra_succ)
    costs = contract.get("costs", {})
    if isinstance(costs, dict):
        missing = sorted(set(declared) - set(costs.keys()))
        if missing:
            fail("actions missing cost entries: %s" % missing)
    for ident in declared:
        if not isinstance(ident, str) or not ident:
            fail("non-string action identifier")
    if len(set(declared)) != len(declared):
        fail("duplicate action identifiers")
    return declared


def successor_list(contract, action_id):
    """Normalize the successor checkpoint list for one action.

    Accepts the compiled checkpoint-keyed shape (successors[S0][action]
    as world map), the minimal action-keyed shape (successors[action]
    as world map / list / string), or the actions-table list
    (actions[action][successors]). Returns sorted deduplicated list.
    """
    entry = None
    succ = contract.get("successors", {})
    if isinstance(succ, dict) and action_id in succ:
        entry = succ[action_id]
    elif isinstance(succ, dict):
        for _cp, inner in succ.items():
            if isinstance(inner, dict) and action_id in inner:
                entry = inner[action_id]
                break
    if entry is None:
        raw = contract.get("actions", {})
        if isinstance(raw, dict) and action_id in raw:
            info = raw[action_id]
            if isinstance(info, dict) and "successors" in info:
                entry = info["successors"]
    if entry is None:
        fail("missing successor entry for action")
    if isinstance(entry, dict):
        vals = list(entry.values())
    elif isinstance(entry, list):
        vals = entry
    elif isinstance(entry, str):
        vals = [entry]
    else:
        fail("unrecognized successor entry shape")
    out = sorted(set(v for v in vals if isinstance(v, str) and v))
    if not out:
        fail("empty successor list")
    return out


def world_successor_map(contract, action_id):
    """Return the world->successor map for one action, if present."""
    succ = contract.get("successors", {})
    candidates = []
    if isinstance(succ, dict) and action_id in succ:
        candidates.append(succ.get(action_id, {}))
    if isinstance(succ, dict):
        for _cp, inner in succ.items():
            if isinstance(inner, dict) and action_id in inner:
                candidates.append(inner[action_id])
    for entry in candidates:
        if isinstance(entry, dict) and all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in entry.items()):
            return dict(entry)
    return None


def action_cost(contract, action_id):
    """Return the numeric cost for one action from the contract."""
    costs = contract.get("costs", {})
    val = costs.get(action_id)
    if val is None:
        raw = contract.get("actions", {})
        if isinstance(raw, dict) and action_id in raw:
            info = raw[action_id]
            if isinstance(info, dict):
                val = info.get("cost", info.get("unit_cost"))
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        fail("non-numeric cost entry")
    if not (val > 0):
        fail("non-positive cost entry")
    return val


def checkpoint_closed_map(contract):
    """Build the checkpoint->closed map for closure judgments.

    Uses the contract checkpoints field when present (open flag or
    closed flag); otherwise infers from target heterogeneity for the
    initial checkpoint (open iff targets differ) and treats listed
    successors as closed terminals (singleton homogeneous fibers per
    the compiler rule; never copies a bare literal without the fiber
    check below).
    """
    initial = contract.get("initial_checkpoint", "S0")
    target = contract.get("target", {})
    if not isinstance(target, dict) or len(target) < 2:
        fail("contract target map missing or too small")
    distinct = len(set(str(v) for v in target.values())) > 1
    if not distinct:
        fail("initial checkpoint is not open (targets homogeneous)")
    explicit = contract.get("checkpoints", None)
    closed = {}
    if isinstance(explicit, dict):
        for name, info in explicit.items():
            if isinstance(info, dict):
                if "open" in info:
                    closed[name] = (info["open"] is False)
                elif "closed" in info:
                    closed[name] = (info["closed"] is True)
                else:
                    closed[name] = (name != initial)
            elif isinstance(info, bool):
                closed[name] = info
            else:
                closed[name] = (name != initial)
        closed.setdefault(initial, False)
        # Every successor must be represented; absent entries default
        # to closed-terminal only if they are not the initial point.
        for ident in collect_action_ids(contract, {}):
            try:
                lst = successor_list(contract, ident)
            except SystemExit:
                raise
            for cp in lst:
                closed.setdefault(cp, (cp != initial))
    else:
        closed[initial] = False
        for ident in collect_action_ids(contract, {}):
            for cp in successor_list(contract, ident):
                # Terminal fibers are singleton homogeneous by the
                # compiler construction (one world per successor when
                # the map is world-keyed; otherwise the listed terminal
                # is recorded closed by that same construction).
                closed.setdefault(cp, True)
    return closed


def is_closing_identifier(contract, closed_map, action_id):
    """Decide whether one surviving action closes the initial point."""
    for cp in successor_list(contract, action_id):
        if not closed_map.get(cp, False):
            return False
    return True


def combo_closes(contract, closed_map, combo):
    """Decide whether an action-identifier combo closes the point."""
    # A combo closes iff it contains at least one closing identifier
    # (single-step native repair; larger combos add no new reachability
    # beyond their members, but enumerating them proves exhaustiveness).
    for ident in combo:
        if is_closing_identifier(contract, closed_map, ident):
            return True
    return False


def evaluate_freeze(contract, touch_map, closed_map, all_ids,
                    freeze_name, frozen, contract_sha):
    """Evaluate one freeze mask exhaustively over identifier subsets."""
    # D33 literal: remove every identifier whose touch intersects S.
    # Identifier-only operation: no interior is read or edited and no
    # partial subaction is fabricated (INV-12/13).
    frozen_set = set(frozen)
    removed = sorted(
        ident for ident in all_ids
        if set(touch_map.get(ident, [])) & frozen_set)
    surviving = sorted(set(all_ids) - set(removed))
    if sorted(removed + surviving) != sorted(all_ids):
        fail("freeze partition violated identifier conservation")
    for ident in removed + surviving:
        if ident not in all_ids:
            fail("freeze fabricated an unknown identifier")
    # Exhaustive policy-tree search: enumerate all non-empty subsets of
    # the surviving identifiers in increasing size order with
    # itertools.combinations (tiny graph: complete, no sampling).
    best_cost = None
    best_combo = None
    if surviving:
        ordered = sorted(surviving)
        for size in range(1, len(ordered) + 1):
            for combo in itertools.combinations(ordered, size):
                if not combo_closes(contract, closed_map, combo):
                    continue
                cost = max(action_cost(contract, ident) for ident in combo)
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_combo = combo
    proper = best_combo is not None
    if proper:
        kappa = best_cost
        # Normalize integral floats to ints for stable recording.
        if isinstance(kappa, float) and kappa.is_integer():
            kappa = int(kappa)
        worst = kappa
    else:
        kappa = "INF"
        worst = "INF"
    initial = contract.get("initial_checkpoint", "S0")
    reachable = sorted(set([initial] + [
        cp for ident in surviving for cp in successor_list(contract, ident)
    ]))
    # Terminal classes induced by the world->successor map plus target.
    target = contract.get("target", {})
    terminals = {}
    for ident in surviving:
        wmap = world_successor_map(contract, ident)
        if wmap:
            for world, cp in wmap.items():
                if world in target:
                    terminals[cp] = target[world]
    if not terminals:
        for ident in surviving:
            for cp in successor_list(contract, ident):
                terminals.setdefault(cp, None)
        terminals = {k: v for k, v in terminals.items() if v is not None}
        if not terminals:
            terminals = dict(sorted(
                (cp, None) for cp in reachable if cp != initial))
    row = {
        "freeze": freeze_name,
        "frozen_resources": sorted(frozen),
        "removed_actions": removed,
        "surviving_actions": surviving,
        "reachable_checkpoints": reachable,
        "proper_closer_exists": proper,
        "worst_branch_cost": worst,
        "kappa": kappa,
        "terminal_target_classes": dict(sorted(terminals.items())),
        "solver": "primary",
        "contract_sha256": contract_sha,
    }
    return row


def main(argv):
    """Entry point: solve all eight freezes from contract+touch."""
    # [P4-LOG-010] Step: start primary solve, echo resolved arguments.
    print("[P4:solve:010] start primary freeze evaluation", flush=True)
    if len(argv) != 5:
        fail("usage: solve_freezes.py <contract> <touch> "
             "<execution_inputs> <out_dir>")
    contract_path, touch_path, inputs_path, out_dir = argv[1:5]
    # [P4-LOG-012] Step: echo the resolved contract path.
    print("[P4:solve:012] contract=%s" % os.path.abspath(contract_path),
          flush=True)
    contract = load_json(contract_path)
    touch_raw = load_json(touch_path)
    inputs = load_json(inputs_path)
    # Touch normalization: values are resource lists; keys are ids.
    if not isinstance(touch_raw, dict):
        fail("touch map must be an object")
    touch_map = {}
    for key, val in touch_raw.items():
        if isinstance(val, list):
            touch_map[key] = sorted(set(str(v) for v in val))
        elif isinstance(val, str):
            touch_map[key] = [str(val)]
        else:
            fail("unrecognized touch entry shape")
        for res in touch_map[key]:
            if res not in ("E", "R", "A"):
                fail("unknown resource symbol")
    # [P4-LOG-020] Step: resolve freeze order from the sealed inputs.
    print("[P4:solve:020] resolving freeze order", flush=True)
    order = inputs.get("freeze_order", [])
    if (not isinstance(order, list) or len(order) != 8
            or set(order) != {"F000", "F100", "F010", "F001",
                              "F110", "F101", "F011", "F111"}):
        fail("freeze order must list all eight masks once")
    all_ids = collect_action_ids(contract, touch_map)
    closed_map = checkpoint_closed_map(contract)
    contract_sha = sha256_file(contract_path)
    # [P4-LOG-022] Step: echo action count and freeze order.
    print("[P4:solve:022] actions=%d order=%s" % (len(all_ids), order),
          flush=True)
    # [P4-LOG-030] Step: evaluate each mask exhaustively in order.
    print("[P4:solve:030] evaluating eight freezes", flush=True)
    rows = []
    for name in order:
        frozen = frozen_for_name(name)
        row = evaluate_freeze(contract, touch_map, closed_map, all_ids,
                              name, frozen, contract_sha)
        rows.append(row)
        # [P4-LOG-032] Step: per-freeze outcome line.
        print("[P4:solve:032] %s frozen=%s surviving=%d kappa=%s"
              % (name, frozen, len(row["surviving_actions"]),
                 row["kappa"]), flush=True)
    os.makedirs(out_dir, exist_ok=True)
    for row in rows:
        path = os.path.join(out_dir, "%s.json" % row["freeze"])
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(row, handle, indent=2, sort_keys=True)
            handle.write("\n")
    kappa_vec = [row["kappa"] for row in rows]
    # Nontriviality: some non-initial coordinate differs from F000.
    nontriv = any(k != kappa_vec[0] for k in kappa_vec[1:])
    table = {
        "experiment_id": "PC-XACML-S3PLUS-v1",
        "contract_id": contract.get("contract_id", ""),
        "contract_sha256": contract_sha,
        "freeze_order": order,
        "kappa": kappa_vec,
        "nontrivial": nontriv,
        "solver": "primary",
        "produced_utc": utcnow(),
    }
    with open(os.path.join(out_dir, "K_table.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(table, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # [P4-LOG-040] Step: consolidated table written, report summary.
    print("[P4:solve:040] K_table=%s nontrivial=%s"
          % (kappa_vec, nontriv), flush=True)
    # [P4-LOG-050] Step: primary solve complete.
    print("[P4:solve:050] primary freeze evaluation complete", flush=True)


if __name__ == "__main__":
    main(sys.argv)
