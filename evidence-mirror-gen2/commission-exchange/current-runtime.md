# Current runtime — the machine, how to start it, and what it shares

    generated:      2026-09-02
    projection_of:  artifacts/baseline/ and runtime/  (this file is NOT authoritative; see ../README-FIRST.md)
    drawn_from:
      - artifacts/baseline/runtime-baseline.md        (and its machine twin runtime-baseline.json)
      - artifacts/baseline/ce-isolation-baseline.md   (and ce-isolation-baseline.json)
      - artifacts/baseline/pristine-baseline-20260901.md
      - artifacts/baseline/testrun-portable-parallel-1.log
      - runtime/firstmate/  (the live home: data/, state/, config/, enter-firstmate.sh)
      - runtime/ce-config/  (the scoped Compound Engineering config)
    caution: version numbers and liveness facts below were true when the baselines
             were recorded (2026-09-01 / 2026-09-02). Re-check before acting on one.

---

## 1. The layout

| | |
|---|---|
| Clean-room root | `E:\FirstMate-Cleanroom\` — WSL `/mnt/e/FirstMate-Cleanroom` — **not a git repository** |
| Code root (read-only, pristine) | `upstream/firstmate` @ `41d0ab3910ece4e90db0194f756437b3abe8ab8f`, branch `main` |
| Operational home (`FM_HOME`) | `runtime/firstmate` — a **primary** home (no secondmate marker) |
| Qualification tool | `tools/no-mistakes` @ `0af0be63…` (v1.61.0); **isolated binary** at `tools/bin/no-mistakes` |
| Execution substrate | `tools/machinist` @ `75964acb…` (v0.4.0-4) |
| Planning/review plugin | `tools/compound-engineering` @ `cd313380…` (v3.24.0), installed **only** into `runtime/ce-config` |
| Host | WSL2 (Linux 6.18.33.2-microsoft-standard-WSL2) over Windows; E: has 932G, 727G free |

Every checkout is an independent git repository with its own provenance.

## 2. How to start it

The upstream at this pin ships **no Windows launcher and no documented recipe for
a primary home at a separate `FM_HOME`** — its Quick Start assumes the home *is*
the code root. So the entry point is authored, and it lives in the **home**
because the code root is read-only:

    /mnt/e/FirstMate-Cleanroom/runtime/firstmate/enter-firstmate.sh

It exports `FM_HOME`, prepends the clean-room tools bin and `~/.local/bin`, cds
to the code root, and execs the harness. `FM_ENTRY_DRY_RUN=1` prints the resolved
launch without starting it.

**Recommended: start Herdr first, then run the entry script inside a Herdr pane.**
That makes crew placement resolve from the launcher's own workspace identity and
completely sidesteps the shared workspace-label problem in §4.

One-off from Windows Terminal, PowerShell, or Run:

    wt.exe --window new-tab --title "FirstMate Cleanroom" wsl.exe -d Ubuntu -- bash -lc /mnt/e/FirstMate-Cleanroom/runtime/firstmate/enter-firstmate.sh

As a Windows Terminal profile: `"commandline": "wsl.exe -d Ubuntu -- bash -lc /mnt/e/FirstMate-Cleanroom/runtime/firstmate/enter-firstmate.sh"`, `"startingDirectory": null`.

**A login shell is required** — `bash -c` cannot find the harness, `bash -lc` can,
because `~/.local/bin` is where every harness lives. And an inline `$`-bearing
script passed straight to `wsl.exe` is **unreliable**: substitutions were observed
to be lost before bash saw them. That is exactly why the entry is a script file
and not an inline command.

## 3. What is verified working

A full `fm-session-start.sh` runs end to end against this home: it takes the
home's own lock, drains an empty wake queue, renders the supervision block, prints
the fleet and context digests, and completes its deferred network stage clean
(gh-auth 559ms, fleet-sync 1016ms, no actionable finding). The verification lock
was **released** afterwards, so the captain's first real session starts on a free
lock.

Files the home carries: `data/backlog.md` (empty skeleton), `data/projects.md`
(empty registry), `.tasks.toml` (**a necessary adaptation** — FirstMate runs
tasks-axi with cwd = the home, not the code root, so the tracked config is never
discovered), and `enter-firstmate.sh`. `captain.md`, `learnings.md` and
`secondmates.md` were deliberately **not** created, because upstream defines
ABSENT as meaningful for each — and the digest reported them ABSENT exactly as
intended.

## 4. What is shared with the other, **live** home — and why that matters

**Correct a premise first:** `~/kun-agent-workspace` is **not retired**. When the
baseline was taken it held a live session (pid 321, 8 days uptime), its watcher
beacon had been touched 34 seconds earlier, and it had ten or more live crew
lanes. **Every collision below is a live risk, not a dormant one.**

**Verified NOT shared:** the session lock (per-`FM_HOME` file); `data/`, `state/`,
`config/`, `projects/`; FirstMate's own Claude hooks (project-scoped, so this
home's session loads the clean-room checkout's scripts); the treehouse pool.

**Shared, ranked:**

| # | Surface | Risk | The consequence |
|---|---|---|---|
| 1 | **Herdr workspace label** | **HIGH** | The pinned upstream resolves **every** primary home to the constant label `firstmate`, with no discriminator — unlike the cmux and zellij backends. A workspace with that label is live and belongs to the other home. Spawning from **inside** a Herdr pane is safe. Spawning from **outside** with one such workspace present **adopts it** — this home's workers would appear inside the other home's workspace. Recovery keeps first-match-by-label regardless of launcher identity. |
| 2 | **`~/.claude/skills/no-mistakes/SKILL.md`** | **HIGH** | One user-global file loaded identically by both homes. Whether it carries v1.61.0 guidance is **could-not-observe** (no version marker in the file). The host-wide CLI is v1.40.3, so the other home reads newer instructions than its binary implements. |
| 3 | **`~/.local/bin` binaries** | **HIGH for remediation** | claude, codex, pi, herdr, treehouse, tasks-axi, quota-axi, lavish-axi, gh-axi, no-mistakes are single host-wide installs. Upgrading the three floor-failing axi tools changes the live home's tools mid-flight. |
| 4 | **`~/.no-mistakes/` root, daemon, socket, sqlite** | **HIGH** | One daemon (v1.40.3) serving every lane. A separate clean-room daemon runs v1.61.0 against its own root, but `--root` is not a documented public flag and FirstMate calls plain `no-mistakes axi run` with no root threading — so a v1.61.0 client on PATH would default to the **shared** root and its v1.40.3 daemon. **That skew is unresolved.** **Never stop, restart or update the shared daemon — it kills other lanes' in-flight runs.** |
| 5 | Herdr server, socket, `default` session | MEDIUM | one server, one session, 12 live workspaces, addressed by both homes |
| 6 | tmux fallback session name | MEDIUM (latent) | constant session name `firstmate`; colliding task ids would collide on window names |
| 7 | `~/.claude/settings.json` | LOW, observed-good | none of its hooks resolve `FM_HOME`, so they do not cross-wire the homes |
| 8 | `gh` authentication | LOW, observed-good | one account, `sbracewell64`; both homes act as the same GitHub identity |

## 5. Version floors — three are below

| Tool | Floor at the pin | Installed | Verdict |
|---|---|---|---|
| no-mistakes | 1.46.0 | 1.40.3 | **cleared** by PATH-prepending the clean-room tools bin (v1.61.0) |
| tasks-axi | 0.2.4 | 0.2.3 | **below** |
| lavish-axi | 0.1.46 | 0.1.43 | **below** |
| quota-axi | 0.1.29 | 0.1.16 | **below** |
| gh-axi | 0.1.29 | 0.1.29 | at floor |

Harnesses present: claude 2.1.258, codex 0.146.0, pi 0.81.1. Herdr client/server
0.7.5, protocol 17 — which **meets** the spawn, events and workspace-move floors
and is **below** the presentation floors (protocol 19 / version 0.8.0), so this
home gets the flat per-home layout rather than one workspace per task.

The three below-floor tools are the **unavoidable local setup effect** and their
resolution is a captain decision (`current-decisions.md` §3).

## 6. The filesystem, and two real consequences

`/mnt/e` is 9p / DrvFs. Probed directly:

| Property | Result | Consequence |
|---|---|---|
| `chmod` | **no-op** — everything reads `0777` | The mode-sensitive call sites at this pin test *readability*, which `0777` satisfies, so it is currently non-blocking. But **`fm-check-register.sh` refuses** on this mount (it requires exactly `700`), so the authenticated watcher mechanism is unavailable here — a documented listener config plus a bounded poll ran instead, and **which one ran is recorded rather than implied**. Write-once on the frozen schema is likewise enforced by **digest comparison**, not by permission. |
| symlinks | supported | fine |
| `flock` | supported | session and wake locks work |
| `mkfifo` | **fails** every attempt | non-blocking: the one Herdr fifo is created under `TMPDIR`, which is ext4 |
| exec bit | honored | scripts run |

## 7. The pristine checkout is genuinely pristine

Before and after: HEAD identical, tree identical, **485 files outside `.git`,
byte-for-byte identical set**, `git status --porcelain` empty **and** the
`--ignored` sweep empty too. Nothing was installed, upgraded, started or stopped
on the host; no daemon was restarted; no npm global changed.

## 8. Upstream test-suite baseline — attributed

One lane was run against the pinned upstream: **11 scripts executed, 3 failed,
1 gate-skip, 267s**, runner exit 1. All three failures are **host-environment
gaps, not upstream defects** — observed:

1. `fm-captain-hold-lifecycle` — teardown **did** refuse and preserve metadata,
   but worded the refusal through its tasks-axi feature guard because this host
   runs 0.2.3; the test greps for the other wording.
2. `fm-test-run` — needs ruby to parse the CI workflow as YAML; ruby is absent.
3. `fm-lint` — the lint owner pins a shellcheck version; host gap, not fully
   isolated.

**No observed upstream defect at this pin in this lane.** Reproducibility needs
host provisioning (ruby, tasks-axi ≥ 0.2.4, pinned shellcheck), after which the
lane should be re-run to prove green. The other two lanes have not been run.

## 9. Compound Engineering, scoped

CE is installed **only** into `runtime/ce-config`, from the pinned local
checkout — 33 skills, 309 reference files, **zero agents, zero hooks, zero MCP
servers, zero binaries**. It is a prompt corpus, not a runtime.

The install is a real copy, not a link: the installed snapshot's tree digest is
byte-identical to the pinned source's and the recorded `gitCommitSha` is the pin
itself. The host `~/.claude` was probed before, after, and after every live
scoped session and is **unchanged** — and that result is trustworthy *because*
the identical probe returns non-zero CE hits against the scoped dir as its own
positive control. The probe is kept and re-runnable at
`runtime/ce-config/cleanroom/host-isolation-probe.sh`.

**Cross-model review / egress is OFF**, enforced at the environment layer in the
scoped settings and tested at the chokepoint with a red negative control. The
documented switch itself is a model-compliance instruction and was **never
observed doing anything** — which is precisely why the environment layer exists.
The operating policy is at `runtime/ce-config/cleanroom/POLICY.md`.

**CE stops at a local commit. It is never the publisher.** Delivery is the
isolated v1.61.0 binary. `lfg` and `ce-commit-push-pr` both exist and are both
**forbidden** here.

**The first-operator surprise worth knowing:** 25 of 33 skills are
model-invocable, so the model can fire several of them *without a slash command*,
and several write files into the repo.

## 10. Could-not-observe, stated as results

- **End-to-end crew placement was never verified.** No worker was spawned in this
  home; the upstream ships no dry-run and no standalone spawn-capability probe.
  What was verified is the read-only capability surface.
- **Whether the spawned Windows Terminal window rendered correctly** — `wt`
  detaches, so the session that opened it could not read it.
- **The CE spine was never run end to end.** `ce-work` was never invoked in either
  mode; everything about its completion behaviour is read from its own skill
  files, not measured.
- **Which process refreshed the host's marketplace timestamp** is unattributed.
- **`permissions.deny` coverage is not enumerated.** One bypass was found and
  reported; the list is not exhaustive.
