# Compound Engineering isolation baseline

**Phase 0, Track 2.** Establish and verify a clean-room-scoped Compound
Engineering (CE) capability. No implementation increment was started.

| | |
|---|---|
| **Date** | 2026-09-02 (UTC) |
| **Scoped config dir** | `/mnt/e/FirstMate-Cleanroom/runtime/ce-config` |
| **CE source (pinned)** | `/mnt/e/FirstMate-Cleanroom/tools/compound-engineering` @ `cd31338034920c9a8239e8a3fc390778edd06ab8` |
| **CE version** | `3.24.0` (`plugin.json:3`) |
| **Claude Code** | `2.1.258` |
| **no-mistakes (isolated)** | `v1.61.0 (0af0be6) 2026-08-31T14:04:25Z` at `/mnt/e/FirstMate-Cleanroom/tools/bin/no-mistakes` |
| **Host** | WSL2 Linux, user `shane` |
| **Prerequisite read** | `artifacts/scouts/compound-engineering-usage-report.md` |

Machine-readable companion: `ce-isolation-baseline.json`.
Operating policy inside the scope: `runtime/ce-config/cleanroom/POLICY.md`.

## Grading legend

Three values, never two.

| Grade | Meaning |
|---|---|
| **OBSERVED-GOOD** | I ran it and watched the intended result, with a control where a control was possible. |
| **OBSERVED-BAD** | I ran it and watched it fail or fall short. A result, not a gap. |
| **COULD-NOT-OBSERVE** | I could not establish it. A result, not an omission. |
| **DOCUMENTED** | The subject's own code or docs assert it; I read the assertion, not the behavior. |
| **RECOMMENDED** | My judgment for the clean-room, not a property of the subject. |

---

## 1. Scoped install, and the host left alone

**OBSERVED-GOOD.**

CE was installed only into the scoped config dir, from the pinned local
checkout. No global or host install was performed.

```
export CLAUDE_CONFIG_DIR=/mnt/e/FirstMate-Cleanroom/runtime/ce-config
claude plugin marketplace add /mnt/e/FirstMate-Cleanroom/tools/compound-engineering
  -> Successfully added marketplace: compound-engineering-plugin (exit 0)
claude plugin install compound-engineering@compound-engineering-plugin
  -> Successfully installed plugin (scope: user) (exit 0)
claude plugin list
  -> compound-engineering@compound-engineering-plugin  Version: 3.24.0  Status: enabled
claude plugin details compound-engineering
  -> Skills (33)  Agents (0)  Hooks (0)  MCP servers (0)  LSP servers (0)
     Always-on: ~2,011 tok
```

### The pin is real

`plugins/installed_plugins.json` records the source commit itself:

```
"gitCommitSha": "cd31338034920c9a8239e8a3fc390778edd06ab8"
```

and the installed snapshot is byte-identical to the pinned source:

| | Source checkout | Installed snapshot |
|---|---|---|
| File count (excl. `.git`) | 1073 | 1073 |
| Tree digest | `e25a034d61f8c17910b8e567a6a08714d432f8021f335d091bfb7d7b5daa5fb7` | `e25a034d61f8c17910b8e567a6a08714d432f8021f335d091bfb7d7b5daa5fb7` |
| `plugin.json` inode | 1125899906901608 | 281474976974221 |

Same bytes, different inodes: a real copy, not a link. The running corpus stays
at `cd31338` until someone deliberately re-installs. The source checkout was
unmodified afterwards (`git status --short` empty, HEAD still `cd31338`).

### Host `~/.claude` untouched — with a positive control

The same probe was run against the host config before the install, after the
install, and after every live scoped session, and against the scoped config as
the probe's own positive control. The probe is kept at
`runtime/ce-config/cleanroom/host-isolation-probe.sh` and is re-runnable.

