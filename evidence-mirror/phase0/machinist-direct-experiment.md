# Machinist direct mode — executed experiment

**Phase 0 Track 5 proof — clean-room architecture directive, 2026-09-02**

| | |
|---|---|
| **Subject** | `/mnt/e/FirstMate-Cleanroom/tools/machinist` at `75964acbdb944b4456a51c9bfaa4948e76b0c041` (`v0.4.0-4-g75964ac`) |
| **Prior reading** | `artifacts/scouts/machinist-substrate-report.md` (read-not-run; this proof runs it) |
| **Laboratory** | `/mnt/e/FirstMate-Cleanroom/experiments/machinist` — disposable, self-contained |
| **FirstMate trunk cited** | `6d1a000e4e9c836eb120286d63682ca135577dfe` |
| **Boundary catalogue cited** | `artifacts/scouts/upstream-firstmate-boundary-report.md` §5 (pinned upstream `41d0ab39`) |
| **Mode** | `machinist run` (direct) only. No control plane, no worker daemon, no triggers, no Foreman, no Shepherd, no `no-mistakes` inside Machinist. |
| **Verdict** | **ADOPT_LATER — narrowly, conditionally.** See §7. This experiment authorizes no architectural adoption. |

**Three-valued grading.** Every row below carries one of:
`observed-good` — I ran it and the behavior is what a caller wants ·
`observed-bad` — I ran it and the behavior is a hazard a caller must handle ·
`could-not-observe` — the question has no answer I established, which is a result and not a pass.

Nothing here is graded from reading code alone. Where I read code, it is cited as supporting context for something I ran.

---

## 1. Method

I installed a user-space Go toolchain inside the experiment directory, built the pinned Machinist checkout without modifying it, and ran twenty-nine measured invocations against a purpose-built scratch git repository with two linked worktrees. Executors were deterministic shell scripts I wrote, so every input and every exit code was mine to choose; one measurement (§6.9) used the real `claude` harness.

Evidence for every run is on disk under `experiments/machinist/evidence/<slug>/` as separate `stdout.txt`, `stderr.txt`, `exitcode.txt`, `wall_seconds.txt`, plus that run's own `datadir/runs/<run_id>/{result.json,events.jsonl}`. Streams are never merged, because two of the findings below are precisely about stream merging.

**Build fidelity, executed.** The subject's own test suite runs green under this toolchain: `go test -count=1 -v ./internal/runner/... ./internal/config/... ./internal/cli/...` → **114 tests passed, 0 failed, 0 skipped**, exit 0 (`evidence/gotest.log`). The pinned checkout was byte-clean before the build, after the build, and after the tests (`git status --porcelain` empty at each point; HEAD still `75964ac`).

### What could not be observed

| Question | Why | Grade |
|---|---|---|
| Managed-mode at-least-once re-execution, lease lapse, duplicate side effects | Out of bounds by directive — managed mode was never started | could-not-observe |
| Trigger-driven autonomous work admission | Out of bounds by directive — no `[triggers.*]` table was ever written | could-not-observe |
| Behavior on a native Linux filesystem | Everything ran on a Windows-mounted `drvfs` path (`/mnt/e`). Atomic result publication and directory fsync worked there, but timing-sensitive results are from that filesystem | could-not-observe |
| Whether a GitHub repository exists | `gh-axi repo view` answered `REPO_NOT_FOUND`, but **no declared verifier covers repository existence** (`bin/fm-verify.sh --list` → `browser`, `pr-checks`, `merge-clean`, `review-exec`, `review-mutation`). Graded by hand as observed; the missing verifier is reported as a gap | gap |
| Long-run behavior (hours), memory growth, log-rotation pressure | Longest measured run was 16 s | could-not-observe |

---

## 2. Environment-change ledger

Everything is inside `/mnt/e/FirstMate-Cleanroom/experiments/machinist`. **Nothing was installed system-wide, and no environment variable was exported outside a single sourced script.** Deleting that one directory reverts every change in this ledger.

