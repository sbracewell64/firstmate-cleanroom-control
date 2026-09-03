# Live relaunch 1 - FAILED - 2026-09-03T21:16Z (immutable adverse evidence for control #8)

Sequence, from the clean-room Herdr session's own server log (excerpt beside this file):
- 21:15:51Z  server shutdown (captain's server stop); session persisted with each pane's Claude session id (`agent_session`, source `herdr:claude`).
- 21:16:26Z  new server started by the Desktop launcher (`enter-firstmate.sh` -> `ensure_session`); `persist.restore` evaluated, workspaces=1.
- 21:16:28Z  Herdr's native resume-on-restore (`[session] resume_agents_on_restore`, default true) typed `claude --resume <persisted id>` into BOTH restored panes: pane 1 = captain console w5:p1 (id 7887031a-...), pane 2 = worker w5:p8 (id 75b088f3-...). Both Claude processes exited within ~1.5 s: `No conversation found with session ID` (rc=1; reproduced by the probe file).
- The launcher's `console_record_pane` saw the recorded pane w5:p1 still present and reported the console as `existing`; `enter-firstmate.sh --console` (cold-start arm, style settings, permission policy) never ran, so `state/cold-start-arm.log` does not exist and no `supervision:` line was printed.
- 21:18:53Z  captain's manual temporary recovery: bare `claude` in w5:p1 (exited 21:22:31Z), then 21:22:34Z `claude --dangerously-skip-permissions` in w5:p1 = the recovery session that wrote this evidence. Neither is the #8 live proof.

Worker pane w5:p8 scrollback (captured 2026-09-03T21:3xZ) shows the same native resume failure for the control9 worker.
This directory is never overwritten; the repaired relaunch is recorded beside it.