| Field | Host (before, after, final) | Scoped (positive control) |
|---|---|---|
| `marketplace_names` | `claude-plugins-official` | `compound-engineering-plugin` |
| `settings.json` `enabledPlugins` | `ABSENT_KEY` | `{"compound-engineering@compound-engineering-plugin":true}` |
| `settings.json` `extraKnownMarketplaces` | `ABSENT_KEY` | present, pointing at the pinned checkout |
| `~/.claude.json` `enabledPlugins` | `ABSENT_KEY` | — |
| `plugins_tree_entry_count` | 669 → 669 → 669 | 1358 |
| `plugins_tree_sha256` | `d0ad0ae8…` unchanged throughout | `2dd0162b…` |
| `ce_string_hits_in_config_surface` | **0** | **3** |
| `ce_paths_under_plugins` | **0** | **2** |
| `settings.json` sha256 | `9aff3f33…` unchanged throughout | `374dca08…` |

The host result is trustworthy **because** the identical probe returns non-zero
CE hits on the scoped dir. A zero without that control would be
could-not-observe.

**One host field did change**, and it is not CE: `known_marketplaces.json`'s
`lastUpdated` on the pre-existing `claude-plugins-official` entry moved from
`2026-09-02T00:53:48.729Z` to `2026-09-02T01:35:50.709Z`. Structurally the file
is identical with that timestamp removed — same single marketplace, same source,
same install location, and the marketplace directory's own contents and mtime
(`Sep 1 15:16`) did not move. The CE usage scout recorded the same benign
self-refresh. **Which process refreshed it is COULD-NOT-OBSERVE** — several
Claude Code sessions run on this host and the scoped sessions do not write to
`~/.claude`. The probe now strips `lastUpdated` before hashing so this stops
producing a false alarm.

### Consequences of the scope that an operator must know

**OBSERVED-GOOD, each verified in the scoped config.**

1. **The scoped dir starts with no credentials.** A first `claude -p` returned
   `Not logged in · Please run /login`. Resolved by symlinking, not copying:
   `<scope>/.credentials.json -> /home/OPERATOR/.claude/.credentials.json`. The
   secret stays on ext4 at mode 0600 and never lands on the `/mnt/e` Windows
   mount, whose permissions are nominal (`drwxrwxrwx`). After the symlink a
   scoped session authenticated (`PONG`).
2. **The scope does not inherit the host's `settings.json`** — not its model
   (`opus[1m]`), `effortLevel: high`, theme, or its `SessionStart` hooks
   (`gh-axi`, `chrome-devtools-axi`, `lavish-axi`, the Herdr state hook). A CE
   lane gets harness defaults unless the recipe sets them.
3. **Project instructions still leak in from the working directory.** The
   `ce-plan` control run was executed inside this task's Firstmate worktree, and
   the CE session picked up that repo's `CLAUDE.md` — its reply addressed the
   operator as "Captain". A CE lane must run in the clean-room repo, not nested
   under another project's instruction tree.

---

## 2. Cross-model review / egress: OFF

The clean-room requirement is that `ce-doc-review` in this config will not reach
a second provider. The honest answer is three layers of unequal strength.

### Where the documented switch actually lives

**DOCUMENTED, and structurally important.** `cross_model_review_mode` is a
**repo-local checkout key**, not a config-dir key. It is resolved from
`<repo-root>/.compound-engineering/config.local.yaml` then `config.yaml`, where
`<repo-root>` is `git rev-parse --show-toplevel`
(`skills/ce-doc-review/references/cross-model-review.md:32`, and the shared
`ce-config-layers` block at `:24-30`). Valid values are `auto` (the default) and
`off`; anything else falls through to `auto`. The same key gates
`ce-code-review` (`skills/ce-code-review/SKILL.md:28`;
`skills/ce-code-review/references/cross-model-review.md:41`).

**So the scoped `CLAUDE_CONFIG_DIR` cannot hold this key.** Setting it is a
per-repo obligation. A template is provided at
`runtime/ce-config/templates/compound-engineering-config.yaml` and was applied
to the verification lab repo. It is honoured by the model reading the skill, not
by code — treat it as a declaration of intent, not as enforcement.

### The enforced control: environment, in the scoped settings

**OBSERVED-GOOD.** The scoped `settings.json` carries:

```json
"env": { "CROSS_MODEL_PEERS": "none", "CROSS_MODEL_MAX_PEERS": "0" }
```

Two things were verified, both live in the scoped config:

- The keys are delivered to the session's Bash tool
  (`PEERS=none MAX=0`), and
- they are **inherited by a nested shell** (`sh -c '…'` printed the same), which
  is what makes them reach a CE worker script however it is launched.