| # | Change | Exact detail | Reversal |
|---|---|---|---|
| 1 | Go toolchain downloaded | `go1.26.8.linux-amd64.tar.gz`, sha256 `d0f743b33e8d8945e6b1f432edd15785c70507121d6e2a723b21285eddf8b57b`, **verified equal to the sha256 published at `https://go.dev/dl/?mode=json`** before extraction | `rm -rf toolchain/` |
| 2 | Toolchain extracted | `toolchain/go/` (304 MB). `go version` → `go1.26.8 linux/amd64`. `go` is **not** on the ambient `PATH` (`command -v go` → not found outside the sourced script) | same |
| 3 | Build environment | `env.sh` exports **only**: `GOROOT`, `GOPATH`, `GOMODCACHE`, `GOCACHE`, `GOTOOLCHAIN=local`, and a `PATH` prefix — every value under the experiment directory | `unset` / do not source |
| 4 | Module cache | 11 modules fetched from the Go module proxy into `gomodcache/` (294 MB); build cache `gocache/` (322 MB) | `rm -rf gomodcache gocache` |
| 5 | Binary built | `build/machinist`, sha256 `1c382d481e4731849b04198a07c99868316ac295f5f1a78527e582b4a8cade77`, built as `go build -buildvcs=false -trimpath -ldflags="-X main.version=v0.4.0-4-g75964ac" ./cmd/machinist` (the flags `scripts/release.sh:39` itself uses). `machinist version` → `v0.4.0-4-g75964ac` | `rm -rf build/` |
| 6 | Subject repository | **Unmodified.** Clean before build, after build, after `go test`. HEAD unchanged at `75964ac` | n/a |
| 7 | Machinist data directory | `data_directory` was overridden to the experiment tree on **every** invocation. The default `~/.machinist/worker` was never created — `~/.machinist` does not exist, nor does `~/.factory` | n/a |
| 8 | Scratch git repository | `scratch/repo` (`git init`), two linked worktrees `scratch/wt/lane1`, `scratch/wt/lane2`. `origin` set to `https://github.com/sbracewell64/machinist-experiment-nonexistent.git` — a repository confirmed **not to exist**, so no push could ever create or mutate anything | `rm -rf scratch/` |
| 9 | Configuration written | `mconfig/worker.toml` (executors + one repository), `mconfig/config.toml` (commands only — **no `[triggers.*]`, no `foreman`, no `shepherd`**), `mconfig/prompts/implement.md` | `rm -rf mconfig/` |
| 10 | One orphaned process | The §6.5 timeout measurement leaked one `sleep 600` (pid 1397154) that outlived Machinist's kill. **Killed manually.** No process from this experiment is running | done |
| 11 | Files outside the experiment tree | This report; `data/cleanroom-machinist-experiment/report.md`; the task status file; one scratch marker `/tmp/machinist-m5-pids` (removed) | n/a |
| 12 | Paid services | **None activated.** The one agent invocation (§6.9) used the session's existing Claude subscription auth. Its own telemetry reported `five_hour` window utilization 0.16, `overageStatus: rejected`, `costBasis: list` — list-price accounting inside the existing entitlement, not new spend | n/a |

---

## 3. Measurements table

