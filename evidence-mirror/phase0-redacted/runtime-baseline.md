# Clean-room FirstMate runtime baseline

Phase 0 Track 1, under the Captain's 2026-09-02 Phase 0 directive.
Produced 2026-09-01 21:36 -0400 by task `cleanroom-runtime-env`.
Machine-readable twin: [`runtime-baseline.json`](runtime-baseline.json).

Every claim below is graded **observed-good**, **observed-bad**, or **could-not-observe**.
A verification that could not run is could-not-observe, never a pass.

---

## 1. Bottom line

The environment is **online and usable**. A full `fm-session-start.sh` runs end to end against the new
home: it takes the home's own lock, drains an empty wake queue, renders the Claude supervision block,
prints the fleet and context digests, and completes its deferred network stage clean.

Four things are not clean, and none of them is a defect in the setup itself:

1. Three host tools are **below the pinned upstream's version floors** and are shared with the other,
   currently **live** FirstMate home. Fixing them changes that home's tools mid-flight.
2. Herdr resolves **every** primary home to the constant workspace label `firstmate`. A workspace with
   that label is live right now and belongs to the other home.
3. The brief's premise that `~/kun-agent-workspace` is *retired* is **wrong** - it is running.
4. No crew was spawned, so end-to-end spawn placement is **could-not-observe**.

---

## 2. What was built

| | |
|---|---|
| Code root (read-only) | `/mnt/e/FirstMate-Cleanroom/upstream/firstmate` |
| Pinned at | `41d0ab3910ece4e90db0194f756437b3abe8ab8f` - `fix: surface inbound Relay media to responding agents (#3442)`, 2026-09-01 |
| Branch | `main`, tracking `origin/main` (`https://github.com/kunchenguid/firstmate`) |
| Operational home (`FM_HOME`) | `/mnt/e/FirstMate-Cleanroom/runtime/firstmate` |
| Role | primary home (no `.fm-secondmate-home` marker) |
| Contract followed | `docs/configuration.md` section **FM_HOME** @41d0ab39 |

### The supported path, and where it ran out

The upstream ships **no documented recipe for a primary home at a separate `FM_HOME`**. Its Quick Start
is "clone the repo, launch a harness in it", where the home *is* the code root. `bin/fm-home-seed.sh`
exists but provisions **secondmate** homes - it writes `.fm-secondmate-home`, which would have made this
a second mate rather than a primary. So the layout follows the `FM_HOME` contract directly:
scripts keep coming from the code root; `data/`, `state/`, `config/`, `projects/` come from the home.

### Files this task authored in the home

| Path | SHA-256 | Why |
|---|---|---|
| `data/backlog.md` | `f74c5faf4593…` | tasks-axi markdown target; empty `## In flight` / `## Queued` / `## Done` skeleton |
| `data/projects.md` | `cd8838df9226…` | empty project registry, with the `bin/fm-project-mode.sh` line format in a comment |
| `.tasks.toml` | `c5ea09bba244…` | **necessary adaptation.** FirstMate runs tasks-axi with cwd = the data directory's parent (this home), not the code root, so the tracked `.tasks.toml` is never discovered. This copy preserves the upstream defaults (`archive = data/done-archive.md`, `done_keep = 10`). |
| `enter-firstmate.sh` | `030b5ce00be1…` | captain entry point; see section 5 |

`data/captain.md`, `data/learnings.md`, `data/secondmates.md` were deliberately **not** created.
Upstream defines ABSENT as meaningful for each (built-in defaults / created lazily / none registered),
and the session digest reported them as ABSENT exactly as intended.

### Files upstream created on the first locked start

`config/startup-memory-budget` = `7500` (`0d5f578726…`), plus eleven `state/` records including
`.session-start-complete`, `.wake-queue`, `.startup-network.*`, `home-summary.json`, `terminal-outcomes/`.

---

## 3. Bring-up evidence — observed-good

```
cd /mnt/e/FirstMate-Cleanroom/upstream/firstmate
FM_HOME=/mnt/e/FirstMate-Cleanroom/runtime/firstmate bin/fm-session-start.sh
```

