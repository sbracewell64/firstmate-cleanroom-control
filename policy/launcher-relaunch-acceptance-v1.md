# Acceptance policy: final clean-room launcher relaunch (control #7 ruling 3 + control #8 REVISE 2/2b)

    policy_id:     cleanroom-launcher-relaunch-acceptance-v1
    ruled_by:      control issue #8 (REVISE, REVISE 2, PROCEED_WITH_CONDITIONS on native resume, relaunch-2 addenda)
                   and control issue #7 (ruling_3 IMPLEMENT_PRIVATE_RUNTIME_NOW, live permission-mode PROCEED_WITH_CONDITIONS)
    scope:         ONE final real Herdr server stop + Desktop relaunch of the clean-room captain console, as the combined
                   #7/#8 live acceptance run. Transport and launcher/session-recovery semantics only. Proof A, Proof B,
                   the architecture review and control #10 stay held by their existing sequencing.
    pinned:        before the request envelope is compiled. Write-once.

## What is being asked

Browser Sol is asked to dispose the request: ADOPT_OPTION A authorizes FirstMate to ask the Captain for exactly one
server stop + Desktop relaunch and to grade it against the predicates below; ADOPT_OPTION B names one further scratch
proof or repair that must be observed BEFORE that relaunch; ADOPT_OPTION C holds the relaunch and names the reason.
INSUFFICIENT_EVIDENCE names the failing predicate. A NO_ANSWER at `expires_at` is a preserved terminal: nothing is
relaunched and nothing is graded.

## Acceptance predicates for the relaunch (three-valued, all measured, none skipped)

| # | Predicate | Instrument |
|---|---|---|
| L1 | Herdr's native restore is observed if it occurs, and the launcher converges the console pane through the canonical console contract (stranded shell restarted, or natively resumed harness exited and relaunched with the same session id) | console pane capture; `state/console-launch.log` `converge:` lines; `state/captain-console.json` `launch_mode`/`resume_id` |
| L2 | the canonical watcher is armed BEFORE the harness starts (`supervision: watcher started|attached ... cold-start owner`) | console pane capture; `state/cold-start-arm.log`; watcher lock pid alive with a fresh beacon |
| L3 | FirstMate bootstrap (session-start digest) runs under the console contract, not merely because a resumed conversation's hooks fired | `state/captain-console.json` `launch_stage=launching` before the harness; digest present in the console |
| L4 | clean-room `NM_HOME` reaches the restarted Herdr server and its panes | server and pane process environment |
| L5 | the console is Fable 5.1 with the configured profile | console banner |
| L6 | the console footer reads `bypass permissions on`, never `auto mode on`; argv recorded in the console record carries `--dangerously-skip-permissions` and the clean-room `--settings` | console pane capture; `state/captain-console.json` `argv` |
| L7 | zero-Captain-turn control intake: a commission or ruling already waiting on the venue is captured and becomes a handling turn with no Captain message | `state/procevent-inbox/<source>.<seq>.result` timestamps versus the first Captain message; console pane capture of the typed watcher wake |

Each predicate is reported as observed-good, observed-bad or could-not-observe with its evidence; none is narrowed.

## Fold

All seven observed-good -> combined #7/#8 live acceptance PASS; FirstMate reports it and the sequencing holds
(Proof A next) are for Browser Sol to lift. Any observed-bad -> FAIL on that predicate; the run is preserved as
immutable evidence and the defect is reported before any further relaunch is requested. could-not-observe on L7
alone (no venue item happened to be waiting) leaves L7 unmeasured and is reported as such, never as a pass.