| # | Measurement | Grade | Result in one line | Evidence |
|---|---|---|---|---|
| 1 | Basic `machinist run` happy path | **observed-good** | Exit 0; child process ran 88 ms inside a 192 ms end-to-end invocation; cwd pinned to the repo toplevel; prompt delivered on stdin; three `MACHINIST_*` vars injected; `result.json` + `events.jsonl` written atomically — on `drvfs` | `m1-happy-path/` |
| 1b | Git-environment scrub | **observed-good** | Parent `GIT_DIR` and `GIT_WORK_TREE` were set to a decoy path; the child saw both `<unset>` and resolved the correct repository | `m1-happy-path/stdout.txt` |
| 1c | Environment isolation | **observed-bad** | An arbitrary parent variable (`FM_PROBE_MARKER`) reached the child verbatim. There is no environment allowlist — only the 20-name `GIT_*` denylist | `m1-happy-path/stdout.txt` |
| 2 | Approved command → process → typed result | **observed-good** | Command name resolves to a worker-owned argv; unknown command → exit 2 with no run; non-git path → exit 2; `.git/worktrees/<n>` admin dir → exit 2 | `m2-unknown-command/`, `m2-nongit/`, `m3-gitadmin/` |
| 2b | No shell interpolation | **observed-good** | A prompt of `$(touch …) \`touch …\` ; rm -rf …` arrived on stdin byte-for-byte; **neither marker file was created** | `m2-injection/` |
| 2c | `command_hash` integrity coverage | **observed-bad** | Swapping the executor's argv to a **completely different executable** produced an **identical** `command_hash` (`0dbfddbf…`). The hash covers the executor *name*, not what ran | `m2-injection/` vs `m2-hashswap/` |
| 3 | Linked-worktree handling | **observed-good** | `--repo` at a linked worktree resolved to **itself** (`…/wt/lane1`), reported branch `lane1`, and did not leak to the main checkout | `m3-linked-worktree/` |
| 3b | Subdirectory widening | **observed-bad** | `--repo …/wt/lane1/subdir` **silently** became `…/wt/lane1`; `--repo …/repo/sub` silently became `…/repo`. No warning, and `result.json.repository` records the widened path as if it were asked for | `m3-subdir/`, `m3-main-subdir/` |
| 4 | Deterministic `result.json` discovery | **observed-bad** (as shipped) | The run id reaches the caller **only** on stderr, on the same stream as child output, and there is no `--run-id`/`--result-json`/`--json` flag anywhere in `run --help` | `m4-spoof/`, `m4-nonewline/` |
| 4b | Scrape hazard — forgery | **observed-bad** | A child printing `machinist: run run_000…dead succeeded; events: /tmp/attacker-controlled/…` to stderr defeats a first-match scrape: the naive parse returned the **child's** id | `m4-spoof/stderr.txt` |
| 4c | Scrape hazard — partial line | **observed-bad** | A child ending stderr without a newline **concatenates** with Machinist's status line (`…without-newlinemachinist: run run_24d8…`). An anchored `^machinist: run` regex does not match | `m4-nonewline/` (od dump) |
| 4d | Deterministic workaround | **observed-good** | A fresh per-invocation `data_directory` makes `<datadir>/runs/*/result.json` a one-element glob. Verified: 1 result on success, **0 on every failure that never ran** | `m4-fresh-datadir/`, `m2-*/discovered_results.txt` |
| 4e | Shared-directory heuristics | **observed-bad** | Two concurrent runs in one `data_directory` produced two run dirs with **identical mtimes**. "Newest directory" is not merely racy here, it is undecidable | `m4-concurrent/` |
| 4f | Unwritable data directory | **observed-good** | Mode-`500` data dir → exit **1**, explicit message, **child never started**. Fails closed | `m4-unwritable/` |
| 5 | Timeout / SIGKILL residue — worktree | **observed-bad** | A 10 s timeout left the worktree with a **staged** file and an **untracked** file. No SIGTERM: the child's `trap … TERM` never fired. This is exactly `fm-teardown.sh`'s refusal condition | `m5-timeout/residue.txt` |
| 5b | Timeout — typed result | **observed-good** | Exit 124, `state: timed_out`, `duration_millis: 10023` against a 10 s budget, `run.completed` event carrying `state=timed_out exit_code=124` | `m5-timeout/` |
| 5c | Timeout — process residue | **observed-bad** | A `setsid` descendant **survived** the kill (pid 1397154, own session, reparented to pid 11, still alive 32 s after a 10 s run). The in-group `sleep` was killed. Process-group kill does not reach a session-detached descendant | `m5-timeout/residue.txt` |
| 6 | 124 / 130 disambiguation | **observed-bad** (by design) | Machinist timeout → exit **124** `state: timed_out`. Executor exiting 124 → exit **124** `state: failed`. Machinist SIGINT → exit **130** `state: cancelled`. Executor exiting 130 → exit **130** `state: failed`. **The process exit code is identical in each pair** | `m5-timeout/`, `m6-exec124/`, `m6-cancel/`, `m6-exec130/` |
| 6b | Disambiguation is possible | **observed-good** | `result.json.state` separates all four cases cleanly, and the stderr line carries the same word — but that line is the forgeable one (§4b) | same |
| 7 | Large-output truncation | **observed-good** | 40 MiB emitted. Caller received **all 41,943,095 bytes** live. Log recorded **25,067,542 bytes (59.8 %)**, then emitted exactly one explicit `process.output_truncated` event and stopped | `m7-firehose/` |
| 7b | Which limit actually binds | **observed-bad** | The advertised output budget is 64 MiB, but base64 inflation makes the **32 MiB event-file cap bind first**, at ~25 MB of real output. The truncation message names both limits and does not say which one fired | `m7-firehose/` events tail |
| 7c | Truncation reaches the typed result | **observed-bad** | `result.json` for that run says `"state": "succeeded"` and **carries no truncation field at all**. A caller reading only the typed result cannot tell that its durable log is 40 % incomplete | `m7-firehose/…/result.json` |
| 8 | Operation with publication credentials unavailable | **observed-good** (achievable) / **observed-bad** (not provided) | Baseline: the child was **fully authenticated** — `gh auth status` exit 0 as `sbracewell64`, and the push reached GitHub past authentication. Machinist supplies no credential control of its own | `m8a-ambient/` |
| 8b | Separation that works | **observed-good** | `GH_CONFIG_DIR=<empty dir>` → `gh auth status` exit 1, `gh pr create` exit 4, `git push` → `fatal: could not read Username … terminal prompts disabled`, exit 128. Adding `HOME=<empty dir>` also emptied the credential helper | `m8b1-ghconfigdir/`, `m8b3-emptyhome/` |
| 8c | Separation Machinist actively defeats | **observed-bad** | Setting `GIT_CONFIG_COUNT/KEY_0/VALUE_0` to null the credential helper — the standard env-only way to do it — is **stripped by Machinist's own git scrub**. The child kept the helper and authenticated normally | `m8b2-gitconfigenv/` |
| 9 | Bounded implementation task → local committed candidate | **observed-good** | Real `claude` (sonnet) via Machinist, 16 s, exit 0, `state: succeeded`. Contract **red before** (7/7 failing) and **green after** (7/7 passing, verified by me, not by the worker). One commit `35866d2 feat: implement tools/slugify.py`, clean worktree | `m9-implement/` |
| 9b | No publication occurred | **observed-good** | Zero remote-tracking refs after the run; reflog shows only the two local commits. The identical environment was proven unable to push, authenticate, or open a PR | `m9-capability-check/` |
| 9c | Token accounting | **observed-good** | `result.json.token_usage: 163104`, collected by the native `claude` parser with **no** `token_usage` file present — and exactly equal to the harness's own `10 + 745 + 147773 + 14576` | `m9-implement/…/result.json` |
| 10 | Steering feasibility (the judgment question's hinge) | **observed-bad** | The child's stdin is a pipe, **not** a tty, and is **closed immediately after the prompt**: a second read returned EOF instantly, not a blocked read. There is no channel to steer a Machinist-hosted worker | `m10-stdin/` |
| 10b | Data-directory retention | **observed-bad** | Zero `os.RemoveAll` in non-test code; no pruning of `runs/`. Up to 32 MiB of event log per run is retained forever unless the caller reaps it | source scan at `75964ac` |

---

## 4. What the runs actually showed, in detail

### 4.1 The happy path is genuinely clean (§3 rows 1, 1b, 1c)

```
$ machinist run --config worker.toml --command probe --repo …/scratch/repo --prompt 'hello from the caller…'
PROBE_CWD: …/scratch/repo
PROBE_MACHINIST_RUN_ID: run_cdbe6dae0c0ae2851bdfd3af
PROBE_GIT_DIR: <unset>            # parent had GIT_DIR=/tmp/should-be-stripped
PROBE_MARKER_ENV: inherited-from-parent
PROBE_STDIN_BEGIN
hello from the caller; this is the work request
PROBE_STDIN_END
[stderr] machinist: run run_cdbe6dae0c0ae2851bdfd3af succeeded; events: …/events.jsonl
exit 0 · invocation wall 192 ms · result.json duration_millis 88
```

`result.json` is complete and honest: `state`, `exit_code`, both timestamps, `duration_millis`, `token_usage`, `command_hash`, `definition`, `repository`, `events_path`. `events.jsonl` is eleven ordered, timestamped events with base64 payloads that decode byte-exactly, including the interleaved stderr line in correct sequence position.

The two soft spots are next to each other in the same output. `GIT_DIR` and `GIT_WORK_TREE` were stripped — a real control, and it worked. `FM_PROBE_MARKER` was not, because there is no allowlist. **Machinist's boundary is over *what may be named*, not over *what the process can reach*.**

### 4.2 The approved-command boundary holds; `command_hash` does not mean what it looks like (§3 rows 2, 2b, 2c)

Shell metacharacters in `--prompt` are inert — I checked for the side effect, not just the text, and neither marker file existed afterwards.

But `command_hash` is a weaker binding than its name suggests, and I measured it rather than inferring it: I ran the `probe` command twice, changing only `worker.toml`'s `[executors.probe]` argv to point at an entirely different script. The second run printed `DIFFERENT_EXECUTOR_BODY` — different code, different output — and produced the **same** `command_hash: 0dbfddbf5f83…`. So `command_hash` answers "was the same command *definition* used", never "did the same code run". A caller must not treat it as provenance for the executed work.

### 4.3 Linked worktrees are handled correctly; subdirectories are silently widened (§3 rows 3, 3b)

This is the single most FirstMate-relevant repository result and it lands well: pointing `--repo` at a linked worktree gave `cwd = …/wt/lane1`, `git rev-parse --show-toplevel = …/wt/lane1`, branch `lane1`. A FirstMate task worktree handed to Machinist stays in its own lane.

The widening is the cost, and it is silent in both directions. `--repo …/wt/lane1/subdir` ran in `…/wt/lane1`; `--repo …/repo/sub` ran in `…/repo`. Worse for auditing: `result.json.repository` records the **widened** path, so the durable record shows a repository the caller never asked for, with nothing marking the substitution. A caller that means "scope this agent to `packages/foo`" gets the whole repository and no warning.

### 4.4 Finding your own result is the substrate's weakest contract (§3 rows 4–4f)

The scout flagged that the run id appears only on stderr. Running it makes the consequence sharper than "a bit ugly", because the child owns that same stream:

**Forgery.** My `spoof` executor printed one line to stderr:
```
machinist: run run_00000000000000000000dead succeeded; events: /tmp/attacker-controlled/events.jsonl
```
Machinist's real line followed. A first-match scrape returned `run_00000000000000000000dead`. Nothing distinguishes the two — same stream, same prefix, same shape.

**Collision.** A child whose last stderr write lacks a trailing newline merges with Machinist's line. The raw bytes:
```
t r a i l i n g - p a r t i a l - s t d e r r - l i n e - w i t h o u t - n e w l i n e m a c h
i n i s t :   r u n   r u n _ 2 4 d 8 3 1 a a b a d 2 0 8 8 a 5 4 6 0 d 5 7 2   s u c c e e d …
```
`grep -E '^machinist: run run_[0-9a-f]+ '` does not match. An agent harness that ends output without a newline — an ordinary thing — breaks an anchored parse.

**The workaround, measured.** Give every invocation its own fresh `data_directory`; then `<datadir>/runs/*/result.json` is a single unambiguous path, no stderr involved. This held for all four outcome classes, and it is *also* the clean three-valued reading: the glob is empty exactly when the run never happened (`m2-unknown-command`, `m2-bad-repo`, `m2-nongit`, `m4-unwritable`) and holds exactly one file when it did. That is a caller-side convention, not a Machinist feature — Machinist does not document, enforce, or assist it, and `runner.Options` has the `RunID` field that would remove the problem entirely but the `run` CLI never exposes it (`internal/cli/root.go:303-309`).

**Mtime heuristics are not a fallback.** Two concurrent runs sharing one data directory produced two directories stamped `21:40:29.697072400` — identical to the nanosecond on this filesystem.

### 4.5 A killed worker leaves work FirstMate must refuse to discard (§3 rows 5–5c)

The 10 s timeout produced exactly the typed outcome it should — exit 124, `state: timed_out`, `duration_millis: 10023` — and exactly the residue FirstMate cannot absorb:

```
$ git -C …/wt/lane1 status --porcelain
A  sleeper-staged.txt
?? sleeper-uncommitted.txt
```

The child's `trap … TERM` handler never ran, confirming SIGKILL with no grace. There is no flush, no commit, no cleanup. `bin/fm-teardown.sh` at `6d1a000e` refuses to discard uncommitted work; a Machinist timeout manufactures that state as its normal failure mode.

The new result the scout could not reach is the **process** residue. My executor spawned two descendants: one ordinary background child and one `setsid` child. Machinist's `syscall.Kill(-pid, SIGKILL)` killed the first and **missed the second**:

```
PID     PPID  PGID  SESS  ETIMES  ARGS
1397154   11  1397154 1397154   32   sleep 600     # own session — survived a 10 s run
```

Process-group termination is the right tool and it is correctly implemented, but a descendant that calls `setsid` leaves the group and outlives the run. Real agent harnesses do daemonize helpers. **A caller cannot treat "Machinist returned" as "nothing of mine is still running."**

### 4.6 The 124/130 collision is real, and only the typed state resolves it (§3 rows 6, 6b)

| Scenario | Process exit | `result.json.state` | `result.json.exit_code` |
|---|---|---|---|
| Machinist timeout | 124 | `timed_out` | 124 |
| Executor itself exits 124 | 124 | `failed` | 124 |
| Machinist cancelled (SIGINT) | 130 | `cancelled` | 130 |
| Executor itself exits 130 | 130 | `failed` | 130 |
| Executor exits 7 | 7 | `failed` | 7 |

All five ran. The exit code alone misclassifies in two of five cases, and 124/130 are not exotic values — 124 is what GNU `timeout` returns, 130 is what any Ctrl-C'd shell script returns, so an agent harness that internally wraps a `timeout` will produce a false Machinist-timeout reading. Disambiguation requires reading `result.json` — which requires solving §4.4 first. The two weaknesses compound: **the only trustworthy disambiguator lives in the file whose path is hardest to obtain honestly.**

### 4.7 Truncation is honest in the log and silent in the result (§3 rows 7–7c)

This is the row where Machinist's discipline is best and its gap is most FirstMate-relevant.

Best: 40 MiB emitted, the caller got every one of 41,943,095 bytes live, and the log stopped with an explicit, sequenced, machine-readable event rather than quietly ending:
```json
{"sequence":769,"type":"process.output_truncated",
 "message":"recording stopped after 67108864 output bytes or 33554432 event bytes; live output continues"}
```
That is exactly the could-not-observe discipline FirstMate wants: a log that says when it stopped being complete.

Gap: the discipline stops at the log boundary. `result.json` for that same run reads `"state": "succeeded"` and has **no truncation field**. A caller that does the right thing everywhere else — reads the typed result rather than scraping — receives an unqualified success for a run whose durable evidence is 40 % missing. And the truncation message's own numbers mislead: the binding limit was the 32 MiB **event-file** cap, reached at 25,067,542 bytes of real output because base64 inflates by 4/3. Anyone reading "64 MiB" as their output budget is wrong by a factor of 2.6.

### 4.8 Capability separation is achievable, entirely by the caller, and Machinist removes one lever (§3 rows 8–8c)

Baseline first, because a separation claim is worthless without a control showing the capability was there to remove. With ambient session credentials the Machinist-hosted child was **fully authenticated**:

```
PUSH_GH_AUTH_STATUS: ✓ Logged in to github.com account sbracewell64 … Token scopes: 'gist','read:org','repo','workflow'
PUSH_ATTEMPT: remote: Repository not found.        # authenticated, then rejected for a repo that does not exist
```

The credential never travelled as an environment variable — `GH_TOKEN` and `GITHUB_TOKEN` were both unset. It travelled through `HOME` → `~/.config/gh/hosts.yml` plus the global git credential helper `!/usr/bin/gh auth git-credential`. So "strip `GH_TOKEN` from the child env" would have been a **null control** here, and would have looked like a pass.

What actually works, measured:

| Arm | Lever | `gh auth` | `git push` | `gh pr create` |
|---|---|---|---|---|
| baseline | none | exit 0, logged in | authenticated, `Repository not found`, 128 | GraphQL repo-not-found, 1 |
| B1 | `GH_CONFIG_DIR=<empty>` | exit 1, not logged in | `could not read Username … prompts disabled`, 128 | `please run gh auth login`, 4 |
| B2 | `GIT_CONFIG_COUNT/KEY_0/VALUE_0` nulling `credential.helper` | **exit 0, still logged in** | **authenticated**, 128 | GraphQL repo-not-found, 1 |
| B3 | `HOME=<empty>` + `GH_CONFIG_DIR=<empty>` | exit 1 | `could not read Username`, 128 | exit 4 |

Arm B2 is the finding. Machinist's `GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*` scrub — a good control, aimed at repository redirection — **also strips the standard environment-only mechanism for neutralising a git credential helper.** The child's effective helper was still `!/usr/bin/gh auth git-credential`, and it authenticated. A caller who reaches for the obvious lever gets a silent no-op that looks like it worked, because the push still fails for an unrelated reason. `GIT_ASKPASS`, `GIT_SSH_COMMAND`, `SSH_AUTH_SOCK` and `GH_TOKEN` pass through untouched; the scrub is about *where* git points, never about *what it can prove*.

Conclusion for the directive's capability-separation requirement: it is **achievable and was achieved** (arm B1, then used for the §6.9 agent run), but it is entirely the caller's construction. Machinist offers no flag, no config key, and no documentation for it, and its one relevant control cuts the wrong way.

### 4.9 A real bounded implementation task completed as a local committed candidate (§3 rows 9–9c)

Setup was a genuine executable contract, red first: `tests/test_slugify.sh` with 7 assertions including unicode folding, committed in `lane2` while `tools/slugify.py` did not exist. Pre-run: **7/7 failing**, exit 1. Worktree clean.

One invocation, with `GH_CONFIG_DIR` pointed at an empty directory:
```
machinist run --command implement --model sonnet --repo …/scratch/wt/lane2 --prompt '<work request>'
→ exit 0, 16 s, state: succeeded, token_usage: 163104
```
The `implement` command's prompt file carries the bounds ("must NOT push, must NOT open a pull request, must NOT merge; finish with a clean worktree and your work committed"), with `{{machinist.prompt}}` interpolating the work request.

Verified by me afterwards, not taken from the worker's own report:
- `35866d2 feat: implement tools/slugify.py`, 1 file, +16 lines
- `git status --porcelain` empty — clean worktree
- `bash tests/test_slugify.sh` → **7/7 ok, exit 0**
- `git for-each-ref refs/remotes` → **zero refs**; reflog shows only the two local commits
- The identical environment, re-probed in the same worktree, could not authenticate, push, or open a PR

Token accounting deserves its own note because it is a capability FirstMate does not have today: `token_usage: 163104` was collected by Machinist's native `claude` stdout parser with no `MACHINIST_TOKEN_USAGE_PATH` file written, and it equals the harness's own reported `input 10 + output 745 + cache_read 147773 + cache_creation 14576` exactly.

This is the one measurement where Machinist looks like a substrate a fleet would want: a named command, a repository, a prompt, and a typed successful result with a per-run token figure — and a candidate that stopped exactly where it was told to stop, provably rather than obediently.

---

## 5. The judgment question — removal or a new layer?

The directive asks whether Machinist actually removes FirstMate execution machinery — worker spawn, log capture, typed outcome — or merely adds a layer. Answered against the boundary scout's §5 catalogue and the code at `6d1a000e`.

### 5.1 Worker spawn

`bin/fm-spawn.sh` is **3,482 lines** at `6d1a000e`. What it does, per its own header and the boundary catalogue §5.1: resolve and validate an **isolated worktree** distinct from the primary checkout (two independent layers, mechanical and prose); create a **persistent interactive endpoint** on a selected backend; publish `state/<id>.meta`; refuse brief/meta mode drift; enforce route, capability floor, provider capacity, admission, qualification and concurrency; record attempt lineage; arm turn-end wiring.

Machinist's direct mode replaces exactly one element of that list: start a child process with the working directory pinned and the environment partially scrubbed. It creates no worktree, allocates no endpoint, publishes no task record, and has no concept of any of the admission machinery. `bin/fm-backend.sh` (**996 lines**) survives untouched, because a Machinist run has **no pane at all** — measured: `STDIN_IS_TTY: no`, `STDOUT_IS_TTY: no`, stdin is `pipe:[…]`.

**Verdict: adds a layer.** Nothing in `fm-spawn.sh` becomes deletable.

### 5.2 Log capture

Here the honest answer runs the other way, and it is the strongest thing this experiment found.

FirstMate's log capture today is `state/<id>.status` — a typed **event** log of supervisor-actionable transitions (`bin/fm-status-event-lib.sh`, 236 lines) — plus the worker's terminal scrollback, which is a rendered pane, not a durable byte-exact record. FirstMate does **not** durably capture a worker's process output: the closest thing is `tmux capture-pane` reads for a busy signature and a bounded tail (`bin/fm-tmux-lib.sh:321,358,377` at `6d1a000e`), which sample rendered screen content at the moment of the read and are not replayable.

Machinist's `events.jsonl` is a different artifact class: ordered, sequenced, UTC-timestamped, base64 byte-exact, size-bounded, and explicitly marked when it stops being complete. Nothing in FirstMate does this.

**Verdict: this is an addition of something FirstMate lacks, not a removal of something it has.** It is worth having, and it is the reason this verdict is not REJECT. Its one defect (§4.7) is that the truncation marker does not reach the typed result.

### 5.3 Typed outcome

These look like the same thing and are not, and conflating them would be the classic wrong-subject error.

`bin/fm-crew-state.sh` (**1,050 lines**) answers **"what is this crew doing right now?"** — mid-run, by reconciling a possibly-stale event log against an authoritative live source (an attributed no-mistakes run-step, else a pane busy signature), emitting `state: … · source: … · detail`. Its whole reason for existing, per its own header at `6d1a000e:1-20`, is that a `tail -1` of the event log reports the last *event*, not the current *state*.

Machinist's typed result answers **"how did this process end?"** — and only after it has ended. During a run the only Machinist artifact is a partial `events.jsonl` with **no state field at all**; `result.json` does not exist until the process is over. Machinist cannot answer `fm-crew-state.sh`'s question, at any point in the run.

**Verdict: adds a layer.** Machinist's four-state terminal vocabulary is good and invariant-checked, but it is a *different question*, and `fm-crew-state.sh` is not made smaller by it.

### 5.4 The machinery that is structurally out of reach

| FirstMate machinery | Lines at `6d1a000e` | Under Machinist |
|---|---|---|
| `bin/fm-send.sh` — steering, durable sequenced inbox | 422 | **Impossible.** Stdin is closed immediately after the prompt; a second read returned EOF instantly (§3 row 10). One prompt in, one outcome out |
| `bin/fm-watch.sh` — wake classification, staleness, wedge timers | 1,365 | No pane to read, no busy verdict, no `.childcpu`. A silently looping agent is indistinguishable from a working one until its timeout |
| `bin/fm-teardown.sh` — recoverable-work test | 2,667 | Unchanged, and Machinist makes it fire **more** often (§4.5) |
| `bin/fm-attempt.sh` — attempt budget, execution lineage | 1,630 | Direct mode has no retry at all. Unchanged |
| `bin/fm-brief.sh` — brief contract, status protocol | 736 | The prompt file is a weaker analogue; the status protocol has no counterpart |
| Ask-user / decision-hold loop | — | A run cannot pause, ask, and continue. `needs-decision` has no representation |

### 5.5 The answer

**Machinist does not remove FirstMate execution machinery. It adds a layer — and for one narrow class of work, a layer worth adding.**

For a *supervised* lane it subsumes nothing at all: steering, pane, mid-run state, decision holds and attempt budgeting are the substance of a supervised lane, and Machinist forecloses the first four structurally.

For an *unsupervised, bounded, single-shot* lane — a scout probe, an audit pass, a fixed verification command — it genuinely subsumes process start, cwd pinning, one timeout, process-group termination, a closed terminal-state vocabulary, a durable byte-exact bounded log, and per-run token accounting. Three of those (durable log, invariant-checked terminal state, token accounting) FirstMate does not have.

But even there, adoption **deletes no FirstMate code** and **requires new FirstMate code**: a per-invocation data-directory convention (§4.4), a `result.json` reader that prefers `state` over the exit code (§4.6), a truncation check that `result.json` will not give you (§4.7), a credential-separation preamble that Machinist neither provides nor documents (§4.8), and a post-run descendant sweep (§4.5). The net is *more* machinery, buying better evidence.

---

## 6. Bounds compliance

| Bound | Held? | Evidence |
|---|---|---|
| Direct mode only | yes | Only `machinist run` was ever invoked. `machinist start`, `worker`, `submit` never ran; no SQLite database exists anywhere under the experiment tree |
| No triggers | yes | `mconfig/config.toml` contains no `[triggers.*]` table |
| No Foreman / Shepherd | yes | Neither command is defined; the shipped prompts were never used |
| No Machinist-owned PR/merge orchestration | yes | No forge-mutating path was configured or invoked |
| `no-mistakes` never run inside Machinist | yes | Not defined as a command, never invoked |
| Hosted worker must not push / PR / merge | yes | Proven by capability separation and by outcome: zero remote-tracking refs, and the identical env could not authenticate (§4.8, §4.9) |
| No paid services | yes | Ledger row 12 |
| Pinned checkout unmodified | yes | Clean before build, after build, after tests; HEAD `75964ac` |
| Build artifacts under `experiments/machinist/` | yes | Ledger rows 1–5 |

---

## 7. Verdict

# ADOPT_LATER — narrowly scoped, conditionally, and not on the strength of this experiment alone.

**Scope of what this verdict covers:** `machinist run` (direct mode) as the executor for **unsupervised, bounded, single-shot** FirstMate work that needs no steering and tolerates a hard kill. Nothing else. Managed mode, triggers, Foreman and Shepherd are out of scope here and were measured not at all (§1); the scout's reading of them stands unexecuted.

**Why not REJECT.** The execution core did everything it claims, under execution, on every measurement I ran. 114 of the subject's own tests pass under a from-source build. The typed terminal state is real and separates all four outcome classes. The log is byte-exact, bounded, and — uniquely among things I have measured in this fleet — *tells you when it stopped being complete*. Linked worktrees resolve correctly, which is the property a FirstMate lane most needs. The approved-command boundary genuinely prevents a caller from naming an executable or injecting shell. And a real agent task completed through it as a local committed candidate with publication capability provably removed. Rejecting that would be rejecting working, well-made code.

**Why not adopt now, and why not ADOPT.** Adoption would be a net *increase* in FirstMate machinery (§5.5), and five measured behaviors each require caller-side compensation that does not exist yet:

1. **Result discovery is unsound as shipped** (§4.4). The only path to the typed result is a stderr line the child can forge and can accidentally corrupt. The workaround is sound but is a convention I invented during this experiment, not a contract Machinist offers.
2. **The typed result hides its own incompleteness** (§4.7). `state: succeeded` on a run whose log lost 40 % of the output, with no field to check, is the exact shape of failure FirstMate's three-valued rule exists to prevent.
3. **A timeout manufactures the state teardown must refuse** (§4.5), and leaks session-detached descendants. FirstMate's supervision deliberately never signals a worker; adopting Machinist imports a kill path the fleet does not currently have.
4. **Capability separation is the caller's job, and one obvious lever is silently disabled by Machinist itself** (§4.8, arm B2). A lever that no-ops while the operation still fails for an unrelated reason is worse than no lever.
5. **Maturity.** Six weeks old, four incompatible config migrations, bus factor one, self-described early access — against a `config.toml`/`worker.toml` schema an adoption would depend on.

**Preconditions I would want satisfied before adoption is even proposed.** Each is checkable, and the first two are small upstream contributions squarely inside Machinist's own stated scope:

- **P1.** A `--run-id` or `--result-json` flag on `machinist run`, so the caller names the result path instead of discovering it. `runner.Options.RunID` already exists and the CLI simply does not pass it (`internal/cli/root.go:303-309`). Until then, the per-invocation `data_directory` convention (§4.4) is mandatory and must be written down as a contract, not a habit.
- **P2.** A truncation indicator in `result.json`, so a typed-result reader cannot mistake a partial log for a complete one.
- **P3.** A FirstMate-side adapter that: reads `state` and never branches on 124/130; treats an empty result glob as could-not-observe; runs every worker under an explicit credential-stripped preamble (`GH_CONFIG_DIR`, and `HOME` where the harness permits) with a **positive control** proving the capability was there to remove; sweeps for surviving descendants after every run; and reaps `runs/` on a retention policy Machinist does not have.
- **P4.** A decision, recorded, that unsupervised single-shot work is a class FirstMate actually wants to run headless — because that is the entire addressable surface. Everything supervised is structurally excluded by a closed stdin, and that is a property of Machinist's design, not a missing feature.

**The alternative the captain should weigh against adoption.** Of the seven things Machinist subsumes for a single-shot lane, four (`cwd` pinning, one timeout, group kill, exit-code capture) are a short shell wrapper. The three that are genuinely hard to reproduce well are the escaped-descendant pipe handling, the atomic durable result publication, and the bounded truncation-honest log. If FirstMate wants only those three, the honest question is whether they justify a Go toolchain dependency, a TOML schema dependency, and a six-week-old upstream — or whether ~150 lines of shell plus a small result writer buys most of it with no new dependency at all. This experiment does not answer that; it is the captain's call, and it is the one I would put in front of them.

**No architectural adoption follows from this experiment.** The measurements are in; the decision is not mine.

---

## 8. Evidence index

All under `/mnt/e/FirstMate-Cleanroom/experiments/machinist/evidence/`. Each directory holds `cmd.txt` or `worker.toml`, `stdout.txt`, `stderr.txt`, `exitcode.txt`, `wall_seconds.txt`, and that run's `datadir/runs/<run_id>/{result.json,events.jsonl}`.

| Slug | Measurement | Process exit | `result.state` |
|---|---|---|---|
| `m1-happy-path` | happy path, env scrub, injected vars | 0 | `succeeded` |
| `m2-injection` | shell metacharacters inert | 0 | `succeeded` |
| `m2-hashswap` | `command_hash` unchanged across executables | 0 | `succeeded` |
| `m2-unknown-command` | unknown command name | 2 | *(no run)* |
| `m2-bad-repo` | nonexistent repository path | 2 | *(no run)* |
| `m2-nongit` | non-git directory | 2 | *(no run)* |
| `m3-linked-worktree` | linked worktree resolves to itself | 0 | `succeeded` |
| `m3-subdir` | worktree subdirectory silently widened | 0 | `succeeded` |
| `m3-main-subdir` | main-checkout subdirectory widened | 0 | `succeeded` |
| `m3-gitadmin` | `.git/worktrees/<n>` refused | 2 | *(no run)* |
| `m4-spoof` | child forges the status line | 0 | `succeeded` |
| `m4-nonewline` | partial line collides with the status line | 0 | `succeeded` |
| `m4-fresh-datadir` | per-invocation data dir, one result | 0 | `succeeded` |
| `m4-concurrent` | two runs, identical directory mtimes | 0, 0 | `succeeded` ×2 |
| `m4-unwritable` | mode-500 data dir, child never started | 1 | *(no run)* |
| `m5-timeout` | SIGKILL residue: dirty worktree + orphan | 124 | `timed_out` |
| `m6-exec124` | executor exits 124 | 124 | `failed` |
| `m6-exec130` | executor exits 130 | 130 | `failed` |
| `m6-exec7` | executor exits 7 | 7 | `failed` |
| `m6-cancel` | SIGINT to Machinist | 130 | `cancelled` |
| `m7-firehose` | 40 MiB output, explicit truncation event | 0 | `succeeded` |
| `m8a-ambient` | credential baseline (positive control) | 0 | `succeeded` |
| `m8b1-ghconfigdir` | `GH_CONFIG_DIR` separation works | 0 | `succeeded` |
| `m8b2-gitconfigenv` | `GIT_CONFIG_*` lever stripped by Machinist | 0 | `succeeded` |
| `m8b3-emptyhome` | `HOME` + `GH_CONFIG_DIR` separation | 0 | `succeeded` |
| `m9-implement` | claude implementation → local committed candidate | 0 | `succeeded` |
| `m9-capability-check` | same env proven unable to publish | 0 | `succeeded` |
| `m10-stdin` | stdin closed after the prompt; no tty | 0 | `succeeded` |
| `gotest.log` | subject test suite, 114 pass / 0 fail / 0 skip | 0 | n/a |

**Reproducing.** `source experiments/machinist/env.sh`, then `experiments/machinist/mrun.sh <slug> <command> <repo> <prompt>`. Configuration in `experiments/machinist/mconfig/`, executors in `experiments/machinist/execs/`, scratch repository in `experiments/machinist/scratch/`.
