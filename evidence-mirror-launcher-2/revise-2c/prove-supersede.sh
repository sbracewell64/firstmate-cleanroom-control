#!/usr/bin/env bash
# Scratch proof of the control #8 revise-2c seam repair, in controlled conditions
# on a temp state dir (no live console, no Herdr): a Stop-hook-named orphan holds
# an open (arming) auto-arm generation with a fresh beacon; the launcher's
# supersede + the upstream claim primitive must let a new owner take gen+1, and
# the orphan must then read as NOT the owner (self-stand-down), while a
# cold-start-owner claim is left deferrable.
set -u
R=/mnt/e/FirstMate-Cleanroom/upstream/firstmate
L=/home/OPERATOR/.firstmate-cleanroom/enter-firstmate.sh
fail() { printf 'not ok - %s\n' "$1" >&2; exit 1; }
pass() { printf 'ok - %s\n' "$1"; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/fm-supersede-proof.XXXXXX") || fail mktemp
trap 'rm -rf "$TMP"; [ -z "${ORPHAN:-}" ] || kill "$ORPHAN" 2>/dev/null; [ -z "${CS:-}" ] || kill "$CS" 2>/dev/null' EXIT
export FM_HOME="$TMP/home"; export FM_CODE_ROOT="$R"
mkdir -p "$FM_HOME/state"
state="$FM_HOME/state"

# Load the launcher's pure helpers (definitions only) and the upstream ledger lib.
# shellcheck disable=SC1090
FM_ENTRY_LIB=1 . "$L" || fail "launcher lib load"
# shellcheck disable=SC1090
. "$R/bin/fm-wake-lib.sh" || fail "wake-lib load"
# The launcher lib load reassigns the hardcoded FM_HOME/FM_CODE_ROOT; re-pin them
# at the temp home so cold_arm_supersede_stale (which reads global FM_HOME) and
# every check below act on this scratch ledger, never the real home.
export FM_HOME="$TMP/home"; export FM_CODE_ROOT="$R"; state="$FM_HOME/state"

# A long-lived process whose argv contains 'fm-claude-stop-autoarm' so
# fm_pid_identity/liveness treat it as a real, live Stop-hook owner.
bash -c 'exec -a "bash /mnt/e/FirstMate-Cleanroom/upstream/firstmate/bin/fm-claude-stop-autoarm.sh" sleep 300' & ORPHAN=$!
sleep 0.3
grep -qa 'fm-claude-stop-autoarm' "/proc/$ORPHAN/cmdline" || fail "orphan argv did not carry the stop-hook name"

# Seed the ledger as gen 32 owned by that orphan, outcome=arming, with the
# orphan's real identity line and a fresh beacon (exactly the relaunch-3 shape).
identity=$(fm_pid_identity "$ORPHAN") || fail "identity for orphan"
printf 'epoch=32 owner_pid=%s outcome=arming updated_at=%s\n%s\n' "$ORPHAN" "$(date +%s)" "$identity" > "$state/.claude-autoarm-epoch"
: > "$state/.last-watcher-beat"   # fresh beacon
fm_autoarm_claim_open "$state" 300 || fail "precondition: the seeded orphan claim must read as OPEN (as it did at 22:51:24)"
pass "seeded a live Stop-hook orphan holding open gen 32 with a fresh beacon (relaunch-3 shape)"

# The probe classifies the owner as a stop-hook, and the launcher decides 'stale'.
kind=$(grep -qa 'fm-claude-stop-autoarm' "/proc/$ORPHAN/cmdline" && echo stop-hook || echo other)
[ "$kind" = stop-hook ] || fail "probe owner-kind classification"
[ "$(cold_arm_claim_deliverable "$kind")" = stale ] || fail "launcher must judge a live Stop-hook claim stale for a cold-start console"
pass "the orphan claim is judged stale-for-this-console (would defer under the OLD launcher, the L7 bug)"

# The repair: supersede the stale claim, then a NEW owner claims gen+1.
out=$(cold_arm_supersede_stale 32 "$ORPHAN")
[ "$out" = superseded ] || fail "cold_arm_supersede_stale returned '$out', want superseded"
grep -q 'outcome=superseded' "$state/.claude-autoarm-epoch" || fail "ledger not flipped to superseded"
fm_autoarm_claim_open "$state" 300 && fail "after supersede the claim must NOT read as open"
pass "supersede flipped gen 32 to superseded; the claim is no longer open"

# A fresh 'launcher owner' now claims the next generation (this is what the
# spawned --arm-owner does after ensure supersedes).
( . "$R/bin/fm-wake-lib.sh"; fm_autoarm_claim_next "$state" 300; rc=$?; [ "$rc" = 0 ] && [ "$FM_AUTOARM_MY_GEN" = 33 ] && echo "CLAIMED $FM_AUTOARM_MY_GEN" || echo "CLAIMFAIL rc=$rc gen=${FM_AUTOARM_MY_GEN:-none}" ) > "$TMP/claim.out" 2>&1
grep -q 'CLAIMED 33' "$TMP/claim.out" || fail "the launcher's own owner could not claim gen 33 after supersede: $(cat "$TMP/claim.out")"
pass "the launcher's own typed-delivery owner claims gen 33 (delivery path restored)"

# The orphan, still alive, now reads as NOT the owner of the current gen -> it
# would stand down at its next close instead of exit-2 into a dead harness.
newowner=$(sed -n 's/^.*owner_pid=\([0-9]*\).*/\1/p' "$state/.claude-autoarm-epoch" | head -1)
[ "$newowner" != "$ORPHAN" ] || fail "the orphan is still the ledger owner after claim"
pass "the orphan is no longer the ledger owner; its next close self-stands-down (no exit-2 to a dead harness)"

# Negative control: a LIVE cold-start arm-owner claim must be left deferrable
# (the launcher must NOT supersede a valid typed-delivery owner).
printf '#!/usr/bin/env bash\nexec sleep 300\n' > "$TMP/enter-firstmate-arm-owner"; chmod +x "$TMP/enter-firstmate-arm-owner"
# argv must contain 'arm-owner' and NOT 'fm-claude-stop-autoarm'
bash -c 'exec -a "enter-firstmate.sh --arm-owner herdr t h" sleep 300' & CS=$!
sleep 0.3
csident=$(fm_pid_identity "$CS") || fail "identity for cold-start owner"
printf 'epoch=40 owner_pid=%s outcome=arming updated_at=%s\n%s\n' "$CS" "$(date +%s)" "$csident" > "$state/.claude-autoarm-epoch"
: > "$state/.last-watcher-beat"
cskind=$(grep -qa 'fm-claude-stop-autoarm' "/proc/$CS/cmdline" && echo stop-hook || (grep -qa 'arm-owner' "/proc/$CS/cmdline" && echo cold-start || echo other))
[ "$cskind" = cold-start ] || fail "cold-start owner classified as '$cskind'"
[ "$(cold_arm_claim_deliverable "$cskind")" = deliverable ] || fail "a live cold-start arm-owner must stay deliverable (never superseded)"
pass "negative control: a live cold-start arm-owner claim stays deliverable and is left to deliver"

echo "all supersede-seam proofs passed"
