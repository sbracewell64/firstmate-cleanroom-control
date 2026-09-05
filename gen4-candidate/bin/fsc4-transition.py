#!/usr/bin/env python3
"""Generation-transition APPLIER (gen-3 -> gen-4) + fake-forge seam proof, control#15.

CORRECTED per Browser Sol's transition-contract review:
  * The transition is carried by an ORDINARY frozen-gen-3 `kind="request"` (built by the
    quarantined one-use recovery compiler `fsc4-activation-compiler.py`), NOT a custom envelope
    kind. This module does NOT build that request.
  * The applier accepts ONLY a full schema-valid gen-3 `fm-sol-control/v2` ruling with
    directive=ADOPT_OPTION selecting the activation option, and revalidates EXACT applicability
    on every binding before any effect. It obtains the complete ruling universe and refuses
    ambiguity / lineage forks. Replay is zero-effect.
  * The only effect, on an applicable ruling and after effect-boundary revalidation, is ONE
    atomic advance of the active control-tooling generation from 3 to 4 (a digest-bound
    activation record). Nothing else.

The activation request encodes the target in ordinary gen-3 vocabulary:
  work_id                     = "cleanroom-gen4-activation-transition"
  subject                     = document_package over the gen-4 candidate files; the member for
                                schema/....json binds the target gen-4 vocabulary and the member for
                                schema/FREEZE.json binds the target manifest; identity_line is the
                                sorted 'sha256  path' manifest digest
  valid_while.subject_head_sha= the immutable candidate commit; .control_config_generation_digest = source config
  acceptance_policy.digest    = the published activation policy (Option A/B)
  evidence_refs               = the candidate files at immutable raw locators + the commit
  valid_while.evidence_digest = the gen-3 SCHEMA 3-tuple (kind\\tlocator\\tsha256)

Usage:
  fsc4-transition.py apply <request.json> <ruling.json> <universe.json> <active-gen-file> <record-out>
  fsc4-transition.py roundtrip     bounded fake-forge proof over REAL gen-3 request + ruling shapes
"""
import hashlib
import json
import os
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
import fsc4_config   # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

GEN4 = fsc4_config.CONTROL_ROOT
CONTROL_DIR = os.path.dirname(GEN4)
GEN3_SCHEMA_PATH = os.path.join(CONTROL_DIR, "gen3", "schema", "fm-sol-control-v2.schema.json")
GEN4_FREEZE = os.path.join(GEN4, "schema", "FREEZE.json")
GEN4_SCHEMA = os.path.join(GEN4, "schema", "fm-sol-control-v2.schema.json")


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def gen3_schema():
    return json.loads(open(GEN3_SCHEMA_PATH, "rb").read())


def gen3_validate(kind, obj):
    """Validate a gen-3 envelope against the frozen gen-3 schema-of-record."""
    schema = gen3_schema()
    errs = [e.message for e in Draft202012Validator(schema).iter_errors(obj)]
    if obj.get("kind") != kind:
        errs.append("kind is %r, expected %r" % (obj.get("kind"), kind))
    return errs


ACTIVATION_OPTION_ID = "A"

# The exact applies_to bindings that must match, request-field -> ruling.applies_to-field.
_APPLIES_BINDINGS = [
    ("work_id", "work_id"),
    ("work_generation", "work_generation"),
    ("request_generation", "request_generation"),
]


