# Current proofs — what was executed, and exactly what it established

    generated:      2026-09-02
    projection_of:  artifacts/proofs/  (this file is NOT authoritative; see ../README-FIRST.md)
    drawn_from:
      - artifacts/proofs/proof-a/observer/observer-report.md   (independent observer, read-only)
      - artifacts/proofs/proof-b/observer/observer-report.md   (independent observer, read-only)
      - artifacts/proofs/machinist-direct-experiment.md        (29 measured invocations)
      - artifacts/proofs/proof-a/attempt-1/                    (disposition, trace, observations, raw/)
      - artifacts/proofs/proof-b/attempt-1/                    (disposition, PINNED.json, ruling, receipt, trace)
      - artifacts/plans/architecture-synthesis.md §2           (what the proofs established)
    note: the observer reports are cited in preference to the executors' own
          records wherever both speak, because the observers re-derived the
          values independently. Both are on disk; neither was edited here.

---

## 1. Three executed proofs, and their honest verdicts

| Proof | What it tested | Terminal outcome | The caveat that travels with it |
|---|---|---|---|
| **A** — green merged pull request | can a candidate go *code → green exact-head PR → mergeable → protected merge → observed merged state → typed disposition* with **no step resting on an agent's judgement**? | `PROVED` | **the fold rule was rewritten mid-run, with the answer in view.** Read it as *proved under a fold rule authored during the run and disclosed*, not under the rule the design pre-registered |
| **B** — FirstMate ↔ Browser Sol round trip | can one engineering decision leave the system, be answered outside, and come back as a **typed, head-bound, deterministically validated** artifact? | `CNO_AT_B-S3` | the round trip **completed**; the grade is the earliest could-not-observe under a rule **pinned before the first measurement**. The subject was an already-merged candidate in an **archived** repo, so the staleness ladder passed against a subject incapable of failing it |
| **Machinist direct mode** | does the execution substrate behave as its source describes? | **ADOPT_LATER — narrowly, conditionally** | authorizes **no** architectural adoption. Direct mode only: no control plane, no worker daemon, no triggers |

## 2. Proof A — what GitHub itself shows

Re-derived by a separate observer process from GitHub, **not** from the
executor's record: the seed tree digest, branch protection field-for-field,
three negative controls reddening on GitHub's own check runs, the trusted
`.no-mistakes.yaml` on `main`, both required checks green **at the exact
published head**, the eight-condition mergeability ladder, the merge commit's
second parent, the default-branch ref, and the protection generation before and
after the merge. A declared verifier (`fm-verify.sh pr-checks`) returned
`PASS / verified` on the candidate PR.

**The single most consequential observation:** the forge **refused** a merge
whose candidate had not been through the pipeline —

> `Required status check "PR must be raised via no-mistakes" is failing. (HTTP 405)`

— with `enforce_admins: true`, so the operator's own token could not bypass it.
**Mandatory qualification is enforced by the server, not by a rule an agent was
told to follow.**

**And the honest counterweight:** that same check is a *contributor guardrail,
not a forgery-proof security boundary*. A hand-written pull-request body
reproducing the documented format passes — Proof A's own negative-control setup
demonstrated exactly that.

**Two heads, kept apart** exactly as designed: the locally committed candidate
`d29527ed` (tree matching the pinned digest) and the published head `281e15b2`
the pipeline authored on top of it. Every downstream binding used the published
one.

**Record state:** disposition `outcome: PROVED`, **seven disclosed deviations**
`D-1`…`D-7`, two **retained** refusals on a `PROVED` record, trace 231 lines with
zero sequence gaps. The observer re-ran the fold against the settled file and
reproduced `{good: 116, bad: 0, could-not-observe: 0}` from 152 observations.
Two of the seven deviations were found independently by the observer before it
read the register — which is what makes the register a real inventory rather than
a formality.

**Artifacts:** repository publicly readable and **archived** at
`sbracewell64/fm-cleanroom-proof`; the candidate is PR #2.

## 3. Proof B — the round trip that closed

A schema-valid escalation left the executor, an outside party answered it, the
answer was validated on **fifteen predicates** (V1–V10, L1–L5) and consumed **by
byte identity**, and a receipt closed the loop. The observer **rebuilt the
consumption from public artifacts alone and got the same tree**.

