# The first implementation — ordered increments, each with its watched red

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: knowledge-work
product_contract_source: Captain clean-room directive, 2026-09-01, section 10
authored_by: scout task cleanroom-architecture-synthesis, 2026-09-02
status_of_this_document: DESIGN ONLY - no increment below has been built
owns: the ordered increment list, the watched-red acceptance per increment, and the do-not-build list
headline: 12 increments plus one decision taken first. 9 promote code that already exists and ran,
          1 builds the single missing component, 2 close a could-not-observe.
```

**Master document:** [`architecture-synthesis.md`](architecture-synthesis.md) owns the component list
(§8) these increments build, and the vocabulary (§0.3). Grading legend and citation forms: §0.1 there.

---

## 1. The starting position — most of this already exists and ran

**OBSERVED.** The two executed proofs left working code on disk. The first implementation is
substantially a **promotion of that code into named components with single responsibilities**, not a
rewrite. Building it from scratch would discard the only thing in this whole effort that has been seen
to work end to end.

| Component | Existing code that already does this, and ran | Change required |
|---|---|---|
| **K1** `observe`, **K2** `journal` | `proof-a:tools/proofa.py` and `proof-b:tools/proofb.py` — capture-before-parse, three-valued observation, stage enter/exit, trace append, refusal | **merge the two into one library.** Two harnesses is two sources of truth for one contract |
| **K3** `pin` | `proof-b:inputs/PINNED.json` and its sha256 sidecar — the shape is right and it was **verified never rewritten** across the whole run | promote from a hand-written file to a **written-once record with a refusing writer** |
| **K4** `fold` | `proof-a:tools/s15_disposition.py`, `proof-b:tools/s14_disposition.py` — the latter **refuses because the record is write-once** | add the **derived-ledger** rule (§4, I1) |
| **K5** `vocabulary` | `proof-b:tools/build_schema.py`, `render_reply_contract.py`, `validate_envelope.py`, and `proof-b:schemas/fm-sol-control-v1.schema.json`; plus `proof-a:schemas/fm-proof-vocab-v1.schema.json` | make the two schemas share their `$defs` block properly, as the design intended |
| **K6** `control-harness` | `proof-b:tools/s0b_falsifiers.py`, `s0b_v7_addendum.py`; `proof-a:tools/s4_negative_controls.py`, `s4b_local_controls.py` | add `neighbours` as a **required** field and read `target` from the pin (§4, I3) |
| **D1** `candidate` | `proof-a:tools/s5_candidate.py`, `s6_pregate.py` | add **G12** (§4, I4) |
| **D2** `qualify` | `proof-a:tools/s8_verdict.py`, `qualparse.py`, `run_axi.sh` | none structural |
| **D3** `forge-observe` | `proof-a:tools/s9_s10_gate.py` | none structural |
| **D4** `authorize`, **D5** `land` | `proof-a:tools/s11_s12_merge.py`, `s13_s14_post.py`, `s14_bounded.py` | add **per-record store isolation** (§4, I7) |
| **D6** `attempt` | *(does not exist)* | **the one genuinely new component in Lane A** |
| **R1** `boundary` | `proof-b:tools/s3_boundary.py` | none structural |
| **R2** `compile` | `proof-b:tools/s4_compile.py`, `s5_readiness.py`, `s6_emit.py`, `s8_poll.py` | CHANGES 2, 3, 4 (§4, I9) |
| **R3** `consume` | `proof-b:tools/ladder.py`, `s9_s12_consume.py` — **already carries the corrected three-valued gate** | CHANGE 6 (§4, I10) |
| — | `proof-a:tools/dod_verify.py` — an independent verifier that **imports none of the harness** | **promote to a declared verifier** — this is D2-S1's eliminating machinery, and it already exists |

**INFERRED, and it is why the increment list is short:** the two proofs together already implement
**fourteen of the fifteen** components. Exactly one — **D6**, attempt arithmetic — does not exist at
all. The rest of the work is **one merged kernel** and the six changes execution taught.

---

## 2. Ordering, and why

1. **Kernel first (I1–I3)**, because every other component types on it. Building Lane A on an
   un-pinned fold is how Proof A's `PROVED` became contestable.
2. **Lane A next (I4–I8)**, because Lane B reuses its landing path and because Lane A is the lane that
   ships.
3. **Lane B after (I9–I10)**, because its subject is a candidate Lane A produced.
4. **The two could-not-observe closers last (I11–I12)**, because each needs most of the rest to exist.

**One thing is decided before any of it (I0), because deciding it afterwards is the corpus's largest
self-inflicted wound.**

---

## 3. I0 — decide the bootstrap exception before building the gate

**Not code. A decision, written down first.**

The retired fleet's largest architectural mistake was a gate that governed its own delivery path: the
publication guard was itself unlanded, so no candidate could be published; lanes were finished, clean,
validated and **parked**; the queue reached **359 items** while roughly a dozen fully validated
candidates sat in custody (`corpus:§3.1`, OBSERVED there). The ruled lesson is to write the exception
**before** the gate exists.

**Acceptance:** the exception text of [`architecture-synthesis.md`](architecture-synthesis.md) §9.3 is
written into the pin, and its falsifiable check — *the protected branch's first-parent chain carries
exactly one non-merge commit* — is a predicate in I7's acceptance set. Proof A used the exception
exactly once and the check confirms it (DoD 6b, re-run by me).

**Cost: an hour. Skipping it cost the retired fleet its throughput.**

---

## 4. The increments

Each increment names: what is built, and the **watched red** that must be seen before the increment is
trusted. *A control is not real until it has been seen to fail for its own reason*, and the target is
**read from the pin, never from the observation** ([`architecture-synthesis.md`](architecture-synthesis.md)
§6.4).

---

### I1 — the kernel: observe, journal, pin, fold

**Build.** One `observe`/`journal` library merged from the two proof harnesses. A `pin` writer that
refuses a second write. A `fold` that reads only the journal and the pin, refuses without stage
coverage, and **derives every ledger** in the disposition from the journal and trace.

**Watched red — five, and each closes a defect that was actually observed:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | write the disposition twice | **refuse the second write.** Proof A wrote it four times (P-A-CAP-1) |
| 2 | delete one `STAGE_EXIT` from the trace | **refuse with `CNO_AT_<that stage>`** — not proceed. Proof A's T8 did exactly this and **stopped the merge** |
| 3 | attempt to amend the pinned fold rule after the first observation | **refuse.** Proof B's pin carries `amendable: false` and `amendments: 0` |
| 4 | record an instrument defect in the trace and **omit it** from the ledger input | **the projection still contains it.** This is P-B-CAP-3 made structurally unreachable |
| 5 | coerce a could-not-observe into a pass in the fold | **refuse.** The non-coercion rule is a code path, not a habit |

**Positive acceptance, and it already passes:** re-run both proofs' folds from their records and get
`PROVED` and `CNO_AT_B-S3`. I did this on 2026-09-02 and both reproduce
([`architecture-synthesis.md`](architecture-synthesis.md) §0.2).

---

### I2 — one vocabulary source, and the generated reply contract

**Build.** One schema file per protocol, sharing a `$defs` block. A validator both producer and consumer
call. A renderer that **walks the schema** to emit the reply contract, with a **byte self-check** after
posting. `vocabulary_digest` carried in every envelope.

**Watched red:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | a ruling with one required field misspelt | `RULING_MALFORMED`, **and the refusal names the field** |
| 2 | a ruling whose `vocabulary_digest` is another schema generation | `RULING_MALFORMED` — drift caught mechanically, not discovered by a ruling that will not attach |
| 3 | edit the posted reply contract by hand | the renderer's self-check is a **build failure**, not a diff to eyeball |
| 4 | add an unknown field to any envelope | refused, because `additionalProperties: false` on every object |

**Positive acceptance:** the reply contract contains **no field name typed by a human**, verifiable by
regenerating it and byte-comparing. **OBSERVED in Proof B: the ruler's field names matched on the first
attempt, zero malformed blocks** (`obs-b:§8` rec 1).

---

### I3 — the control harness, with the tautology removed

**Build.** A falsifier runner that reads `target` **from the pin**, records `observed` and — as a
**required field** — the state of every neighbouring control at the same head, and computes
`distinct = (target == observed) ∧ (neighbours stayed green)`.

**Watched red — and this one is subtle, because the control under test is the harness itself:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | a mutation that reddens a **neighbouring** control | record `distinct = false` **with its reason**, not a pass. This is P-A-CAP-4: Proof A's NC-1 reddened both required checks and `distinct_match` was computed as `target == observed` from one call — a tautology |
| 2 | relabel a falsifier's target after the observation | **refuse**, because the target is read from the pin. This is P-B-CAP-5: falsifier 1's pinned target was `V2` and the executed record declared `V1` |
| 3 | a three-valued predicate whose falsifier can reach only one non-green branch | **report the unreachable branch as unwatched.** This is INSTR-3: V7 had no `observed-bad` branch, so its falsifier could only redden the CNO path |

**Positive acceptance:** every declared refusal code in both vocabularies has at least one falsifier
whose pinned target is that code, and every falsifier ran **before the run**, not immediately before
the act it falsifies (P-A-CAP-9).

---

### I4 — the candidate state machine and the pre-gate

**Build.** The candidate states, and G0–G12
([`no-mistakes-integration.md`](no-mistakes-integration.md) §3).

**Watched red:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | change the pipeline config **only in the candidate worktree**, leaving the default-branch copy untouched | **G6 passes** — and that is correct, because the trusted copy is what executes. Then change the **trusted** copy and watch G6 go red. *Both halves*, or G6 is credited with a subject it never examined |
| 2 | enable repo-supplied commands in the trusted copy | **G6b red** |
| 3 | rename a workflow job while leaving the required context unchanged | **G9 red.** A required check whose name matches nothing is never satisfied and never blocks, **and the record still reads as protected** |
| 4 | make the branch-ownership surface unreadable | **G7 could-not-observe** — never "no active run". Proof A's pre-gate refused on exactly this, and the defect was the **instrument**, not the world |
| 5 | put a build artifact in the diff | **G12 red** |
| 6 | dirty the worktree | **G2 red** |

**Positive acceptance:** the pre-gate is the **last free stopping point**, and its refusal costs
nothing — verifiable because no forge state exists when it runs.

---

### I5 — the qualification adapter

**Build.** The `outcome:`-field parse, attestation extraction and head bind, and the branch-sync read.

**Watched red:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | a captured output with exit 0 and `outcome: ci-monitor-interrupted` | `CNO_INDETERMINATE`, **not** `QUALIFIED`. Proof A ran this as NC-5 |
| 2 | a captured output with a `gate:` object and no `outcome:` | `QUALIFICATION_PARKED` → `DECISION_OWED` |
| 3 | an attestation whose head differs by **one character** | non-compliant. Proof A ran this as NC-6 |
| 4 | a body carrying two attestation markers | refuse — more than one live marker is a defect, not a formatting quirk |
| 5 | an attestation with `document: skipped` | non-compliant; `skipped` is not `completed` |

**Positive acceptance:** the exit code appears **nowhere** in the fold. My re-run of Proof A's
independent verifier confirms this holds in the executed record.

---

### I6 — the forge observer

**Build.** Exact-head check reading with a completeness predicate, the eight-condition merge predicate,
and the policy generation digest.

**Watched red:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | cap the check-run listing below its reported total | **`CNO_INCOMPLETE_UNIVERSE`**, not "no failing check". *Zero findings is not evidence of cleanliness unless the verifier also establishes its completeness predicate* (`corpus:§1.2`) |
| 2 | present a check run that is `success` at a **different** head | **the required context is not satisfied.** Each entry records its own head, so relabelling one cannot re-attribute the others |
| 3 | present `mergeable: null` | **CNO**, re-polled under the declared bound, then `CNO_INDETERMINATE` — never `false` |
| 4 | change one required context after the digest was recorded | the policy generation digest **differs**, and the change is visible in the record |
| 5 | fail two ladder conditions at once | **both are reported**, not just the first |

---

### I7 — the authorization store and the landing chokepoint

**Build.** The one-use authorization with `minted → spending → spent | refused`, **per-record store
isolation**, the act constructed at spend, the single merge call, and the post-merge identity check.

**Watched red — the strongest set, and four of them already have executed evidence:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | attempt a merge on a candidate that has not been through qualification | **HTTP 405**, refused **by the forge**, with `enforce_admins: true` so the owner's own token cannot bypass. **Already observed** (`proof-a:raw/…-nc2-merge-attempt.stderr`) |
| 2 | call the merge with `sha` set to the base | **HTTP 409**, and a follow-up read confirms `merged: false`. **Already observed** (`proof-a:raw/…-nc4-moved-head.*`) |
| 3 | tamper with the constructed act after minting | the digest check **refuses** before the call |
| 4 | mint a second authorization over a record in `spending` | **refuse.** Resolve from the **forge**, not from the record |
| 5 | put one malformed record in the store | **the other records still work.** At the retired fleet's barrier **84%** of the authority store was quarantined because one out-of-vocabulary record blinded the whole store (`corpus:§1.4`, OBSERVED there) |
| 6 | land, then compare the merge commit's second parent to a **different** head | `IDENTITY_MISMATCH`, terminal, **never reported as success** |
| 7 | push a second non-merge commit directly to the protected branch | **refused**, and the bootstrap-exception check (I0) shows exactly one |

**Positive acceptance:** the landed merge commit's **second parent is the authorized head**, on the live
forge. **Already true and still true**: I re-verified it on 2026-09-02 (DoD 4b).

**And one repository setting is part of this increment, not an afterthought:** squash and rebase merges
**disabled**, so a true merge commit is the only possible landing and the identity check is a pure
identity test rather than a patch-id heuristic.

---

### I8 — attempt arithmetic

**Build.** The one genuinely new Lane A component: a durable `{attempt, attempt_budget, failures,
terminal}` record, and the rules of [`no-mistakes-integration.md`](no-mistakes-integration.md) §6.

**Watched red:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | exhaust the budget | **`BUDGET_EXHAUSTED`**, a terminal state — not a prompt to try harder |
| 2 | a CNO that resolves on a re-poll **inside** its declared bound | **spends nothing.** A bounded wait is not a retry |
| 3 | re-enter at a **different** candidate head | a **new** attempt record, with the prior disposition recording that it was superseded — never a resume onto a moved head |
| 4 | make the attempt record unwritable | a **different** terminal state from budget exhaustion. A bound that was reached and a bound that was never enforceable are different facts |

**Why this is the new component:** upstream has **no durable attempt record, no budget, no lineage and
no terminal-state vocabulary**; every `attempt` variable in its `bin/` is a local loop counter
(`boundary:§7.1`, OBSERVED there). Without it, nothing stops the same failing work being re-dispatched
indefinitely across sessions, because conversation memory is the only record that it already failed.

---

### I9 — the boundary classifier and the request compiler

**Build.** BP1–BP7, the compiler, the derived correlation id, the readiness probe, the one-issue
emitter, and the complete retriever. Includes CHANGES 2, 3 and 4 from
[`sol-control-v1.md`](sol-control-v1.md) §9.

**Watched red:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | an option patch touching a path on the deny list | **`BOUNDARY_CAPTAIN_RESERVED`** → routed to the captain **as a record**; no request is compiled |
| 2 | an option that does not revert cleanly | **stop** — BP3 executes the revert; it does not read a claim about it |
| 3 | an evidence locator that is a **branch** URL | **refused by schema, before emission** |
| 4 | a locator whose bytes hash to something other than its declared digest | **per-ref refusal.** The aggregate is a conjunction of per-ref observations, **never a count** (P-B-CAP-4) |
| 5 | `base_sha` equal to `head_sha` | **refuse** — the diff would resolve to an empty range (INSTR-1) |
| 6 | cap the comment fetch below the reported total | **`CNO_INCOMPLETE_UNIVERSE`**, not "no ruling found" |
| 7 | change the evidence set while the correlation id stays constant | the `evidence_digest` in `valid_while` **differs** (CHANGE 4) |

---

### I10 — the ruling consumer

**Build.** V1–V10, L1–L5, the three-valued terminal gate, the total directive→action map, the
applied-bytes identity check, and the receipt. Includes CHANGE 6 (the credential-path independence
axis).

**Watched red — the six synthetic universes, which is the method that found INSTR-4:**

| # | Universe | Must resolve to |
|---|---|---|
| 1 | one valid ruling | `CONSUMED` |
| 2 | a ruling bound to the wrong head | `REFUSED_MISMATCH` |
| 3 | a malformed ruling | `REFUSED_MALFORMED` — **named as malformed, not as a transport failure** |
| 4 | **two rulings, neither naming the other in `supersedes`** | **`REFUSED_AMBIGUOUS`, with nothing consumed and the newer not picked** |
| 5 | a comment that merely mentions the correlation id in prose | `CONSUMED` — the mention **neither counted nor suppressed** |
| 6 | no ruling at all | `CNO_TRANSPORT` |

**Universe 4 is the increment's whole point.** A terminal gate keyed on `observed-bad` alone let a
lineage fork — which the vocabulary classes as **CNO** — fall straight through to consumption
(P-B-CAP-3). **A three-valued vocabulary needs a three-valued gate.**

**Two further watched reds:**

| # | Mutation | Must be seen to |
|---|---|---|
| 7 | a ruler login equal to a maker login | independence **`observed-bad`**; nothing consumed. And separately, an unmeasurable case → **CNO**. Both branches must be reachable, or V7 is not watched red (INSTR-3) |
| 8 | a directive whose byte-pinned patch does not produce the pinned tree | `REFUSED_MISMATCH` — the consumption identity check is a conjunction of three conditions, and each must be individually falsifiable |

---

### I11 — run Lane B against a **live, open** candidate

**This increment exists to close a could-not-observe, and it is the highest-value thing on the list
after the kernel.**

**OBSERVED (P-B-CAP-2, `obs-b:§5.2`):** the executed round trip's subject was a **merged** pull request
in an **archived** repository. L1 passed trivially, L3 passed against protection nobody could change,
and **falsifier 4's live half and falsifier 5's positive live half could not be run at all**. So the
proof establishes that the ladder's **comparators** behave correctly and leaves **could-not-observe** on
whether the ladder catches a real moving candidate.

**Build.** Nothing new. Run I9 + I10 against a live, open, qualified candidate.

**Watched red — on the live forge, not against a comparator:**

| # | Mutation | Must be seen to |
|---|---|---|
| 1 | push one trivial commit to the candidate branch **after** the ruling | **`RULING_SUPERSEDED`**, and a **new** correlation id is required. The old ruling is **not** carried forward |
| 2 | change one required context in branch protection **after** the ruling | **`RULING_SUPERSEDED`** via L3 |
| 3 | move the default branch with **byte-identical** policy | **L3 stays green.** *A design that only ever proves its refusals fire has not shown that it can also stay quiet* — and the negative half **was** run in the executed proof, so this half is already evidenced |
| 4 | close the pull request after the ruling | **`RULING_SUPERSEDED`** via L2 |

**Acceptance:** the staleness claim rests on **the control**, not on the comparator.

---

### I12 — Lane A attempt 2, under a fold rule pinned in advance

**This increment closes the other could-not-observe, and it is a captain decision, not an engineering
one.**

**OBSERVED (P-A-CAP-1, `obs-a:§4 D1`):** Proof A's disposition was written four times and its outcome
changed **because the fold rule was rewritten mid-run with the answer in view** — not because any
observation changed value. Every amendment is disclosed and the final fold is reproducible; the criteria
were simply not fixed before the result.

**Two honest options, and the captain owns the choice** (registered as
`cleanroom-proof-a-observer-decision-proof-a-verdict-under-amended-fold`):

| Option | What it buys |
|---|---|
| **Accept `PROVED` as recorded**, with its amendment disclosed | nothing further is spent; the record's own caveat travels with every citation of it |
| **Commission attempt 2 under a pinned rule** | the same `PROVED` would carry **pre-registered authority**. Proof B demonstrates this is achievable: its rule was pinned before the first measurement, it pre-registered its expected verdict, and it graded **stricter** than expected |

**Acceptance if commissioned:** the pin exists before the first observation, carries
`amendable: false`, names the **expected** outcome, and the run's actual outcome is compared against
that expectation in the record — whichever direction it falls.

---

## 5. What this plan does **not** schedule, and why

Two experiments are named, sized, and deliberately left for the captain.

| Experiment | What it would measure | Why it is not scheduled |
|---|---|---|
| **The control-plane economics experiment** — N concurrent decision subjects against a **moving** trunk | whether the plane's economics close. The retired fleet measured **22 requests, 5 rulings, 45% superseded** — a property of **volume against movement** (`corpus:§3.2`, OBSERVED there), and one round trip against a frozen candidate says nothing about it either way | it is a different experiment with real forge cost, and it is a registered captain decision (`control-plane-economics-experiment`, disposition `CAPTAIN_DEFERRED`) |
| **The four Machinist runtime experiments** | whether Machinist behaves as its source describes | adoption is deferred ([`machinist-integration-plan.md`](machinist-integration-plan.md) §1), and deferral means not spending the time |

---

## 6. Deliberately not built

### 6.1 Imported verbatim from the corpus's own do-not-import list

**DOCUMENTED (`corpus:R9`).** The scout that read the retired fork named three things not to import,
and this plan adopts all three.

| # | Not built | The corpus's reason, and the measurement behind it |
|---|---|---|
| 1 | **The external ruling plane as built** — long-lived forum threads polled through a paginated API | the **concept** earned its place: a delegated engineering authority that is neither the operator nor the maker. Its **realisation** produced six-day blindness, lineage forks, and a **23% ruling rate** across **31 control directories**. This architecture keeps the concept and replaces the realisation with **one issue per question** |
| 2 | **The 12-collision vocabulary register** | a well-run remedy for a problem a clean start avoids by **naming things once, in one owner, and reserving authority-bearing words**. This package has one glossary ([`architecture-synthesis.md`](architecture-synthesis.md) §0.3) and one owner per contract |
| 3 | **182 shell scripts / 98,560 lines with a 1.39:1 test-to-code ratio as the substrate** | several of the corpus's named incidents are **artifacts of that substrate**: `grep -c` counting lines rather than matches, a broken-pipe write in a racing transition, argv length limits truncating briefs, a quoted command substitution executing during transport. Whether another substrate has fewer defects overall is **UNPROVEN**; that these specific ones are substrate-shaped is **OBSERVED** |

### 6.2 Not built because no property in §3 of the master needs it

| Not built | Why |
|---|---|
| a **decision surface** / composed control-plane read layer | every record has one writer; a surface composing them is worth building when there are enough owners to compose, not before |
| **route / capacity / qualification registries** | nothing in either lane dispatches to a pool |
| a **commitment register**, a **loopspec registry** | remedies for problems a clean start avoids |
| a **supervision watcher, wake queue, or pane model** | neither lane supervises a live worker. When one does, the thing to carry over is upstream's **event-log-versus-current-state split** and its **absorb-only-on-positive-evidence** classification (`boundary:§10.7`) — not the 1,962-line watcher |
| a **publication guard** | the push happens inside the qualification tool. A guard around a call this architecture does not make would be **a control credited to something it never examines** — the exact wrong-subject class the proofs exist to avoid |
| a **second reviewer stage** around qualification | the selected path owns its own rigor; adding an independent reviewer is the anti-double-review error upstream is emphatic about (`boundary:§6.2`) |
| a **semantic adapter** at any typed-to-typed boundary | one boundary looked like it needed one and does not: the plan-to-intent transformation is total and mechanical, so a **deterministic serializer** eliminates it ([`no-mistakes-integration.md`](no-mistakes-integration.md) §9.1) |
| **Machinist** | [`machinist-integration-plan.md`](machinist-integration-plan.md) |
| **signed attestations** | the qualification tool names this as deferred work and instructs implementers not to build it into the enforcement action. Building our own would be a **second** enforcement surface that the forge does not check |

### 6.3 Three habits deliberately not carried, with their measurements

| Habit | Measurement | Instead |
|---|---|---|
| **A contract shipped by value to every worker** | 625 briefs, mean ~4,072 estimated tokens, **88–92% identical boilerplate** by bytes on three sampled tasks — roughly 2.5M tokens of brief text, ~89% of it restating the same lifecycle contract (`corpus:§3.3`) | a **stable versioned contract read once**, with the task carrying a pointer and its base binding |
| **An always-loaded prose surface that only grows** | `AGENTS.md` at 649 lines / ~31,309 estimated tokens, plus memory files totalling ~54,772 against a **self-declared 7,500-token budget — a 7.3× overrun**, with a script that **measured** the overrun and nothing that refused (`corpus:§3.4`, OBSERVED there) | a **fixed-size** always-loaded contract where adding a paragraph requires removing one, and a budget that is a **build failure** rather than a report. Incident-derived rules go **into the generator or the guard**, never into the always-loaded prose |
| **Guarding an exemption branch that has no honest instances** | nine documented escape levels in one task, each closing a door and the next-cheapest one being used; a worker's own summary: *"every exemption you write is a door that gets tried"* (`corpus:§1.7`) | **delete the branch.** *There is no door to try if there is no door.* And every exemption that does exist gets a **closed vocabulary** and a condition **mechanically verified at the point of use, anchored to something the checked party cannot modify** |

---

## 7. What "done" means for the first implementation

Not a date. A set of conditions, each checkable from the record alone by a reader with no access to the
session — the same bar both proofs set for themselves.

1. Every increment I1–I10 is built, and **every watched red in this document has been seen red for its
   own pinned target**, with the neighbour's state recorded.
2. One candidate travels **Lane A end to end**, under a fold rule **pinned before the first
   observation**, and the disposition is written **once**.
3. One decision travels **Lane B end to end against a live, open candidate** (I11), and L1/L2/L3 are
   watched red **on the live forge**.
4. The disposition's `outcome` is **reproducible** from the journal and the pin by an independent
   verifier that **imports none of the harness** — the shape `proof-a:tools/dod_verify.py` already
   has, promoted to a **declared** verifier so D2-S1 closes.
5. **Positive executed counts are reported, never the absence of failures**: how many checks ran, how
   many conditions were evaluated, how many falsifiers were watched red — never *"no failures found"*.
   `0/0/0` was once an exit-code triple no reader could distinguish from a suite that ran nothing
   (`corpus:§1.8`).
6. Every **D2 that fired** is in the record with the cognition it required and the machinery that would
   remove it ([`determinism-assessment.md`](determinism-assessment.md) §4).
7. The **could-not-observe register is non-empty and honest.** A first implementation with nothing it
   could not observe has not looked.

---

## 8. Could-not-observe register for this plan

| # | Question | Value |
|---|---|---|
| 1 | How long does the first implementation take? | **UNPROVEN, and deliberately unestimated.** Nine of twelve increments promote code that already exists and ran; the estimate a reader would want depends on a substrate choice this document does not make. |
| 2 | Does promoting the proof harnesses carry defects the proofs did not surface? | **could-not-observe.** Both harnesses were exercised on exactly one run each. I1's five watched reds target the defect classes the observers actually found; other classes may exist. |
| 3 | Will the increment order survive contact? | **UNPROVEN.** The ordering claim — kernel first, Lane A next, the CNO-closers last — is an argument, not a measurement. The evidence for the first half of it is that Proof A's contestable verdict is exactly what building on an un-pinned fold produces. |
| 4 | Is the do-not-build list complete? | **No, and it should not read as complete.** It names what was **considered and rejected**, with reasons. Something absent from both the build list and this list has simply not been considered yet. |
