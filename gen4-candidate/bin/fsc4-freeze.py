#!/usr/bin/env python3
"""Declare the write-once freeze of fm-sol-control/v2 SCHEMA GENERATION 4.

The freeze record names every artifact whose bytes the protocol's behaviour
depends on, so drift in any one of them is detectable rather than assumed away.
Generation 4 adds the gen4 evidence-digest watched-red suite to the frozen set,
because the evidence_digest canonical-owner law is exactly what this generation
exists to make invariant.

The control-config generation is recorded as a SNAPSHOT, explicitly non-binding:
the config generation is DESIGNED to move (a repository, routing or listener
change must move it), so freezing the schema to one config value would make a
legitimate configuration change look like schema drift.

Usage: fsc4-freeze.py <out FREEZE.json>
"""
import datetime
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fsc4_config  # noqa: E402

GEN4 = fsc4_config.CONTROL_ROOT
PRIOR = os.path.join(os.path.dirname(GEN4), "gen3", "schema", "fm-sol-control-v2.schema.json")

FROZEN = [
    ("schema", "schema/fm-sol-control-v2.schema.json"),
    ("renderer", "bin/fsc4.py"),
    ("resolver", "bin/fsc4_config.py"),
    ("consumer", "bin/fsc4-consume.py"),
    ("redactor", "bin/fsc4-redact.py"),
    ("emitter", "bin/fsc4-emit-request.py"),
    ("envelope_verifier", "bin/fsc4-verify-envelope.py"),
    ("listener_tool", "bin/fsc4-listener.py"),
    ("listener_extension_manifest", "listener/firstmate-extension.json"),
    ("listener_extension_entrypoint", "listener/cleanroom-control-inbound.mjs"),
    ("schema_builder", "bin/build-gen4-schema.py"),
    ("reply_contract_request", "schema/reply-contract.request.txt"),
    ("reply_contract_ruling", "schema/reply-contract.ruling.txt"),
    ("reply_contract_receipt", "schema/reply-contract.receipt.txt"),
    ("watched_reds", "reds/watched-reds.py"),
    ("watched_reds_evidence_digest", "reds/gen4-evidence-digest-reds.py"),
    ("watched_reds_fake_forge", "reds/fixture-fake-gh.sh"),
]


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    out = sys.argv[1]
    if os.path.exists(out):
        sys.stderr.write("REFUSED: %s already exists; a freeze is write-once\n" % out)
        return 6
    artifacts = {}
    for name, rel in FROZEN:
        p = os.path.join(GEN4, rel)
        artifacts[name] = {"path": "artifacts/control/gen4/" + rel,
                           "sha256": sha(p), "bytes": os.path.getsize(p)}
    gen, _cfg, _norm = fsc4_config.generation()
    record = {
        "record": "fm-sol-control-v2-schema-freeze/v4",
        "protocol": "fm-sol-control/v2",
        "schema_generation": 4,
        "frozen_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "supersedes": {
            "schema_generation": 3,
            "path": "artifacts/control/gen3/schema/fm-sol-control-v2.schema.json",
            "schema_sha256": sha(PRIOR),
            "freeze_record": "artifacts/control/gen3/schema/FREEZE.json",
            "disposition": (
                "Generations 1, 2 and 3 stay frozen, published and untouched (Browser Sol "
                "control#15 transport-recovery disposition). The historical transactions on "
                "issues #1, #2 and #3 -- and the completed generation-3 transactions, including "
                "the REFUSED_STALE receipt on #15 -- are never revalidated under generation 4: an "
                "immutable historical record is not a defect to retrofit. Generation 4 is a "
                "SEPARATE, UNACTIVATED candidate; no control_config_generation moves for it."),
        },
        "recovery_basis": (
            "control#15: generation 3 carried two disagreeing evidence_digest definitions -- the "
            "schema text declared the 3-tuple while fsc3.evidence_digest computed the 4-tuple, and "
            "evidence_digest was not verifier-covered, so the disagreement was invisible at emit "
            "and only surfaced at consume (REFUSED_STALE on #15). Generation 4 makes evidence_digest "
            "ONE declared, schema-visible, verifier-covered canonical law ($defs.evidence_digest_"
            "derivation), adopting the 4-tuple deliberately (digest_basis load-bearing; observer 4.5)."),
        "artifacts": artifacts,
        "control_config_generation_snapshot": {
            "owner_path": gen["owner_path"],
            "digest": gen["digest"],
            "resolver_digest": gen["resolver_digest"],
            "binding": "NON-BINDING SNAPSHOT",
            "note": (
                "Recorded so a reader can see which configuration was in force at the freeze, and "
                "NOT as a freeze constraint. Generation 4 does NOT move the control-config "
                "generation; activation is a separate Browser Sol disposition."),
        },
        "write_once": True,
        "activated": False,
        "superseded_by": None,
        "freeze_ordering": (
            "FROZEN as an UNACTIVATED candidate. No fm-sol-control/v2 generation-4 envelope has "
            "been emitted; generation-3 authority-bearing delivery remains fail-closed until "
            "activation is separately dispositioned by Browser Sol (control#15). The gen4 "
            "evidence-digest watched-red suite was run green against these exact bytes."),
        "enforcement": (
            "Enforcement is DIGEST COMPARISON ONLY -- detective, not preventive -- through "
            "bin/fsc4-verify-freeze.sh, which re-hashes every artifact above and refuses on any "
            "drift. The drvfs mount carries no file modes, so write-once cannot be enforced by "
            "permission; this is a real limit, recorded rather than assumed away."),
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("FROZE %d artifacts at %s" % (len(artifacts), record["frozen_at"]))
    for name, a in sorted(artifacts.items()):
        print("  %-30s %s  %6d  %s" % (name, a["sha256"][:16], a["bytes"], a["path"]))
    print("freeze record sha256 %s" % sha(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
