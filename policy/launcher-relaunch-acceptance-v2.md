# Acceptance policy: clean-room launcher relaunch, SUCCESSOR v2 (control #8 after relaunch-3 L7 FAIL)

    policy_id:     cleanroom-launcher-relaunch-acceptance-v2
    supersedes:    cleanroom-launcher-relaunch-acceptance-v1 (issue #11, ADOPT_OPTION A; the authorized relaunch ran as relaunch-3 and FAILED L7)
    ruled_by:      control issue #8 post-L7-failure engineering disposition (2026-09-03T23:56Z)
    scope:         ONE new real Herdr server stop + Desktop relaunch of the clean-room captain console, as the combined
                   #7/#8 live acceptance run, ONLY after this successor request is ruled. Transport and launcher/session
                   recovery semantics only. Proof A, Proof B, architecture re-review and control #10 stay held.
    pinned:        before the successor request envelope is compiled. Write-once.

## Why a successor is needed

Relaunch-3 passed L1/L4/L5/L6, was CNO on L3, and FAILED L7: the launcher deferred zero-turn wake delivery to an
open Stop-hook auto-arm generation orphaned by the server stop, whose only delivery path (exit-2 rewake) targeted the
killed harness; the launcher's own typed-composer delivery owner stood down. revise-2c changes the startup predicate:
at cold-start only a LIVE cold-start arm-owner is a valid defer target; a Stop-hook/dead/foreign owner is stale for the
new console, is superseded, and a fresh typed-delivery owner claims the next generation while reusing the singleton
watcher. The subject of THIS request is that revise-2c fix and the relaunch-3 evidence; the fix is proven only in
controlled/scratch conditions, so live L1-L7 composition remains the open question.

## What is being asked

ADOPT_OPTION A authorizes exactly one new real relaunch, graded three-valued against L1-L7 below; ADOPT_OPTION B names
one further scratch proof or repair to observe first; ADOPT_OPTION C holds. INSUFFICIENT_EVIDENCE names the failing
predicate. NO_ANSWER at expires_at is a preserved terminal: nothing is relaunched.

## Acceptance predicates (three-valued, all measured, none skipped; L7 is NOT weakened)

| # | Predicate | Instrument |
|---|---|---|
| L1 | native-restore convergence through the canonical console contract | console pane capture; state/console-launch.log converge: lines |
| L2 | the canonical watcher armed before the harness is one THIS launch owns for delivery, not a deferred prior-incarnation orphan | state/cold-start-arm.log decision (arm or supersede-then-arm, never a bare defer to a stop-hook/dead owner); ledger owner kind = cold-start |
| L3 | FirstMate bootstrap runs under the console contract | captain-console.json launch_stage; digest present in the console |
| L4 | clean-room NM_HOME reaches the restarted server/panes | server/pane environ |
| L5 | Fable 5.1 configured identity | console banner |
| L6 | bypass footer + recorded dangerous-skip argv | console pane capture; captain-console.json argv |
| L7 | zero-Captain-turn control intake: a waiting commission/ruling becomes a handling turn with no Captain message, delivered by the launcher's own typed-delivery owner | procevent result timestamps vs first Captain message; console capture of the typed FIRSTMATE_OP watcher wake; cold_arm_deliver in the log |

## Fold

All seven observed-good -> combined #7/#8 live acceptance PASS. Any observed-bad -> FAIL on that predicate; preserve the
run and diagnose before any further relaunch. L7 could-not-observe only if no commission/ruling happens to be waiting;
never narrowed to a pass.
