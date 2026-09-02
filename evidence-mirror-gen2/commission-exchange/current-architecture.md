# Current architecture — what is designed, and what it rests on

    generated:      2026-09-02
    projection_of:  artifacts/plans/  (this file is NOT authoritative; see ../README-FIRST.md)
    authoritative_master: artifacts/plans/architecture-synthesis.md
    drawn_from:
      - artifacts/plans/architecture-synthesis.md      (master: vocabulary, boundary, state machines, records, merge predicate, component list)
      - artifacts/plans/no-mistakes-integration.md     (mandatory qualification composition)
      - artifacts/plans/sol-control-v1.md              (control-plane wire schemas and lifecycle)
      - artifacts/plans/machinist-integration-plan.md  (adoption position)
      - artifacts/plans/determinism-assessment.md      (D0/D1/D2/D3 classification)
      - artifacts/plans/first-implementation-plan.md   (increments, watched reds, do-not-build)
      - artifacts/scouts/upstream-firstmate-boundary-report.md
    status_of_the_subject: DESIGN ONLY. Nothing in the package has been built.

---

## 1. The shape of it

The architecture is **one six-document package with one owner per contract**. The
master document owns the shared vocabulary; the five companions each own exactly
one area and restate nothing.

| Document | The only place these contracts appear |
|---|---|
| `architecture-synthesis.md` | vocabulary; upstream boundary; proof findings; both state machines; record ownership and pinning; merge predicate and expected-head gate; component list |
| `no-mistakes-integration.md` | pre-gate predicates, outcome-field consumption, custody rules, repair/retry budgets, exact-head qualification |
| `sol-control-v1.md` | request/ruling/receipt wire schemas, V1–V10 and L1–L5, correlation, refusal vocabulary, one-issue-per-question |
| `machinist-integration-plan.md` | the adoption decision, the typed interface if adopted, the re-open conditions |
| `determinism-assessment.md` | every operation classified; **78 operations: D0 = 66, D1 = 3, D2 = 9, D3 = 0** |
| `first-implementation-plan.md` | ordered increments I0–I12, watched-red acceptance per increment, the do-not-build list |

The three earlier proof-design documents (`proof-a-green-pr-design.md`,
`proof-b-sol-roundtrip-design.md`, `proofs-shared-contracts.md`) are **superseded
as architecture** and retained as evidence. Where the synthesis differs from
them, the difference is something execution taught.

## 2. Two lanes, and nothing else

- **Lane A — delivery.** A candidate becomes a landed change. Its terminal
  authority is a one-use, head-bound authorization whose *spend constructs the
  act*.
- **Lane B — decision.** An engineering decision leaves the system as a typed
  artifact, is answered outside, and is consumed by byte identity against a
  pre-registered action.

## 3. The eleven load-bearing properties

These are what the architecture must reproduce **structurally**. Anything not on
this list is deliberately out of the first build.

| # | Property | Owner |
|---|---|---|
| L1 | Every observation is three-valued, folds under `FAIL > CNO > PASS`, and cannot be coerced | K1 `observe` |
| L2 | Every recorded value is derived from a file written **before** the value was parsed | K1 |
| L3 | The verdict's rule, stage order, bounds and input digests are **pinned before the first observation** and never amended | K3 `pin` |
| L4 | The terminal record is **written once**, refuses without stage coverage, and its outcome is folded rather than asserted | K4 `fold` |
| L5 | Every field name lives in **exactly one schema file**, and the reply instructions are generated from it | K5 `vocabulary` |
| L6 | Every control has been **watched red for its own pinned target**, with the neighbour's state recorded | K6 `control-harness` |
| L7 | Qualification is **mandatory**, read from a typed field and never an exit code; `checks-passed` is non-terminal | D2 `qualify` |
| L8 | Green is asserted only **at an exact head**, over a **complete** universe | D3 `forge-observe` |
| L9 | An irreversible outward effect **spends a one-use, head-bound authority whose spend constructs the act**; post-condition checked by **identity** | D4 `authorize`, D5 `land` |
| L10 | Retry-versus-stop is **arithmetic against a durable record**; budget exhaustion is terminal | D6 `attempt` |
| L11 | An external decision travels as a **typed artifact compiled from machine state**, validated by a three-valued ladder, consumed by **byte identity** | R1, R2, R3 |

## 4. Fifteen components, one responsibility each

**Kernel (both lanes):** `observe`, `journal`, `pin`, `fold`, `vocabulary`,
`control-harness`.
**Lane A:** `candidate`, `qualify`, `forge-observe`, `authorize`, `land`,
`attempt`.
**Lane B:** `boundary`, `compile`, `consume`.

