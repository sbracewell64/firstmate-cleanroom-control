# Current status — the whole clean-room effort, on one page

    generated:      2026-09-02
    projection_of:  artifacts/  (this file is NOT authoritative; see ../README-FIRST.md)
    drawn_from:
      - artifacts/baseline/pristine-baseline-20260901.md
      - artifacts/baseline/runtime-baseline.md
      - artifacts/baseline/ce-isolation-baseline.md
      - artifacts/proofs/proof-a/observer/observer-report.md
      - artifacts/proofs/proof-b/observer/observer-report.md
      - artifacts/proofs/machinist-direct-experiment.md
      - artifacts/plans/architecture-synthesis.md  (and its five companions)
      - artifacts/control/bootstrap-report.md
      - artifacts/control/observer/observer-report.md
    grading: every grade below is carried over from the artifact named beside it,
             not re-judged here. Three values, never two.

---

## 1. Where this stands, in five sentences

Phase 0 is **substantially complete**. Four subjects were investigated and pinned,
a clean-room environment was built and verified, two end-to-end proofs were
executed with independent observers, a six-document architecture package was
written from what the proofs actually taught, and a second-generation control
plane was built and exercised. **One thing is not working: the external ruling
circuit.** The v2 control plane's first transaction reached a terminal
`NO_ANSWER` — no ruling arrived within its 90-minute bound — so the architecture
package has **not been reviewed**, and the reason for the silence is genuinely
unresolved between two candidates with different repairs.

## 2. The scoreboard

| Track | State | Grade, and who graded it |
|---|---|---|
| Four subjects pinned, independent checkouts, clean-room root is not a git repo | done | observed-good — `baseline/pristine-baseline-20260901.md` |
| Upstream firstmate boundary map | done | `scouts/upstream-firstmate-boundary-report.md` |
| Retired-fork corpus lessons | done | `scouts/historical-corpus-lessons.md` |
| no-mistakes qualification characterization | done | `scouts/no-mistakes-qualification-report.md` |
| Machinist substrate study (read-not-run) | done | `scouts/machinist-substrate-report.md` |
| Machinist executed experiment (29 runs, direct mode) | done | verdict **ADOPT_LATER, narrowly** — `proofs/machinist-direct-experiment.md` |
| Compound Engineering usage study | done | `scouts/compound-engineering-usage-report.md` |
| Clean-room runtime home built and started end to end | done | observed-good — `baseline/runtime-baseline.md` §3 |
| CE installed scope-isolated, host `~/.claude` untouched with a positive control | done | observed-good — `baseline/ce-isolation-baseline.md` §1 |
| **Proof A** — green merged PR with no agent judgement in the chain | executed | `PROVED`, **under a fold rule authored mid-run** — `proofs/proof-a/observer/observer-report.md` §1 |
| **Proof B** — FirstMate ↔ Browser Sol round trip | executed | `CNO_AT_B-S3`, round trip completed, terminal record written once — `proofs/proof-b/observer/observer-report.md` §1 |
| Architecture package (6 documents) | written | DESIGN ONLY; nothing in it has been built — `plans/architecture-synthesis.md` |
| **Control plane v2** built, frozen, 23 guards exercised | done | machinery observed-good — `control/bootstrap-report.md` §7 |
| **Control plane v2 usable end to end** | **NO** | **could-not-observe** — `control/bootstrap-report.md` §11 |
| Architecture package reviewed by an independent ruler | **NO** | no ruling exists — `control/observer/observer-report.md` §9 |
| First implementation (increments I0–I12) | not started | `plans/first-implementation-plan.md` |

## 3. The one thing blocking forward motion

**The ruling party cannot be shown to have received anything.** The v2 request
was posted to the new venue and polled 89 times over 90 minutes with a
completeness predicate on every poll (`fetched == reported`), so "no ruling
arrived" is an observation over a complete universe rather than an absence of
looking. But *why* nothing arrived splits into two candidates that need
different repairs:

1. **The credential path may not reach the new repository.** The ruling on the
   retired venue was written through the `chatgpt-codex-connector` GitHub App. A
   GitHub App installed with `repository_selection: selected` does not gain a
   repository created afterwards. Both API endpoints that would settle this
   refuse for the operator's token (401 and 403) — **could-not-observe**
   (`control/evidence/ruler-credential-path-reachability.md`).
2. **Browser Sol's own project binding may still point at the retired venue.**
   Not observable from this side at all.

Until that is settled, **a timeout is not evidence that the ruler declined**, and
every other property of the plane is untested in the only way that matters. Both
candidates are account-owner actions. This is the one blocking item among
**25 open captain decisions** (21 distinct questions — four are registered
twice). `current-decisions.md` lists every one of them, with what each blocks.

## 4. What is genuinely proven, and what only reads as proven

**Proven by execution:**

- A candidate can travel *correct code → green exact-head PR → objectively
  mergeable → expected-head protected merge → observed merged state → typed
  disposition* with no step resting on an agent's judgement. Independently
  re-derived from GitHub by a separate observer process (proof A observer §1).
- The forge refused a merge whose candidate had not been through the pipeline,
  with `enforce_admins: true`, so the operator's own token could not bypass it.
  Mandatory qualification is enforced by the server, not by a rule.
- A decision can leave FirstMate, be answered by an outside party, and come back
  as a typed, head-bound, deterministically validated artifact consumed by byte
  identity. The observer rebuilt the consumption from public artifacts alone and
  got the same tree (proof B observer §1).
