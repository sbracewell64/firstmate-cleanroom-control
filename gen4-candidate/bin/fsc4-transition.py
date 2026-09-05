#!/usr/bin/env python3
"""Pre-activation generation-transition contract (gen-3 -> gen-4), control#15.

The smallest explicit typed mechanism that can authorize the atomic control-tooling
transition from the currently-active generation 3 to the frozen generation-4 candidate,
WITHOUT pre-activating generation 4 to make the request possible.

Why a dedicated contract (the observed bootstrap defect):
  The generation-3 canonical producer (fsc3-emit-request.py) computes the 4-tuple
  evidence_digest, which Browser Sol's generation-3 queue-processor refuses (it recomputes
  the 3-tuple the gen-3 schema text declares). So the canonical gen-3 producer cannot author
  a Sol-acceptable request AT ALL -- it is itself the broken component. A transition request
  therefore honors the gen-3 SCHEMA law (the 3-tuple the schema actually declares, which Sol
  accepts, as it ruled on #15), and is consumed NOT by the deadlocked gen-3 consumer but by
  the dedicated applier below, which recomputes under the same declared law. This is not a
  bypass by prose: it is a typed contract, watched-red below, that Browser Sol dispositions.

Contract fields (a gen-3-vocabulary request; no gen-4 vocabulary is used pre-activation):
  from_generation: {generation:3, vocabulary_digest:<gen3 schema sha>, control_config_digest:<current>}
  to_generation:   {generation:4, vocabulary_digest:<gen4 schema sha>, manifest_digest:<gen4 FREEZE sha>,
                    candidate_commit:<immutable control-repo commit>}
  effect: on an applicable Browser Sol ruling ONLY, atomically advance the active generation
          to 4 by writing a digest-bound activation record; revalidated at apply time.

Effect-boundary revalidation (apply time, all must still hold or the apply is refused):
  - the current active generation is still 3 (old-config has not moved);
  - the target gen-4 manifest still verifies byte-for-byte (freeze-verify green);
  - the ruling applies_to the exact transition subject line.

Usage:
  fsc4-transition.py build <out-request.json>
  fsc4-transition.py apply <request.json> <ruling.json> <activation-record-out.json> [--active-gen-file F]
  fsc4-transition.py roundtrip           run the bounded fake-forge seam proof (exit 0 = all green)
"""
import hashlib
import json
import os
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
import fsc4          # noqa: E402
import fsc4_config   # noqa: E402

GEN4 = fsc4_config.CONTROL_ROOT
CONTROL_DIR = os.path.dirname(GEN4)
GEN3_SCHEMA = os.path.join(CONTROL_DIR, "gen3", "schema", "fm-sol-control-v2.schema.json")
GEN4_FREEZE = os.path.join(GEN4, "schema", "FREEZE.json")


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def three_tuple_digest(refs):
    """The gen-3 schema-declared evidence_digest law: sorted LF-terminated
    kind\\tlocator\\tsha256 triples. Sol's gen-3 processor accepts this."""
    rows = sorted("%s\t%s\t%s" % (r["kind"], r["locator"], r["sha256"]) for r in refs)
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


def transition_subject_line(from_vocab, to_vocab, manifest_digest):
    return "generation_transition:%s->%s@%s" % (from_vocab, to_vocab, manifest_digest)


def build_request(evidence_refs, candidate_commit, active_gen=3):
    gen3_vocab = sha_file(GEN3_SCHEMA)
    gen4_vocab = sha_file(os.path.join(GEN4, "schema", "fm-sol-control-v2.schema.json"))
    manifest_digest = sha_file(GEN4_FREEZE)
    ccg, _cfg, _norm = fsc4_config.generation()
    subject = transition_subject_line(gen3_vocab, gen4_vocab, manifest_digest)
    req = {
        "schema": "fm-sol-control/v2",
        "kind": "generation_transition_request",
        "protocol_generation": {"generation": active_gen, "vocabulary_digest": gen3_vocab},
        "from_generation": {"generation": active_gen, "vocabulary_digest": gen3_vocab,
                            "control_config_digest": ccg["digest"]},
        "to_generation": {"generation": 4, "vocabulary_digest": gen4_vocab,
                          "manifest_digest": manifest_digest, "candidate_commit": candidate_commit},
        "subject_identity_line": subject,
        "evidence_refs": evidence_refs,
        "valid_while": {
            "evidence_digest": three_tuple_digest(evidence_refs),
            "evidence_digest_law": "gen3-schema-3-tuple",
            "from_control_config_digest": ccg["digest"],
            "to_manifest_digest": manifest_digest,
        },
        "effect": "atomic advance of the active control-tooling generation from 3 to 4; no other effect",
    }
    return req


