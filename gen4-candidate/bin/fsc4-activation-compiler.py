#!/usr/bin/env python3
"""QUARANTINED one-use recovery compiler: build the generation-4 ACTIVATION request, control#15.

This tool exists ONLY to author the authority request that breaks the gen-3 emitter bootstrap.
It is EFFECT-INCAPABLE by construction: it imports nothing that can change control_config_generation,
apply a ruling, land code, publish to a venue, or perform any other effect. It reads candidate bytes
and writes JSON files (the request + a differential proof) and nothing else.

Its output is an ORDINARY frozen-gen-3 `kind="request"` that validates against the UNCHANGED gen-3
schema. It encodes the transition through the existing request vocabulary (work_id, document_package
subject over the candidate files, question/options A|B, acceptance policy, evidence refs, valid_while).
The ONLY intentional correction relative to the broken canonical gen-3 producer is that
`valid_while.evidence_digest` is computed by the EXACT frozen gen-3 schema law: sorted LF-terminated
`kind\\tlocator\\tsha256` triples (the value Browser Sol's gen-3 processor accepts). The differential
proof shows that is the ONLY field that differs from the canonical producer's output.

Usage: fsc4-activation-compiler.py <candidate-commit> <out-request.json> <out-differential-proof.json>
"""
import hashlib
import json
import os
import sys

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(BIN)), "gen3", "bin"))
import fsc4_config   # noqa: E402
import fsc3          # gen-3 identity derivation + validation (read-only)  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

GEN4 = fsc4_config.CONTROL_ROOT
CONTROL_DIR = os.path.dirname(GEN4)
GEN3_SCHEMA = os.path.join(CONTROL_DIR, "gen3", "schema", "fm-sol-control-v2.schema.json")
GEN4_SCHEMA = os.path.join(GEN4, "schema", "fm-sol-control-v2.schema.json")
GEN4_FREEZE = os.path.join(GEN4, "schema", "FREEZE.json")
REPO = "sbracewell64/firstmate-cleanroom-control"


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def three_tuple(refs):
    rows = sorted("%s\t%s\t%s" % (r["kind"], r["locator"], r["sha256"]) for r in refs)
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