| Stage | Result |
|---|---|
| Lock | `lock acquired: harness pid 784718` at `<home>/state/.lock` |
| Bootstrap | herdr auto-detected; four `MISSING:` version-floor lines (section 4) |
| Wake queue | drained, empty |
| Supervision | one operating block rendered for primary harness `claude` |
| Fleet digest | backlog listing rendered (compact fallback, tasks-axi incompatible); no live work |
| Context digest | `projects.md` printed; `secondmates.md`, `captain.md`, `captain-shared.md`, `learnings.md` correctly `ABSENT` |
| Deferred network | completed in 2s - gh-auth 559ms, secondmate-liveness 11ms, secondmate-sync 98ms, handoff-delivery 2ms, fleet-sync 1016ms. No actionable finding. |

The verification lock was **released** afterwards, so the captain's first real session starts on a free
lock rather than inheriting one that names a since-dead worker.

### Host filesystem semantics — the home lives on a Windows drive

`/mnt/e` is 9p / DrvFs. Probed directly:

| Property | Result | Consequence |
|---|---|---|
| `chmod` | **no-op** - every file and directory reads `0777` | observed-bad, currently **non-blocking**: the mode-sensitive call sites at 41d0ab39 (`fm-fleet-snapshot.sh:866`, `fm-pr-lib.sh:216`, `fm-config-inherit-lib.sh:96`) test *readability* (`& 0444`), which `0777` satisfies. No world-writable refusal exists in `bin/`. The `chmod 0600` / `chmod 0700` writes all exit 0 and silently do nothing. |
| symlinks | supported | fine |
| `flock` | supported | session and wake locks work |
| `mkfifo` | **fails** (`EEXIST` every attempt) | non-blocking: the one Herdr fifo (`bin/backends/herdr.sh:3318`) is created under `${TMPDIR:-/tmp}`, which is ext4 |
| exec bit | honored | scripts run |

---

## 4. Toolchain — versions and floors

**Harnesses present:** claude `2.1.258`, codex `codex-cli 0.146.0`, pi `0.81.1`.
**Absent:** grok, pi-signed, opencode, cursor-agent, kimi, muse.

**Herdr:** binary `/home/OPERATOR/.local/bin/herdr`, client **0.7.5**, server **0.7.5**, protocol **17**,
compatible `yes`, socket `/home/OPERATOR/.config/herdr/herdr.sock`, session `default` (running).

**GitHub:** `gh 2.96.0`, logged in to `github.com` as **`sbracewell64`**, scopes `gist, read:org, repo,
workflow`. observed-good.

**Other:** tmux 3.6, git 2.53.0, jq 1.8.1, treehouse v2.1.0 (v2.3.0 available).

### Version floors — observed-bad

| Tool | Floor @41d0ab39 | Host installed | Verdict |
|---|---|---|---|
| no-mistakes | 1.46.0 | 1.40.3 | **below** → cleared by PATH-prepending `/mnt/e/FirstMate-Cleanroom/tools/bin` (**v1.61.0**) |
| tasks-axi | 0.2.4 | 0.2.3 | **below** |
| lavish-axi | 0.1.46 | 0.1.43 | **below** |
| quota-axi | 0.1.29 | 0.1.16 | **below** |
| gh-axi | 0.1.29 | 0.1.29 | at floor |

Floor owners: `bin/fm-bootstrap.sh:893,901,902`, `bin/fm-tasks-axi-lib.sh:37`, `bin/fm-quota-axi-lib.sh:12`.

Verified directly:

```
$ FM_BOOTSTRAP_DETECT_ONLY=1 FM_HOME=<home> bin/fm-bootstrap.sh
MISSING: no-mistakes …   MISSING: lavish-axi …   MISSING: quota-axi …   MISSING: tasks-axi …

$ PATH=/mnt/e/FirstMate-Cleanroom/tools/bin:$PATH  … same command
MISSING: lavish-axi …   MISSING: quota-axi …   MISSING: tasks-axi …
```

**The remaining three are the unavoidable local setup effect.** They are single host-wide npm installs
shared with the other, *live* home. Upgrading them changes that home's tools while it is running. That is
the captain's call - see section 7.

---

## 5. Herdr integration

### Can Herdr host this home's sessions? Yes.