Every CE peer dispatch passes through one of exactly three worker scripts, and
all three read these variables before contacting a provider:

| Script | Allowlist gate | Max-peers gate |
|---|---|---|
| `skills/ce-doc-review/scripts/cross-model-doc-review.sh` | `:496` | `:503` |
| `skills/ce-code-review/scripts/cross-model-adversarial-review.sh` | `:449` | `:456` |
| `skills/ce-pov/scripts/cross-model-pov.sh` | `:434` | none |

`CROSS_MODEL_PEERS=none` covers all three; `CROSS_MODEL_MAX_PEERS=0` covers two.
Both are set.

### The chokepoint test, with a red negative control

**OBSERVED-GOOD (gate holds) and OBSERVED-BAD (the ungated default really does
egress).** `cross-model-doc-review.sh` was run directly against a throwaway
two-line document I wrote for this purpose — no clean-room material — with a
host family of `claude` and a fixed route of `codex`:

| Run | Setting | Result |
|---|---|---|
| **A** | `CROSS_MODEL_PEERS=none` | `provider 'codex' not in CROSS_MODEL_PEERS allowlist; skipping` … `no different-provider peer reachable`. **No dispatch, no egress line, 0 artifacts.** |
| **B** — negative control | *(no allowlist)* | `peer run: provider=codex route=codex model=gpt-5.6-luna (effort xhigh) … full document content egresses to this provider via this route`. **codex was launched.** |
| **C** | `CROSS_MODEL_PEERS=codex` | Same dispatch as B — the allowlist is the discriminator, not something else. |
| **D** | `CROSS_MODEL_MAX_PEERS=0` | `CROSS_MODEL_MAX_PEERS=0; cross-model pass disabled`. **No dispatch.** |

The control went red exactly where it had to: without the gate, the document
leaves. With it, the script exits before choosing a route.

**Two honest notes on run B.** First, I intended to strip every peer CLI from
`PATH` as a second safety net and **failed** — a second `codex` exists at
`/mnt/c/Users/shane/AppData/Roaming/npm/codex` (Windows npm), which my
`PATH` filter did not remove. So B and C really did launch codex with the
document embedded. The document was the trivial throwaway I authored for the
test; no clean-room material was exposed. Second, that Windows codex is broken
(`Error: Missing optional dep …`, Node 22.22.1), so it aborted before any
network call — but **I cannot claim no packet left the machine**, only that the
process failed at module load. Treat "codex is broken here" as availability
noise, never as a control.

### The weak layer, named as weak

**OBSERVED-BAD as a boundary.** The scoped `settings.json` also denies the peer
CLIs and the publishing commands:

```json
"permissions": { "deny": [
  "Bash(codex:*)", "Bash(grok:*)", "Bash(cursor-agent:*)", "Bash(cursor:*)",
  "Bash(opencode:*)", "Bash(git push:*)", "Bash(gh pr create:*)",
  "Bash(gh pr merge:*)", "Bash(gh-axi pr create:*)", "Bash(gh-axi pr merge:*)" ] }
```

Verified, each with a control:

- `codex --version` → `Permission to use Bash with command codex --version has been denied.`
- `/bin/echo control-ok` → ran.
- `git push origin HEAD` → denied. `git status --short` → ran.
- Deny **holds under `--permission-mode bypassPermissions`**.
- **But it is bypassed by an indirect call:** `sh -c "/home/OPERATOR/.local/bin/codex --version"` **ran** and printed `codex-cli 0.146.0`.

It is a command-prefix match on the Bash tool input. It catches an accident. It
is **not** a boundary and must never be cited as proof that egress cannot
happen. The environment layer is the boundary, because it is read inside the
script rather than matched outside it.

### End-to-end evidence from the live run

**OBSERVED-GOOD, with a stated limit.** The live `/ce-plan` control run (§3)
auto-invoked `ce-doc-review` in non-interactive mode. Its output names
`coherence`, `adversarial`, and `feasibility` reviewers — `adversarial` is one
of the three conditional trio lenses that gate the cross-model pass
(`references/cross-model-review.md:13`), so the cross-model gate really was
reached, not skipped for lack of an activated lens. No cross-model artifact was
written, no egress announcement appeared, no CE scratch root
(`/tmp/compound-engineering-1000/`) was created, and no `codex`, `grok`, or
`cursor-agent` process was launched by the run.

