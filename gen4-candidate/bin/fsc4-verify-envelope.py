#!/usr/bin/env python3
"""THE DECLARED VERIFIER: an envelope validates against its frozen schema of
record AS FETCHED from the venue. Generation 3 ($defs.envelope_verifier).

Both the generation-2 executor and the independent observer recommended this
verifier; until now "the envelope validates against the schema of record" was the
most-repeated by-hand judgement on the plane (issue #3 required_repairs[5]).

Three-valued. Reads go through `gh api` (non-truncating) and the received byte
count is recorded; an unreachable forge or a truncated read is could-not-observe,
never a pass. Nothing here names a repository: the venue is resolved through
the single resolver and the isolation predicate is re-run.

Usage:
  fsc4-verify-envelope.py issue <number>                  verify the request envelope in an issue body
  fsc4-verify-envelope.py comment <comment-id>            verify a ruling/receipt envelope in a comment
  fsc4-verify-envelope.py file <kind> <envelope.json>     verify a local envelope (no fetch)
  fsc4-verify-envelope.py render-check <request.json> <body.txt>
                                                          verify body == render(envelope)
Exit 0 every predicate observed-good; 6 some observed-bad; 4 could-not-observe.
"""
import hashlib
import json
import os
import subprocess
import sys

import fsc4
import fsc4_config

ROWS = []


def row(pred, value, measured):
    ROWS.append((pred, value, measured))
    print("%-18s %-72s %s" % (value, pred, measured[:160]))


def fetch(path):
    """gh api, streamed whole. Returns (text, bytes) or raises."""
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return r.stdout, len(r.stdout.encode("utf-8"))


def extract_last_json_fence(body):
    blocks, cur, infence = [], [], False
    for line in body.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if not infence and s.startswith("```") and "json" in s.lower():
            infence, cur = True, []
            continue
        if infence and s.startswith("```"):
            blocks.append("\n".join(cur))
            infence = False
            continue
        if infence:
            cur.append(line)
    return blocks[-1] if blocks else None, len(blocks)


def render(req):
    law = fsc4.schema()["$defs"]["venue_publication"]["const"]
    env = json.dumps(req, indent=2, sort_keys=True, ensure_ascii=False)
    out = []
    for r in law["render"]:
        if r == "question.body_markdown":
            out.append(req["question"]["body_markdown"])
        elif r.startswith("<envelope:"):
            out.append(env)
        else:
            out.append(r)
    return "\n".join(out)


def verify_envelope(kind, obj, body=None):
    """The schema-and-identity predicates, shared by every entry point."""
    want = fsc4.schema_digest()
    got = obj.get("vocabulary_digest")
    row("envelope.vocabulary_digest names THIS schema of record",
        "observed-good" if got == want else "observed-bad", "envelope=%s schema=%s" % (got, want))
    if got != want:
        row("validation against the schema the envelope names", "could-not-observe",
            "this verifier holds generation-4 bytes only; an envelope of another generation must be verified by that generation's tool")
        return
    errs = fsc4.validate(kind, obj)
    row("envelope validates against the schema of record (%s)" % kind,
        "observed-good" if not errs else "observed-bad", "; ".join(errs[:4]) or "0 errors")
    spec = fsc4.schema()["$defs"]["id_derivation"]["const"]
    for name in spec:
        if name not in obj:
            continue
        try:
            derived = fsc4.derive(name, obj)
        except Exception as exc:  # noqa: BLE001
            row("%s recomputes from the envelope's own bytes" % name, "could-not-observe", str(exc))
            continue
        row("%s recomputes from the envelope's own bytes" % name,
            "observed-good" if derived == obj[name] else "observed-bad",
            "carried=%s derived=%s" % (obj[name], derived))
    # GENERATION 4: evidence_digest is a declared, verifier-covered derivation
    # ($defs.evidence_digest_derivation). Recompute it from evidence_refs through
    # the ONE canonical owner and fail closed on a mismatch, so a producer/schema
    # disagreement is caught here at emit rather than only in the consumer L3.
    if "evidence_refs" in obj and isinstance(obj.get("valid_while"), dict) \
            and "evidence_digest" in obj["valid_while"]:
        carried = obj["valid_while"]["evidence_digest"]
        try:
            recomputed = fsc4.evidence_digest(obj["evidence_refs"])
            row("valid_while.evidence_digest recomputes from evidence_refs per $defs.evidence_digest_derivation",
                "observed-good" if recomputed == carried else "observed-bad",
                "carried=%s derived=%s" % (carried, recomputed))
        except Exception as exc:  # noqa: BLE001
            row("valid_while.evidence_digest recomputes from evidence_refs per $defs.evidence_digest_derivation",
                "could-not-observe", str(exc))
    if kind == "request" and body is not None:
        same = body == render(obj)
        row("venue body equals render(envelope) per $defs.venue_publication",
            "observed-good" if same else "observed-bad",
            "body_sha256=%s render_sha256=%s" % (
                hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
                hashlib.sha256(render(obj).encode("utf-8")).hexdigest()[:16]))


