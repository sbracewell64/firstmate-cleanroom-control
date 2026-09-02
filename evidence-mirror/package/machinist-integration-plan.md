# Machinist integration — a reasoned deferral, with the interface specified anyway

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: knowledge-work
product_contract_source: Captain clean-room directive, 2026-09-01, section 10
authored_by: scout task cleanroom-architecture-synthesis, 2026-09-02
status_of_this_document: DESIGN ONLY - Machinist was never built or executed on this host
owns: the Machinist adoption position, the smallest typed interface if it is adopted,
      the must-never-own list, and the re-open conditions
recommendation: DEFER ADOPTION for the first implementation
```

**Master document:** [`architecture-synthesis.md`](architecture-synthesis.md) owns the shared
vocabulary and the component list this document refers to. Grading legend and citation forms: §0.1
there.

---

## 1. The recommendation, stated first

> **Defer adoption. Build the first implementation without Machinist.**
>
> Not because Machinist is bad — its execution core is a genuinely good bounded local execution
> substrate, and it is better at process supervision than shell — but because **it replaces nothing
> that either executed proof exercised**, because **it structurally cannot host the one lane it would
> most obviously serve**, and because **its contract has changed roughly monthly for six weeks**.
>
> Adopting it now would be adding machinery ahead of a concrete blocker, which is the exact failure the
> corpus measured: governing machinery roughly tripled — 36,425 → 105,214 lines of shell across
> 38 days — while landed throughput fell about ninefold over the same window, reaching a six-day period
> with **zero** landings (`corpus:§0`, OBSERVED there).

**The deferral is falsifiable and cheap to reverse.** §5 specifies the exact interface that would be
adopted, §6 names the four experiments that would settle the unknowns, and §7 names the concrete
conditions that would re-open the question. If the captain rules for adoption, §5 is implementable as
written.

**This is a recommendation, not the decision.** The decision is registered as a durable captain hold,
`cleanroom-machinist-substrate-decision-machinist-adoption-scope`, raised by the machinist scout and
deliberately left open by it.

---

## 2. What the proofs say about Machinist — nothing, and that is the finding

**OBSERVED.** Neither proof used Machinist, mentions it in its stage table, or has a stage it would
occupy.

| Proof stage that produced work | How it actually ran | Would Machinist have helped? |
|---|---|---|
| Proof A's candidate production | `git apply` of a **byte-pinned patch**, tree asserted against a pinned digest — **D0** | **No.** There is no agent turn to bound. The proof deliberately has no authoring step so that it measures the *path*, not a model's coding. |
| Proof A's qualification run | the qualification tool's own daemon, its own detached worktree, its own agent invocations, its own timeouts | **No.** That tool already owns process execution for its steps, and it bounds every agent invocation by its own timeout (`nm-scout:§3.6` theme 4, `no-mistakes` PR #810). |
| Proof B's option application | `git apply` of a **byte-pinned patch**, applied bytes verified by identity | **No.** Same reason. |
| Proof B's ruling | an external party writing a comment | **No.** Not a local process at all. |

**INFERRED, and it is the crux:** the architecture in
[`architecture-synthesis.md`](architecture-synthesis.md) has **no component whose responsibility is
"run an agent turn as a bounded local process"**. Component **D2** invokes the qualification tool, and
that tool owns the process execution of its own steps. Machinist's strongest offering — bounded process
execution with a typed outcome — has **no consumer** in the architecture the proofs established.

Adopting it would therefore mean **inventing a consumer for a substrate**, which is backwards.

---

## 3. The three findings that make the deferral more than caution

### 3.1 Steering is structurally impossible, and that is decisive

**DOCUMENTED (`machinist-scout:§5.2`, OBSERVED there at `internal/runner/runner.go:191, 422-432`):** the runner
writes the prompt to the child's stdin and **immediately closes the pipe**. It is called exactly once.
There is **no code path anywhere that writes to a running child again**.

> **A Machinist run is one prompt in, one process, one outcome — a batch job.**

The scout states the consequence plainly and it is correct: a mid-run steering channel *has no analogue
and cannot have one*. Everything that depends on writing to a live agent — correcting a confused
worker, **delivering an ask-user decision so the worker can answer its own gate**, nudging a stalled
lane — is foreclosed.

**This bites the architecture at exactly one place, and it is the place that matters most.** Lane A's
`DECISION_OWED` state ([`architecture-synthesis.md`](architecture-synthesis.md) §4.1) exists because a
qualification gate parks and must be answered **into the running lane**. A Machinist-hosted lane cannot
receive that answer. So the one delivery lane the architecture actually has is the worst fit for the
substrate.

### 3.2 "Bounded" means bounded interface, not bounded blast radius

**DOCUMENTED (`machinist-scout:§3.1`, OBSERVED there):** a grep for every sandbox primitive across all non-test Go
returns **three hits, all false positives**. No resource limits, no filesystem confinement, no
privilege drop. What exists is: no shell (worker-owned argv), a pinned working directory, a process
group used for killing rather than confinement, a **git-environment scrub** (a genuinely good control,
tested), and three injected variables. **Everything else in the parent environment is inherited
verbatim — every API key, every token.** And the shipped reference configuration **explicitly disables
the agents' own sandboxes** (`examples/worker.toml:10,14`).

> **The architecture must not read Machinist's boundedness as containment.** On this axis it offers
> essentially nothing beyond what a plain subprocess already has.

### 3.3 SIGKILL with no grace produces exactly the state teardown refuses to discard

**DOCUMENTED (`machinist-scout:§3.3`, OBSERVED there at `internal/runner/process_unix.go:16-25`):** on timeout or
cancellation, Machinist sends **SIGKILL to the process group with no SIGTERM and no grace period**. A
timed-out coding agent is killed outright with no chance to commit or flush.

**INFERRED, and specific to this architecture:** that leaves a **dirty worktree with uncommitted
changes**, which is precisely the state the corpus's teardown rule treats as *never landed* and refuses
to discard (`corpus:` via `boundary:§7.4`). So a Machinist timeout does not produce a clean failure; it
produces an **unrecoverable-work refusal** that a human must resolve.

### 3.4 The maturity profile, measured

**DOCUMENTED (`machinist-scout:§1.4`, OBSERVED there):** 399 commits over roughly six and a half weeks; tags v0.1.0
through v0.4.0 all cut within **three days**; contributors 384 / 21 / 1, i.e. effectively solo;
**four incompatible config migrations already**, three of them removals of whole features; self-declared
early-access.

Against that, the engineering quality is markedly high — strict TOML and JSON parsing, constant-time
token comparison, atomic write-fsync-rename for the result file, and a genuinely thorough test suite
including adversarial escaped-descendant cases.

> **INFERRED: the code you would depend on is good; the contract you would depend on has changed
> roughly monthly.** That is the correct shape for a deferral rather than a rejection.

---

## 4. What Machinist must never own — unchanged, and it is the load-bearing half

**Even under adoption**, these stay with the workflow authority. Each row names the collision.

| # | Must never own | Why |
|---|---|---|
| 1 | **Work admission** | The trigger scheduler is a real, durable, autonomous work source: cron, interval, and GitHub-label triggers admit jobs and **write back to the forge** (`machinist-scout:§4.1`). A fleet that delegated this would have work entering it that it never dispatched, never briefed, and cannot account for. **Triggers are opt-in**: a config with no trigger table starts no scheduler goroutines. Ship one. |
| 2 | **Landing authority** | The shipped `shepherd` prompt **merges pull requests**, gated only by a GitHub label anyone with write access can add (`machinist-scout:§4.3`). This architecture's landing authority is a one-use, head-bound authorization whose spend constructs the act ([`architecture-synthesis.md`](architecture-synthesis.md) §7). **A fleet must never run shepherd against a repository it delivers into.** |
| 3 | **Task identity, attempt budgeting, retry policy** | Machinist's managed retry is a **30-second lease timeout**, not a decision. This architecture's is arithmetic against a durable record (component **D6**). |
| 4 | **Worktree lifecycle and teardown** | Machinist never creates, inspects, or cleans a worktree; it only refuses non-git paths. The recoverable-work test stays here — and §3.3 makes it *more* necessary, not less. |
| 5 | **Delivery-mode selection and the qualification pipeline** | Nothing in Machinist models these. |
| 6 | **Decision holds and escalation** | A Machinist run cannot pause, ask, and continue. `DECISION_OWED` has **no representation** (§3.1). |
| 7 | **Cross-task supervision** | `max_concurrent_jobs` is a count, not a policy. |
| 8 | **The delivery lifecycle in prompt form** | The real orchestrator is **488 lines of prompt** — `foreman.md` and `shepherd.md` — reimplementing task identity, worktree isolation, branch and PR lifecycle, repair budgets, and durable resume state **in GitHub issue comments** (`machinist-scout:§4.2`). Adopting `foreman` would not delegate execution; it would hand the whole delivery lifecycle to a **second authority keeping its own state where this architecture cannot see it**. |

**Credit where due, recorded rather than omitted:** `foreman.md` says *"Never merge"* twice, and the
project's own README states *"Machinist hands back a pull request. It does not decide what ships."*
The default workflow stops at a reviewable pull request. It is `shepherd`, not `foreman`, that collides
with landing authority.

---

## 5. If adopted: the smallest typed interface

Specified so the deferral is a decision rather than an omission. **Direct mode only.**

```
machinist run --command=<approved-name> --repo=<absolute path to the task worktree> \
              --prompt=<text> [--model=<alias>]

  → exit code   : typed — 0 success | N executor's own code | 124 timeout
                          | 130 cancelled | 1 runner failure | 2 config/usage
  → stdout+stderr : the child's own streams, live, to the caller's streams
  → <data_dir>/runs/<run_id>/result.json   : the typed Result
  → <data_dir>/runs/<run_id>/events.jsonl  : ordered, timestamped, base64, bounded,
                                             and EXPLICITLY MARKED when truncated
