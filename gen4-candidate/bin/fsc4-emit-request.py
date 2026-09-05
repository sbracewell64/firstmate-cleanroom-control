#!/usr/bin/env python3
"""Emit ONE fm-sol-control/v2 request into the resolved venue, ATOMICALLY. Generation 3.

GENERATION 3 REPAIRS (control issue #3, tooling_supersession required_repairs[1]):
the frozen generation-2 emitter passed title and labels[] as `-f` flags beside
`--input -`, so they landed in the URL query string which the forge ignores for
a POST; the call refused with 422 and the frozen emitter could not emit without
a bridge (observer finding 4.4). Generation 3 carries title, labels AND body as
fields of ONE JSON request body, so the frozen emitter itself performs the single
atomic issue+labels creation. The venue body is rendered from the envelope per
$defs.venue_publication (issue_body == render(envelope)), so the envelope a
third party fetches validates as fetched (required_repairs[0]).

Observer finding 4.6: under generation 1 the venue item was created at 11:42:12Z
and its declared routing labels were applied at 11:52:37Z, ten minutes and
twenty-five seconds later. For those ten minutes the request sat in the venue
without the routing metadata the canonical configuration declares, so any
label-keyed discovery path could not have fired, and latency measured from
creation was not latency from routability.

Generation 2 creates the item and its labels in ONE forge call and checks the
post-condition AGAINST THE CREATION RESPONSE. A label observed on a later read
does not establish that it was present at creation, so a later read is not
accepted as evidence of atomicity.

This lane is NOT authorized to emit a generation 4 request. The default is
--dry-run, and posting additionally requires FSC2_EMIT_AUTHORIZED_LANE to carry
the authorizing lane's token: an emitter that can post by accident is one
mistyped flag away from an unauthorized outward effect.

Usage:
  fsc4-emit-request.py plan <request.json>
        validate, resolve the labels, and print the single call that would run
  fsc4-emit-request.py check <request.json> <creation-response.json>
        run the atomicity post-condition against a creation response
  fsc4-emit-request.py post <request.json> <out-response.json>
        actually create it; refuses without FSC2_EMIT_AUTHORIZED_LANE
"""
import hashlib
import json
import os
import subprocess
import sys

import fsc4
import fsc4_config

LANE_TOKEN = "cleanroom-control-v2-request-generation-3"


def resolved_labels():
    """The declared routing labels, from the ONE resolver. Never typed here."""
    cfg = fsc4_config.load()
    return [cfg["routing"]["escalation_label"], cfg["routing"]["destination_label"]]


def preflight(req):
    """Everything that must hold before a single byte reaches the venue."""
    out = []
    errs = fsc4.validate("request", req)
    out.append(("request validates against the schema of record",
                "observed-good" if not errs else "observed-bad",
                "; ".join(errs[:6]) or "0 errors"))
    repo = fsc4_config.get("control.repository")
    proto = fsc4_config.get("control.protocol")
    admit, reason = fsc4_config.isolation_admits(repo, proto)
    out.append(("venue isolation admits the resolved venue and protocol",
                "observed-good" if admit else "observed-bad", reason))
    declared, carried = resolved_labels(), req.get("routing_labels", [])
    out.append(("request.routing_labels equals the canonical configuration's routing labels",
                "observed-good" if sorted(declared) == sorted(carried) else "observed-bad",
                "config=%s request=%s" % (declared, carried)))
    return out, repo


def render_body(req):
    """issue_body == render(envelope), per $defs.venue_publication in the schema of
    record. The rendering rows are READ from the schema, never typed here."""
    law = fsc4.schema()["$defs"]["venue_publication"]["const"]
    env = json.dumps(req, indent=2, sort_keys=True, ensure_ascii=False)
    out = []
    for row in law["render"]:
        if row == "question.body_markdown":
            out.append(req["question"]["body_markdown"])
        elif row.startswith("<envelope:"):
            out.append(env)
        else:
            out.append(row)
    return "\n".join(out)


def creation_call(req, repo):
    """The ONE call. Title, labels and body are all fields of the JSON request
    body of a single POST, so the item is created carrying its labels. Nothing
    goes to the query string (generation-2 defect, observer 4.4)."""
    return ["gh", "api", "--method", "POST", "repos/%s/issues" % repo, "--input", "-"]


def creation_payload(req):
    return {"title": req["question"]["title"],
            "labels": list(req["routing_labels"]),
            "body": render_body(req)}


def post_condition(req, response):
    """Atomicity, measured on the CREATION RESPONSE alone."""
    got = sorted(l["name"] if isinstance(l, dict) else l for l in response.get("labels", []))
    want = sorted(req["routing_labels"])
    checks = [
        ("the created body equals render(envelope) per $defs.venue_publication",
         "observed-good" if response.get("body") == render_body(req) else "observed-bad",
         "created_body_sha256=%s render_sha256=%s" % (
             hashlib.sha256((response.get("body") or "").encode("utf-8")).hexdigest()[:16],
             hashlib.sha256(render_body(req).encode("utf-8")).hexdigest()[:16])),
        ("every declared routing label is present in the creation response",
         "observed-good" if set(want) <= set(got) else "observed-bad",
         "declared=%s in_creation_response=%s" % (want, got)),
        ("the item was never observed without its labels: created_at == updated_at",
         "observed-good" if response.get("created_at") == response.get("updated_at") else "observed-bad",
         "created_at=%s updated_at=%s" % (response.get("created_at"), response.get("updated_at"))),
    ]
    return checks


def report(rows):
    bad = 0
    for pred, value, measured in rows:
        print("%-18s %-70s %s" % (value, pred, measured))
        if value != "observed-good":
            bad += 1
    return bad


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    cmd = argv[1]
    req = json.load(open(argv[2], encoding="utf-8"))
    rows, repo = preflight(req)
    if cmd == "plan":
        bad = report(rows)
        print()
        print("single creation call:")
        print("  " + " ".join(creation_call(req, repo)))
        payload = creation_payload(req)
        print("  stdin JSON fields: title=%r labels=%r body=<%d bytes, render(envelope)>"
              % (payload["title"], payload["labels"], len(payload["body"].encode("utf-8"))))
        print()
        print("REFUSED: %d preflight predicate(s) not observed-good" % bad if bad else "PLAN OK")
        return 8 if bad else 0
    if cmd == "check":
        response = json.load(open(argv[3], encoding="utf-8"))
        bad = report(rows + post_condition(req, response))
        print("ATOMIC OK" if not bad else "REFUSED: %d predicate(s) not observed-good" % bad)
        return 8 if bad else 0
    if cmd == "post":
        if os.environ.get("FSC2_EMIT_AUTHORIZED_LANE") != LANE_TOKEN:
            sys.stderr.write(
                "REFUSED: emitting a generation 4 request is a separately authorized lane.\n"
                "         Set FSC2_EMIT_AUTHORIZED_LANE=%s only in that lane.\n" % LANE_TOKEN)
            return 9
        bad = report(rows)
        if bad:
            sys.stderr.write("REFUSED: preflight failed; nothing was posted\n")
            return 8
        body = json.dumps(creation_payload(req), ensure_ascii=False)
        r = subprocess.run(creation_call(req, repo), input=body, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write("REFUSED: creation call failed: %s\n" % r.stderr.strip()[:300])
            return 8
        response = json.loads(r.stdout)
        json.dump(response, open(argv[3], "w", encoding="utf-8"), indent=2)
        bad = report(post_condition(req, response))
        return 8 if bad else 0
    sys.stderr.write("REFUSED: unknown command %r\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
