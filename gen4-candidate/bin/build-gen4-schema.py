#!/usr/bin/env python3
"""Build the fm-sol-control/v2 SCHEMA GENERATION 4 from the frozen generation 3.

The protocol string is UNCHANGED (`fm-sol-control/v2`); the generation is
distinguished by `vocabulary_digest`, exactly as generation 3 was distinguished
from generation 2. Generation 3 stays frozen and untouched at
artifacts/control/gen3/; this script only READS it.

Generation 4 exists for ONE reason (Browser Sol disposition on control#15): the
evidence_digest law had two disagreeing definitions inside frozen generation 3 --
the schema text ($defs.valid_while) declared the 3-tuple `kind\\tlocator\\tsha256`,
while the code (fsc3.evidence_digest, used by BOTH the producer at emit and the
consumer's staleness ladder L3, and by the applicability recomputation) computed
the 4-tuple `kind\\tlocator\\tsha256\\tdigest_basis`. Because evidence_digest was
not a declared, verifier-covered derivation, the disagreement was invisible at
emit and only surfaced at consumption. Request #14 (4-tuple) was refused by the
3-tuple queue-processor; request #15 (3-tuple, which Browser Sol then ruled) was
REFUSED_STALE by the 4-tuple consumer. No single value satisfied both.

Generation 4 makes evidence_digest ONE explicit, schema-visible, verifier-covered
canonical law, and adopts the 4-tuple deliberately (see gen4/DECISION.md): the
4-tuple binds digest_basis into the aggregate, closing observer finding 4.5 (a ref
silently switching fetched_bytes -> locator_identity without moving the aggregate).
The 3-tuple would regress that binding. digest_basis is therefore load-bearing and
is now DECLARED in the schema rather than hidden in code.

Usage: build-gen4-schema.py <gen3-schema.json> <out-gen4-schema.json>
"""
import hashlib
import json
import sys

GEN3, OUT = sys.argv[1], sys.argv[2]
raw3 = open(GEN3, "rb").read()
GEN3_SHA = hashlib.sha256(raw3).hexdigest()
d = json.loads(raw3)
D = d["$defs"]
CHANGES = []


def change(cid, source, what):
    CHANGES.append({"id": cid, "source": source, "change": what})


# --------------------------------------------------------------------------
# CHANGE G4-0 -- self-describing lineage.
# --------------------------------------------------------------------------
d["$comment"] = (
    "THE single source of truth for the clean-room control plane, SCHEMA GENERATION 4. "
    "Producer validation, consumer validation, the envelope-as-fetched verifier and the human "
    "reply-contract projection are all derived from THIS FILE and from nothing else. No field "
    "name may be typed by a human or an agent anywhere. The PROTOCOL STRING IS UNCHANGED at "
    "fm-sol-control/v2: a generation is distinguished by vocabulary_digest. Generation 4 "
    "supersedes generation 3 (sha256 " + GEN3_SHA + ") under the Browser Sol transport-recovery "
    "disposition of 2026-09-05 on control issue #15: it makes evidence_digest one explicit, "
    "schema-visible, verifier-covered canonical law and resolves the 3-tuple/4-tuple divergence "
    "in favour of the 4-tuple (digest_basis load-bearing). Generations 1, 2 and 3 remain frozen, "
    "published and historical; nothing emitted under them is ever revalidated under this one."
)
D["schema_generation"] = {
    "const": {
        "protocol": "fm-sol-control/v2",
        "generation": 4,
        "supersedes_schema_sha256": GEN3_SHA,
        "supersedes_generation": 3,
    },
    "$comment": (
        "Machine-readable lineage. The protocol string is deliberately NOT bumped, for the same "
        "reason as generations 2 and 3: the venue-isolation law compares it by exact equality and "
        "the retired venue owns fm-sol-control/v1 over a different envelope."
    ),
}
change("G4-0", "lineage", "generation 4 declared, generation 3 digest recorded in $defs.schema_generation")

