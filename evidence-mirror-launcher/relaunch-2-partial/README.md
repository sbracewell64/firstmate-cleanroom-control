# Live relaunch 2 - 2026-09-03T21:50Z - PARTIAL (immutable evidence for control #8 / #7)

Timeline, all OBSERVED from the clean-room Herdr server log, the launch log, the watcher cycle ledger, and this session's own transcript timestamps:
- 21:50:08Z  the previous console's turn ended; its Stop hook armed watcher pid 180869 (cycle ledger).
- 21:50:15Z  captain stopped the Herdr server; that watcher cycle ended `arm-interrupted` (it lived in the console's process tree). From here until 22:09:10Z NO watcher cycle ran (watch-cycles file).
- 21:50:31Z  Desktop launcher started the server; `persist.restore` evaluated; the worker pane (pane 2) spawned headlessly, the console pane (pane 1) did NOT.
- 21:50:32-44Z  launcher inline convergence: `converge: restore did not settle on pane w5:p1 within 12s (last: unreadable)` then `class=absent ... action=leave` (console-launch.log). No cold-start-arm entry: `--console` never ran on this launch.
- 21:50:44.427Z  TUI client attached; 21:50:44.446Z pane 1 terminal spawned (pid 219863); 21:50:45Z Herdr's native resume ran `claude --resume 455c55cd-6938-4493-88a4-c5c60905e751` (pid 219960, parent 219863) - no `--dangerously-skip-permissions`, no `--settings`; footer `auto mode on`.
- 21:53-21:56Z  Browser Sol posted new rulings on #7 and #8 (venue timestamps). Nothing captured them: no watcher was running, so no process-event poll ran, no result was stored, no wake was queued (wake queue empty at the resume's session start: `--ack-through 0`; last capture before the gap: seq 9 at 21:49:07Z; next capture: seq 10 at 22:09:14Z).
- 21:58:13Z  CAPTAIN NUDGE (manual): "I've already stopped the herdr server and relaunched. Check browser sol's recent post for 7 and 8." This was the first turn of the resumed session; FirstMate's session start ran inside it. Zero-Captain-turn control intake is therefore NOT_PROVED on this run - and could not have passed, because no watcher existed to capture anything before the nudge.
- 22:09:10Z  first watcher cycle after the gap, armed by the Stop hook at the end of the nudge-handling turn; it captured seq 10 (Sol's 21:53-22:02Z comments) at 22:09:14Z and woke FirstMate at 22:09:30Z.

Predicates for this run:
- native restore observed: YES (pane 1 native `claude --resume`, succeeded because the transcript existed).
- launcher convergence through the canonical contract: FAILED (inline convergence ran before the pane existed; separate #8 defect, fixed in revise-2b).
- watcher-before-harness: FAILED (no arm; no watcher 21:50:15-22:09:10Z).
- canonical FirstMate bootstrap: PARTIAL - the session-start digest ran, but only because the natively resumed conversation's SessionStart hooks fired; not under the launcher contract.
- clean-room NM_HOME inheritance by the restarted server and its panes: YES (server and pane shell environ carry NM_HOME=/home/OPERATOR/.firstmate-cleanroom/no-mistakes).
- Fable 5.1 identity: YES (resumed session banner; global model setting) - inference from the same account/settings, the pane's own banner was not captured.
- --dangerously-skip-permissions / bypass footer: FAILED (argv lacked it; `auto mode on`).
- zero-Captain-turn intake: NOT_PROVED (manual nudge at 21:58:13Z preceded any capture).
- delivery seam (captured result not turned into a turn): NOT IMPLICATED - no result existed to deliver; the cold-start owner that would type a watcher wake never started because the contract never ran.
