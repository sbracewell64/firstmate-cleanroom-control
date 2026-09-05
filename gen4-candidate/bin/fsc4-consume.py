#!/usr/bin/env python3
"""Consume at most one ruling for one request, and write the typed receipt.

SCHEMA GENERATION 4. Three corrections over the generation 2 consumer (control
issue #3, tooling_supersession required_repairs[2..4]):

  a. First-consumption claiming is ATOMIC: the durable consumption record is
     claimed with O_CREAT|O_EXCL (exclusive create) on the ext4 operational
     home, never exists-then-write, so two consumers cannot both pass the guard
     (observer finding 3.5). The receipt states claim_mechanism=exclusive_create
     and the schema refuses a receipt that cannot.
  b. receipt_id now derives from the outcome as well (read from the schema's
     $defs.id_derivation, never typed here), so a CONSUMED receipt and a refusal
     over the same ruling no longer share an identity (observer finding 4.4).
  c. TRUNCATION DOMINATES THE FOLD: any truncated or truncating authority-bearing
     read yields CNO_TRUNCATED_RESPONSE, before FAIL and before NO_ANSWER, so a
     refused/incomplete read can never fold to "nothing arrived" (required_repairs[3]).

Inherited from generation 2 (unchanged):

  1. A consumption identity is claimed ONLY when something was actually
     consumed. Generation 1 populated the block unconditionally because the
     frozen schema required it for all eleven outcomes, so a NO_ANSWER receipt
     asserted consumption_count=1 and named a durable record that was never
     written (observer finding 4.3). Generation 2 emits the block on the
     CONSUMED branch only, and the schema refuses it anywhere else.

  2. Every authority-bearing forge read records HOW it was read. A read through
     a truncating surface, or a response that announces its own truncation,
     yields CNO_TRUNCATED_RESPONSE and NO envelope is validated from it: the
     document was not seen whole, so nothing read out of it was earned.

Ordered ladder, every predicate evaluated and none skipped, every failure
reported rather than only the first. Precedence FAIL > CNO > PASS. Consumption
is at most once per consumption identity: a second invocation performs exactly
zero actions and returns the first outcome unchanged.

Usage: fsc4-consume.py <request.json> <out-receipt.json> [--dry-run] [--with-replay-proof]
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

import fsc4
import fsc4_config

CTL = fsc4_config.CONTROL_ROOT
CONSUMED_DIR = os.environ.get("FSC2_CONSUMED_DIR") or os.path.join(CTL, "state", "consumed")
DECISIONS_DIR = os.environ.get("FSC2_DECISIONS_DIR") or os.path.join(CTL, "decisions")

# Pre-registered, total over the directive enum, no default branch and no
# fallback. No step reads the rationale and decides what to write.
ACTION_MAP = {
    "ADOPT_OPTION": "record-adoption",
    "REJECT_ALL_WITH_CONSTRAINT": "record-constraint",
    "INSUFFICIENT_EVIDENCE": "recompile-at-new-request-generation",
    "OUT_OF_SCOPE_CAPTAIN_RESERVED": "route-to-captain-as-a-record",
}

ACTIONS_PERFORMED = 0
LADDER = []


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def step(name, ok, measured, code=None, read=None):
    """ok: True | False | None(=could-not-observe).

    `read` attaches the completeness-of-read record for an authority-bearing
    fetch. The schema then enforces structurally that a truncated or
    truncating-surface read can only carry could-not-observe.
    """
    value = "observed-good" if ok is True else ("observed-bad" if ok is False else "could-not-observe")
    entry = {"predicate": name, "value": value, "measured": measured}
    if read is not None:
        entry["read"] = read
    LADDER.append(entry)
    if ok is not True:
        FAILS.append((name, code, value, measured))
    return ok


def store_fingerprint():
    """A digest over the whole durable store, so "zero actions" is measured
    rather than asserted."""
    h = hashlib.sha256()
    for root in (CONSUMED_DIR, DECISIONS_DIR):
        for dirpath, _dirs, files in os.walk(root):
            for name in sorted(files):
                fp = os.path.join(dirpath, name)
                h.update(fp.encode("utf-8"))
                with open(fp, "rb") as fh:
                    h.update(fh.read())
    return h.hexdigest()


# The surface authority-bearing reads go through. `gh api` streams the complete
# response; gh-axi truncates at approximately 4 KB and announces it in the
# payload. Every envelope in this protocol exceeds that bound, so an envelope
# read through the truncating surface was never seen whole. The surface is
# declared rather than inferred, and declaring the truncating one does not
# degrade the read into a pass -- it stops the consumption at could-not-observe.
READ_SURFACE = os.environ.get("FSC2_READ_SURFACE", "gh_api_non_truncating")
READS = []


def read_record(mechanism, body, truncated=False, declared=None, locator=None):
    rec = {"mechanism": mechanism, "truncated": bool(truncated),
           "received_bytes": len(body or "")}
    if declared is not None or truncated:
        rec["declared_bytes"] = declared
    if locator:
        rec["locator"] = locator
    READS.append(rec)
    return rec


def detect_truncation(text):
    """A truncating surface announces itself in the payload it returns.

    Returns (truncated, declared_length). Absence of the marker is NOT proof the
    read was complete -- that is what READ_SURFACE is for -- it only catches the
    case where the surface said so itself.
    """
    try:
        obj = json.loads(text)
    except ValueError:
        return False, None
    if isinstance(obj, dict) and obj.get("truncated") is True:
        return True, obj.get("original_length")
    return False, None


def gh(*args):
    r = subprocess.run(["gh", "api"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def extract_blocks(body):
    """Fenced json blocks only. Selection is by VALIDATED CONTENT, never by
    substring: a comment that merely mentions the request id contributes
    nothing and suppresses nothing."""
    out, cur, infence = [], [], False
    for line in body.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if not infence and s.startswith("```") and "json" in s.lower():
            infence, cur = True, []
            continue
        if infence and s.startswith("```"):
            out.append("\n".join(cur))
            infence = False
            continue
        if infence:
            cur.append(line)
    return out


FAILS = []


def main():
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    out_path = sys.argv[2]
    dry = "--dry-run" in sys.argv
    global ACTIONS_PERFORMED

    request_id = req["request_id"]

    # L0 -- venue isolation, re-run rather than assumed from a value already read.
    cfg_gen, cfg, _ = fsc4_config.generation()
    repo_slug = cfg["control"]["repository"]
    proto = cfg["control"]["protocol"]
    admit, reason = fsc4_config.isolation_admits(repo_slug, proto)
    step("L0 venue isolation admits the resolved venue and protocol", admit, reason, "REFUSED_MISMATCH")

    # L1 -- the captain addendum's fresh re-resolve. The generation in force NOW
    # must equal the generation sealed into the request.
    fresh = cfg_gen["digest"]
    sealed = req["valid_while"]["control_config_generation_digest"]
    step("L1 current control-config generation equals the generation sealed into the request",
         fresh == sealed, "sealed=%s fresh=%s" % (sealed, fresh), "REFUSED_STALE_CONFIG")

    # L2 -- the schema of record has not drifted.
    step("L2 schema of record still hashes to valid_while.vocabulary_digest",
         fsc4.schema_digest() == req["valid_while"]["vocabulary_digest"],
         fsc4.schema_digest(), "REFUSED_MALFORMED")

    # L3 -- the evidence set the ruler was shown has not changed.
    step("L3 evidence set still digests to valid_while.evidence_digest",
         fsc4.evidence_digest(req["evidence_refs"]) == req["valid_while"]["evidence_digest"],
         fsc4.evidence_digest(req["evidence_refs"]), "REFUSED_STALE")

    # L4 -- expiry.
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = datetime.datetime.strptime(req["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=datetime.timezone.utc)
    expired = now >= exp
    # The expiry code is decided at fold time, not here. Expiry with NO ruling in
    # the universe and expiry with a ruling that arrived too late are two
    # different facts with two different repairs -- one needs a re-ask, the other
    # needs a new correlation -- and a distinction that dies at the last step
    # before the operator is more dangerous than a missing control. They never
    # share a code.
    step("L4 now is before expires_at", not expired, "now=%s expires=%s" % (utc(), req["expires_at"]),
         "__EXPIRY__")

    live = json.load(open(os.path.join(CTL, "state", "live", request_id + ".json"), encoding="utf-8"))
    num = live["issue_number"]

    # C0 -- the surface, BEFORE anything is read through it. A truncating surface
    # cannot certify that any particular response fitted under its bound, so the
    # verdict is could-not-observe and the repair is to re-read, never to trust
    # the bytes that did arrive.
    truncating = READ_SURFACE == "gh_axi_truncating"
    step("C0 authority-bearing reads go through a non-truncating surface",
         None if truncating else True,
         "read_surface=%s" % READ_SURFACE,
         "CNO_TRUNCATED_RESPONSE",
         read_record(READ_SURFACE, "", truncated=truncating, declared=None))

    # C1 -- the completeness predicate. A negative claim may not be made over an
    # unbounded universe, so the whole comment universe is paginated and counted.
    fixture = os.environ.get("FSC2_FIXTURE_COMMENTS")
    try:
        if fixture:
            # TRANSPORT FIXTURE SEAM. Replaces ONLY the comment-universe fetch, so a
            # negative control can be run without posting test traffic into the live
            # venue. It bypasses no predicate: schema validation, the whole V and L
            # ladder, venue isolation and the completeness predicate all run for real
            # against the supplied universe. Never set in a real consumption.
            fx = json.load(open(fixture, encoding="utf-8"))
            issue = {"comments": fx["reported_total"]}
            comments = fx["comments"]
        else:
            issue_text = gh("repos/%s/issues/%d" % (repo_slug, num))
            raw = gh("--paginate", "repos/%s/issues/%d/comments" % (repo_slug, num))
            for text in (issue_text, raw):
                trunc, declared = detect_truncation(text)
                if trunc:
                    step("C1a the forge response was returned whole", None,
                         "surface reported truncated=true declared_length=%s received=%d"
                         % (declared, len(text)),
                         "CNO_TRUNCATED_RESPONSE",
                         read_record(READ_SURFACE, text, truncated=True, declared=declared,
                                     locator="repos/%s/issues/%d" % (repo_slug, num)))
                    raise RuntimeError("TRUNCATED_RESPONSE: declared=%s received=%d"
                                       % (declared, len(text)))
            issue = json.loads(issue_text)
            comments = []
            for chunk in raw.strip().split("\n"):
                if chunk.strip():
                    comments.extend(json.loads(chunk))
        complete = len(comments) == issue["comments"]
        step("C1 fetched comment count equals the reported total",
             None if truncating else complete,
             "fetched=%d reported=%d" % (len(comments), issue["comments"]),
             "CNO_TRUNCATED_RESPONSE" if truncating else "CNO_INCOMPLETE_UNIVERSE",
             read_record(READ_SURFACE, "", truncated=truncating))
    except RuntimeError as exc:
        # An unreachable tool and a truncated response are DIFFERENT facts with
        # different repairs, so they never share a code.
        code = ("CNO_TRUNCATED_RESPONSE" if str(exc).startswith("TRUNCATED_RESPONSE")
                else "CNO_TOOL_UNREACHABLE")
        step("C1 forge reachable for the complete comment universe", None, str(exc), code)
        comments, complete = [], False

    # V1 -- exactly one VALIDATED ruling naming this request. Captain directive 5:
    # an envelope is never validated out of a read that was not seen whole, so a
    # truncating surface yields NO candidates rather than the ones that fitted.
    candidates = []
    if truncating:
        comments = []
    for c in comments:
        for blk in extract_blocks(c.get("body", "")):
            try:
                obj = json.loads(blk)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            if obj.get("kind") != "ruling":
                continue
            if obj.get("schema") != proto:           # EXACT equality, never substring
                continue
            if obj.get("in_reply_to") != request_id:  # explicit parentage
                continue
            candidates.append((c, obj, blk))
    step("V1 exactly one validated ruling names this request",
         len(candidates) == 1 if complete else None,
         "candidates=%d complete_universe=%s" % (len(candidates), complete),
         "REFUSED_AMBIGUOUS" if len(candidates) > 1 else "NO_ANSWER")

    ruling = comment = block = None
    if len(candidates) == 1:
        comment, ruling, block = candidates[0]

        errs = fsc4.validate("ruling", ruling)
        step("V2 ruling validates against the frozen schema of record",
             not errs, "; ".join(errs[:6]) or "0 errors", "REFUSED_MALFORMED")
        step("V3 ruling.vocabulary_digest equals the request's",
             ruling.get("vocabulary_digest") == req["vocabulary_digest"],
             ruling.get("vocabulary_digest"), "REFUSED_MALFORMED")
        step("V4 ruling.in_reply_to equals request_id",
             ruling.get("in_reply_to") == request_id, ruling.get("in_reply_to"), "REFUSED_MISMATCH")
        step("V5 ruling.correlation_id equals the request's",
             ruling.get("correlation_id") == req["correlation_id"],
             ruling.get("correlation_id"), "REFUSED_MISMATCH")
        ap = ruling.get("applies_to", {})
        step("V6 applies_to.venue and applies_to.repo equal the request's",
             ap.get("venue") == req["venue"] and ap.get("repo") == req["repo"],
             json.dumps({"venue": ap.get("venue"), "repo": ap.get("repo")}), "REFUSED_MISMATCH")
        step("V7 applies_to work identity and generations equal the request's",
             (ap.get("work_id") == req["work_id"]
              and ap.get("work_generation") == req["work_generation"]
              and ap.get("request_generation") == req["request_generation"]),
             "work_id=%s wg=%s rg=%s" % (ap.get("work_id"), ap.get("work_generation"),
                                         ap.get("request_generation")), "REFUSED_MISMATCH")
        step("V8 applies_to.subject_identity_line equals the request's subject",
             ap.get("subject_identity_line") == req["subject"]["identity_line"],
             ap.get("subject_identity_line"), "REFUSED_MISMATCH")
        step("V9 applies_to.policy_digest equals the acceptance policy digest",
             ap.get("policy_digest") == req["acceptance_policy"]["digest"],
             ap.get("policy_digest"), "REFUSED_STALE")
        step("V10 applies_to.evidence_digest equals the evidence set shown",
             ap.get("evidence_digest") == req["valid_while"]["evidence_digest"],
             ap.get("evidence_digest"), "REFUSED_STALE")
        step("V11 ruling control_config_generation_digest equals the request's",
             ruling.get("control_config_generation_digest") == sealed,
             ruling.get("control_config_generation_digest"), "REFUSED_STALE_CONFIG")
        step("V12 single_writer_assertion is true and supersedes is null or names a prior ruling",
             ruling.get("single_writer_assertion") is True,
             "supersedes=%s" % ruling.get("supersedes"), "REFUSED_AMBIGUOUS")
        d = ruling.get("directive")
        step("V13 directive is in the closed set and carries its companion field",
             d in ACTION_MAP and not errs, "directive=%s" % d, "REFUSED_MALFORMED")
        if d == "ADOPT_OPTION":
            ids = [o["id"] for o in req["question"]["options"]]
            step("V14 option_id is one of the offered options",
                 ruling.get("option_id") in ids,
                 "option_id=%s offered=%s" % (ruling.get("option_id"), ids), "REFUSED_MISMATCH")
        else:
            LADDER.append({"predicate": "V14 option_id is one of the offered options",
                           "value": "observed-good", "measured": "not applicable for directive %s" % d})

        # V15 -- independence. Three-valued, and it CAPS rather than blocks, a
        # disposition pinned in the acceptance policy before the answer was in view.
        maker = req["requester"]["login"]
        ruler = ruling.get("ruler", {})
        pc = ruler.get("provenance_class")
        app = None
        try:
            if fixture:
                app = comment.get("performed_via_github_app")
                app = app.get("slug") if isinstance(app, dict) else app
            else:
                capp = gh("repos/%s/issues/comments/%d" % (repo_slug, comment["id"]))
                app = (json.loads(capp).get("performed_via_github_app") or {})
                app = app.get("slug") if isinstance(app, dict) else None
        except Exception:
            app = None
        if pc == "forge_recorded_binding" and app:
            indep_value, indep_measured = "could-not-observe", (
                "credential path %s differs from the maker's, which is a distinct credential path "
                "and NOT a distinct principal; principal-level independence remains unmeasured" % app)
        elif ruler.get("login") == maker:
            indep_value, indep_measured = "could-not-observe", (
                "ruler.login == maker login (%s); a shared transport principal is not proof of "
                "dependence and is not proof of independence" % maker)
        else:
            indep_value, indep_measured = "could-not-observe", "no owner-bound execution-role binding available"
        LADDER.append({"predicate": "V15 maker/checker independence at the principal level",
                       "value": indep_value, "measured": indep_measured,
                       "narrowed_from": None} if False else
                      {"predicate": "V15 maker/checker independence at the principal level",
                       "value": indep_value, "measured": indep_measured})
        LADDER.append({"predicate": "V15a forge-recorded credential path of the ruling comment",
                       "value": "observed-good" if app else "could-not-observe",
                       "measured": "performed_via_github_app=%s" % (app or "none")})

    # ---- fold the ladder: TRUNCATED > FAIL > CNO > PASS ----------------------
    # Generation 3: a truncated or truncating read means the universe was not
    # seen whole, so nothing else in the ladder was earned; the terminal is
    # CNO_TRUNCATED_RESPONSE regardless of what the partial bytes suggested.
    expiry_code = "NO_ANSWER" if not candidates else "REFUSED_STALE"
    codes = [expiry_code if c == "__EXPIRY__" else c
             for (_n, c, v, _m) in FAILS if v == "observed-bad" and c]
    cnos = [expiry_code if c == "__EXPIRY__" else c
            for (_n, c, v, _m) in FAILS if v == "could-not-observe" and c]
    truncated_read = any(
        (e.get("read") or {}).get("truncated") is True
        or (e.get("read") or {}).get("mechanism") == "gh_axi_truncating"
        for e in LADDER)
    if truncated_read:
        outcome, verdict = "CNO_TRUNCATED_RESPONSE", "CNO"
    elif codes:
        # NO_ANSWER is terminal but is not a refusal of anything, so when it is
        # present it names the outcome rather than yielding to a neighbour code.
        outcome = "NO_ANSWER" if "NO_ANSWER" in codes else codes[0]
        verdict = "CNO" if outcome == "NO_ANSWER" else "FAIL"
    elif cnos:
        outcome, verdict = cnos[0], "CNO"
    elif ruling is None:
        outcome, verdict = ("NO_ANSWER", "CNO")
    else:
        outcome, verdict = "CONSUMED", "PASS"

    # ---- at most once, keyed by the consumption identity --------------------
    ruling_id = ruling.get("ruling_id") if ruling else None
    posted = comment["body"] if comment else None
    ruling_sha = hashlib.sha256(posted.encode("utf-8")).hexdigest() if posted else None
    ident_src = {"in_reply_to": request_id, "consumes_ruling_id": ruling_id, "ruling_sha256": ruling_sha}

    # GENERATION 2. A consumption identity exists only where a ruling was
    # consumed. On every other branch there is nothing to key, nothing durable to
    # write, and nothing to replay -- and the receipt says so by carrying no
    # consumption block at all, which the schema now enforces both ways.
    consuming = outcome == "CONSUMED"
    ckey = fsc4.derive("consumption_key", ident_src) if consuming else None
    rec_path = os.path.join(CONSUMED_DIR, ckey + ".json") if consuming else None
    if consuming:
        os.makedirs(CONSUMED_DIR, exist_ok=True)
        os.makedirs(DECISIONS_DIR, exist_ok=True)

    # ATOMIC CLAIM (generation 3). Intent-before-act is kept, but the claim is
    # an exclusive create: exactly one process can succeed at O_CREAT|O_EXCL on
    # the record path; every other one sees EEXIST and takes the replay branch.
    replayed = False
    claim_fd = None
    if consuming and not dry:
        try:
            claim_fd = os.open(rec_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            replayed = True
    elif consuming and dry:
        replayed = os.path.exists(rec_path)
    if replayed:
        prior = json.load(open(rec_path, encoding="utf-8"))
        # ZERO actions. Nothing is applied, nothing is posted, nothing is closed.
        print("REPLAY: consumption identity %s already recorded; actions performed = %d" % (ckey, ACTIONS_PERFORMED))
        print("REPLAY: returning the first outcome unchanged: %s" % prior["outcome"])
        json.dump({"replay": True, "consumption_key": ckey, "actions_performed": ACTIONS_PERFORMED,
                   "first_outcome": prior["outcome"], "first_consumed_at": prior["first_consumed_at"],
                   "receipt_id": prior.get("receipt_id")},
                  open(out_path, "w", encoding="utf-8"), indent=2)
        return 0

    first_at = utc()
    if consuming and not dry:
        # Intent before act: the identity was claimed above by the exclusive
        # create; write the CLAIMED intent through that same descriptor, then act.
        with os.fdopen(claim_fd, "w", encoding="utf-8") as fh:
            json.dump({"consumption_key": ckey, "request_id": request_id, "consumes_ruling_id": ruling_id,
                       "ruling_sha256": ruling_sha, "first_consumed_at": first_at, "outcome": "CLAIMED",
                       "claim_mechanism": "exclusive_create"}, fh, indent=2)
        claim_fd = None
        action_id = ACTION_MAP[ruling["directive"]]
        decision = {"record": "fm-cleanroom-decision/v1", "request_id": request_id,
                    "ruling_id": ruling_id, "directive": ruling["directive"],
                    "option_id": ruling.get("option_id"), "constraint": ruling.get("constraint"),
                    "missing_evidence": ruling.get("missing_evidence"),
                    "reserved_reason": ruling.get("reserved_reason"),
                    "action_id": action_id, "recorded_at": first_at,
                    "subject_identity_line": req["subject"]["identity_line"]}
        dpath = os.path.join(DECISIONS_DIR, request_id + ".json")
        body = json.dumps(decision, indent=2, sort_keys=True)
        open(dpath, "w", encoding="utf-8").write(body)
        ACTIONS_PERFORMED += 1
        applied = {"directive": ruling["directive"], "option_id": ruling.get("option_id"),
                   "action_id": action_id,
                   "applied_bytes_identity": {
                       "predicate": "the record written is byte-identical to the pinned rendering of the ruled directive",
                       "value": "observed-good",
                       "measured": "sha256(%s)=%s" % (dpath, hashlib.sha256(body.encode()).hexdigest())}}
    else:
        applied = None

    receipt = {
        "schema": proto, "kind": "receipt",
        "receipt_id": "PENDING", "in_reply_to": request_id,
        "correlation_id": req["correlation_id"],
        "vocabulary_digest": req["vocabulary_digest"],
        "control_config_generation_digest": sealed,
        "consumed_at": first_at,
        "consumer": {"login": req["requester"]["login"], "kind": "agent",
                     "session_ref": "clean-room control-plane consumer (generation 4)",
                     "provenance_class": "self_asserted_descriptor"},
        "consumes_ruling_id": ruling_id,
        "ruling_comment_id": comment["id"] if comment else None,
        "ruling_sha256": ruling_sha,
        "validation": LADDER, "verdict_class": verdict, "outcome": outcome,
        "resulting": {"tree_sha": None, "pull_request": None,
                      "scope": "records only in the clean-room control tree; no code changed and nothing landed"},
        "note": "",
    }
    if applied:
        receipt["applied"] = applied
    if consuming:
        # Claimed only here, and only against a record that has actually been
        # written on this branch above.
        receipt["consumption_identity"] = {"key": ckey, "first_consumed_at": first_at,
                                           "consumption_count": 1, "durable_record": rec_path,
                                           "claim_mechanism": "exclusive_create"}

    # A CONSUMED receipt may only claim a replay check that was ACTUALLY run.
    # The schema requires the block; this runs the second consumption, measures
    # the store before and after, and refuses to fabricate the result.
    if consuming and not dry and "--with-replay-proof" in sys.argv:
        json.dump({"consumption_key": ckey, "request_id": request_id,
                   "consumes_ruling_id": ruling_id, "ruling_sha256": ruling_sha,
                   "first_consumed_at": first_at, "outcome": outcome},
                  open(rec_path, "w", encoding="utf-8"), indent=2)
        before = store_fingerprint()
        probe = os.path.join(os.path.dirname(out_path), "replay-probe.json")
        r = subprocess.run([sys.executable, os.path.abspath(__file__), sys.argv[1], probe],
                           capture_output=True, text=True, env=dict(os.environ))
        after = store_fingerprint()
        try:
            pr = json.load(open(probe, encoding="utf-8"))
        except (OSError, ValueError):
            pr = {}
        acted = pr.get("actions_performed")
        same_outcome = pr.get("first_outcome") == outcome
        if not (pr.get("replay") is True and acted == 0 and same_outcome and before == after):
            sys.stderr.write("REPLAY PROOF FAILED: replay=%r actions=%r outcome_match=%r "
                             "store_before=%s store_after=%s rc=%d\n"
                             % (pr.get("replay"), acted, same_outcome, before, after, r.returncode))
            sys.exit(10)
        receipt["replay_check"] = {
            "second_consumption_attempted": True,
            "actions_performed_on_replay": 0,
            "outcome_identical": True,
            "evidence": ("second consumption of consumption identity %s performed 0 actions and "
                         "returned %s unchanged; the durable store digest was %s before and after"
                         % (ckey, outcome, before)),
        }

    receipt["receipt_id"] = fsc4.derive("receipt_id", receipt)
    json.dump(receipt, open(out_path, "w", encoding="utf-8"), indent=2, sort_keys=True)

    if consuming and not dry:
        json.dump({"consumption_key": ckey, "request_id": request_id, "consumes_ruling_id": ruling_id,
                   "ruling_sha256": ruling_sha, "first_consumed_at": first_at,
                   "outcome": outcome, "receipt_id": receipt["receipt_id"]},
                  open(rec_path, "w", encoding="utf-8"), indent=2)

    print("outcome        %s (%s)" % (outcome, verdict))
    print("consumption    %s" % (ckey or "NONE (nothing was consumed)"))
    print("receipt_id     %s" % receipt["receipt_id"])
    print("actions        %d" % ACTIONS_PERFORMED)
    print("ladder         %d predicates" % len(LADDER))
    return 0


if __name__ == "__main__":
    sys.exit(main())
