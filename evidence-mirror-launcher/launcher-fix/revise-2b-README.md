# Control #8 REVISE 2b - post-attach convergence (after live relaunch 2, 2026-09-03T21:50Z)

Relaunch 2 (immutable evidence beside this directory: live-relaunch-2-2026-09-03T2150Z-PARTIAL) showed why the inline convergence
could not act: a headless Herdr server evaluates the restore at start but spawns the restored console pane's terminal only when a
TUI client attaches (server log: `client connected` 21:50:44.427, `pane.spawn.start` pane 1 at 21:50:44.446, 13 s after app.startup),
and the launcher attaches LAST. The inline convergence saw the pane unreadable for its whole 12 s settle window (`class=absent action=leave`),
then Herdr's native resume ran `claude --resume 455c55cd...` unopposed: no cold-start arm, no --settings, no --dangerously-skip-permissions,
hence `auto mode on`. The canonical argv was never used on that run.

Fix (this directory): when THIS launch started the server, the convergence is delegated to one detached `--converge-owner <ws> <pane>`
(setsid, same idiom as the cold-start arm owner) started immediately before `exec herdr --session`; it waits up to 120 s for the pane to
materialize, lets the restore settle, waits up to 60 s for a just-restored harness's composer to read empty, then applies exactly the same
classification: stranded shell -> console contract typed into the pane; native harness -> `/exit` through the upstream verified submit core,
then `--console --resume <same id>`. Scratch proof (`proofs/converge-owner.log`, `proofs/converge-pane.out`): a bare `claude` (footer
`auto mode on`) in a scratch pane was classified foreign-harness with an empty composer, exited, and relaunched through `--console`;
the relaunch tried the same session id (no transcript for a zero-turn session -> fresh), and the pane ended with
`bypass permissions on` under `claude --dangerously-skip-permissions --settings <clean-room settings>`.