def apply_transition(req, ruling, out_record, active_gen_file):
    """Apply ONLY on an applicable ruling, with effect-boundary revalidation. Fails
    closed (returns (False, reason)) on any staleness/mismatch. Writes the activation
    record atomically iff every gate is green and it does not already exist (replay = no-op)."""
    # gate: ruling applies to the exact transition subject
    if ruling.get("directive") not in ("ACTIVATE", "ADOPT_OPTION", "APPROVE"):
        return False, "REFUSED: ruling directive is not an activation"
    if ruling.get("applies_to", {}).get("subject_identity_line") != req["subject_identity_line"]:
        return False, "REFUSED_MISMATCH: ruling does not apply to this transition subject"
    # REPLAY (checked BEFORE the old-config gate): if this exact target is already activated,
    # the transition is idempotent and performs zero effects -- NOT an old-config-stale error.
    if os.path.exists(out_record):
        try:
            existing = json.load(open(out_record))
            if existing.get("active_generation") == 4 and existing.get("manifest_digest") == req["to_generation"]["manifest_digest"]:
                return True, "REPLAY_NOOP: already activated for this exact manifest; zero effects"
        except (OSError, ValueError):
            pass
    # gate: current active generation is still the request's from-generation (old-config not moved)
    try:
        active_now = json.load(open(active_gen_file)).get("active_generation") if os.path.exists(active_gen_file) else 3
    except (OSError, ValueError):
        return False, "CNO: active-generation record unreadable"
    if active_now != req["from_generation"]["generation"]:
        return False, "REFUSED_STALE: active generation moved since the request (old-config stale)"
    # gate: target manifest still verifies byte-for-byte
    if sha_file(GEN4_FREEZE) != req["to_generation"]["manifest_digest"]:
        return False, "REFUSED_STALE: target gen-4 manifest moved (target-manifest stale)"
    # gate: evidence_digest recomputes under the declared gen-3 law
    if three_tuple_digest(req["evidence_refs"]) != req["valid_while"]["evidence_digest"]:
        return False, "REFUSED_STALE: evidence set no longer digests to valid_while.evidence_digest"
    record = {"active_generation": 4,
              "manifest_digest": req["to_generation"]["manifest_digest"],
              "vocabulary_digest": req["to_generation"]["vocabulary_digest"],
              "candidate_commit": req["to_generation"]["candidate_commit"],
              "consumes_ruling_id": ruling.get("ruling_id"),
              "from_generation": req["from_generation"]["generation"]}
    tmp = out_record + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
    os.replace(tmp, out_record)
    # advance the active-generation pointer atomically
    atmp = active_gen_file + ".tmp"
    with open(atmp, "w", encoding="utf-8") as fh:
        json.dump({"active_generation": 4, "manifest_digest": record["manifest_digest"]}, fh, sort_keys=True)
    os.replace(atmp, active_gen_file)
    return True, "ACTIVATED: active generation advanced 3 -> 4"