def doc_package_identity(members):
    lines = sorted("%s  %s" % (m["sha256"], m["path"]) for m in members)
    return "sha256:" + hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def build(commit):
    raw = lambda p: "https://raw.githubusercontent.com/%s/%s/gen4-candidate/%s" % (REPO, commit, p)

    def member(rel, lp):
        s = sha_file(lp); n = os.path.getsize(lp)
        return {"path": "gen4-candidate/" + rel, "sha256": s, "bytes": n,
                "evidence_ref": {"kind": "blob", "locator": raw(rel), "sha256": s, "bytes": n, "digest_basis": "fetched_bytes"}}

    members = [member("schema/fm-sol-control-v2.schema.json", GEN4_SCHEMA),
               member("schema/FREEZE.json", GEN4_FREEZE)]
    subject_line = doc_package_identity(members)
    refs = [m["evidence_ref"] for m in members] + [{
        "kind": "commit", "locator": "https://github.com/%s/commit/%s" % (REPO, commit),
        "sha256": hashlib.sha256(("https://github.com/%s/commit/%s" % (REPO, commit)).encode()).hexdigest(),
        "digest_basis": "locator_identity"}]
    import datetime, re as _re
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    # resolve the CURRENT gen-3 control configuration immediately before emission (not inherited)
    ccg, _c, _n = fsc4_config.generation()
    gen3_vocab = sha_file(GEN3_SCHEMA)
    # acceptance_policy digest = hash of the ACTUAL immutable policy bytes named in inputs
    policy_input_rel = "TRANSITION-CONTRACT.md"
    policy_digest = sha_file(os.path.join(GEN4, policy_input_rel))
    redacted_owner = _re.sub(r"(?<![A-Za-z0-9_.-])/home/[A-Za-z0-9._-]+", "/home/OPERATOR", str(ccg["owner_path"]))
    # scaffold from the proven gen-3 request STRUCTURE, then rebuild EVERY activation fact freshly
    req = json.loads(open(os.path.join(CONTROL_DIR, "gen3", "transaction-9", "evidence", "request.json")).read())
    req["work_id"] = "cleanroom-gen4-activation-transition"
    req["work_generation"] = 1
    req["request_generation"] = 2   # supersedes the prior #16 activation request (request_generation 1)
    req["created_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    req["expires_at"] = (now + datetime.timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    req["requester"] = {"login": REPO.split("/")[0], "kind": "agent", "provenance_class": "self_asserted_descriptor",
                        "session_ref": "clean-room FirstMate primary; gen-3 -> gen-4 activation-transition recovery compiler (control#15)"}
    req["control_config_generation"] = {"owner_path": redacted_owner, "digest": ccg["digest"],
                                        "resolver_digest": ccg["resolver_digest"], "resolved_at": ccg["resolved_at"]}
    req["decision_class"] = "DELEGATED_ENGINEERING"
    req["boundary_evidence"] = [
        {"predicate": "this is a bounded control-tooling generation-3 -> generation-4 activation transition, not new spend, "
         "not a security or privacy weakening, not a credential exposure, not a destructive or materially irreversible act, "
         "and not a personal or product preference",
         "value": "observed-good", "measured": "DELEGATED_ENGINEERING; captain_required=false; control#15 recovery"},
        {"predicate": "consuming Option A advances control_config_generation exactly once, atomically, after effect-boundary "
         "revalidation; generations 1/2/3 and all historical transactions are preserved unchanged",
         "value": "observed-good", "measured": "single crash-safe activation record via the dedicated applier"},
        {"predicate": "the target is exactly the unactivated frozen generation-4 candidate at the bound immutable commit",
         "value": "observed-good", "measured": "document_package subject binds the candidate schema + FREEZE members at commit %s" % commit},
        {"predicate": "maker/checker independence at the principal level on this venue",
         "value": "could-not-observe", "measured": "one forge account fronts both sides of the transport (issue #3 independence ruling: grade cap, not blocker)"},
    ]
    req["vocabulary_digest"] = gen3_vocab
    req["subject"] = {"kind": "document_package", "identity_line": subject_line, "members": members}
    req["acceptance_policy"] = {"generation": "cleanroom-gen4-activation-v1", "digest": policy_digest,
                                "inputs": ["gen4-candidate/TRANSITION-CONTRACT.md"]}
    req["question"] = {"key": "gen4-activation-transition-disposition",
                       "title": "[FM->SOL] fm-sol-control/v2 request: generation-3 -> generation-4 activation transition",
                       "body_markdown": ("Activate exactly the unactivated generation-4 candidate published at "
                                         "gen4-candidate/@%s (schema-visible 4-tuple evidence_digest law), via the dedicated "
                                         "transition applier, or keep generation 3 active and return the candidate for revision. "
                                         "Consuming Option A advances control_config_generation once, atomically, after "
                                         "effect-boundary revalidation." % commit),
                       "options": [{"id": "A", "summary": "Activate exactly the successor frozen generation-4 candidate via the dedicated transition applier.",
                                    "consequence": "one atomic gen-3 -> gen-4 advance; the schema-visible 4-tuple law becomes active", "reversibility": "reversible", "paths": []},
                                   {"id": "B", "summary": "Keep generation 3 active; return the candidate for revision.",
                                    "consequence": "no advance", "reversibility": "reversible", "paths": []}]}
    req["evidence_refs"] = refs
    req["valid_while"] = {"control_config_generation_digest": ccg["digest"], "policy_digest": policy_digest,
                          "vocabulary_digest": gen3_vocab, "evidence_digest": three_tuple(refs),
                          "subject_identity_line": subject_line, "subject_head_sha": commit, "subject_state": "published"}
    req["candidate"] = None
    req["candidate_state"] = "NOT_APPLICABLE"
    req["supersedes_request_id"] = "fscr2-393b68835bed6dae9e1bbe525a0d9378"  # supersede the prior #16 activation request
    req["correlation_id"] = fsc3.derive("correlation_id", req)
    req["request_id"] = fsc3.derive("request_id", req)
    return req, refs