def applicable(request, ruling):
    """Full exact-applicability gate. Returns (True,'') or (False, reason). No effect."""
    re_ = gen3_validate("request", request)
    if re_:
        return False, "REFUSED_MALFORMED: request not gen-3 schema-valid: %s" % "; ".join(re_[:2])
    ru_ = gen3_validate("ruling", ruling)
    if ru_:
        return False, "REFUSED_MALFORMED: ruling not gen-3 schema-valid: %s" % "; ".join(ru_[:2])
    if ruling.get("single_writer_assertion") is not True:
        return False, "REFUSED_AMBIGUOUS: ruling.single_writer_assertion is not true"
    if ruling.get("supersedes") not in (None,) and not isinstance(ruling.get("supersedes"), str):
        return False, "REFUSED_AMBIGUOUS: ruling.supersedes malformed"
    if ruling.get("directive") != "ADOPT_OPTION":
        return False, "REFUSED_MISMATCH: directive is not ADOPT_OPTION"
    if ruling.get("option_id") != ACTIVATION_OPTION_ID:
        return False, "REFUSED_MISMATCH: adopted option is not the activation option A"
    if ruling.get("in_reply_to") != request.get("request_id"):
        return False, "REFUSED_MISMATCH: in_reply_to != request_id"
    if ruling.get("correlation_id") != request.get("correlation_id"):
        return False, "REFUSED_MISMATCH: correlation_id mismatch"
    if ruling.get("vocabulary_digest") != request.get("vocabulary_digest"):
        return False, "REFUSED_STALE: vocabulary_digest mismatch"
    if ruling.get("control_config_generation_digest") != (request.get("control_config_generation") or {}).get("digest"):
        return False, "REFUSED_STALE_CONFIG: control_config_generation_digest mismatch"
    ap = ruling.get("applies_to") or {}
    if ap.get("subject_identity_line") != (request.get("subject") or {}).get("identity_line"):
        return False, "REFUSED_MISMATCH: subject_identity_line mismatch"
    if ap.get("policy_digest") != (request.get("acceptance_policy") or {}).get("digest"):
        return False, "REFUSED_STALE: policy_digest mismatch"
    if ap.get("evidence_digest") != (request.get("valid_while") or {}).get("evidence_digest"):
        return False, "REFUSED_STALE: evidence_digest mismatch"
    for rq_field, ap_field in _APPLIES_BINDINGS:
        if ap.get(ap_field) != request.get(rq_field):
            return False, "REFUSED_MISMATCH: applies_to.%s mismatch" % ap_field
    for vk in ("venue", "repo"):
        if ap.get(vk) != request.get(vk):
            return False, "REFUSED_MISMATCH: applies_to.%s mismatch" % vk
    return True, ""


def document_package_identity(members):
    """The gen-3 document_package identity_line: sha256 over the sorted 'sha256  path' manifest."""
    lines = sorted("%s  %s" % (m["sha256"], m["path"]) for m in members)
    return "sha256:" + hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def _target_from_request(request):
    """Read the target the request binds through ORDINARY gen-3 vocabulary: commit + source
    config from valid_while; gen-4 vocabulary + manifest from the document_package members
    (the member for schema/....json is the gen-4 vocabulary; for schema/FREEZE.json the manifest)."""
    vw = request.get("valid_while") or {}
    subj = request.get("subject") or {}
    members = subj.get("members") or []
    gen4_vocab = manifest = None
    for m in members:
        p = m.get("path", "")
        if p.endswith("schema/fm-sol-control-v2.schema.json"):
            gen4_vocab = m.get("sha256")
        elif p.endswith("schema/FREEZE.json"):
            manifest = m.get("sha256")
    if not (gen4_vocab and manifest and vw.get("subject_head_sha")):
        return None
    return {"from_cfg": vw.get("control_config_generation_digest"),
            "gen4_vocab": gen4_vocab, "manifest": manifest, "commit": vw.get("subject_head_sha"),
            "subject_line": subj.get("identity_line"), "members": members}


def active_generation_of(record_path):
    """The ONE authoritative source of the active generation: derived from the single activation
    record. A valid gen-4 record => generation 4; anything else (absent/partial/unreadable) =>
    generation 3. There is no second pointer file, so there is no partial-write window between two
    files, and a crash either leaves the record fully written (os.replace is atomic) or absent."""
    if not os.path.exists(record_path):
        return 3
    try:
        r = json.load(open(record_path))
    except (OSError, ValueError):
        return 3
    return 4 if r.get("active_generation") == 4 and r.get("manifest_digest") else 3