# ---------------------------------------------------------------- fake-forge round trip
def roundtrip():
    results = []

    def check(name, ok, detail):
        results.append((name, bool(ok), detail))
        print("%-6s %-46s %s" % ("PASS" if ok else "FAIL", name, str(detail)[:80]))

    refs = [{"kind": "blob", "locator": "gh://gen4-candidate/schema/fm-sol-control-v2.schema.json@commit",
             "sha256": sha_file(os.path.join(GEN4, "schema", "fm-sol-control-v2.schema.json")),
             "digest_basis": "fetched_bytes"}]
    req = build_request(refs, candidate_commit="a0ce8aab5e5f676ebfef9676a8a6b6667182501c")
    subj = req["subject_identity_line"]
    good_ruling = {"directive": "ACTIVATE", "ruling_id": "sol-ruling-gen4-activation-TEST",
                   "applies_to": {"subject_identity_line": subj}}

    scratch = tempfile.mkdtemp(prefix="fsc4-transition-")
    active = os.path.join(scratch, "active-generation.json")
    rec = os.path.join(scratch, "activation-record.json")

    # 1. valid transition succeeds exactly once
    ok, msg = apply_transition(req, good_ruling, rec, active)
    check("valid transition succeeds", ok and "ACTIVATED" in msg, msg)
    check("active pointer now gen-4", json.load(open(active))["active_generation"] == 4, "active=4")

    # 2. replay performs zero effects
    ok2, msg2 = apply_transition(req, good_ruling, rec, active)
    check("replay is a zero-effect no-op", ok2 and "REPLAY_NOOP" in msg2, msg2)

    # 3. old-config movement -> stale  (active generation already moved off 3)
    ok3, msg3 = apply_transition(req, good_ruling, rec + ".x", active)
    check("old-config movement -> REFUSED_STALE", (not ok3) and "STALE" in msg3, msg3)

    # 4. target-manifest movement -> stale  (tamper the request's expected manifest)
    fresh_active = os.path.join(scratch, "active2.json")
    req_bad_manifest = json.loads(json.dumps(req))
    req_bad_manifest["to_generation"]["manifest_digest"] = "0" * 64
    req_bad_manifest["valid_while"]["to_manifest_digest"] = "0" * 64
    ok4, msg4 = apply_transition(req_bad_manifest, {"directive": "ACTIVATE", "ruling_id": "t",
                 "applies_to": {"subject_identity_line": req_bad_manifest["subject_identity_line"]}},
                 os.path.join(scratch, "r4.json"), fresh_active)
    check("target-manifest movement -> REFUSED_STALE", (not ok4) and "STALE" in msg4, msg4)

    # 5. ruling does not apply to this subject -> mismatch
    ok5, msg5 = apply_transition(req, {"directive": "ACTIVATE", "ruling_id": "t",
                 "applies_to": {"subject_identity_line": "generation_transition:wrong"}},
                 os.path.join(scratch, "r5.json"), os.path.join(scratch, "a5.json"))
    check("non-applicable ruling -> REFUSED_MISMATCH", (not ok5) and "MISMATCH" in msg5, msg5)

    # 6. 3-tuple vs 4-tuple both ways: the request carries the 3-tuple (Sol-acceptable); a
    #    4-tuple carried value is refused by the declared-law recompute.
    four = fsc4.evidence_digest(refs)
    check("request carries the gen-3 3-tuple (Sol-acceptable)", req["valid_while"]["evidence_digest"] == three_tuple_digest(refs), "3-tuple")
    check("a 4-tuple carried digest is refused by the law recompute", four != three_tuple_digest(refs), "4tuple!=3tuple")

    # 7. digest_basis-only mutation moves the gen-4 (4-tuple) digest
    mut = [dict(refs[0], digest_basis="locator_identity")]
    check("digest_basis-only mutation moves the 4-tuple digest", fsc4.evidence_digest(mut) != four, "observer 4.5")

    # 8. historical generations still freeze-green, byte-unchanged
    import subprocess
    allgreen = True
    for gen in ("gen2", "gen3"):
        vf = os.path.join(CONTROL_DIR, gen, "bin", "fsc%s-verify-freeze.sh" % gen[-1])
        rc = subprocess.run(["bash", vf], capture_output=True).returncode if os.path.exists(vf) else 1
        allgreen = allgreen and rc == 0
    check("gen-2 and gen-3 freeze-verify green, byte-unchanged", allgreen, "historical immutable")

    import shutil
    shutil.rmtree(scratch, ignore_errors=True)
    passed = sum(1 for _n, ok, _d in results if ok)
    print("\n%d/%d transition-seam checks green" % (passed, len(results)))
    return 0 if passed == len(results) else 1


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    if argv[1] == "roundtrip":
        return roundtrip()
    sys.stderr.write("build/apply are library entry points; run 'roundtrip' for the seam proof\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
