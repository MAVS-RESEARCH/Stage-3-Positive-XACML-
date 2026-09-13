"""Phase-3 PC data models for PC-XACML-S3PLUS-v1.

Frozen dataclasses for World / Checkpoint / Action / Contract with
canonical JSON serialization (sorted keys) and SHA-256 helpers.
Input models carry no touch fields by construction (INV-11): touch is a
derived output artifact, never an input field.

Step console lines use the [P3:models:NNN] tag, each marked by a
[P3-LOG-NNN] comment for Path.md citation. This module is a pure data
library: its only console lines live in the --self-check entry point
below, which exercises construction, canonical round-trip, and the
no-touch-field invariant.
"""

import hashlib
import json
import sys
from dataclasses import dataclass, field

# [P3-LOG-010] Step: pin experiment and contract identifiers.
EXPERIMENT_ID = "PC-XACML-S3PLUS-v1"
CONTRACT_ID = "pc-xacml-s3plus-primary"


def canonical_json_bytes(obj):
    """Return deterministic canonical JSON bytes (sorted keys).

    Canonical form: sort_keys=True, separators (",", ": ") matching the
    sealed corpus convention, ensure_ascii default, trailing newline is
    added by writers, not here.
    """
    return json.dumps(obj, sort_keys=True, separators=(", ", ": "),
                      ensure_ascii=False).encode("utf-8")


def sha256_bytes(data):
    """Return the hex SHA-256 digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


def sha256_canonical(obj):
    """Return the hex SHA-256 digest of the canonical JSON form."""
    return sha256_bytes(canonical_json_bytes(obj))


def sha256_file(path):
    """Return the hex SHA-256 digest of a file's bytes."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump_canonical(obj, path):
    """Write obj as deterministic JSON (sorted keys, indent 2, LF)."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


@dataclass(frozen=True)
class World:
    """One latent complete-request world (value only, no outcome)."""

    name: str
    missing_attribute_value: str

    def to_dict(self):
        """Return the canonical dict form."""
        return {"name": self.name,
                "missing_attribute_value": self.missing_attribute_value}


@dataclass(frozen=True)
class Checkpoint:
    """One PC checkpoint with its world fiber and openness.

    Openness is always computed from fiber/target homogeneity by the
    compiler, never copied from an input literal.
    """

    checkpoint_id: str
    fiber: tuple
    is_open: bool
    reason: str

    def to_dict(self):
        """Return the canonical dict form (open flag, no touch)."""
        return {"fiber": list(self.fiber),
                "open": bool(self.is_open),
                "reason": self.reason}


@dataclass(frozen=True)
class ActionSpec:
    """One native repair action (interface only, no touch)."""

    action_id: str
    pre: str
    successors: tuple
    cost: float
    construction_rule: str = ""

    def to_dict(self):
        """Return the canonical dict form (no touch field)."""
        return {"action_id": self.action_id,
                "pre": self.pre,
                "successors": list(self.successors),
                "cost": self.cost,
                "construction_rule": self.construction_rule}


@dataclass(frozen=True)
class Contract:
    """Primary PC contract (input schema carries no touch field)."""

    contract_id: str
    experiment_id: str
    worlds: tuple
    initial_checkpoint: str
    checkpoints: dict = field(default_factory=dict)
    target: dict = field(default_factory=dict)
    h: dict = field(default_factory=dict)
    pr: dict = field(default_factory=dict)
    lambda_obj: dict = field(default_factory=dict)
    omega: dict = field(default_factory=dict)
    actions: dict = field(default_factory=dict)
    successors: dict = field(default_factory=dict)
    costs: dict = field(default_factory=dict)
    atomicity: dict = field(default_factory=dict)
    freeze_order: tuple = field(default_factory=tuple)
    provenance: dict = field(default_factory=dict)

    def to_dict(self):
        """Return the canonical dict form (no touch/resource keys)."""
        # [P3-LOG-020] Step: serialize without any touch/resource field.
        return {
            "actions": dict(self.actions),
            "atomicity": dict(self.atomicity),
            "checkpoints": {k: (v.to_dict() if isinstance(
                v, Checkpoint) else v)
                for k, v in self.checkpoints.items()},
            "contract_id": self.contract_id,
            "costs": dict(self.costs),
            "experiment_id": self.experiment_id,
            "freeze_order": list(self.freeze_order),
            "H": dict(self.h),
            "initial_checkpoint": self.initial_checkpoint,
            "Lambda": dict(self.lambda_obj),
            "omega": dict(self.omega),
            "PR": dict(self.pr),
            "provenance": dict(self.provenance),
            "successors": dict(self.successors),
            "target": dict(self.target),
            "worlds": list(self.worlds),
        }


def _self_check():
    """Exercise construction, canonical round-trip, no-touch invariant."""
    # [P3-LOG-100] Step: start the models self-check.
    print("[P3:models:100] start models self-check", flush=True)
    world = World(name="x_permit", missing_attribute_value="riddle me this")
    assert world.to_dict() == {"name": "x_permit",
                               "missing_attribute_value": "riddle me this"}
    # [P3-LOG-102] Step: checkpoint openness is carried, never inferred.
    print("[P3:models:102] checkpoint carry check", flush=True)
    checkpoint = Checkpoint(checkpoint_id="S0",
                            fiber=("x_permit", "x_nonpermit"),
                            is_open=True, reason="self-check")
    assert checkpoint.to_dict()["open"] is True
    # [P3-LOG-104] Step: contract serializes with no touch/resource keys.
    print("[P3:models:104] contract no-touch check", flush=True)
    contract = Contract(contract_id=CONTRACT_ID,
                        experiment_id=EXPERIMENT_ID,
                        worlds=("x_permit", "x_nonpermit"),
                        initial_checkpoint="S0")
    blob = canonical_json_bytes(contract.to_dict())
    assert b"touch" not in blob and b"resource" not in blob
    # [P3-LOG-110] Step: self-check complete.
    print("[P3:models:110] self-check ok sha256=%s"
          % sha256_bytes(blob), flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        print("usage: models.py --self-check")
        sys.exit(1)
