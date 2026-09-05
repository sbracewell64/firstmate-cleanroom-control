#!/usr/bin/env bash
# THE canonical outbound emit contract (generation 3, NON-frozen orchestration).
#
# Every transaction that emits an fm-sol-control/v2 request goes through this
# script. It sequences the FROZEN emitter (which creates the venue item
# atomically) with the canonical live-record owner (bin/fsc4-live-record.py):
#
#   1. plan       frozen emitter preflight
#   2. post       frozen emitter creates the labeled issue (caller sets the lane
#                 token FSC2_EMIT_AUTHORIZED_LANE; this script never types it)
#              -- or, with --creation-response <file>, `check` an issue that was
#                 already created (resume of the crash window between creation
#                 and record persistence; the response bytes are re-verified)
#   3. register   the LIVE record state/live/<request_id>.json is derived from the
#                 creation response, persisted durably and re-read
#   4. verify     the record names the request identity AND the created issue
#   5. as-fetched the declared envelope verifier reads the item back
#
# PUBLICATION IS INCOMPLETE UNTIL STEP 4 IS GREEN. A failure at 3 or 4 exits 7
# and prints INCOMPLETE loudly; nothing here ever reports success on a missing
# record. If the issue was created (creation-response.json exists) but this script
# stopped before step 4, re-run with --creation-response; if the response was
# lost, `fsc4-live-record.py reconcile <issue>` rebuilds the record from the
# verified venue envelope.
#
#   fsc4-emit.sh <request.json> <evidence-dir> [--creation-response <file>]
set -euo pipefail
G="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
B="$G/bin"
[ $# -ge 2 ] || { echo "usage: fsc4-emit.sh <request.json> <evidence-dir> [--creation-response <file>]" >&2; exit 2; }
REQ="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; EV="$2"; shift 2
mkdir -p "$EV"; EV="$(cd "$EV" && pwd)"
RESP="$EV/creation-response.json"; MODE=post
while [ $# -gt 0 ]; do
  case "$1" in
    --creation-response) RESP="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; MODE=resume; shift 2 ;;
    *) echo "REFUSED: unknown argument $1" >&2; exit 2 ;;
  esac
done
incomplete() {
  echo "" >&2
  echo "################################################################" >&2
  echo "# PUBLICATION INCOMPLETE: $1" >&2
  echo "# no verified live record -> rulings on this request CANNOT be captured" >&2
  [ -f "$RESP" ] && echo "# issue was created; resume: fsc4-emit.sh $REQ $EV --creation-response $RESP" >&2
  echo "# or reconcile from the venue: fsc4-live-record.py reconcile <issue-number>" >&2
  echo "################################################################" >&2
  exit 7
}
ambiguous() {
  echo "" >&2
  echo "################################################################" >&2
  echo "# PUBLICATION INCOMPLETE: the frozen emitter exited non-zero and recorded NO creation response." >&2
  echo "# The forge MAY still have created the item (timeout / partial read). Do NOT re-post blindly:" >&2
  echo "#   check the venue for an issue carrying request $RID; if it exists:" >&2
  echo "#   fsc4-live-record.py reconcile <issue-number>   (record derived from the verified envelope)" >&2
  echo "#   only if no such issue exists, re-run this emit." >&2
  echo "################################################################" >&2
  exit 8
}
RID=$(jq -r .request_id "$REQ")

echo "== emit 1. plan (frozen emitter preflight) =="
(cd "$B" && python3 fsc4-emit-request.py plan "$REQ") | tee "$EV/plan.txt"

if [ "$MODE" = post ]; then
  echo "== emit 2. post through the frozen emitter (lane token supplied by the caller) =="
  [ -f "$RESP" ] && { echo "REFUSED: $RESP already exists; the issue may already be created. Use --creation-response $RESP" >&2; exit 6; }
  (cd "$B" && python3 fsc4-emit-request.py post "$REQ" "$RESP") | tee "$EV/emit.txt" \
    || { [ -f "$RESP" ] && incomplete "frozen emitter post-condition failed after creation" || ambiguous; }
else
  echo "== emit 2. resume: re-check the existing creation response through the frozen emitter =="
  (cd "$B" && python3 fsc4-emit-request.py check "$REQ" "$RESP") | tee "$EV/emit-check.txt" || incomplete "creation response does not pass the frozen post-condition"
fi
NUM=$(jq -r .number "$RESP"); URL=$(jq -r .html_url "$RESP")

echo "== emit 3. register the LIVE outbound record (canonical owner) =="
(cd "$B" && python3 fsc4-live-record.py register "$REQ" "$RESP") | tee "$EV/register-live.txt" || incomplete "live record not persisted"

echo "== emit 4. verify the live record against request identity and created issue =="
(cd "$B" && python3 fsc4-live-record.py verify "$RID" --issue "$NUM") | tee "$EV/verify-live.txt" || incomplete "live record does not verify"

echo "== emit 5. verify as fetched (declared verifier) =="
(cd "$B" && python3 fsc4-verify-envelope.py issue "$NUM") | tee "$EV/verify-as-fetched.txt" \
  || { echo "REFUSED: as-fetched verification not green (record IS complete; investigate the venue item)" >&2; exit 6; }
echo "== emit complete: request $RID issue #$NUM $URL; live record verified =="
