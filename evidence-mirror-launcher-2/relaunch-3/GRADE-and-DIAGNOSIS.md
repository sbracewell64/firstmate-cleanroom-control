# Live relaunch 3 - 2026-09-03T22:51Z - L7 FAIL (immutable evidence, control #7/#8)

Browser Sol sealed L7 FAIL on #8 (comment 5533433558): the repaired console reached `bypass permissions on`,
but for >25 min with the issue #11 ruling already waiting, no handling turn began without a Captain message.
Overall run = FAIL regardless of L1-L6, per the pinned policy. L1-L6 graded here from exact records; not rerun.

## L1-L6 (this run, from records)

| # | Predicate | Grade | Basis (OBSERVED unless noted) |
|---|---|---|---|
| L1 | native-restore convergence through the canonical contract | PASS | console-launch.log 22:51:08-24: converge-owner materialized pane w5:p1, class=foreign-harness composer=empty action=converge, exited the native `claude --resume`, restarted the console contract (pid 4047204), relaunched same session id |
| L2 | canonical watcher armed before the harness | PASS (with defect) | cold-start-arm.log 22:51:24: healthy=1 watcher 2589225 beacon 7s BEFORE the harness exec. DEFECT: that watcher was a DEFERRED pre-relaunch generation-32 orphan, not one this launch armed - the direct cause of L7 |
| L3 | FirstMate bootstrap runs under the console contract | CNO | the launch WAS under the contract (launch_stage=launching, pid 4047204, correct argv - OBSERVED); the session-start digest itself is turn-gated and no turn ran, so its execution is inseparable from L7 |
| L4 | clean-room NM_HOME reaches the restarted server/panes | PASS | console env and launcher export NM_HOME=<home>/no-mistakes; server/pane environ carry it |
| L5 | Fable 5.1 configured identity | PASS (INFERRED) | config model claude-fable-5-1 and this resumed session is Fable 5.1; the pane banner was not screen-captured this run (that instrument CNO) |
| L6 | bypass footer + recorded dangerous-skip argv | PASS | Sol OBSERVED `bypass permissions on` in the footer; captain-console.json argv carries `--dangerously-skip-permissions --settings <clean-room settings>` |
| L7 | zero-Captain-turn control intake | FAIL | sealed by Browser Sol; diagnosed below |

## L7 diagnosis - which seam, with timestamps

Sol's five candidate stages, resolved against records:

1. watcher never armed - NO. A healthy watcher (pid 2589225, beacon fresh) existed at 22:51:24 (cold-start-arm.log).
2. watcher armed but no poll/capture - NO. It polled and CAPTURED result seq 13 at 23:26:51Z (procevent-seq13.result.json mtime; .watch-deliveries.log names 2589225).
3. result captured but wake not queued - NO. The wake is durably queued (state/.wake-queue holds seq 84/85/86, all the seq-13 check).
4. **wake queued but not delivered/submitted - YES. This is the seam.** `cold_arm_deliver` ran 0 times (grep count 0 in cold-start-arm.log); no `FIRSTMATE_OP: v1 watcher:` line was ever typed into the console composer.
5. submitted but Claude did not start a turn - NO. Nothing was submitted.

### Root cause (OBSERVED)

At 22:51:24 the launcher's cold-start step (`cold_arm_ensure`) found an OPEN auto-arm claim: generation 32,
owner pid 2588837, watcher 2589225 healthy (beacon 7s). Decision: `defer-open-claim` - "that owner delivers
its close to this console." (cold-start-arm.log line 8-9.)

But generation 32's owner 2588837 is a **Stop-hook auto-arm** (`fm-claude-stop-autoarm.sh`, from the ledger's
identity line), armed at ~22:28Z by the PRE-relaunch harness incarnation (pid 219960, relaunch 2's console).
A Stop-hook auto-arm delivers its actionable close ONLY by **exit-2 rewake into its own harness**
(fm-claude-stop-autoarm.sh header: "the harness delivers the collected stderr only on exit 2"). That harness
(219960) was killed by the Captain's server stop at 22:50:45. Its auto-arm owner and watcher survived detached
and kept beating, but their exit-2 delivery target no longer existed.

So when watcher 2589225 captured seq 13 at 23:26:51 and closed, owner 2588837 exited 2 to rewake a dead harness;
nothing reached the NEW console (harness 4072253). The one path that CAN deliver to a freshly-resumed, turn-idle
console - the launcher's own cold-start owner, which types a `watcher`-kind operational input into the composer
(`cold_arm_deliver`) - had stood down under `defer-open-claim`. Watcher 2589225 died right after (last beat 23:27:03Z).

One line: **`defer-open-claim` deferred zero-turn delivery to a pre-relaunch Stop-hook generation whose only
delivery mechanism (exit-2 rewake) targets a harness the relaunch had already killed; the launcher's own
typed-composer delivery owner - the sole path to a turn-idle resumed console - stood down.**

### Why the two prior fixes did not cover this

Revise-2/2b fixed the CONVERGENCE (getting the console under the contract), which is why L1/L6 pass now. They did
not touch the DELIVERY owner selection. The trap needs both: a console correctly relaunched under the contract
(so cold-start runs and sees the ledger) AND a surviving orphan Stop-hook claim from the prior incarnation.
Relaunch 2 never ran the contract at all, so it never hit this branch.