```

The caller supplies a **command name**, an **absolute repository path**, and a **prompt**. Nothing
else. It cannot name an executable or a shell string: the argv is resolved worker-side from the
approved-command table (`machinist-scout:§1.2`, `§2.4`).

### 5.1 The five adoption rules

| # | Rule | Reason |
|---|---|---|
| 1 | **Direct mode only.** Never run the control plane. | This single choice eliminates all three significant gaps at once — at-least-once re-execution, the missing per-job read, and the unreadable managed logs are **managed-mode-only** (`machinist-scout:§5.3`). |
| 2 | **No trigger table, and no `foreman`/`shepherd` commands** in the shipped config. | §4 rows 1, 2, 8. |
| 3 | **Never branch on 124/130 without reading `result.json`.** | An executor that itself exits 124 or 130 is **indistinguishable by exit code alone** from a Machinist timeout or cancellation; only the `state` field disambiguates (`machinist-scout:§2.3`). This is a wrong-subject trap in the exit-code surface. |
| 4 | **Pass the task worktree's own path, never a subdirectory.** | `ResolveRepository` runs `git rev-parse --show-toplevel` and uses **that** as the working directory. A linked worktree resolves to **itself** — verified by execution (`machinist-scout:§3.2`) — but a **subdirectory silently widens** to the repository root with no warning. |
| 5 | **Treat every timeout as producing a dirty worktree.** | §3.3. The recoverable-work refusal is expected behaviour, not an incident. |

### 5.2 What it would replace, honestly

| FirstMate machinery | Replaced? |
|---|---|
| process-group termination, escaped-descendant handling, write deadlines on blocked output, drain grace | **yes, and better than shell** — this is Machinist's strongest 680 lines, with three dedicated tests for session-detached descendants holding pipes open (`machinist-scout:§5.1`) |
| structured, bounded, **truncation-honest** log capture | **yes.** `events.jsonl` is ordered, timestamped, byte-exact, size-bounded, and emits an explicit truncation event while **live streaming continues**. That last property maps directly onto the three-valued rule: a truncated log **says** it is truncated rather than silently reading as complete |
| the approved-command boundary | **yes** — a cleaner expression of "approved capabilities against logical repositories" than an argv assembled inline |
| per-run token accounting | **yes**, for the two executors it has native collectors for, plus a generic file-based fallback |
| **everything in §4** | **no** |

**And the honest total:** the architecture's kernel (**K1**–**K6**) and Lane B (**R1**–**R3**) contain
no process execution at all, and Lane A's only long-running process is the qualification tool's own.
So the replacement set above, while real, currently has **no caller**.

### 5.3 The one upstream contribution worth making either way

**RECOMMENDED (`machinist-scout:§2.4`).** The run id is random and appears **only on stderr**, so a
caller must scrape stderr or scan the data directory to find its own `result.json` — even though the
Go API already exposes a `RunID` field the CLI does not pass through. A `--result-json` or `--run-id`
flag on `machinist run` is a handful of lines, removes the only real ugliness in the substrate
contract, and is squarely within the project's stated scope. It is worth contributing **whether or not
this architecture adopts Machinist**, because it is the difference between a typed result and a scraped
one.

---

## 6. The four experiments that would settle the unknowns

**Nothing about Machinist's runtime behaviour has been observed.** No Go toolchain exists on this host
and no prebuilt binary exists anywhere in the clean room, so the scout **could not build or execute
it** (`machinist-scout:§0`, UNPROVEN there). Every execution-guarantee claim above is read-not-run.

| # | Experiment | Settles |
|---|---|---|
| **E1** | Confirm the exit-code table end to end, **especially an executor that itself exits 124** | whether §5.1 rule 3 is a real hazard or a theoretical one |
| **E2** | Time a real timeout and inspect the worktree afterwards | whether SIGKILL leaves the dirty state §3.3 predicts |
| **E3** | Drive a managed job, suspend the worker past the 30-second lease, observe the duplicate execution directly | whether at-least-once is reachable in practice — relevant only if managed mode is ever considered |
| **E4** | Point `--repo` at a linked task worktree and confirm the resolution | whether the good half of §5.1 rule 4 holds as the scout's local `git` reproduction predicts |

**All four are cheap**, and E1/E2/E4 together are the minimum before any adoption. **They are not on
the first-implementation increment list**, because deferral means not spending the time.

---

## 7. Re-open conditions — what would change this recommendation

Named concretely, so the deferral is a decision with an expiry rather than a permanent no.

| # | Condition | Why it changes the answer |
|---|---|---|
| **R1** | The architecture acquires a component whose responsibility is **"run an unsupervised bounded single-shot agent turn"** — a scout probe, an audit pass, a batch transformation | that is Machinist's stated best fit, and it needs no steering, benefits from the typed result and bounded log, and tolerates SIGKILL on timeout |
| **R2** | Machinist ships a **config-schema stability commitment**, or two consecutive releases with no breaking migration | §3.4's maturity objection expires; the code was never the objection |
| **R3** | Machinist gains a **mid-run stdin channel** | §3.1's structural objection expires and supervised lanes become reachable — but this is a **change to the execution model**, not a missing flag, so treat it as unlikely |
| **R4** | The first implementation's own process handling produces a **concrete, measured defect** of the class Machinist's runner solves — an escaped descendant holding pipes open, a blocked-output hang, a lost result | this is the *direct path exposing a concrete blocker*, which is the only sanctioned reason to add machinery |

**Until one of those holds, this architecture treats process execution as a solved problem it does not
own**, and says so in the record rather than leaving the absence to be read as an oversight.

---

## 8. Could-not-observe register

| # | Question | Value |
|---|---|---|
| 1 | Does Machinist behave at runtime as its source describes? | **could-not-observe** — no Go toolchain, no binary, never built or executed (`machinist-scout:§0`). One claim was confirmed by execution: `git rev-parse --show-toplevel` resolves a linked worktree to itself, which is the exact call the resolver makes. |
| 2 | Would a Machinist-hosted lane be cheaper than the current path? | **UNPROVEN.** No measurement exists on either side. |
| 3 | Does `--result-json` exist upstream now? | **could-not-observe at this pin.** The scout read `75964acbdb944b4456a51c9bfaa4948e76b0c041` (v0.4.0-4) and found no `--json` anywhere in the CLI; the project moves fast enough that this may already have changed. |
| 4 | Does adopting the runner reduce total machinery? | **INFERRED no, currently** — it adds a dependency and a config surface while replacing code this architecture does not yet have. That inference flips under re-open condition R1. |