- Machinist's direct mode runs, and its own test suite is green under a
  clean-room toolchain (114 tests passed, 0 failed).

**Reads stronger than it is:**

- **Proof A's `PROVED`.** It first said `REFUSED_AT_A-S11`; the outcome changed
  because the *fold rule was rewritten mid-run with the answer in view*, not
  because any observation changed value. Every amendment is disclosed and the
  final fold is reproducible. Read it as *proved under a fold rule authored
  during the run*, not under the rule the design pre-registered.
- **Proof B's staleness ladder.** Its subject was an already-merged candidate in
  an archived repository. A head that cannot move cannot go stale, so L1/L2/L3
  passed against a subject incapable of failing them.
- **Independence, everywhere.** One GitHub account fronts candidate, request,
  ruling and receipt. Independence is **could-not-observe at the principal
  level** in both proofs and on the v2 plane. Process independence is
  observed-good; that is a weaker claim.
- **The v2 plane's machinery vs the v2 plane's usability.** The components are
  observed-good against fixtures. The circuit has never closed. These are
  different claims and only the first has evidence.

## 5. Defects the work found in itself

Reported here because a corpus that hides its bruises is worth less.

| Found in | Defect | State |
|---|---|---|
| v2 consumer | The schema refused its author's own receipt — it claimed a consumption without demonstrating the replay. Fixed by making the consumer *execute* the replay and refuse to emit a receipt otherwise. | fixed, watched red (R14) |
| v2 consumer | Expiry shared a refusal code with a late ruling, collapsing "nobody answered" and "somebody answered too late" into one token. Now resolved at fold time. **Not caught by 18 fixtures** — every fixture ran while the request was still live. | fixed, watched red (R13, R15) |
| v2 schema | Cannot express "nothing was consumed": `consumption_identity` is required regardless of outcome. A **design gap**, not a slip; needs a new schema generation. | open — `control/observer/observer-report.md` §4.3 |
| Proof B record | The most severe instrument defect found (INSTR-4) is in the trace and **absent from the terminal record's own defect ledger**. | disclosed; fixed structurally in the architecture (§6.2 derivation rule) |
| Fleet-wide tooling | **`gh-axi` silently truncates output at ~4 KB.** Every envelope in this protocol exceeds it. An agent reading an issue, ruling or PR body through it and believing it saw the whole document is exposed. | open hazard — `control/observer/observer-report.md` §1 |
| Verifier registry | `fm-verify.sh --list` declares only `browser, pr-checks, merge-clean, review-exec, review-mutation`. **None covers schema conformance, config generation, locator readiness, universe completeness or replay.** Every grade on the v2 plane was reached by hand. | open gap, reported not worked around |
| Host, during the Proof A run | Initializing the *isolated* qualification tool **also rewrote a shared host instruction file** (`~/.claude/skills/no-mistakes/SKILL.md`). The isolation covers database, socket, daemon lock and worktrees — not that path. **Every worker on this machine now reads v1.61.0 guidance while the installed binary is v1.40.3.** Disclosed as a deviation and independently confirmed by the observer. | open captain decision |
| The qualification tool itself | Proof A observed it author a commit whose message says *docs already accurate and no updates needed* and **whose entire content is five `.pyc` bytecode files** left by the earlier test and lint steps. Review runs before those steps, so it never saw them — and that commit became the published head, the attested head, the head both required checks went green on, and the head that landed. **The candidate change itself was clean.** | recorded, not filed upstream — open captain decision |

## 6. What happens next, in order

1. **Settle the return path** (captain / account owner). Nothing else about the
   plane can be established until a ruling can physically arrive.
2. **Re-run the v2 handshake unchanged.** Nothing needs rebuilding; a new request
   at `request_generation: 2` recompiles from the same frozen schema, the same
   config generation and the same evidence mirror commit.
3. **Get the architecture package ruled on** — that was the point of the
   transaction.
4. **Then, and only then, start the first implementation** at I0 (decide the
   bootstrap exception before building the gate) and run I1–I12.
5. **Do not retire the old venue** until one v2 round trip completes end to end.
   The retirement plan was deliberately not drafted for exactly this reason.

Running alongside all of it: **25 captain decisions are open**, and three of them
shape the first implementation before it can start — whether the qualification
tool is reimplemented, adopted or stubbed; whether outward effects are gated by
code or by instruction; and which repositories the implementation may create,
given nothing it creates can be deleted.

## 7. What this page could not observe

- Whether Browser Sol received, read, or declined the v2 request. The transport
  and the ruler remain unseparated.
- Whether the ruling party is an independent principal. One shared forge account
  makes this unobservable from here.
- Whether the architecture package is sound. **No review took place.**
- End-to-end crew placement in the clean-room home: no worker was ever spawned
  there, so spawn behaviour is unverified (`baseline/runtime-baseline.md` §5).
- **Whether this page is still complete.** While it was being written, another
  lane wrote 22 new files under `artifacts/control/gen2/` and
  `artifacts/baseline/gen2/` — apparently a second-generation control plane,
  which is what both the bootstrap report and the observer report recommend
  building. **None of it was read**; only its paths and timestamps were observed.
  What it is, whether it is complete, and whether it changes anything above is
  could-not-observe. Every artifact this page *does* cite was re-hashed at close
  and was unchanged.