def apply_activation(request, ruling, universe, record_path):
    """Apply ONLY on an applicable ruling, a complete universe with EXACTLY ONE member ruling equal
    to the supplied ruling, and a green effect boundary. ONE crash-safe atomic state file."""
    # complete, non-truncated universe
    if universe.get("truncated") is True:
        return False, "CNO_TRUNCATED_RESPONSE: ruling universe not seen whole"
    terminal = [r for r in universe.get("rulings", []) if isinstance(r, dict) and r.get("kind") == "ruling"]
    applicable_here = [r for r in terminal if r.get("in_reply_to") == request.get("request_id")]
    # EXACTLY ONE applicable ruling in the observed universe (not zero, not many)
    if len(applicable_here) == 0:
        return False, "REFUSED_AMBIGUOUS: no ruling for this request in the observed universe"
    if len(applicable_here) > 1:
        return False, "REFUSED_AMBIGUOUS: more than one ruling for this request (lineage fork)"
    # the supplied ruling MUST BE that observed universe member (no out-of-universe injection)
    if ruling != applicable_here[0]:
        return False, "REFUSED_MISMATCH: supplied ruling is not the observed universe member"
    ok, reason = applicable(request, ruling)
    if not ok:
        return False, reason
    tgt = _target_from_request(request)
    if not tgt:
        return False, "REFUSED_MALFORMED: activation target not bound in subject members + valid_while"
    # subject integrity: the document_package identity_line recomputes from its members
    if tgt["subject_line"] != document_package_identity(tgt["members"]):
        return False, "REFUSED_MISMATCH: subject identity_line does not recompute from its members"
    # REPLAY: the one authoritative record already activates this exact target -> zero effects
    if os.path.exists(record_path):
        try:
            ex = json.load(open(record_path))
            if ex.get("active_generation") == 4 and ex.get("manifest_digest") == tgt["manifest"] and ex.get("candidate_commit") == tgt["commit"]:
                return True, "REPLAY_NOOP: already activated for this exact target; zero effects"
            return False, "REFUSED_STALE: an activation record already exists for a different target"
        except (OSError, ValueError):
            return False, "CNO: activation record unreadable"
    # effect boundary: source generation still 3 (derived from the one record, which is absent here)
    if active_generation_of(record_path) != 3:
        return False, "REFUSED_STALE: active generation is not 3"
    # source control-config digest still what the request bound
    ccg, _c, _n = fsc4_config.generation()
    if tgt["from_cfg"] != ccg["digest"]:
        return False, "REFUSED_STALE_CONFIG: source control-config generation moved since the request"
    # target manifest + vocabulary still verify byte-for-byte
    if sha_file(GEN4_FREEZE) != tgt["manifest"]:
        return False, "REFUSED_STALE: target gen-4 manifest moved"
    if sha_file(GEN4_SCHEMA) != tgt["gen4_vocab"]:
        return False, "REFUSED_STALE: target gen-4 vocabulary moved"
    # whole target candidate byte-consistent (freeze-verify green)
    import subprocess
    vf = os.path.join(GEN4, "bin", "fsc4-verify-freeze.sh")
    if subprocess.run(["bash", vf], capture_output=True).returncode != 0:
        return False, "REFUSED_STALE: target gen-4 candidate failed freeze-verify"
    # ONE atomic advance: a single canonical record, written by one os.replace. active_generation is
    # derived from THIS record, so there is no second file to fall out of sync on a crash.
    record = {"active_generation": 4, "manifest_digest": tgt["manifest"],
              "vocabulary_digest": tgt["gen4_vocab"], "candidate_commit": tgt["commit"],
              "consumes_ruling_id": ruling.get("ruling_id"), "in_reply_to": request.get("request_id")}
    tmp = record_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, record_path)
    return True, "ACTIVATED: active generation advanced 3 -> 4"