**On Proof A's provenance lesson, the answer is unambiguous and positive.** Proof
A's disposition was written four times; Proof B's was written **once** and never
rewritten across 36 subsequent observer poll cycles. Its fold rule was pinned
**before the first measurement**, marked `amendable: false`, carries
`amendments: 0`, and even **pre-registered the expected verdict** — and the actual
grade came out **stricter** than the pin expected, not softer.

**The ruler genuinely inspected the evidence:** the ruling cites two workflow-run
ids that are **absent from the evidence set it was given**, and the observer
verified both are real, at the exact head, and successful.

| Question | Value |
|---|---|
| Round trip completed request → ruling → validated consumption → receipt | **observed-good** |
| Terminal record written once, fold rule pinned first | **observed-good** |
| Applied bytes are the ruled bytes | **observed-good** (observer reproduced the tree) |
| Escalation compiled from machine state | **observed-good** (52 predicates, each naming a command) |
| Ruler is a distinct *execution context* | **observed-good** (credential path differs) |
| Ruler is a distinct *principal* | **could-not-observe** (one account owns all four roles) |
| Staleness controls exercised against a subject that could go stale | **could-not-observe** (subject archived) |
| Terminal record lists every instrument defect found | **observed-bad** — INSTR-4 is in the trace and missing from the ledger |
| Every evidence locator resolves to the bytes its digest names | **observed-bad** — 5 of 6 verified; one did not |
| Any human decided anything inside the round trip | **observed-bad**, i.e. **none did** — two decision records, both captain-deferred, no captain input before terminal |

**Positive executed counts, never "no failures found":** 330 observer trace
events with zero gaps; 291 raw captures each written before any parse; 71 poll
cycles; 141 executor observations independently re-folded (139 good, 0 bad,
2 could-not-observe); **0** terminal-record rewrites; 21 append-only journal
versions verified prefix-extending; 373 venue comments sampled for the
independence control; **0** mutating forge calls by the observer.

## 4. Machinist — read-not-run, then run

The substrate scout could not build or execute Machinist (no Go toolchain on the
host) and said so as a result rather than a gap. The later experiment installed a
**user-space** Go toolchain inside a disposable lab, built the pinned checkout
without modifying it, and made **29 measured invocations** with `stdout`,
`stderr`, exit code and wall time kept in separate files — because two of the
findings are precisely about stream merging.

**Build fidelity, executed:** the subject's own suite runs green under that
toolchain — **114 tests passed, 0 failed, 0 skipped**. The pinned checkout was
byte-clean before the build, after the build, and after the tests.

**Verdict: ADOPT_LATER, narrowly and conditionally.** The design package's
independent position is **DEFER for the first implementation**, because Machinist
*replaces nothing either proof exercised*, *structurally cannot host the one lane
it would most obviously serve*, and *its contract has changed roughly monthly for
six weeks*. The deferral is falsifiable: the interface is specified, four
experiments would settle the unknowns, and the re-open conditions are named.

## 5. The five things execution taught that the designs did not contain

Each is now answered **structurally** in the architecture, not by discipline:

1. **A fold rule authored during a run is not a verification contract.**
2. **A three-valued vocabulary needs a three-valued gate** — a terminal gate
   written against two values silently consumes the exact case it was built to
   refuse.
3. **A path fence bounds paths and cannot bound content.**
4. **A distinctness test that computes `target == observed` from one call is a
   tautology** — the target must be pinned before the observation, with the
   neighbour's state a required field.
5. **A record's own defect ledger must be derived from the trace, not typed
   alongside it.**

## 6. What none of the three proofs established

- **Independence at the principal level.** One GitHub account fronts candidate,
  request, ruling and receipt. Both observers state this about themselves too:
  process independence observed-good, identity independence could-not-observe.
  They share the host, the credential, and the firstmate that commissioned them.
- **That the machinery scales.** One candidate, one lane, one landing; one
  decision, one round trip. Neither proof is a benchmark and neither claims to be.
- **That the control plane's economics close.** That is a property of volume
  against a **moving** trunk. One round trip against a frozen candidate says
  nothing about it either way, and the experiment that would measure it is a
  registered captain decision.
- **That any of it is covered by a declared verifier.** `fm-verify.sh --list`
  declares `browser, pr-checks, merge-clean, review-exec, review-mutation`. Only
  `pr-checks` applied, once. Everything else was graded by hand under the
  three-valued rule, with a negative control watched red before each green.