**Limit:** absence of a peer process is consistent with the gate holding, but on
its own it is could-not-observe — it cannot distinguish "gate fired" from "pass
never armed". The decisive evidence is the chokepoint test above, plus the fact
that `ce-doc-review` contains exactly two scripts
(`cross-model-doc-review.sh`, `peer-job-runner.py`) and no `curl`, `wget`, or
API URL anywhere in the skill directory. `peer-job-runner.py` is a process
supervisor that receives its argv from the gated script.

### The other egress paths — blocked by policy, not invoked

**DOCUMENTED. None were run.**

| Path | Mechanism | Status |
|---|---|---|
| `ce-explain` publishing | Publishes a page to `ht-ml.app` — public internet (`ce-explain/SKILL.md:77`) | FORBIDDEN for clean-room material |
| `ce-pov` cross-model panel | `scripts/cross-model-pov.sh` shells out to a second provider on an `oracle`/panel summons | FORBIDDEN; also covered by `CROSS_MODEL_PEERS=none` at `:434` |
| `ce-proof` | Publishes to / reads from `proofeditor.ai` | FORBIDDEN |
| `ce-code-review` | Invocation is itself standing authorization for its peer route (`ce-code-review/SKILL.md:28`) | FORBIDDEN — review belongs to no-mistakes |

Recorded in `runtime/ce-config/cleanroom/POLICY.md`.

---

## 3. The implementation spine is invocable

**OBSERVED-GOOD.**

### Resolution, with a negative control

A scoped session asked for its own skill names returned:

```
compound-engineering:ce-plan
compound-engineering:ce-doc-review
compound-engineering:ce-work
compound-engineering:ce-worktree
compound-engineering:lfg
compound-engineering:ce-commit-push-pr
```

Negative control: `/compound-engineering:nope-not-real` returned
`Unknown command: /compound-engineering:nope-not-real`. So a resolving command
is distinguishable from a non-resolving one, and the six above are not "no error"
masquerading as a pass.

### Live positive control — `ce-plan`

Run in a throwaway git repo with the clean-room `.compound-engineering/config.yaml`
applied. Command:

```
/compound-engineering:ce-plan Add a --version flag to a small hello.sh script in
this repo that prints 0.1.0 and exits 0. Trivial throwaway; produce the plan
artifact only, write no implementation code.
```

Exit 0, 6m35s. It produced a 73-line implementation-ready plan at
`ce-artifacts/plans/2026-09-01-2135-feat-hello-version-flag-plan.md` with front
matter `artifact_contract: ce-unified-plan/v1`,
`artifact_readiness: implementation-ready`, and the sections Goal Capsule,
Product Contract, Requirements, Scope Boundaries, Planning Contract,
Implementation Units, Verification Contract, Definition of Done.

Two things fell out of that run:

- **`docs_root` works.** Artifacts landed under `ce-artifacts/`, not `docs/`.
- **`ce-plan` auto-invokes `ce-doc-review`.** The run performed a non-interactive
  document review of its own plan without being asked. So `ce-doc-review` was
  *also* live-exercised, and the spine's second stage may fire whether or not
  the operator calls it. Plan for it; do not be surprised by it.

### `ce-work` — where its behavior ends, and what is required to keep it there

**OBSERVED-BAD for the bare form; OBSERVED-GOOD for the guarded form.** All
citations against `cd31338`.

`ce-work` **does not stop at a local commit by default.**

| Location | What it says |
|---|---|
| `skills/ce-work/SKILL.md:12` | "In standalone use, **the shipping workflow takes the verified change through review and delivery.**" |
| `skills/ce-work/SKILL.md:48` | Standalone "must read `references/shipping-workflow.md` before quality checks or **delivery**." |
| `skills/ce-work/references/shipping-workflow.md:91` | Step "**Commit and Create Pull Request**" |
| `…/shipping-workflow.md:99` | "Load the `ce-commit-push-pr` skill with `branding:on` to handle **committing, pushing, and PR creation.**" |
| `…/shipping-workflow.md:112` | Local-commit-only is the *alternative*: "If the user prefers to commit without creating a PR, load the `ce-commit` skill instead." |