# ---------------------------------------------------------------- fake-forge round trip
def roundtrip():
    import fsc4  # noqa: E402
    sys.path.insert(0, os.path.join(CONTROL_DIR, "gen3", "bin"))
    import fsc3  # gen-3 identity derivation + validation  # noqa: E402
    results = []

    def check(name, ok, detail):
        results.append((name, bool(ok), detail))
        print("%-6s %-50s %s" % ("PASS" if ok else "FAIL", name, str(detail)[:74]))

    # RUN-TO-CANDIDATE BINDING: this transcript names the EXACT frozen candidate bytes it was run
    # against, so it cannot be an inherited stale blob. Browser Sol recomputes the committed
    # FREEZE.json sha256 and the gen-4 schema sha256 and confirms they equal the values printed here;
    # the UTC run time shows the run happened after the final freeze. (control#19 provenance gap.)
    import datetime as _dt
    _run_at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("RUN-TO-CANDIDATE BINDING run_at=%s freeze_sha256=%s gen4_schema_sha256=%s applier_sha256=%s" % (
        _run_at, sha_file(GEN4_FREEZE), sha_file(GEN4_SCHEMA), sha_file(os.path.abspath(__file__))))

    # Build a REAL gen-3 request shape for the activation, with gen-3-admitted immutable locators.
    commit = os.environ.get("FSC4_CANDIDATE_COMMIT", "24b5ab062b6fb0d6bf1b86b271ee50d07d4686e3")
    gen3_vocab = sha_file(GEN3_SCHEMA_PATH)
    gen4_vocab = sha_file(GEN4_SCHEMA)
    manifest = sha_file(GEN4_FREEZE)
    ccg, cfg, _n = fsc4_config.generation()
    raw = lambda p: "https://raw.githubusercontent.com/sbracewell64/firstmate-cleanroom-control/%s/gen4-candidate/%s" % (commit, p)
    three = lambda rs: hashlib.sha256(("\n".join(sorted("%s\t%s\t%s" % (r["kind"], r["locator"], r["sha256"]) for r in rs)) + "\n").encode()).hexdigest()
    # document_package members: the gen-4 schema (binds the target vocabulary) and the frozen
    # manifest (binds the target manifest). The applier reads the target from these + valid_while.
    def member(relpath, localpath):
        s = sha_file(localpath); n = os.path.getsize(localpath)
        return {"path": "gen4-candidate/" + relpath, "sha256": s, "bytes": n,
                "evidence_ref": {"kind": "blob", "locator": raw(relpath), "sha256": s, "bytes": n, "digest_basis": "fetched_bytes"}}
    members = [member("schema/fm-sol-control-v2.schema.json", GEN4_SCHEMA),
               member("schema/FREEZE.json", GEN4_FREEZE)]
    subject_line = document_package_identity(members)
    refs = [m["evidence_ref"] for m in members] + [
        {"kind": "commit", "locator": "https://github.com/sbracewell64/firstmate-cleanroom-control/commit/%s" % commit,
         "sha256": hashlib.sha256(("https://github.com/sbracewell64/firstmate-cleanroom-control/commit/%s" % commit).encode()).hexdigest(),
         "digest_basis": "locator_identity"}]
    policy_digest = hashlib.sha256(b"activation-policy-A/B-v1").hexdigest()
    # Adapt the proven schema-valid gen-3 request (#15) into the activation shape: this is a REAL
    # gen-3 request structure, retargeted to the activation decision. The recovery compiler builds
    # the actual published request the same way; here we exercise the applier against a real shape.
    req = json.loads(open(os.path.join(CONTROL_DIR, "gen3", "transaction-9", "evidence", "request.json")).read())
    req["work_id"] = "cleanroom-gen4-activation-transition"
    req["control_config_generation"]["digest"] = ccg["digest"]
    req["subject"] = {"kind": "document_package", "identity_line": subject_line, "members": members}
    req["acceptance_policy"] = {"generation": "cleanroom-gen4-activation-v1", "digest": policy_digest,
                                "inputs": ["gen4-candidate/TRANSITION-CONTRACT.md"]}
    req["question"] = {"key": "gen4-activation-transition-disposition", "title": "[FM->SOL] activate gen-4 candidate",
                       "body_markdown": "Activate the successor gen-4 candidate (schema-visible 4T law) via the dedicated transition applier, or keep gen-3.",
                       "options": [{"id": "A", "summary": "Activate exactly the successor frozen gen-4 candidate via the dedicated transition applier.",
                                    "consequence": "one atomic gen3->gen4 advance", "reversibility": "reversible", "paths": []},
                                   {"id": "B", "summary": "Keep generation 3 active; return the candidate for revision.",
                                    "consequence": "no advance", "reversibility": "reversible", "paths": []}]}
    req["evidence_refs"] = refs
    req["valid_while"] = {"control_config_generation_digest": ccg["digest"], "policy_digest": policy_digest,
                          "vocabulary_digest": gen3_vocab, "evidence_digest": three(refs),
                          "subject_identity_line": subject_line, "subject_head_sha": commit, "subject_state": "published"}
    req["correlation_id"] = fsc3.derive("correlation_id", req)
    req["request_id"] = fsc3.derive("request_id", req)
    req_errs = gen3_validate("request", req)
    check("activation request is a schema-valid gen-3 request", not req_errs, "; ".join(req_errs[:2]) or "0 errors")

    # A REAL gen-3 ruling shape adopting Option A for this request.
    def ruling_for(r, **over):
        base = {"schema": "fm-sol-control/v2", "kind": "ruling", "ruling_id": "sol-ruling-gen4-activation-TEST",
                "in_reply_to": r["request_id"], "correlation_id": r["correlation_id"], "vocabulary_digest": r["vocabulary_digest"],
                "control_config_generation_digest": r["control_config_generation"]["digest"], "ruled_at": "2026-09-05T07:05:00Z",
                "ruler": {"login": "browser-sol", "kind": "agent", "provenance_class": "self_asserted_descriptor", "session_ref": "test"},
                "applies_to": {"venue": r["venue"], "repo": r["repo"], "work_id": r["work_id"], "work_generation": r["work_generation"],
                               "request_generation": r["request_generation"], "subject_identity_line": r["subject"]["identity_line"],
                               "policy_digest": r["acceptance_policy"]["digest"], "evidence_digest": r["valid_while"]["evidence_digest"]},
                "inspection": {"evidence_refs_inspected": r["evidence_refs"],
                               "observations": [{"predicate": "gen-4 candidate inspected and byte-verified at the bound commit",
                                                 "value": "observed-good", "measured": "freeze-verify green"}]},
                "directive": "ADOPT_OPTION", "option_id": "A", "single_writer_assertion": True, "supersedes": None}
        base.update(over); return base
    good = ruling_for(req)
    universe = {"truncated": False, "rulings": [good]}
    scratch = tempfile.mkdtemp(prefix="fsc4-activation-")
    rp = lambda n: os.path.join(scratch, n + ".json")   # a fresh single record per test
    # a universe that contains exactly the supplied ruling (so applicability, not membership, is tested)
    uni = lambda rl: {"truncated": False, "rulings": [rl]}

    rec = rp("main")
    ok, msg = apply_activation(req, good, universe, rec); check("valid activation succeeds once", ok and "ACTIVATED" in msg, msg)
    check("active generation derived as 4 from the one record", active_generation_of(rec) == 4, "active=4")
    ok2, m2 = apply_activation(req, good, universe, rec); check("replay zero-effect no-op", ok2 and "REPLAY_NOOP" in m2, m2)
    # applicability negatives (universe contains the supplied mutated ruling, so membership passes)
    bad_ir = ruling_for(req, in_reply_to="fscr2-" + "0"*32)
    ok3, m3 = apply_activation(req, bad_ir, uni(bad_ir), rp("r3")); check("wrong in_reply_to -> refused", (not ok3) and ("AMBIGUOUS" in m3 or "MISMATCH" in m3), m3)
    bad_corr = ruling_for(req, correlation_id="fsc2-" + "0"*32)
    ok4, m4 = apply_activation(req, bad_corr, uni(bad_corr), rp("r4")); check("wrong correlation_id -> MISMATCH", (not ok4) and "MISMATCH" in m4, m4)
    badap = ruling_for(req); badap["applies_to"]["evidence_digest"] = "0"*64
    ok5, m5 = apply_activation(req, badap, uni(badap), rp("r5")); check("mutated applies_to.evidence_digest -> STALE", (not ok5) and "STALE" in m5, m5)
    badcfg = ruling_for(req); badcfg["control_config_generation_digest"] = "0"*64
    ok6, m6 = apply_activation(req, badcfg, uni(badcfg), rp("r6")); check("mutated control-config digest -> STALE_CONFIG", (not ok6) and "STALE_CONFIG" in m6, m6)
    badvoc = ruling_for(req); badvoc["vocabulary_digest"] = "0"*64
    ok7, m7 = apply_activation(req, badvoc, uni(badvoc), rp("r7")); check("mutated vocabulary_digest -> STALE", (not ok7) and "STALE" in m7, m7)
    swf = ruling_for(req, single_writer_assertion=False)
    ok8, m8 = apply_activation(req, swf, uni(swf), rp("r8")); check("single_writer_assertion false -> refused", (not ok8) and ("AMBIGUOUS" in m8 or "MALFORMED" in m8), m8)
    optb = ruling_for(req, option_id="B")
    ok9, m9 = apply_activation(req, optb, uni(optb), rp("r9")); check("non-activation option -> MISMATCH", (not ok9) and "MISMATCH" in m9, m9)
    # NEW: exactly-one-in-universe + supplied==observed-member
    okZ, mZ = apply_activation(req, good, {"truncated": False, "rulings": []}, rp("rZ")); check("zero-ruling universe -> refused (no ruling)", (not okZ) and "AMBIGUOUS" in mZ, mZ)
    injected = ruling_for(req, ruling_id="out-of-universe-injected")
    okY, mY = apply_activation(req, injected, universe, rp("rY")); check("out-of-universe injected ruling -> MISMATCH", (not okY) and "not the observed universe member" in mY, mY)
    dup = {"truncated": False, "rulings": [good, ruling_for(req, ruling_id="dup")]}
    okA, mA = apply_activation(req, good, dup, rp("rA")); check("duplicate rulings (lineage fork) -> AMBIGUOUS", (not okA) and "AMBIGUOUS" in mA, mA)
    okB, mB = apply_activation(req, good, {"truncated": True, "rulings": []}, rp("rB")); check("truncated universe -> CNO_TRUNCATED", (not okB) and "TRUNCATED" in mB, mB)
    # NEW: crash safety of the single record. A partial/corrupt record must derive gen-3 (never a
    # false gen-4), and must NOT be treated as a replay of the real target.
    crashp = rp("crash")
    open(crashp, "w").write('{"active_generation": 4}')   # partial: missing manifest_digest
    check("partial/corrupt record derives gen-3 (no false activation)", active_generation_of(crashp) == 3, "partial=>3")
    okX, mX = apply_activation(req, good, universe, crashp); check("apply over a partial record -> refused, not false replay", (not okX) and "STALE" in mX, mX)
    check("no record derives gen-3", active_generation_of(rp("absent")) == 3, "absent=>3")
    # source control-config movement: request binds a from_cfg that no longer matches current config
    req_badcfg = json.loads(json.dumps(req)); req_badcfg["valid_while"]["control_config_generation_digest"] = "0"*64
    req_badcfg["control_config_generation"]["digest"] = "0"*64
    req_badcfg["correlation_id"] = fsc3.derive("correlation_id", req_badcfg); req_badcfg["request_id"] = fsc3.derive("request_id", req_badcfg)
    okC, mC = apply_activation(req_badcfg, ruling_for(req_badcfg), {"truncated": False, "rulings": [ruling_for(req_badcfg)]}, rp("rC")); check("source control-config moved -> STALE_CONFIG", (not okC) and "STALE_CONFIG" in mC, mC)
    # target-manifest movement: tamper the subject's FREEZE member digest
    req_badm = json.loads(json.dumps(req))
    for m in req_badm["subject"]["members"]:
        if m["path"].endswith("schema/FREEZE.json"):
            m["sha256"] = "0" * 64
    req_badm["subject"]["identity_line"] = document_package_identity(req_badm["subject"]["members"])
    req_badm["valid_while"]["subject_identity_line"] = req_badm["subject"]["identity_line"]
    req_badm["correlation_id"] = fsc3.derive("correlation_id", req_badm); req_badm["request_id"] = fsc3.derive("request_id", req_badm)
    okD, mD = apply_activation(req_badm, ruling_for(req_badm), {"truncated": False, "rulings": [ruling_for(req_badm)]}, rp("rD")); check("target-manifest moved -> STALE", (not okD) and "STALE" in mD, mD)
    # 3T vs 4T both ways
    check("request carries the gen-3 3-tuple (Sol-acceptable)", req["valid_while"]["evidence_digest"] == three(refs), "3-tuple")
    check("a 4-tuple digest differs from the carried 3-tuple", fsc4.evidence_digest(refs) != three(refs), "4tuple!=3tuple")
    check("digest_basis-only mutation moves the 4-tuple digest", fsc4.evidence_digest([dict(refs[0], digest_basis="locator_identity")]+refs[1:]) != fsc4.evidence_digest(refs), "observer 4.5")
    # historical freeze
    import subprocess
    allg = all(subprocess.run(["bash", os.path.join(CONTROL_DIR, g, "bin", "fsc%s-verify-freeze.sh" % g[-1])], capture_output=True).returncode == 0 for g in ("gen2", "gen3"))
    check("gen-2 and gen-3 freeze-verify green, byte-unchanged", allg, "historical immutable")

    import shutil; shutil.rmtree(scratch, ignore_errors=True)
    passed = sum(1 for _n, ok, _d in results if ok)
    print("\n%d/%d activation-seam checks green" % (passed, len(results)))
    return 0 if passed == len(results) else 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "roundtrip":
        return roundtrip()
    sys.stderr.write("apply is a library entry point; run 'roundtrip' for the seam proof\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