# --------------------------------------------------------------------------
# CHANGE G4-1 -- evidence_digest is ONE declared canonical law (the 4-tuple),
# schema-visible and verifier-covered. Browser Sol control#15 disposition.
# --------------------------------------------------------------------------
# (a) The declared canonical derivation, analogous to $defs.id_derivation. This
#     is now the SINGLE source every surface (producer, as-fetched verifier,
#     applicability recomputation, consumer L3, receipt path) reads its rule from.
D["evidence_digest_derivation"] = {
    "const": {
        "field": "valid_while.evidence_digest",
        "over": "evidence_refs",
        "row": "kind\tlocator\tsha256\tdigest_basis",
        "order": "rows sorted ascending as byte strings",
        "join": "LF between rows, with a trailing LF after the last row",
        "hash": "sha256 of the UTF-8 encoding of the joined rows, lowercase hex",
        "tuple": 4,
        "digest_basis_load_bearing": True,
    },
    "$comment": (
        "THE ONE canonical evidence_digest law, generation 4. evidence_digest = sha256 over the "
        "canonical sorted list of 'kind\\tlocator\\tsha256\\tdigest_basis' QUADRUPLES, one per "
        "evidence ref, LF-terminated. It is a FOUR-tuple, not the three-tuple the generation-3 "
        "schema text declared: digest_basis is load-bearing and BOUND into the aggregate, so a ref "
        "that silently changes from a real byte digest (fetched_bytes) to a digest of its own "
        "locator identity (locator_identity) MOVES evidence_digest instead of leaving the ruler "
        "shown a different kind of binding under an unchanged aggregate (observer finding 4.5). "
        "Generation 3 implemented this four-tuple in code (fsc3.evidence_digest) while its schema "
        "text still declared the three-tuple; that hidden disagreement is the exact defect this "
        "generation removes. Producer, envelope verifier, applicability recomputation, consumer "
        "staleness ladder L3 and the receipt path ALL derive from THIS const and nothing else."
    ),
}
# (b) valid_while.$comment now points at the declared law rather than restating a
#     divergent rule inline.
D["valid_while"]["$comment"] = (
    "THE STALENESS LADDER'S INPUTS. All are identity comparisons against LIVE reads at "
    "consumption. evidence_digest is computed by the ONE declared canonical law "
    "$defs.evidence_digest_derivation (the four-tuple binding kind, locator, sha256 AND "
    "digest_basis); a ruling bound to a request id is not thereby bound to the evidence its ruler "
    "was shown (v1 CHANGE 4). Generation 4 moved this rule OUT of prose and into "
    "$defs.evidence_digest_derivation so producer, verifier, applicability and consumer cannot "
    "disagree the way generation 3's code and schema text did (control#15)."
)
# (c) The as-fetched envelope verifier now COVERS evidence_digest: it recomputes
#     it from evidence_refs per the declared law and fails closed on a mismatch,
#     so a producer/schema disagreement is caught at EMIT, not only at consume.
ev = D["envelope_verifier"]["const"]
ev["tool"] = "artifacts/control/gen4/bin/fsc4-verify-envelope.py"
ev["checks"] = list(ev["checks"]) + [
    "valid_while.evidence_digest recomputes from evidence_refs per $defs.evidence_digest_derivation"
]
D["envelope_verifier"]["$comment"] += (
    " GENERATION 4 adds evidence_digest to the declared verification coverage: the verifier "
    "recomputes valid_while.evidence_digest from evidence_refs under $defs.evidence_digest_derivation "
    "and folds a mismatch to observed-bad, so a producer/schema disagreement fails closed at emit "
    "time rather than surfacing only in the consumer staleness ladder (control#15)."
)
# (d) venue_publication + reply-contract references that name the gen-3 verifier
#     path move to the gen-4 tool (the law is identical; only the generation path
#     differs).
if "venue_publication" in D and "verifier" in D["venue_publication"].get("const", {}):
    D["venue_publication"]["const"]["verifier"] = "artifacts/control/gen4/bin/fsc4-verify-envelope.py"
change("G4-1", "Browser Sol control#15 transport-recovery disposition",
       "evidence_digest declared as ONE canonical four-tuple law in $defs.evidence_digest_derivation; "
       "valid_while.$comment points at it; $defs.envelope_verifier covers evidence_digest recomputation; "
       "digest_basis made load-bearing and schema-visible")

# --------------------------------------------------------------------------
json.dump(d, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False, sort_keys=False)
open(OUT, "a", encoding="utf-8").write("\n")
out_sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
print("gen3 sha256 %s  (%d bytes, unmodified)" % (GEN3_SHA, len(raw3)))
print("gen4 sha256 %s  (%d bytes)" % (out_sha, len(open(OUT, 'rb').read())))
print("changes     %d" % len(CHANGES))
for c in CHANGES:
    print("  %-5s %s" % (c["id"], c["change"].split(";")[0]))
json.dump({"gen3_sha256": GEN3_SHA, "gen4_sha256": out_sha, "changes": CHANGES},
          open(OUT + ".changes.json", "w", encoding="utf-8"), indent=2)
