# no-mistakes as mandatory candidate qualification — the integration contract

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: knowledge-work
product_contract_source: Captain clean-room directive, 2026-09-01, section 10
authored_by: scout task cleanroom-architecture-synthesis, 2026-09-02
status_of_this_document: DESIGN ONLY - nothing here has been executed
owns: the qualification composition - pre-gate predicate set, outcome consumption, custody rules,
      repair/retry budgets, exact-head qualification, and the fence's content dimension
```

**Master document:** [`architecture-synthesis.md`](architecture-synthesis.md) owns the shared
vocabulary (§0.3), the Lane A state machine (§4), the merge predicate (§7), and the component list
(§8). This document owns everything between **"a candidate exists locally"** and **"the candidate is
qualified at an exact head"** — components **D1** and **D2**, and the parts of **D6** that budget a
qualification repair. It does not restate the merge, the authorization, or the disposition.

Grading legend and citation forms: [`architecture-synthesis.md`](architecture-synthesis.md) §0.1.

---

## 1. The rule, stated once

> **Qualification is mandatory. No candidate reaches the landing chokepoint without a qualification
> record that names the exact head being landed. There is no bypass flag, no "small change" path, and
> no manual clean verdict that substitutes for it.**

Two facts make that a real constraint rather than a slogan:

- **OBSERVED (Proof A, `proof-a:raw/20260901T225152Z-nc2-merge-attempt.stderr`, read by me):** the forge
  refused a merge whose candidate had not been through the pipeline —
  `Required status check "PR must be raised via no-mistakes" is failing. (HTTP 405)` — with
  `enforce_admins: true`, so the operator's own token could not bypass it. Mandatoriness is enforced
  by the server, not by a rule an agent was told to follow.
- **DOCUMENTED (`nm-scout:§4.3`, OBSERVED there; the gate's own source at
  `no-mistakes:.github/actions/require-no-mistakes/verify.py:21-32`):** that same check is
  a **contributor guardrail, not a forgery-proof security boundary**. A hand-written pull-request body
  reproducing the documented format passes — and Proof A's NC-2 setup demonstrated exactly that, at
  head `b02acfe6` (`obs-a:§3`).

**Both are true at once, and the architecture records both.** Mandatory means *procedurally mandatory,
enforced against accident by the server*. It does not mean cryptographically enforced. Anything built
on the current body-parsing check inherits its stated forgeability, and the record says so rather than
implying coverage it does not have.

---

## 2. The composition, end to end

```
  candidate produced          →  capture the exact head        →  deterministic pre-gate
  (agent turn, or a bounded      (local_head_sha, tree_sha,       (G0-G12, all machine state,
   process execution)             base_sha, branch)                 the last free stopping point)
        │                                                                   │
        │                                                                   ▼
        │                                                   ┌───────────────────────────────┐
        │                                                   │  the FIRST irreversible act    │
        │                                                   │  follows this gate             │
        │                                                   └───────────────┬───────────────┘
        ▼                                                                   ▼
  qualification run  ──►  typed result  ──►  attestation head bind  ──►  QUALIFIED at published_head
        │                      │
        │                      ├── gate object, no outcome  ──►  DECISION_OWED  (Lane B or the captain)
        │                      ├── outcome: failed|cancelled ──►  repair budget (§6)
        │                      └── outcome: ci-monitor-interrupted ──►  CNO, re-enter, spends an attempt
        ▼
  custody rules govern EVERY local action while the pipeline owns the branch (§5)
