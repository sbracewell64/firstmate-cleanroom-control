#!/usr/bin/env python3
"""THE canonical owner of the LIVE outbound request record. Generation 3, NON-frozen.

The record `state/live/<request_id>.json` is what makes an emitted request
capturable: the inbound listener (liveRequests() in
listener/cleanroom-control-inbound.mjs) classifies a comment as a
ruling_candidate ONLY when a live record names its issue, and the frozen consumer
(bin/fsc4-consume.py) opens the same record to locate the issue. The frozen
emitter creates the venue item but never writes this record; transaction 3 wrote
it by hand and transactions 4 and 5 omitted it, so the rulings on control #11
and #12 were never captured. This file makes the record part of the emit
contract: OUTBOUND PUBLICATION IS INCOMPLETE UNTIL THE RECORD EXISTS DURABLY AND
VERIFIES against the emitted request identity and the created issue.

Laws (in the spirit of the captain addendum):
  * ONE owner of the record shape and path: this module. Nothing else writes,
    moves or deletes a live record. bin/fsc4-register-live.py is a shim onto it.
  * The record is DERIVED only from a verified envelope plus the frozen schema
    and the single resolver -- never from prose, never from a typed id.
  * Fail closed and loud: a record that cannot be persisted AND re-read
    byte-identically is not a record; the exit is non-zero (7) and the word
    INCOMPLETE is printed. Success is never reported on a missing record.
  * Idempotent: a record that already exists with identical bytes is a no-op
    (exit 0, nothing rewritten). A record that exists with DIFFERENT bytes is a
    CONFLICT and is refused (exit 6); nothing is ever silently overwritten.
  * Sealing order: live -> closed happens ONLY on terminal consumption through
    the frozen consumer's receipt (`retire`), never on register or reconcile,
    and reconcile never resurrects a request that was already retired.

Record shape (the one observed in state/closed/*.json since transaction 3):
  {request_id, issue_number, issue_url, created_at, expires_at, generation}

Usage:
  fsc4-live-record.py register  <request.json> <creation-response.json>
        emit contract: derive the record from the creation response, persist it
        durably, re-read it and verify it against the request identity
  fsc4-live-record.py verify    <request_id> [--issue <n>]
        the record exists, parses, names <request_id> (and <n> when given)
  fsc4-live-record.py reconcile <issue-number>
        crash/omission window: issue exists, its envelope verifies as fetched
        through bin/fsc4-verify-envelope.py, live record missing. Reconstructs
        EXACTLY ONE record from the fetched, verified envelope. Idempotent.
  fsc4-live-record.py retire    <request_id> <receipt.json>
        move live -> closed, ONLY against a receipt the frozen consumer produced
        for that request (receipt_id recomputes; a CONSUMED receipt must match
        its durable consumed record)
Exit 0 ok / no-op; 2 usage; 4 could-not-observe (forge, config); 6 identity
mismatch, conflict or refused; 7 persistence failure (record NOT durable).
"""
import importlib.util
import json
import os
import subprocess
import sys

import fsc4
import fsc4_config

HERE = os.path.dirname(os.path.abspath(__file__))
CTL = fsc4_config.CONTROL_ROOT
LIVE_DIR = os.path.join(CTL, "state", "live")
CLOSED_DIR = os.path.join(CTL, "state", "closed")
CONSUMED_DIR = os.environ.get("FSC2_CONSUMED_DIR") or os.path.join(CTL, "state", "consumed")
FREEZE_PATH = os.path.join(CTL, "schema", "FREEZE.json")
VERIFIER_PATH = os.path.join(HERE, "fsc4-verify-envelope.py")
RECORD_KEYS = ("request_id", "issue_number", "issue_url", "created_at", "expires_at", "generation")

EXIT_OK, EXIT_USAGE, EXIT_CNO, EXIT_REFUSED, EXIT_NOT_DURABLE = 0, 2, 4, 6, 7