The boundary the clean-room needs exists, but only in one mode:

| Location | What it says |
|---|---|
| `skills/ce-work/SKILL.md:54` | "Return-to-Caller Mode performs **implementation and local verification only**. It must not enter Phase 3-4 or run final simplify, code review, **PR creation**, CI watching, babysitting, or any other standalone shipping action; the caller owns those gates." |
| `skills/ce-work/SKILL.md:50` | The standalone code-review completion gate "does not apply in Return-to-Caller Mode." |
| `skills/ce-work/references/return-to-caller.md:5` | "performs implementation and local verification only … then returns a structured summary instead of running the standalone shipping tail." |
| `…/return-to-caller.md:32` | "Any goal/workflow engine used here must not open a PR, run the owner workflow tail, or bypass the caller-owned gates." |
| `…/return-to-caller.md:28` | The envelope must carry `standalone_shipping_skipped: true`. |
| `skills/ce-work/references/input-triage.md:27` | The mode is entered by a leading literal `mode:return-to-caller` token, stripped before anything else. |

**Configuration required to guarantee the boundary — RECOMMENDED, two parts:**

1. **Always invoke `ce-work mode:return-to-caller <plan-path>`.** Never the bare
   form. This is the skill's own boundary and the only place the corpus promises
   no push and no PR. Confirm the returned envelope carries
   `standalone_shipping_skipped: true`; treat its absence as a boundary failure,
   not as a formatting quirk.