```

**The seam that matters:** the pre-gate is the **last point at which stopping costs nothing**. Once
the qualification run starts, the pipeline pushes a branch to the remote, and that push is
irreversible.

---

## 3. The deterministic pre-gate — component D1

Every input below is **a command's output**, never a belief. The predicate set is the one Proof A
executed (`proof-a:tools/s6_pregate.py`, read by me at the pinned attempt), with the two content-fence
additions of §7.

| Id | Predicate | Read from | Refusal |
|---|---|---|---|
| **G0** | HEAD is not detached | `git symbolic-ref -q HEAD` | `WRONG_BRANCH` |
| **G1** | branch ≠ the default branch | `git rev-parse --abbrev-ref HEAD` vs the forge's `default_branch` | `WRONG_BRANCH` |
| **G2** | working tree clean | `git status --porcelain` empty | `DIRTY_TREE` |
| **G3** | head recorded, and descended from the pinned base | `git rev-parse HEAD`; `git merge-base --is-ancestor <base> HEAD` | `PRECONDITION_UNMET` |
| **G4** | `HEAD^{tree}` equals the pinned candidate tree | `git rev-parse HEAD^{tree}` | `PRECONDITION_UNMET` |
| **G5** | the diff touches only the path allowlist | `git diff --name-only <base>..HEAD` | `PRECONDITION_UNMET` |
| **G6** | **the config that WILL execute — the default-branch copy — matches its pinned bytes** | `git show origin/<default>:<pipeline config>`, sha256 compared | `PRECONDITION_UNMET`; unreadable → **CNO** |
| **G6b** | **the trusted copy does not enable repo-supplied commands**, so a pushed branch controls nothing that executes | parse of the same trusted copy | `PRECONDITION_UNMET` |
| **G7** | no active run owns this branch | the tool's branch-sync state, **or** its typed `runs_on_current_branch` count | `PRECONDITION_UNMET`; unresolvable → **CNO** |
| **G8** | no pre-existing pull request for this branch | forge PR listing, `--state all` | `PRECONDITION_UNMET` — *a second PR is a duplicate, not a retry* |
| **G9** | **every required context is the display name of a real job at the default branch** | protection contexts vs the `jobs.*.name` strings in the workflow files **at `origin/<default>`** | `PRECONDITION_UNMET`; either side unreadable → **CNO** |
| **G10** | intent present, non-empty, hash matches its pin | sha256 of the intent file | `PRECONDITION_UNMET` |
| **G11** | no forbidden flag in the recorded invocation | string check over the invocation array | `PRECONDITION_UNMET` |
| **G12** | *(new, §7)* the diff contains **no generated or build output** | content classifier over the changed paths + the repository's ignore rules | `PRECONDITION_UNMET` |

### 3.1 The two wrong-subject guards, and why a forward design omits them

**G6/G6b and G9 are the guards that make the pre-gate a check rather than a restatement.** Both are
instances of the class where *a verdict is credited to something the instrument never examined*
(`corpus:§1.1`).

**G6/G6b — validate the config that will actually execute.** The pipeline reads command definitions
and agent selection **only from the trusted default-branch copy at a freshly-fetched pinned SHA**,
never from the pushed SHA, so a contributor cannot self-enable
(`no-mistakes:internal/daemon/manager.go:1019-1021`, `internal/config/config.go:237-243`, both
OBSERVED in `nm-scout:§4.4`). Reading the local worktree's copy would be a **correct read of the wrong
subject**: it would report on a file that never executes. G6b additionally asserts the trusted copy
does not set the flag that would let a pushed branch supply commands.

This forces an **ordering constraint a forward plan gets wrong**: the trusted config must be on the
default branch *before the candidate branch is ever pushed*. If the candidate introduces it, the run
validating the candidate will not use it.

**And it is not merely a read — it is a fail-closed one.** An unreadable trusted tree **aborts the
run** inside the tool rather than silently disabling the boundary
(`no-mistakes:internal/daemon/manager.go:1013-1017`, DOCUMENTED). G6 mirrors that direction: unreadable
is CNO, never "assume fine".

**G9 — a required check whose name matches nothing is never satisfied and never blocks.** A context
that no job produces simply stays `expected`; depending on evaluation, protection either blocks
forever or does not block at all, and **the record still reads as protected either way**. G9 compares
the protection's required contexts to the job display names in the workflow files **at the same ref**,
so a rename on either side is caught before it silently voids the objectivity of the merge predicate.

**OBSERVED in Proof A:** G6/G6b, G8 and G9 are the three of twelve pre-gate predicates the independent
observer could confirm from outside the executor's worktree (`obs-a:§5.6`), and it confirmed the
trusted-config identity itself: `.no-mistakes.yaml` at ref `2ef121a9`, blob `b6c9a207`, sha256 matching
the pin, with no non-comment line enabling repo commands (`obs-a:§2`).

### 3.2 Three-valued, uniformly

An unreadable protection body, an unreachable daemon, or a branch-ownership query that cannot resolve
is **CNO, never a pass**. G7 in particular **must not read "no active run" from an error** — and Proof A
proves the rule earns its keep: the pre-gate's first execution returned `PRECONDITION_UNMET` with
`cnos=['G7']` because the executor's own parser read prose instead of the typed field the surface
prints. The surface was readable the whole time and reported `runs_on_current_branch: 0`; the
**instrument** was the defect. It was repaired, re-run, and passed, with the refusal retained on a
`PROVED` record (`proof-a:refusals.jsonl`, read by me).

**RECOMMENDED, from that incident:** when a predicate has a typed machine field available, read the
field. G7's corrected form reads `branch_sync.state` when present and falls back to the typed
`runs_on_current_branch` count — *an affirmative observation that no run owns the branch, which is not
the same thing as failing to read the surface* (`proof-a:tools/s6_pregate.py`, comment read by me).

---

## 4. Consuming the qualification result — component D2

### 4.1 The verdict is the `outcome:` field, never the exit code

**DOCUMENTED, and it is the single most important integration fact** (`nm-scout:§1.4`, OBSERVED there, citing
`no-mistakes:internal/cli/axi_drive.go:598-666`): the driver returns exit **0** for a parked gate, for
`checks-passed`, for `passed`, **and** for `ci-monitor-interrupted`. Only `failed`/`cancelled` and
operational errors reach exit 1.

> A caller that treats exit 0 as "qualified" accepts a run **parked at an unanswered review gate** and
> a run whose **pipeline was interrupted mid-CI**.

The parse, run against the **captured file** — never a shell variable, never memory:

| Observed in the captured output | Verdict |
|---|---|
| exactly one `outcome:` ∈ `{checks-passed, passed}` | **QUALIFIED** — continue |
| exactly one `outcome:` ∈ `{failed, cancelled}` | `QUALIFICATION_FAILED` |
| exactly one `outcome:` == `ci-monitor-interrupted` | `CNO_INDETERMINATE` — re-enter, **spends an attempt** |
| zero `outcome:`, a `gate:` object present | `QUALIFICATION_PARKED` → `DECISION_OWED` (§8) |
| zero `outcome:`, no gate | `CNO_INDETERMINATE` |
| more than one `outcome:` | `CNO_INDETERMINATE` — an ambiguous surface is not a verdict |

**OBSERVED in Proof A:** `outcome_field: checks-passed`, `exit_code: 0` recorded **and not an input to
the verdict** (`proof-a:qualification.json`, read by me). The verifier I re-ran confirms the exit code
appears nowhere in the fold (§0.2 of the master document).

**Watched red:** NC-5 fed the parser a synthetic exit-0 output carrying `outcome: ci-monitor-interrupted`
and asserted it returned `CNO_INDETERMINATE`, not `QUALIFIED`
(`proof-a:negative-controls.jsonl`, read by me).

### 4.2 `checks-passed` is not terminal, and the record says so

**DOCUMENTED (`nm-scout:§1.4`, `§7.3` G3, OBSERVED there):** `checks-passed` is **not a run status**. It is a hand-back
point — the driver returns while the run stays **non-terminal**, because the CI step monitors the open
pull request until a human merges it. Waiting for `passed` waits on a human merge; treating
`checks-passed` as terminal loses the fact that the run is still open. Both are mistakes, and they are
symmetrical.

**The architecture records both facts as separate fields and checks the second separately:**

```
qualification.outcome_field    = "checks-passed"       # the qualification verdict
qualification.run_status_at_write = "running"          # honest about non-terminality
post_merge.pipeline_terminalized  = { run_status: "completed", value: "observed-good" }
```

**And the terminalization observation must carry a declared bound.** Proof A's first measurement was
taken seconds after the merge, with **no declared bound**, and read `running` — because the CI
reconciler polls on a 30/60/120-second schedule (`no-mistakes:internal/pipeline/steps/ci_checks.go:20-29`).
That premature reading was demoted to non-gating with its reason and replaced by a bounded 16×30s
re-observation that returned `completed` on its first poll (`proof-a:deviations.jsonl D-6`,
`proof-a:terminalization.json`, read by me).

**RECOMMENDED, and it is the generalisation:** *an observation sampled before its mechanism's declared
bound is not a result.* The bound belongs in the pin
([`architecture-synthesis.md`](architecture-synthesis.md) §6.3), **before** the first measurement — not
declared afterwards to justify a re-measurement, which is what made Proof A's fold amendment
contestable (P-A-CAP-1).

**A run that terminalizes as `ci_monitor_interrupted` is CNO for terminalization, and is not a failure
of the merge.** The two are different facts and are recorded apart.

### 4.3 The attestation is the head bind, and it is data only

Extract exactly one marker from the pull-request body, writing the raw marker to a capture file
**before** parsing it. Then require, as three separate observations:

1. **exactly one live marker.** Foreign markers quoted inside step details are neutralised by the
   producer (`no-mistakes:internal/pipeline/steps/prsummary.go:42-46,107-113`, DOCUMENTED), so more
   than one is a defect, not a formatting quirk.
2. **`attestation.head_sha` equals the live published head.**
3. **`review`, `test` and `document` each `completed`.** `skipped` is **not** compliant
   (`verify.py:16-17`, OBSERVED in `nm-scout:§4.3`).

**The attestation is deliberately policy-free** — *"intentionally data only. It does not declare any
step required, passed for a policy, compliant, or mergeable"*
(`no-mistakes:docs/.../pipeline-steps.md:264`, DOCUMENTED). **The architecture supplies that policy
itself and records it**, rather than reading a verdict into the data. This is the difference between
consuming evidence and inheriting a claim.

**Watched red:** NC-6 fed the enforcement logic a body whose attestation head differed by **one
character** and asserted `compliant=false`; NC-3 pushed a commit after the check went green and watched
the required context go red at the new head while its neighbour `test` **stayed green** — a genuine,
target-distinct control (`proof-a:negative-controls.jsonl`, read by me).

**Caveat carried forward, not dropped:** Proof A's attestation recorded `pr: running` and `ci: pending`
at PR-write time (`proof-a:attestation.json`, read by me). The three steps the gate requires were
`completed`; the later two were still in flight, exactly as the producer's snapshot-at-write-time
semantics predict. A consumer that required *all nine* steps `completed` would refuse every compliant
candidate. **Require exactly the three the gate requires, and no more.**

### 4.4 Local head and published head are two facts

The pipeline **may author fix commits**, so the head that lands may not be the head that was committed
locally. That is expected, not a defect. The architecture keeps `local_head_sha` and
`published_head_sha` as **separate fields** and binds **every** downstream stage to the published one —
the corpus's rule that *an identical tree is not identical head-bound evidence… keep old head,
successor head, tree, and applicability as separate fields* (`corpus:§2.2`, DOCUMENTED).

**OBSERVED in Proof A:** local `d29527ed` (tree `7a8d4f55`, the pinned candidate tree) versus published
`281e15b2` (tree `1d88a770`). The independent observer confirmed both, and confirmed that every
downstream binding used the published one (`obs-a:§2`).

---

## 5. Custody — the rules that govern every local action

**DOCUMENTED (`nm-scout:§3.2`, §3.3, OBSERVED there):** branch ownership is a typed state machine — 19 branch-sync
states, 8 `next_action` codes, three run-scoped recovery ref namespaces, and a preserve-anchor that
**fails closed rather than overwriting evidence**. The architecture consumes it rather than
reimplementing it.

| Rule | Why, with the evidence |
|---|---|
| **Read `branch_sync.next_action.code` before any local follow-up commit.** | The codes are the tool's own instruction to the caller; improvising reset/stash/rebase around them is what the custody machinery exists to prevent (`nm-scout:§7.4` rec 6). |
| **Use guarded recovery only when the code is `recover_custody`;** otherwise proceed only when structured status confirms ownership is already returned. | `nm-scout:§3.4`. |
| **Custody recovery settles branch ownership, not content.** After recovery, replace obsolete work from the correct pre-invalidation base rather than building on the recovered-but-obsolete head. | `boundary:§6.5`, OBSERVED there. |
| **Never hand-edit, commit, restart, or start a second run while the pipeline owns the branch.** The one exception is a rebase the pipeline hands back, which the worker resolves and commits itself. | `boundary:§6.5`. |
| **A same-branch push silently supersedes the in-flight run** as `cancelled`, not `failed`. | `nm-scout:§3.5(a)`, `no-mistakes:internal/daemon/manager.go:895`. Treat an unexplained `cancelled` as *someone pushed*, not as *the pipeline broke*. |
| **Post-review HEAD continuity is asserted at every step from Test on**, and Push additionally requires the pushed commit to equal or descend from the **durably recorded review-approved commit**. | `nm-scout:§3.5(b)`, `no-mistakes:internal/pipeline/steps/push.go:112-114`. |
| **Never `--skip review`.** It leaves no approval binding and Push then fails closed — the skipped step takes the push down with it. | `nm-scout:§7.4` rec 4. |
| **Never `--yes`/`-y`.** It is documented as standing consent that explicitly **includes auto-resolving `ask-user` findings**, which defeats the one gate Lane B exists to exercise. | `nm-scout:§6.4`, `no-mistakes:skills/no-mistakes/SKILL.md:294-303`. |
| **Never restart the shared daemon to unstick one lane.** One daemon owns one home and serves every run in it. Use the bounded abort, which refuses to claim success without confirmed quiescence. | `nm-scout:§6.1`, `§7.4` rec 7. |
| **Drive each lane from its own worktree.** An explicit `--run <id>` status is inspection-only by design, and the respond surface has no run selector. | `nm-scout:§6.3`, `§7.4` rec 5. |
| **Abort is the only sanctioned supersession**, and it confirms terminal quiescence before any code changes. Anything else is duplicated pipeline ownership. | `nm-scout:§3.4`; `boundary:§6.5`. |

---

## 6. Repair and retry — deterministic, with budgets

Upstream has **no durable attempt record, no budget, no lineage, and no terminal-state vocabulary**;
retry-versus-stop is judgement with no cross-session memory (`boundary:§7.1`, OBSERVED there). This
architecture does not inherit that gap. Component **D6** owns the arithmetic.

```
attempt record:  { attempt, attempt_budget, failures, terminal }
```

| Rule | Consequence |
|---|---|
| An attempt is spent by re-entering qualification **after a recorded failure**. | A dispatch after a crash or a dead runtime continues the attempt already open; it does not open a new one. |
| **A CNO that resolves on a re-poll inside its declared bound spends nothing.** A bounded wait is not a retry. | This is exactly why the bound must be pinned before the measurement (§4.2). |
| Budget exhausted → **`BUDGET_EXHAUSTED`**, a terminal state, not a prompt to try harder. | Retry-versus-stop becomes arithmetic rather than a judgement call. |
| A re-entry at a **different candidate head is a new candidate**: a new attempt directory, and the previous disposition records that it was superseded. **Never a resume onto a moved head.** | The exact-head law applied to the retry path. |
| **A budget that could not be written is a different terminal state from a budget that was spent.** A bound that was reached and a bound that was never enforceable are different facts. | Imported from the retired fleet's own capacity-deferral vocabulary, which distinguishes them (`boundary:` companion map, `absent_upstream`). |

### 6.1 Repair, when the qualification result is red

**RECOMMENDED.** Two paths, chosen mechanically, never by judgement:

| Observed | Path |
|---|---|
| `outcome: failed` with typed findings whose action is `auto-fix` | the pipeline's **own** repair budget already applied; a further attempt is a **new attempt** against the same candidate and spends budget |
| `outcome: failed` where the findings name a **policy path** | **refuse.** A repair that reaches a workflow file or the pipeline config is the candidate editing the policy that judges it (§7.2) |
| `outcome: cancelled` with cause *superseded by new push* | **not a failure.** Someone pushed. Reconcile custody, re-derive the head, and re-enter — this spends an attempt only if the re-entry follows a *recorded failure* |
| a `gate:` object | `DECISION_OWED`; see §8. The implementation worker **never answers its own finding** |
| `ci-monitor-interrupted` | CNO; re-enter; spends an attempt |

**And the flake question is named, not hidden.** Deciding whether a red required check is a flake or a
real defect is **avoidable cognition (D2-A2)**: the forge reports a conclusion, not a cause. The
machinery that removes it is a base-commit control runner — re-run the identical workflow N times on
the **base** commit and N times on the candidate, and decide from the two rates. Until it exists, this
judgement is a declared D2 and is recorded in the disposition when it fires
([`determinism-assessment.md`](determinism-assessment.md) §4).

---

## 7. The fence: paths, and the content dimension the `.pyc` sweep exposed

### 7.1 What actually happened

**OBSERVED (`proof-a:deviations.jsonl D-4`, `proof-a:qualification.json`, `obs-a:§4 D3`, all read by
me).** The candidate commit `d29527ed` touched exactly two files. The pipeline then authored
`281e15b2`, whose message reads *"no-mistakes(document): docs already accurate for compare(); no
updates needed"* — a step reporting that **no change was needed** — and whose entire content is **five
`.pyc` bytecode files** under `fmproof/__pycache__/` and `tests/__pycache__/`.

Those files were produced by the **test and lint steps, which run after review**, so **review never saw
them**. That commit became the published head, the attested head, the head both required checks went
green on, and the head that landed. The pull-request body says *"build artifacts, likely unintended"*
while its Review section reports *"No issues found"*, and its Test section still asserts a two-file
diff that was true only of the earlier head.

**The path fence passed, correctly.** All five files sit inside `{fmproof/**, tests/**}`, so T5 and T6
as specified both hold, and the executor **deliberately did not invent a new gate mid-run** — raising a
bar the design does not set is the same error as lowering one. Instead the record keeps the pinned
candidate tree `7a8d4f55` and the published tree `1d88a770` as **separate fields**, so no reader can
mistake one for the other.

### 7.2 The implication, stated exactly

> **A path fence bounds *paths* and cannot bound *content*. "The diff is confined to the right
> directories" is a strictly weaker statement than "the diff contains only intended source", and a
> fence cannot tell them apart.**

The fence still does the job it was built for, and that job is **not** this one. Its actual subject is
the corpus's canonical invariant — *a candidate may not alter, select, or supply the acceptance-policy
generation that judges that same candidate* (`corpus:§1.7`, DOCUMENTED) — and against **that** subject
T5/T6 are exactly right, because they read the pull request's own file list from the forge rather than
trusting the intent's out-of-scope prose. Crediting them with content integrity they never examined
would be the wrong-subject class in its purest form.

### 7.3 The repair — three changes, in increasing strength

**RECOMMENDED.**

1. **Give the seed an ignore file.** The specific instance disappears: the pinned lint command
   produces exactly those five files, and the seed carries no `.gitignore`
   (`proof-a:deviations.jsonl D-4`; `obs-a:§8 rec 3`). Cheapest, and it removes the case rather than
   detecting it — the same move as disabling squash and rebase to make the landing identity check
   possible.
2. **Add G12 to the pre-gate and a matching content predicate to the fence.** A **content dimension**
   alongside T5/T6: the changed set contains no file matching the repository's own ignore rules and no
   file whose extension is in a closed generated-output set. Two properties make it honest: the
   condition is **mechanically verified at the point of use**, and it is **anchored to something the
   candidate cannot edit** — the trusted default-branch ignore rules, not a list the candidate ships
   (`corpus:§1.7`, the ruled fix pattern).
3. **Or state plainly in the contract that the fence bounds paths and cannot bound content.** If
   neither 1 nor 2 is built, the honest record says so. What is **not** acceptable is leaving the
   claim implicit, because "confined to the allowlist" then reads as "contains only intended source"
   to every later reader.

**This synthesis adopts 1 and 2**, and treats 3 as the fallback if a content classifier proves to have
no honest instances — in which case, per the corpus's own rule, *delete the exemption branch rather
than guarding it: there is no door to try if there is no door* (`corpus:§1.7`).

### 7.4 The deeper lesson, which is about review ordering

**INFERRED.** The `.pyc` commit is not primarily a fence defect. It is a **review-ordering** fact: the
pipeline's fixed step order runs test and lint **after** review, and the fix commit is built over the
worktree rather than over a named path set, so **content created after review can enter the published
head without review seeing it**. The step order is hardcoded and not configurable
(`nm-scout:§1.1`, OBSERVED there), so this is a property of the tool, not a setting.

The architecture's answer is not to fight the ordering but to **make the two heads separately
observable and separately bound**: the pinned candidate tree and the published tree are distinct
fields; the attestation binds the published head; the fence is re-asserted at authorization time over
the **pull request's own file list**, which is the post-fix reality. A reader can therefore see
exactly what the pipeline added, which is what Proof A's record makes possible and what its observer
used to find the defect independently (`obs-a:§7`).

---

## 8. Gates: the decision the worker may not answer

**DOCUMENTED (`nm-scout:§1.3`, OBSERVED there):** a step parks when it declares `NeedsApproval` **or** when any finding's
effective action is `ask-user`, and an **unclassified finding resolves to `ask-user`** — the pipeline
failing **closed to the human**, working correctly
(`no-mistakes:internal/types/findings.go:409-414`). The review gate's auto-fix budget defaults to
**0**, so blocking review findings park rather than self-fix (`nm-scout:§1.3`).

**The rule, imported wholesale:** *the implementation worker never answers its own ask-user finding.*
A parked gate becomes state `DECISION_OWED`, and the routing is a **pre-registered table**, not a
judgement:

| Gate shape | Route |
|---|---|
| the finding's subject is in the Lane B question catalog | **hand to Lane B** — this is exactly what Lane B is for |
| the finding's subject is outside the catalog | abort the attempt, record the findings verbatim in the captures, escalate. **This is D2-A3**, and the machinery that removes it is a total decision-policy table keyed on `(step, finding.category, finding.action, review_scope)` |
| an unclassified finding | same as above; note it is the pipeline failing closed, not a defect |

**And answer a gate only as a whole.** Responding "fix" on a subset **silently discards every finding
not named, and the discard is invisible because the run simply proceeds** (`corpus:§4.2`, DOCUMENTED).

**Grade a finding before spending authority on it.** Classify each blocking finding **CONFIRMED,
DISPROVED, or CNO** first; a maker may not self-dismiss a reviewer finding, but a deterministic
reproduction or an assignment-distinct reviewer may establish DISPROVED; and *reviewer prose without
source evidence, executable counterexample, or a clearly stated unobservable property is a
hypothesis/CNO, not a proven error* (`corpus:§4.2`, from the captain's own late directive).

---

## 9. The intent string is the acceptance-criteria port

**DOCUMENTED (`nm-scout:§2.4`, §2.5, OBSERVED there):** intent supplied explicitly carries provenance `agent`, which is
**authoritative**; the intent step becomes a pure pass-through; review treats authoritative intent as
**enforceable acceptance criteria** — a change contradicting it must park via an `ask-user` finding;
and a rerun inherits the bytes **verbatim**, with an explicit *"Do not normalize or regenerate this
value"* comment. It is **the only channel by which caller-side machine evidence reaches the reviewer;
there is no structured-criteria input port.**

**The contract this architecture adopts:**

1. The intent bytes are **pinned and hashed before the run**, so their *execution* is deterministic.
   Their **authorship** remains avoidable cognition, recorded as **D2-A1**
   ([`determinism-assessment.md`](determinism-assessment.md) §4).
2. The intent states the acceptance criteria **and the out-of-scope items**. The out-of-scope clause is
   doing real work — it is the fixer fence stated in prose — but **prose is never the evidence**: the
   same boundary is enforced mechanically by T5/T6/G12 over the pull request's own file list.
3. When Lane B produced the change, the intent **cites the ruling**: correlation id and directive, so
   conformance to the ruling becomes enforceable review criteria. **The ruling still does not authorize
   the merge** — a fresh authorization is minted, never transferred
   ([`architecture-synthesis.md`](architecture-synthesis.md) §7.2).

### 9.1 Semantic adapter: only if code cannot transform, and prefer eliminating it

The directive names this explicitly, and the honest answer is:

> **No semantic adapter is required anywhere in the qualification composition, and none should be
> built.** Every input the pipeline needs is either machine state or pinned bytes, and every output it
> produces is a typed field.

| Boundary | Is a semantic adapter needed? | Why |
|---|---|---|
| pre-gate → invocation | **no** | every predicate is a command's output; the invocation is an array with pinned bytes |
| invocation → verdict | **no** | the `outcome:` field, the attestation JSON, and the branch-sync object are all typed (`nm-scout:§5.3`) |
| verdict → forge observation | **no** | check runs and pull-request fields are typed |
| findings → routing | **no**, once the policy table exists | findings are typed objects with closed vocabularies for `action`, `severity`, `source`, `review_scope`, `category` (`nm-scout:§5.3`) |
| **plan / decision record → `--intent` bytes** | **the one place, and it should be eliminated** | there is no structured-criteria port. **Eliminate it with a deterministic serializer** that renders a typed verification contract into intent bytes — the transformation is total and mechanical, so a model is not required for it. Only if that serializer cannot be written does an adapter belong here, and then it is a declared D2 with its output pinned and hashed before the run. |

**The general rule this follows:** an adapter that transforms a typed structure into another typed
structure is code. A model belongs at a boundary only where the input is genuinely unstructured, and
here exactly one such boundary exists — the captain's original request — which is upstream of this
document entirely.

---

## 10. What this integration does not establish

| # | Question | Value |
|---|---|---|
| 1 | Is qualification enforceable against a deliberate forger? | **observed-bad, and stated.** The enforcement action self-documents as a contributor guardrail; NC-2's setup turned it green on a hand-written body. The missing primitive is a **signed attestation**, which the tool names and deliberately defers (`nm-scout:§7.3` G1). |
| 2 | Do the paths Proof A did not exercise behave as described? | **DOCUMENTED, not observed.** Every `--skip` case, Bitbucket's attestation-free bodies, crash recovery, and the non-GitHub providers are from the pinned source via `nm-scout:`, not from a run. |
| 3 | Does a content classifier (G12) have honest instances beyond build output? | **UNPROVEN.** If it does not, per §7.3 the branch should be deleted rather than guarded. |
| 4 | Would the base-commit flake control (D2-A2) change any decision Proof A made? | **could-not-observe.** No required check went red on the real candidate; the only reds were the deliberate negative controls. |
| 5 | Does one shared daemon per home constrain a multi-lane fleet? | **DOCUMENTED (`nm-scout:§7.3` G5).** One failure domain: a daemon restart interrupts every in-flight run, and interrupted CI monitors terminalize as `ci_monitor_interrupted` — which is exit 0. The architecture's answer is §4.1's parse plus §5's never-restart rule; it has not been measured under load. |