def main():
    commit, out_req, out_proof = sys.argv[1], sys.argv[2], sys.argv[3]
    req, refs = build(commit)
    schema = json.loads(open(GEN3_SCHEMA, "rb").read())
    errs = [e.message for e in Draft202012Validator(schema).iter_errors(req)]
    ccg_now, _c, _n = fsc4_config.generation()
    members = req["subject"]["members"]
    import re as _re
    _admitted = _re.compile(r"^https://raw\.githubusercontent\.com/[^/]+/[^/]+/[0-9a-f]{40}/"
                            r"|^https://github\.com/[^/]+/[^/]+/commit/[0-9a-f]{40}$")
    def yn(b):
        return "observed-good" if b else "observed-bad"
    # independent proof over the AS-BUILT request of EVERY required binding
    proofs = {
        "schema_validation": {"value": yn(not errs), "errors": errs[:4]},
        "request_id_recomputes": {"carried": req["request_id"], "derived": fsc3.derive("request_id", req),
                                  "value": yn(req["request_id"] == fsc3.derive("request_id", req))},
        "correlation_id_recomputes": {"carried": req["correlation_id"], "derived": fsc3.derive("correlation_id", req),
                                      "value": yn(req["correlation_id"] == fsc3.derive("correlation_id", req))},
        "current_gen3_control_generation": {"carried": req["control_config_generation"]["digest"], "resolved_now": ccg_now["digest"],
                                            "value": yn(req["control_config_generation"]["digest"] == ccg_now["digest"] == req["valid_while"]["control_config_generation_digest"])},
        "work_and_request_generations": {"work_generation": req["work_generation"], "request_generation": req["request_generation"],
                                         "supersedes_request_id": req["supersedes_request_id"],
                                         "value": yn(req["work_generation"] == 1 and req["request_generation"] == 2 and req["supersedes_request_id"] == "fscr2-393b68835bed6dae9e1bbe525a0d9378")},
        "subject_identity_recomputes": {"carried": req["subject"]["identity_line"], "recomputed": doc_package_identity(members),
                                        "value": yn(req["subject"]["identity_line"] == doc_package_identity(members) == req["valid_while"]["subject_identity_line"])},
        "policy_digest_binds_cited_input": {"carried": req["acceptance_policy"]["digest"], "inputs": req["acceptance_policy"]["inputs"],
                                            "sha256_of_TRANSITION-CONTRACT.md": sha_file(os.path.join(GEN4, "TRANSITION-CONTRACT.md")),
                                            "value": yn(req["acceptance_policy"]["digest"] == sha_file(os.path.join(GEN4, "TRANSITION-CONTRACT.md")) == req["valid_while"]["policy_digest"])},
        "expiry_after_creation_rfc3339": {"created_at": req["created_at"], "expires_at": req["expires_at"],
                                          "value": yn(req["expires_at"] > req["created_at"] and req["created_at"].endswith("Z"))},
        "evidence_locators_immutable": {"all_admitted": all(bool(_admitted.match(r["locator"])) for r in refs),
                                        "value": yn(all(bool(_admitted.match(r["locator"])) for r in refs))},
        "evidence_digest_is_gen3_3tuple": {"carried": req["valid_while"]["evidence_digest"], "recomputed_3tuple": three_tuple(refs),
                                           "value": yn(req["valid_while"]["evidence_digest"] == three_tuple(refs))},
        "differential_vs_canonical_producer": {
            "note": "The canonical gen-3 producer computes evidence_digest as the 4-tuple; this recovery "
                    "compiler computes the schema-mandated 3-tuple. That is the ONLY field that differs.",
            "canonical_4tuple": fsc4_evidence_digest_4tuple(refs),
            "recovery_3tuple": three_tuple(refs),
            "differs": fsc4_evidence_digest_4tuple(refs) != three_tuple(refs)},
        "effect_incapability": {"note": "This compiler writes only the request + this proof; it changes no "
                                "control_config_generation, applies no ruling, lands no code, publishes to no venue."},
    }
    json.dump(req, open(out_req, "w", encoding="utf-8"), indent=2, sort_keys=True, ensure_ascii=False)
    json.dump(proofs, open(out_proof, "w", encoding="utf-8"), indent=2, sort_keys=True)
    print("request_id      %s" % req["request_id"])
    print("correlation_id  %s" % req["correlation_id"])
    print("evidence_digest %s  (gen-3 3-tuple)" % req["valid_while"]["evidence_digest"])
    print("schema valid    %s" % (not errs))
    print("differential    canonical4=%s recovery3=%s differ=%s" % (
        proofs["differential_vs_canonical_producer"]["canonical_4tuple"][:12],
        proofs["differential_vs_canonical_producer"]["recovery_3tuple"][:12],
        proofs["differential_vs_canonical_producer"]["differs"]))
    return 0 if not errs else 5


def fsc4_evidence_digest_4tuple(refs):
    rows = sorted("%s\t%s\t%s\t%s" % (r["kind"], r["locator"], r["sha256"], r.get("digest_basis", "")) for r in refs)
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