Auto-detection selected herdr for this home on both bootstrap runs:

> `NOTICE: auto-detected herdr runtime (HERDR_ENV=1) - spawning into the EXPERIMENTAL herdr backend.
> Set config/backend or pass --backend tmux to opt out.`

`config/backend` was deliberately **not** pinned - which backend to standardise on is the captain's
operating choice. To pin it: `echo herdr > <home>/config/backend`.

| Herdr capability floor @41d0ab39 | Floor | Installed | Verdict |
|---|---|---|---|
| `MIN_PROTOCOL` (spawn) | 14 | 17 | met |
| `MIN_EVENTS_PROTOCOL` (event supervision) | 16 | 17 | met |
| `MIN_WORKSPACE_MOVE_PROTOCOL` | 16 | 17 | met |
| `MIN_PRESENTATION_PROTOCOL` | 19 | 17 | **below** |
| `MIN_PRESENTATION_VERSION` | 0.8.0 | 0.7.5 | **below** |

So this home gets the **flat per-home layout**, not the one-workspace-per-task projection, and warns once
per detected release. (The other home *does* show per-task workspaces - it runs a different, forked code
base, not this pinned upstream.)

### Spawn smoke test — could-not-observe

No crew was spawned: the task forbids it and this brief is not `--herdr-lab` guarded. The upstream ships
**no dry-run and no standalone spawn-capability probe** (no `--dry-run` in `bin/fm-spawn.sh`, no
`spawn_capable`/`preflight` verb in `bin/fm-backend.sh` @41d0ab39). What was verified is the read-only
capability surface: adapter present, version and protocol gates met, `jq` present, server reachable,
auto-detection selecting herdr for this home. **End-to-end placement of a real worker remains unverified.**

---

## 6. Windows Terminal entry procedure

### Upstream ships no Windows launcher

At 41d0ab39, **`firstmate.bat`, `docs/windows-launcher.md`, `bin/fm-launch.sh` and `bin/fm-wsl-entry.sh`
are all ABSENT.** They exist only in the `sbracewell64/firstmate` fork the other home runs. So this
procedure is authored, not adapted from a shipped document — and nothing was written into the pristine
checkout.

### The entry point

`/mnt/e/FirstMate-Cleanroom/runtime/firstmate/enter-firstmate.sh` — it lives in the **home**, because the
code root is read-only. It exports `FM_HOME`, prepends the cleanroom tools bin and `~/.local/bin`, cds to
the code root, and execs the harness. `FM_ENTRY_DRY_RUN=1` prints the resolved launch without starting it.

**Recommended: start Herdr first, then run the entry script inside a Herdr pane.** That makes crew
placement resolve from the launcher's own workspace identity and completely sidesteps the shared
`firstmate` label (section 7).

One-off from Windows Terminal, PowerShell, or Run:

```
wt.exe --window new-tab --title "FirstMate Cleanroom" wsl.exe -d Ubuntu -- bash -lc /mnt/e/FirstMate-Cleanroom/runtime/firstmate/enter-firstmate.sh
```

As a Windows Terminal profile (`settings.json` → new profile), set:

```
"name":        "FirstMate Cleanroom",
"commandline": "wsl.exe -d Ubuntu -- bash -lc /mnt/e/FirstMate-Cleanroom/runtime/firstmate/enter-firstmate.sh",
"startingDirectory": null
```

### Verification

| Claim | Grade | Evidence |
|---|---|---|
| `wsl.exe --cd` reaches the `/mnt/e` code root | observed-good | `PWD=/mnt/e/FirstMate-Cleanroom/upstream/firstmate` |
| A **login** shell is required | observed-good | `bash -c` → `claude NOT on PATH (non-login)`; `bash -lc` → `/home/OPERATOR/.local/bin/claude`. `~/.local/bin` is where every harness lives. |
| The entry script resolves everything through `wsl.exe` | observed-good | dry run printed cwd, `FM_HOME`, claude, herdr, and no-mistakes **v1.61.0** |
| `wt.exe` accepts the command line | observed-good | `wt exit=0` |
| The spawned window rendered correctly | **could-not-observe** | `wt` detaches; this session cannot read the window it opened |
| An inline `$`-bearing script passed straight to `wsl.exe` is unreliable | **observed-bad** | `wsl.exe -d Ubuntu -- bash -lc 'export FM_HOME=/tmp/x; echo "[$FM_HOME]"'` printed `[]` — the substitutions were lost before bash saw them. The mechanism was not isolated (could-not-observe). **This is exactly why the entry is a script file, not an inline command.** |