class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def _verifier():
    """Reuse the frozen envelope verifier's extraction, rendering and fetch
    IN PLACE (loaded from its frozen bytes; nothing is reimplemented here)."""
    spec = importlib.util.spec_from_file_location("fsc3_verify_envelope", VERIFIER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row(pred, value, measured):
    print("%-18s %-72s %s" % (value, pred, str(measured)[:200]))
    return value == "observed-good"


def schema_generation():
    """The generation the record carries is READ from the freeze record."""
    with open(FREEZE_PATH, encoding="utf-8") as fh:
        return int(json.load(fh)["schema_generation"])


def record_path(request_id, base=None):
    if not isinstance(request_id, str) or "/" in request_id or not request_id.startswith("fscr2-"):
        raise Refused(EXIT_REFUSED, "REFUSED: not a request id: %r" % (request_id,))
    return os.path.join(base or LIVE_DIR, request_id + ".json")


def serialize(rec):
    # Same bytes the existing records carry: indent 2, sorted keys, no trailing newline.
    return json.dumps(rec, indent=2, sort_keys=True).encode("utf-8")


def build_record(env, issue_number, issue_url):
    return {
        "request_id": env["request_id"],
        "issue_number": int(issue_number),
        "issue_url": issue_url,
        "created_at": env["created_at"],
        "expires_at": env["expires_at"],
        "generation": schema_generation(),
    }


def envelope_from_body(body, verifier):
    """The request envelope carried by a venue body, identity-checked against the
    frozen schema's own id derivation. Never guesses: exactly one fenced block,
    kind == request, request_id recomputes from the envelope's own bytes."""
    fence, count = verifier.extract_last_json_fence(body or "")
    if count != 1 or fence is None:
        raise Refused(EXIT_REFUSED, "REFUSED: body carries %d fenced JSON block(s), need exactly 1" % count)
    try:
        env = json.loads(fence)
    except ValueError as exc:
        raise Refused(EXIT_REFUSED, "REFUSED: fenced envelope does not parse: %s" % exc)
    if not isinstance(env, dict) or env.get("kind") != "request":
        raise Refused(EXIT_REFUSED, "REFUSED: fenced envelope is not a request (kind=%r)" % (env.get("kind") if isinstance(env, dict) else None,))
    derived = fsc4.derive("request_id", env)
    if derived != env.get("request_id"):
        raise Refused(EXIT_REFUSED, "REFUSED: request_id does not recompute: carried=%s derived=%s" % (env.get("request_id"), derived))
    errs = fsc4.validate("request", env)
    if errs:
        raise Refused(EXIT_REFUSED, "REFUSED: envelope does not validate: %s" % "; ".join(errs[:4]))
    if verifier.render(env) != body:
        raise Refused(EXIT_REFUSED, "REFUSED: body != render(envelope) per $defs.venue_publication")
    return env


def persist(rec):
    """Durable, atomic, verified-by-re-read. Returns 'written' or 'unchanged'.
    Raises Refused(7) when the bytes are not durably on disk, Refused(6) on a
    differing existing record."""
    want = serialize(rec)
    dst = record_path(rec["request_id"])
    if os.path.exists(dst):
        with open(dst, "rb") as fh:
            have = fh.read()
        if have == want:
            return "unchanged"
        raise Refused(EXIT_REFUSED, "REFUSED: CONFLICT: %s exists with different bytes; nothing overwritten" % dst)
    tmp = "%s.%d.tmp" % (dst, os.getpid())
    try:
        os.makedirs(LIVE_DIR, exist_ok=True)
        fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, "wb") as fh:
            fh.write(want)
            fh.flush()
            os.fsync(fh.fileno())
        # EXCLUSIVE CREATE on the final path (same law as the consumer's claim):
        # link() fails with EEXIST if any other writer got there first, so a
        # concurrent differing record is never overwritten -- it is compared.
        try:
            os.link(tmp, dst)
        except FileExistsError:
            with open(dst, "rb") as fh:
                have = fh.read()
            if have == want:
                return "unchanged"
            raise Refused(EXIT_REFUSED, "REFUSED: CONFLICT: %s was written concurrently with different bytes; nothing overwritten" % dst)
        dfd = os.open(LIVE_DIR, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        with open(dst, "rb") as fh:
            back = fh.read()
    except OSError as exc:
        raise Refused(EXIT_NOT_DURABLE, "INCOMPLETE: live record NOT persisted at %s: %s" % (dst, exc))
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    if back != want:
        raise Refused(EXIT_NOT_DURABLE, "INCOMPLETE: live record at %s re-read differs from what was written" % dst)
    return "written"


def check_record(request_id, issue_number=None):
    """Verify predicates over the on-disk record. Returns (ok, rec)."""
    dst = record_path(request_id)
    ok = row("live record exists at the canonical path", "observed-good" if os.path.isfile(dst) else "observed-bad", dst)
    if not ok:
        return False, None
    try:
        with open(dst, encoding="utf-8") as fh:
            rec = json.load(fh)
    except (OSError, ValueError) as exc:
        row("live record parses as JSON", "observed-bad", str(exc))
        return False, None
    ok &= row("live record parses as JSON", "observed-good", "%d bytes" % os.path.getsize(dst))
    missing = [k for k in RECORD_KEYS if k not in rec]
    ok &= row("live record carries the canonical shape", "observed-good" if not missing else "observed-bad",
              "keys=%s missing=%s" % (sorted(rec), missing))
    ok &= row("live record names the request identity in its file name",
              "observed-good" if rec.get("request_id") == request_id else "observed-bad",
              "file=%s record=%s" % (request_id, rec.get("request_id")))
    ok &= row("issue_number is a positive integer",
              "observed-good" if isinstance(rec.get("issue_number"), int) and rec["issue_number"] > 0 else "observed-bad",
              repr(rec.get("issue_number")))
    if issue_number is not None:
        ok &= row("live record names the created issue",
                  "observed-good" if rec.get("issue_number") == int(issue_number) else "observed-bad",
                  "expected=%s record=%s" % (issue_number, rec.get("issue_number")))
    return ok, rec


def not_retired(request_id):
    closed = record_path(request_id, CLOSED_DIR)
    if os.path.exists(closed):
        raise Refused(EXIT_REFUSED, "REFUSED: SEALED: %s already retired at %s; reconcile never resurrects a closed request" % (request_id, closed))
    if os.path.isdir(CONSUMED_DIR):
        for n in sorted(os.listdir(CONSUMED_DIR)):
            if not n.endswith(".json"):
                continue
            try:
                with open(os.path.join(CONSUMED_DIR, n), encoding="utf-8") as fh:
                    c = json.load(fh)
            except (OSError, ValueError):
                continue
            if c.get("request_id") == request_id and c.get("outcome") == "CONSUMED":
                raise Refused(EXIT_REFUSED, "REFUSED: SEALED: %s already CONSUMED (%s); reconcile never resurrects it" % (request_id, n))


def resolved_repo():
    repo = fsc4_config.get("control.repository")
    proto = fsc4_config.get("control.protocol")
    admit, reason = fsc4_config.isolation_admits(repo, proto)
    if not row("venue isolation admits the resolved venue", "observed-good" if admit else "observed-bad", reason):
        raise Refused(EXIT_REFUSED, "REFUSED: %s" % reason)
    return repo


# --- commands ---------------------------------------------------------------

def cmd_register(req_path, resp_path):
    verifier = _verifier()
    with open(req_path, encoding="utf-8") as fh:
        req = json.load(fh)
    with open(resp_path, encoding="utf-8") as fh:
        resp = json.load(fh)
    if not isinstance(resp.get("number"), int) or not resp.get("html_url"):
        raise Refused(EXIT_REFUSED, "REFUSED: creation response carries no issue number/url")
    env = envelope_from_body(resp.get("body"), verifier)
    ok = row("creation response body carries the emitted request envelope",
             "observed-good" if env["request_id"] == req.get("request_id") else "observed-bad",
             "request=%s created=%s" % (req.get("request_id"), env["request_id"]))
    if not ok:
        raise Refused(EXIT_REFUSED, "REFUSED: creation response is not for this request")
    rec = build_record(env, resp["number"], resp["html_url"])
    state = persist(rec)
    row("live record persisted durably (fsync, atomic replace, re-read byte-identical)", "observed-good",
        "%s %s" % (state, record_path(rec["request_id"])))
    ok, _ = check_record(rec["request_id"], resp["number"])
    if not ok:
        raise Refused(EXIT_NOT_DURABLE, "INCOMPLETE: live record written but does not verify")
    print("LIVE RECORD OK (%s): %s issue #%d -> %s" % (state, rec["request_id"], rec["issue_number"], record_path(rec["request_id"])))
    return EXIT_OK


def cmd_verify(request_id, issue_number=None):
    ok, _ = check_record(request_id, issue_number)
    print("LIVE RECORD VERIFY %s: %s" % ("OK" if ok else "BAD", request_id))
    return EXIT_OK if ok else EXIT_REFUSED


def cmd_reconcile(issue_number):
    verifier = _verifier()
    try:
        num = int(issue_number)
    except ValueError:
        raise Refused(EXIT_USAGE, "REFUSED: issue number must be an integer")
    repo = resolved_repo()
    # 1. The declared as-fetched verifier, exactly as a third party would run it.
    r = subprocess.run([sys.executable, VERIFIER_PATH, "issue", str(num)], capture_output=True, text=True, cwd=HERE)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise Refused(EXIT_CNO if r.returncode == 4 else EXIT_REFUSED,
                      "REFUSED: fsc4-verify-envelope.py issue %d exited %d; no record is derived from an unverified item" % (num, r.returncode))
    # 2. One read of the item whose bytes this record is derived from.
    try:
        text, nbytes = verifier.fetch("repos/%s/issues/%d" % (repo, num))
    except RuntimeError as exc:
        raise Refused(EXIT_CNO, "COULD-NOT-OBSERVE: forge unreachable: %s" % exc)
    doc = json.loads(text)
    if doc.get("number") != num or doc.get("pull_request"):
        raise Refused(EXIT_REFUSED, "REFUSED: fetched item is not issue #%d" % num)
    row("venue item read whole through gh api", "observed-good", "received_bytes=%d" % nbytes)
    env = envelope_from_body(doc.get("body"), verifier)
    row("request_id derived from the fetched envelope, not from prose", "observed-good", env["request_id"])
    not_retired(env["request_id"])
    rec = build_record(env, num, doc["html_url"])
    state = persist(rec)
    row("live record reconciled from the verified venue envelope", "observed-good", "%s %s" % (state, record_path(rec["request_id"])))
    ok, _ = check_record(rec["request_id"], num)
    if not ok:
        raise Refused(EXIT_NOT_DURABLE, "INCOMPLETE: reconciled record does not verify")
    print("RECONCILE %s: issue #%d -> %s (%s)" % ("NO-OP" if state == "unchanged" else "RESTORED", num, rec["request_id"], state))
    return EXIT_OK


def cmd_retire(request_id, receipt_path):
    with open(receipt_path, encoding="utf-8") as fh:
        receipt = json.load(fh)
    ok = row("receipt is a receipt for this request", "observed-good" if receipt.get("kind") == "receipt" and receipt.get("in_reply_to") == request_id else "observed-bad",
             "kind=%s in_reply_to=%s" % (receipt.get("kind"), receipt.get("in_reply_to")))
    derived = fsc4.derive("receipt_id", receipt)
    ok &= row("receipt_id recomputes from the receipt's own bytes (frozen consumer product)",
              "observed-good" if derived == receipt.get("receipt_id") else "observed-bad",
              "carried=%s derived=%s" % (receipt.get("receipt_id"), derived))
    errs = fsc4.validate("receipt", receipt)
    ok &= row("receipt validates against the schema of record", "observed-good" if not errs else "observed-bad", "; ".join(errs[:3]) or "0 errors")
    outcome = receipt.get("outcome")
    live = record_path(request_id)
    # Terminal means the request can receive no further ruling that this plane
    # would act on. CNO_* means "re-read", not "done". NO_ANSWER is terminal only
    # once the request has expired (the frozen consumer folds an empty universe
    # to NO_ANSWER before expiry too, and a ruling may still arrive).
    if not isinstance(outcome, str) or not outcome:
        ok &= row("receipt carries a terminal outcome", "observed-bad", repr(outcome))
    elif outcome.startswith("CNO_"):
        ok &= row("receipt carries a terminal outcome", "observed-bad", "%s = could-not-observe; re-read, do not seal" % outcome)
    elif outcome == "NO_ANSWER":
        try:
            with open(live, encoding="utf-8") as fh:
                expires = json.load(fh).get("expires_at")
        except (OSError, ValueError):
            expires = None
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ok &= row("receipt carries a terminal outcome",
                  "observed-good" if isinstance(expires, str) and now >= expires else "observed-bad",
                  "NO_ANSWER now=%s expires_at=%s (sealable only after expiry)" % (now, expires))
    else:
        ok &= row("receipt carries a terminal outcome", "observed-good", outcome)
    if outcome == "CONSUMED":
        key = (receipt.get("consumption_identity") or {}).get("key")
        cpath = os.path.join(CONSUMED_DIR, "%s.json" % key) if key else None
        try:
            with open(cpath, encoding="utf-8") as fh:
                c = json.load(fh)
        except (OSError, ValueError, TypeError):
            c = {}
        ok &= row("CONSUMED receipt matches its durable consumed record",
                  "observed-good" if c.get("receipt_id") == receipt.get("receipt_id") and c.get("request_id") == request_id and c.get("outcome") == "CONSUMED" else "observed-bad",
                  "record=%s receipt_id=%s" % (cpath, c.get("receipt_id")))
    if not ok:
        raise Refused(EXIT_REFUSED, "REFUSED: not a terminal consumption of %s; live record stays" % request_id)
    closed = record_path(request_id, CLOSED_DIR)
    if os.path.exists(closed) and not os.path.exists(live):
        print("RETIRE NO-OP: %s already at %s" % (request_id, closed))
        return EXIT_OK
    if os.path.exists(closed):
        raise Refused(EXIT_REFUSED, "REFUSED: CONFLICT: %s exists in both live and closed" % request_id)
    if not os.path.exists(live):
        raise Refused(EXIT_REFUSED, "REFUSED: no live record for %s" % request_id)
    try:
        os.makedirs(CLOSED_DIR, exist_ok=True)
        os.replace(live, closed)
    except OSError as exc:
        raise Refused(EXIT_NOT_DURABLE, "INCOMPLETE: could not retire %s: %s" % (request_id, exc))
    print("RETIRED %s: %s -> %s" % (request_id, live, closed))
    return EXIT_OK


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return EXIT_USAGE
    cmd, args = argv[1], argv[2:]
    try:
        if cmd == "register" and len(args) == 2:
            return cmd_register(*args)
        if cmd == "verify" and len(args) in (1, 3):
            num = args[2] if len(args) == 3 and args[1] == "--issue" else None
            if len(args) == 3 and num is None:
                raise Refused(EXIT_USAGE, "REFUSED: verify <request_id> [--issue <n>]")
            return cmd_verify(args[0], num)
        if cmd == "reconcile" and len(args) == 1:
            return cmd_reconcile(args[0])
        if cmd == "retire" and len(args) == 2:
            return cmd_retire(*args)
        raise Refused(EXIT_USAGE, "REFUSED: unknown command or wrong arguments: %s" % " ".join(argv[1:]))
    except Refused as exc:
        sys.stderr.write("%s\n" % exc)
        if exc.code == EXIT_NOT_DURABLE:
            sys.stderr.write("PUBLICATION INCOMPLETE: no live record -> this request's rulings CANNOT be captured or consumed\n")
        return exc.code
    except fsc4_config.ConfigRefusal as exc:
        sys.stderr.write("COULD-NOT-OBSERVE: %s\n" % str(exc).split("\n")[0])
        return EXIT_CNO
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write("REFUSED: %s: %s\n" % (type(exc).__name__, exc))
        return EXIT_REFUSED


if __name__ == "__main__":
    sys.exit(main(sys.argv))
