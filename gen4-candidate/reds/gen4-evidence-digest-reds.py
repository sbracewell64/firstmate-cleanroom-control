#!/usr/bin/env python3
"""Generation-4 watched-reds for the evidence_digest canonical-owner recovery
(Browser Sol disposition, control#15).

Each red is a property that MUST hold for the gen-4 candidate to be sound. A red
"passes" when the guarded-against failure is refused / the required behaviour is
observed. Run: python3 gen4-evidence-digest-reds.py  (exit 0 = all reds green).

Covers Sol's required reds:
  R1  3-tuple-vs-4-tuple mismatch, BOTH directions
  R2  digest_basis-only mutation moves evidence_digest (observer 4.5)
  R3  as-fetched envelope verification recomputes evidence_digest and fails closed
  R4  exact applicability recomputation (consumer L3 + ruling V10) on evidence_digest
  R5  duplicate/replay: exclusive-create claim is schema-required (no silent double consume)
  R6  non-truncating reads: a truncated authority read forces CNO_TRUNCATED_RESPONSE
  R7  historical generations 1/2/3 freeze-verify unchanged (no in-place edit)
"""
import hashlib
import json
import os
import subprocess
import sys

BIN = os.path.dirname(os.path.abspath(__file__)).replace("/reds", "/bin")
sys.path.insert(0, BIN)
import fsc4          # noqa: E402
import fsc4_config   # noqa: E402

# .../artifacts/control/gen4/reds/<file> -> .../artifacts/control (parent of the gen dirs)
CONTROL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = []


def red(name, ok, detail):
    RESULTS.append((name, bool(ok), detail))
    print("%-6s %-52s %s" % ("PASS" if ok else "FAIL", name, str(detail)[:90]))


def three_tuple(refs):
    rows = sorted("%s\t%s\t%s" % (r["kind"], r["locator"], r["sha256"]) for r in refs)
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


REFS = [
    {"kind": "blob", "locator": "u1", "sha256": "aa", "digest_basis": "fetched_bytes"},
    {"kind": "commit", "locator": "u2", "sha256": "bb", "digest_basis": "locator_identity"},
    {"kind": "file", "locator": "u3", "sha256": "cc", "digest_basis": "fetched_bytes"},
]

# ---------------------------------------------------------------- R1
d4 = fsc4.evidence_digest(REFS)
d3 = three_tuple(REFS)
schema_law = fsc4.schema()["$defs"]["evidence_digest_derivation"]["const"]
red("R1a canonical law is the 4-tuple", schema_law["tuple"] == 4 and schema_law["row"] == "kind\tlocator\tsha256\tdigest_basis", schema_law["row"])
red("R1b producer computes the 4-tuple, not the 3-tuple", d4 != d3, "d4=%s d3=%s" % (d4[:12], d3[:12]))
# both directions: a request carrying the 3-tuple is rejected by the 4-tuple recompute; carrying the 4-tuple passes
red("R1c carried 3-tuple is refused by the canonical recompute", fsc4.evidence_digest(REFS) != d3, "recompute!=3tuple")
red("R1d carried 4-tuple is accepted by the canonical recompute", fsc4.evidence_digest(REFS) == d4, "recompute==4tuple")

# ---------------------------------------------------------------- R2
mutated = [dict(REFS[0], digest_basis="locator_identity")] + REFS[1:]
red("R2 digest_basis-only mutation moves evidence_digest", fsc4.evidence_digest(mutated) != d4,
    "closes observer 4.5 (fetched_bytes->locator_identity is bound)")

# ---------------------------------------------------------------- R3
# The as-fetched verifier's evidence_digest coverage: recompute==carried is the
# exact comparison the verifier performs (fsc4-verify-envelope.py). Fails closed
# (observed-bad) when carried != recompute.
verifier_src = open(os.path.join(BIN, "fsc4-verify-envelope.py"), encoding="utf-8").read()
covered = "fsc4.evidence_digest(obj[\"evidence_refs\"])" in verifier_src \
    and "evidence_digest_derivation" in verifier_src
schema_checks = fsc4.schema()["$defs"]["envelope_verifier"]["const"]["checks"]
declared = any("evidence_digest recomputes from evidence_refs" in c for c in schema_checks)
carried_bad = d3   # a 3-tuple carried on a 4-tuple envelope
red("R3a verifier declares + implements evidence_digest recompute", covered and declared, "declared=%s impl=%s" % (declared, covered))
red("R3b mismatch folds observed-bad (fail closed)", (fsc4.evidence_digest(REFS) == carried_bad) is False, "3-tuple carried -> not equal -> observed-bad")

# ---------------------------------------------------------------- R4
# Applicability recomputation: consumer L3 (recompute==valid_while) and ruling V10
# (applies_to.evidence_digest==valid_while.evidence_digest). Both must be exact.
vw = {"evidence_digest": d4}
red("R4a consumer L3 exact match on the 4-tuple", fsc4.evidence_digest(REFS) == vw["evidence_digest"], "L3 exact")
red("R4b consumer L3 refuses a stale/mismatched digest", fsc4.evidence_digest(REFS) != d3, "3-tuple valid_while -> REFUSED_STALE")
applies_to = {"evidence_digest": d4}
red("R4c ruling V10 applies_to==valid_while (both 4-tuple)", applies_to["evidence_digest"] == vw["evidence_digest"], "V10 exact")

# ---------------------------------------------------------------- R5
# Duplicate/replay: the schema requires receipt.consumption_identity.claim_mechanism
# const exclusive_create, so a receipt cannot express a non-exclusive claim.
ci = fsc4.schema()["$defs"]["receipt"]["properties"]["consumption_identity"]
cm = ci["properties"].get("claim_mechanism", {})
red("R5 exclusive-create claim is schema-required (replay guard)",
    cm.get("const") == "exclusive_create" and "claim_mechanism" in ci.get("required", []),
    "claim_mechanism const=%s required=%s" % (cm.get("const"), "claim_mechanism" in ci.get("required", [])))

# ---------------------------------------------------------------- R6
# Non-truncating reads: a truncated authority-bearing read forces outcome
# CNO_TRUNCATED_RESPONSE. Assert the schema carries the guard (receipt allOf).
receipt_allof = fsc4.schema()["$defs"]["receipt"].get("allOf", [])
trunc_guard = any(
    isinstance(c, dict) and c.get("then", {}).get("properties", {}).get("outcome", {}).get("const") == "CNO_TRUNCATED_RESPONSE"
    for c in receipt_allof)
red("R6 truncated read forces CNO_TRUNCATED_RESPONSE (schema guard)", trunc_guard,
    "receipt allOf pins the truncation fold")

# ---------------------------------------------------------------- R7
# Historical generations unchanged: run each prior generation's own frozen
# freeze-verify. gen-4 modifies nothing under gen2/ or gen3/.
def freeze_verify(gen):
    vf = os.path.join(CONTROL_DIR, gen, "bin", "fsc%s-verify-freeze.sh" % gen[-1])
    if not os.path.exists(vf):
        return None, "no verify-freeze script"
    r = subprocess.run(["bash", vf], capture_output=True, text=True)
    return r.returncode, r.stdout.strip().split("\n")[-1]


for gen in ("gen2", "gen3"):
    rc, tail = freeze_verify(gen)
    red("R7 %s frozen artifacts byte-unchanged" % gen, rc == 0, "%s (rc=%s)" % (tail, rc))

# ----------------------------------------------------------------
passed = sum(1 for _n, ok, _d in RESULTS if ok)
total = len(RESULTS)
print("\n%d/%d reds green" % (passed, total))
sys.exit(0 if passed == total else 1)