---

## 7. Isolation — every shared host surface

### First, a correction to the premise

The brief calls `~/kun-agent-workspace` **retired**. It is not. observed-bad:

- its session lock holds **live pid 321** (`claude --dangerously-skip-permissions --effort high`, 8d 03h uptime);
- its watcher beacon `state/.last-watcher-beat` was touched **34 seconds** before the check;
- it has ten or more live crew lanes in the Herdr session.

Every collision below is therefore a **live** risk, not a dormant one.

### Not shared — verified clean

| Surface | Evidence |
|---|---|
| **Session lock** | `bin/fm-lock.sh:13-14` resolves `LOCK=$FM_HOME/state/.lock`. This home's lock is `/mnt/e/…/runtime/firstmate/state/.lock`; the other's is `/home/OPERATOR/kun-agent-workspace/state/.lock` (pid 321). This home's lock was acquired **while the other stayed held** - different files, no interaction. A dead holder is taken over automatically (`fm-lock.sh:58-66`). |
| **data/ state/ config/ projects/** | fully per-home under `$FM_HOME`. Backlog, briefs, wake queue, watcher state, registries, clones all private. |
| **FirstMate's own Claude hooks** | project-scoped through `$CLAUDE_PROJECT_DIR` in `<code_root>/.claude/settings.json`, so this home's session loads the **cleanroom** checkout's `bin/` scripts, not the other home's. |
| **treehouse pool** | keyed per repository path. This home has zero clones, so no pool is shared today. |

### Shared — ranked by risk

**1. Herdr workspace label namespace — HIGH, observed-bad.**
`bin/backends/herdr.sh:353-364` @41d0ab39 resolves **every** primary home to the constant label
`firstmate`, with **no** `FM_ROOT` discriminator — unlike cmux and zellij, which use
`bin/fm-backend-hometag-lib.sh`'s prefix + `FM_ROOT`-hash tag. A workspace labeled `firstmate` (id `w12`)
is live right now and belongs to the other home. Consequences:

- spawn from **inside** a Herdr pane → **safe**. `fm_backend_herdr_workspace_ensure` (`herdr.sh:1761-1771`)
  uses the launcher's exact resolved workspace identity and never consults the label.
- spawn from **outside** Herdr, one `firstmate` workspace present → it **adopts** that workspace
  (`herdr.sh:1783-1787`). This home's workers would appear inside the **other home's** workspace.
- spawn from **outside** Herdr, two `firstmate` workspaces → refuses as unresolvable (`herdr.sh:1776-1779`).
- **recovery / list-live** → `fm_backend_herdr_workspace_find` (`herdr.sh:1504-1506`) keeps
  **first-match-by-label** regardless of launcher identity, so it can scan the wrong home's workspace.

*Mitigation:* always enter through a Herdr pane, and/or give this home its own `HERDR_SESSION`.

**2. `~/.claude/skills/no-mistakes/SKILL.md` — HIGH, observed-bad.**
One user-global file, 18844 bytes, mtime **2026-09-01 19:44:50 -0400** (rewritten today), loaded
identically by both homes' Claude sessions. The specific claim that it carries **v1.61.0** guidance is
**could-not-observe**: the file has no version marker (a grep for `1.6x` found only an unrelated sentence
at line 289). The recent mtime and the v1.61.0 binary under the cleanroom tools dir are *consistent* with
the claim but do not establish it. Aggravator: the host-wide no-mistakes CLI is **v1.40.3**, so the other
home's sessions read newer instructions than its binary implements.

**3. `~/.local/bin` binaries — HIGH for remediation, observed-bad.**
claude, codex, pi, herdr, treehouse, tasks-axi, quota-axi, lavish-axi, gh-axi, no-mistakes are single
host-wide installs. Upgrading the three floor-failing axi tools changes the live home's tools mid-flight.

**4. `~/.no-mistakes/` root, daemon, socket, `state.sqlite` — HIGH, observed-bad.**
One daemon, pid 3349937, uptime 6d 13h, `/home/OPERATOR/.no-mistakes/bin/no-mistakes` **v1.40.3**, serving
every lane. A *separate* cleanroom daemon already runs from
`/mnt/e/FirstMate-Cleanroom/tools/bin/no-mistakes` **v1.61.0** with
`--root /home/OPERATOR/.fm-cleanroom-proof-a/nm-home` (pid 1417454). But `--root` is **not** a documented
public flag on `no-mistakes daemon --help`, and FirstMate's worker path calls plain `no-mistakes axi run`
with no root threading — so a v1.61.0 client on `PATH` would default to the **shared** `~/.no-mistakes`
root and its **v1.40.3** daemon. That client/daemon skew is unresolved.
**Never stop, restart or update the shared daemon — it kills other lanes' in-flight pipeline runs.**

**5. Herdr server, socket and `default` session — MEDIUM, observed-bad.**
One running 0.7.5 server, one `default` session, 12 live workspaces, one socket, addressed by both homes.

**6. tmux fallback session name — MEDIUM (latent), observed-bad.**
`bin/backends/tmux.sh:70` uses the constant session name `firstmate` with windows `fm-<id>`. If both homes
ever fall back to tmux, colliding task ids collide on window names. No tmux server is running today.

**7. `~/.claude/settings.json` — LOW, observed-good.**
User-global SessionStart hooks (gh-axi, chrome-devtools-axi, lavish-axi, herdr-agent-state.sh), model
`opus[1m]`, `effortLevel high`, `skipDangerousModePermissionPrompt true`. None resolve `FM_HOME`, so they
do not cross-wire the homes.

**8. `gh` authentication — LOW, observed-good.** One account, `sbracewell64`. Both homes act as the same
GitHub identity.

---

## 8. Pristine checkout — observed-good

```
$ git -C /mnt/e/FirstMate-Cleanroom/upstream/firstmate status --porcelain
                       (no output)
$ git -C … status --porcelain --ignored
                       (no output)
```

| | Before | After |
|---|---|---|
| HEAD | `41d0ab3910ece4e90db0194f756437b3abe8ab8f` | identical |
| Tree | `ca6a21611d8ed450190022d91484666307a836ec` | identical |
| Files outside `.git` | 485 | 485, **byte-for-byte identical set** |

Checked 2026-09-01 21:36:36 -0400. The `--ignored` sweep was run too, so a write that `.gitignore`
would have hidden is also excluded.

### Unavoidable local setup effects

- Created the runtime home and its four subtrees. Reversible.
- Acquired and then **released** this home's session lock. `state/.lock` is absent again.
- The first locked start materialized `config/startup-memory-budget=7500` and eleven `state/` records —
  ordinary FirstMate home state.
- The deferred network stage ran one `gh auth status` and one fleet-sync pass over an **empty**
  `projects/`. No clone was touched.
- **Nothing was installed, upgraded, started or stopped on the host. No daemon was restarted. No npm
  global changed.**

---

## 9. Decisions the captain owns

| # | Decision | Blocks |
|---|---|---|
| 1 | **axi floor upgrade.** tasks-axi, lavish-axi and quota-axi are below floor and are host-wide installs shared with the live home. Upgrade them (changing that home's tools mid-flight), pin cleanroom-local copies the way no-mistakes already is, or run degraded? | automatic backlog transitions, quota-aware array dispatch, rich review surfaces |
| 2 | **Herdr label isolation.** The label `firstmate` is a constant across primary homes. Give this environment its own `HERDR_SESSION`, always enter through a Herdr pane, or accept the adoption / first-match risk? | safe crew placement and recovery whenever the session is not started inside a Herdr pane |
| 3 | **no-mistakes root.** The cleanroom v1.61.0 client would default to the shared `~/.no-mistakes` root served by a v1.40.3 daemon. Which root should this environment use, and how is it threaded when FirstMate calls plain `no-mistakes axi run`? | any no-mistakes delivery mode here |