2. **Give the CE lane's checkout no git remote** until the candidate is handed
   to no-mistakes. Then a dropped mode token cannot publish, because there is
   nothing to push to. This is mechanical rather than instructional.
   Note the asymmetry: `lfg` documents a no-remote refusal
   (`skills/lfg/SKILL.md:35` — "No remote means shipping is local-only … skip
   every push, PR create/edit, and CI-watch action"), but `ce-commit-push-pr`
   documents none, so with a remote absent it fails at `git` rather than
   refusing cleanly. Either way nothing is published.

The `permissions.deny` entries on `git push` / `gh pr create` are a third,
deliberately weak catch — see §2's bypass.

### `lfg` and `ce-commit-push-pr` — both exist, both FORBIDDEN

**OBSERVED-GOOD (existence).** Both are present in the pinned corpus
(`skills/lfg/SKILL.md`, `skills/ce-commit-push-pr/SKILL.md`) and both resolve as
commands in the scoped config (skill listing above).

| Command | Why it is forbidden for clean-room production work |
|---|---|
| `lfg` | `skills/lfg/SKILL.md:3` — "it **pushes and opens a PR without stopping**." `:49` — step 8 invokes `ce-commit-push-pr` with `mode:pipeline`. It runs hands-off with no check-ins and bypasses no-mistakes entirely. |
| `ce-commit-push-pr` | `skills/ce-commit-push-pr/SKILL.md:3` — "**Commit, push, and open a PR.**" It is also what `auto_babysit` (default true) chains into a CI watcher. Publication and landing belong to no-mistakes. |

Both are marked FORBIDDEN in `runtime/ce-config/cleanroom/POLICY.md`.
`ce-commit` (`skills/ce-commit/SKILL.md:8` — "No push, no PR") is the safe
local-commit skill if one is ever needed directly, but the sanctioned path is
`ce-work mode:return-to-caller`, which commits locally on its own.

---

## 4. Operator recipe — starting a CE-scoped implementation lane

**RECOMMENDED. Not executed end to end; §3's `ce-plan` run is the only live
spine invocation.**

### 4.0 Preconditions

- The clean-room repo is checked out somewhere **outside** any other project's
  instruction tree (see §1 consequence 3).
- That checkout has **no git remote** yet (`git remote` prints nothing).
- `<repo-root>/.compound-engineering/config.yaml` exists, copied from
  `runtime/ce-config/templates/compound-engineering-config.yaml`.
- `<repo-root>/.gitignore` ignores `ce-artifacts/` and `.context/`.

### 4.1 Enter the scope

```bash
export CLAUDE_CONFIG_DIR=/mnt/e/FirstMate-Cleanroom/runtime/ce-config
cd <clean-room repo root>
"$CLAUDE_CONFIG_DIR/cleanroom/host-isolation-probe.sh" "$HOME/.claude" HOST      # expect ce_* = 0
"$CLAUDE_CONFIG_DIR/cleanroom/host-isolation-probe.sh" "$CLAUDE_CONFIG_DIR" SCOPED  # expect ce_* > 0
```

The scope supplies `CROSS_MODEL_PEERS=none`, `CROSS_MODEL_MAX_PEERS=0`, and the
deny list automatically. Do not export peer variables by hand and do not
override them.

**Model and effort.** The scope does **not** inherit the host's `opus[1m]` /
`effortLevel: high`. Either pass them per invocation
(`claude --model opus --effort high …`) or add `"model"` and `"effortLevel"` to
the scoped `settings.json`. Pick one and record which — an unpinned lane is not
reproducible.

### 4.2 Plan

```bash
claude --model opus --effort high -p \
  '/compound-engineering:ce-plan <the work, stated as an outcome>'
```

Expect an implementation-ready plan under `ce-artifacts/plans/…-plan.md` and an
automatic non-interactive `ce-doc-review` pass folded into the same run.

### 4.3 Independent document review (when a separate pass is wanted)

```bash
claude -p '/compound-engineering:ce-doc-review mode:non-interactive ce-artifacts/plans/<plan>.md'
```

`mode:non-interactive` matters: the review's interview form blocks on a
synchronous human, which an autonomous lane does not have. Coverage should read
that the cross-model pass was **disabled by checkout config**. If instead it
names an unavailable route or an un-attestable host, the repo config was not
read — stop and fix it before continuing.

### 4.4 Implement to a local committed candidate

```bash
claude --model opus --effort high -p \
  '/compound-engineering:ce-work mode:return-to-caller ce-artifacts/plans/<plan>.md'
```

The `mode:return-to-caller` token is **mandatory**. On return, check:

- `status: complete`
- `standalone_shipping_skipped: true`
- `changed_files` matches the plan's units
- `verification_evidence` has one entry per behavior-bearing unit
- `git log` shows local commits and `git status` is clean
- `git remote` still prints nothing, and no PR exists

Any missing item is a boundary failure. Stop; do not hand it on.

### 4.5 Hand off to no-mistakes — mandatory, and the only publisher

CE stops at the local commit. Delivery is the isolated
`v1.61.0` binary, never CE:

```bash
git remote add origin <the real remote>     # only now
/mnt/e/FirstMate-Cleanroom/tools/bin/no-mistakes axi run
```

The worker that starts the run drives it through its own gates
(`no-mistakes axi respond`) to a PR and green CI. Landing authority is
unchanged and is not CE's to hold.

Never substitute `lfg`, `ce-commit-push-pr`, or `ce-code-review` for any part of
this step.

---

## 5. Could-not-observe — stated as results

- **No declared Firstmate verifier covers any observation here.**
  `bin/fm-verify.sh --list` names `browser`, `pr-checks`, `merge-clean`,
  `review-exec`, `review-mutation` — none applies to third-party plugin
  isolation. Every grade above was reached by hand under the three-valued rule.
  **This is a reported gap, not a pass.**
- **Which process refreshed the host's `known_marketplaces.json` timestamp** is
  unattributed (§1).
- **Whether any network packet left the machine during control runs B and C** is
  unknown. The codex process failed at Node module load; I did not capture
  traffic.
- **`cross_model_review_mode: off` was never observed *doing* anything.** It is a
  model-compliance instruction. Its effect was not isolated from the environment
  layer, which was also in force. Graded DOCUMENTED, and the reason the
  environment layer exists.
- **The spine was not run end to end.** `ce-work` was never invoked, in either
  mode. Everything in §3 about `ce-work`'s completion behavior is read from its
  `SKILL.md` and references — DOCUMENTED-by-the-subject, not measured. §4 is a
  recipe, not a transcript.
- **`ce-explain`, `ce-pov`, `ce-proof`, `ce-code-review` were not invoked**, per
  the task. Their egress descriptions are read, not measured.
- **`permissions.deny` coverage is not enumerated.** One bypass was found and is
  reported; there may be others. Do not treat the list as exhaustive.