**Nine of the fifteen already exist as working code that ran** — the two proofs
left their harnesses on disk, and the first implementation is largely a
*promotion of that code into named components*, not a rewrite. **`attempt` is the
one genuinely new component in Lane A.**

## 5. What execution taught that the designs did not contain

Five findings, each answered structurally rather than by discipline:

1. **A fold rule authored during a run is not a verification contract.** Proof A's
   outcome flipped on a rule written with the answer in view; Proof B pinned its
   rule first, pre-registered the expected verdict, and graded *stricter* than
   expected.
2. **A three-valued vocabulary needs a three-valued gate.** A terminal gate
   written against two values silently consumes the exact case it was built to
   refuse.
3. **A path fence bounds paths and cannot bound content.** "Confined to the right
   directories" is weaker than "contains only intended source".
4. **A distinctness test that computes `target == observed` from one call is a
   tautology.** The target must be pinned before the observation, and the
   neighbour's state is a required field.
5. **A record's own defect ledger must be derived from the trace, not typed
   alongside it.**

## 6. What is deliberately NOT built

This is the load-bearing half of the design. Each entry is out because **no
property in §3 needs it**.

| Not built | Why |
|---|---|
| A decision surface / composed control-plane read layer | every record has one writer; compose when there are enough owners to compose |
| Route / capacity / qualification registries | nothing in either lane dispatches to a pool |
| A commitment register, a loopspec registry, a vocabulary-collision register | remedies for problems a clean start avoids by naming things once |
| A supervision watcher, wake queue, or pane model | neither lane supervises a live worker |
| **A publication guard** | the push happens inside the qualification tool. A guard around a call this architecture never makes would be **a control credited to something it never examines** — the exact wrong-subject error the proofs exist to avoid |
| A second reviewer stage around qualification | the selected path owns its own rigor; adding one is the anti-double-review error |
| A semantic adapter at any typed-to-typed boundary | the one boundary that looked like it needed one is total and mechanical; a deterministic serializer eliminates it |
| Machinist | adoption deferred (see `current-decisions.md`) |
| Signed attestations | the qualification tool names this deferred and instructs implementers not to build it into the enforcement action |

Three habits are also deliberately not carried, each with the measurement behind
it: a contract shipped **by value** to every worker (625 briefs, ~89% identical
boilerplate, roughly 2.5M tokens of restated lifecycle); an always-loaded prose
surface that only grows (`AGENTS.md` at ~31,309 estimated tokens against a
self-declared 7,500 budget — a **7.3× overrun**, measured by a script and refused
by nothing); and guarding an exemption branch with no honest instances (*"every
exemption you write is a door that gets tried"* — nine escape levels in one task).

## 7. The measurement that drives all of it

From the retired fork, at its final main: governing machinery grew from **36,425
to 105,214 lines of shell in 38 days** while landed throughput fell about
ninefold, reaching a six-day window with **zero** landings. The queue reached
**359 items** while roughly a dozen fully validated candidates sat parked, because
the publication guard that governed the delivery path was **itself unlanded**.

That is why I0 — *decide the bootstrap exception before building the gate* — is
the first thing in the plan and is not code.

## 8. The order of the first implementation

`I0` decide the bootstrap exception → `I1–I3` kernel (observe/journal/pin/fold,
one vocabulary source, control harness with the tautology removed) → `I4–I8`
Lane A (candidate + pre-gate, qualification adapter, forge observer,
authorization store and landing chokepoint, attempt arithmetic) → `I9–I10` Lane B
(boundary classifier + request compiler, ruling consumer) → `I11` run Lane B
against a **live, open** candidate → `I12` Lane A attempt 2 under a fold rule
pinned in advance.

Two experiments are named, sized, and left for the captain rather than scheduled:
the control-plane **economics** experiment (N concurrent subjects against a moving
trunk), and the four Machinist runtime experiments.

## 9. What "done" means for the first implementation

Not a date — seven checkable conditions, of which three carry the weight:

- The disposition's `outcome` is **reproducible** from the journal and the pin by
  an independent verifier that **imports none of the harness**.
- **Positive executed counts are reported, never the absence of failures.**
  `0/0/0` was once an exit-code triple no reader could distinguish from a suite
  that ran nothing.
- **The could-not-observe register is non-empty and honest.** A first
  implementation with nothing it could not observe has not looked.

## 10. Status caveat, stated plainly

The package is **design only and has not been reviewed**. The v2 control-plane
transaction that would have obtained an independent ruling on it terminated
`NO_ANSWER`. Treat this document as *the current best design*, not as *an
accepted design*.