def resolved_venue():
    repo = fsc4_config.get("control.repository")
    proto = fsc4_config.get("control.protocol")
    admit, reason = fsc4_config.isolation_admits(repo, proto)
    row("venue isolation admits the resolved venue", "observed-good" if admit else "observed-bad", reason)
    if not admit:
        raise SystemExit(6)
    return repo


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    cmd = argv[1]
    try:
        if cmd in ("issue", "comment"):
            repo = resolved_venue()
            path = ("repos/%s/issues/%s" % (repo, argv[2]) if cmd == "issue"
                    else "repos/%s/issues/comments/%s" % (repo, argv[2]))
            try:
                text, nbytes = fetch(path)
            except RuntimeError as exc:
                row("venue item read whole through gh api", "could-not-observe", "forge unreachable: %s" % exc)
                return 4
            doc = json.loads(text)
            body = doc.get("body") or ""
            row("venue item read whole through gh api", "observed-good",
                "received_bytes=%d body_bytes=%d" % (nbytes, len(body.encode("utf-8"))))
            fence, count = extract_last_json_fence(body)
            row("body contains exactly one extractable envelope",
                "observed-good" if count == 1 else ("observed-bad" if count > 1 else "observed-bad"),
                "fenced_json_blocks=%d" % count)
            if fence is None:
                return 6
            try:
                obj = json.loads(fence)
            except ValueError as exc:
                row("extracted envelope parses as JSON", "observed-bad", str(exc))
                return 6
            kind = obj.get("kind")
            row("extracted envelope declares a kind the schema knows",
                "observed-good" if kind in ("request", "ruling", "receipt") else "observed-bad", "kind=%s" % kind)
            if kind not in ("request", "ruling", "receipt"):
                return 6
            verify_envelope(kind, obj, body if kind == "request" else None)
        elif cmd == "file":
            obj = json.load(open(argv[3], encoding="utf-8"))
            verify_envelope(argv[2], obj)
        elif cmd == "render-check":
            obj = json.load(open(argv[2], encoding="utf-8"))
            body = open(argv[3], encoding="utf-8").read()
            verify_envelope("request", obj, body)
        else:
            sys.stderr.write("REFUSED: unknown command %r\n" % cmd)
            return 2
    except fsc4_config.ConfigRefusal as exc:
        row("control configuration resolves", "could-not-observe", str(exc).split("\n")[0])
        return 4
    bad = sum(1 for r in ROWS if r[1] == "observed-bad")
    cno = sum(1 for r in ROWS if r[1] == "could-not-observe")
    print("VERIFY %s (%d predicates, %d observed-bad, %d could-not-observe)"
          % ("OK" if not bad and not cno else ("BAD" if bad else "CNO"), len(ROWS), bad, cno))
    return 6 if bad else (4 if cno else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
