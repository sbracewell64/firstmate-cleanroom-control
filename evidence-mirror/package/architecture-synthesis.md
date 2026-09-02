# Clean-room architecture synthesis — the smallest architecture that reproduces the proofs

```yaml
artifact_contract: ce-unified-plan/v1     # section shape borrowed as document discipline only
artifact_readiness: implementation-ready
execution: knowledge-work
product_contract_source: Captain clean-room directive, 2026-09-01, section 10
authored_by: scout task cleanroom-architecture-synthesis, 2026-09-02
status_of_this_document: DESIGN ONLY - nothing here has been executed
slot_base_for_fleet_citations: 6d1a000e4e9c836eb120286d63682ca135577dfe
owns: the shared vocabulary, the upstream boundary summary, what the two proofs established,
      both backward-derived state machines, the record-ownership and pinning contracts,
      the merge predicate and expected-head gate, and the minimum component list
```

**This is the master document of a six-document package.** It owns the shared vocabulary, the
upstream boundary summary, what the two executed proofs established, both backward-derived state
machines, the record-ownership and write-once contracts, the merge predicate, and the minimum
component list. It does not restate anything the five companions own.

| Document | Owns, and is the only place these contracts appear |
|---|---|
| **`architecture-synthesis.md`** (this file) | vocabulary; upstream boundary; proof findings; both state machines; record ownership and the pinning contract; the merge predicate and expected-head gate; the component list |
| [`no-mistakes-integration.md`](no-mistakes-integration.md) | the mandatory-qualification composition: pre-gate predicate set, outcome-field consumption, custody rules, repair/retry budgets, exact-head qualification, the fence's content dimension |
| [`sol-control-v1.md`](sol-control-v1.md) | the control-plane wire schemas and lifecycle: request/ruling/receipt, V1–V10, L1–L5, correlation, refusal vocabulary, receipt, one-issue-per-question |
| [`machinist-integration-plan.md`](machinist-integration-plan.md) | the Machinist adoption decision and its typed interface, or the reasoned deferral |
| [`determinism-assessment.md`](determinism-assessment.md) | the D0/D1/D2/D3 classification of every operation, and each D2's eliminating machinery |
| [`first-implementation-plan.md`](first-implementation-plan.md) | ordered increments, watched-red acceptance per increment, and the do-not-build list |

**Prior design documents.** [`proof-a-green-pr-design.md`](proof-a-green-pr-design.md),
[`proof-b-sol-roundtrip-design.md`](proof-b-sol-roundtrip-design.md) and
[`proofs-shared-contracts.md`](proofs-shared-contracts.md) were the *pre-execution* designs. They are
superseded as architecture by this package and retained as evidence: where this synthesis differs
from them, the difference is a thing execution taught, and it is called out.

---

## 0. Grading, method, and the shared vocabulary

### 0.1 Claim grading

Every claim in all six documents carries exactly one grade.

| Grade | Meaning |
|---|---|
| **OBSERVED** | I read the artifact or ran the command **in this task**. The citation or command follows. |
| **DOCUMENTED** | A pinned artifact, executed record, or scout report asserts it; I did not re-derive it. |
| **INFERRED** | Deduced from graded facts. Never presented as an observation. |
| **UNPROVEN** | Could not be established either way. A result, not an absence of effort. |
| **RECOMMENDED** | A design proposal of this synthesis. Not a property of any subject. |

**The second-hand rule, and it is applied throughout.** A scout report that graded something OBSERVED
against a subject **this task did not itself re-read** is cited here as **DOCUMENTED**, with the phrase
*OBSERVED there* naming where the first-hand observation lives. Crediting another party's observation
as my own would be the wrong-subject class applied to this package's own evidence, so only two kinds of
claim carry a bare **OBSERVED**: something I read in the artifact corpus, and something I ran (§0.2).

Citation forms: `proof-a:<file>` and `proof-b:<file>` are relative to
`/mnt/e/FirstMate-Cleanroom/artifacts/proofs/proof-{a,b}/attempt-1/`; `obs-a:` and `obs-b:` name the
two independent observer reports under `.../proof-{a,b}/observer/`; `boundary:` names
`scouts/upstream-firstmate-boundary-report.md`; `corpus:` names `scouts/historical-corpus-lessons.md`;
`nm-scout:` names `scouts/no-mistakes-qualification-report.md`; `machinist-scout:` names
`scouts/machinist-substrate-report.md`; `ce-scout:` names `scouts/compound-engineering-usage-report.md`.
`firstmate:` citations are against `41d0ab3910ece4e90db0194f756437b3abe8ab8f`; `no-mistakes:`
against `0af0be6323bebd61edaf3a1a6170d82c5075e818` (v1.61.0); fleet-corpus code citations against
`6d1a000e4e9c836eb120286d63682ca135577dfe`.

### 0.2 What I re-derived myself, rather than accepting

**OBSERVED, 2026-09-02, this task.** Two independent re-derivations, both against the executed
records:

```
$ cd .../proofs/proof-a/attempt-1 && python3 tools/dod_verify.py
  15/15 Definition-of-Done checks passed        (exit 0)
  DoD 2  : re-derived {good:116, bad:0, cno:0} == recorded
  DoD 4b : the LIVE merge commit still has the authorized head as its second parent
           live parents ['2ef121a9', '281e15b2']
  DoD 6  : tags 0, releases 0, deploy_keys 0, forks 0, issues disabled,
           branches 3, pulls 2  — nothing extra created
```

```
$ cd .../proofs/proof-b/attempt-1 && <independent fold over observations.jsonl under inputs/PINNED.json>
  independent fold: {good:139, bad:0, cno:2} -> CNO_AT_B-S3
  recorded outcome:                              CNO_AT_B-S3      match: True
  disposition.json sha256 374490eb… == its sidecar
  inputs/PINNED.json sha256 276ccf45… == its sidecar
```

The Proof B fold was computed by a script this task wrote, reading only `observations.jsonl` and the
pinned stage order, without reading `disposition.outcome`. Both records reproduce.

**Could-not-observe, stated as a result:** no declared verifier covers either subject.
`bin/fm-verify.sh --list` declares `browser`, `pr-checks`, `merge-clean`, `review-exec`,
`review-mutation` — the same five the proof designs recorded (`proofs-shared-contracts.md` §0.2,
DOCUMENTED) — and none of them addresses a clean-room proof record or a control-plane round trip. Every
grade in this package that is not one of the two re-derivations above is hand-made, and that
undeclared verifier is reported as gap **D2-S1** rather than absorbed.

### 0.3 The shared vocabulary — one definition, used by all six documents

The corpus's costliest transport defect was a field name living in two places (`corpus:§1.4`,
DOCUMENTED). These terms live here and nowhere else.

| Term | Definition |
|---|---|
| **observation** | One three-valued result: `observed-good`, `observed-bad`, or `could-not-observe` (**CNO**). Precedence **FAIL > CNO > PASS**. Narrowing a CNO requires an explicit recorded decision carrying its own evidence. CNO is *reserved*: a limitation the system could enforce but chose not to is a **declared decision not to enforce**, never a CNO. |
| **journal** | The append-only `observations.jsonl`. Nothing in it is ever edited, reordered, or deleted. |
| **trace** | The append-only `trace.jsonl` of `STAGE_ENTER`, `STAGE_EXIT`, `OBSERVATION`, `REFUSAL`, `EFFECT_INTENT`, `EFFECT_RESULT`, `AUTHORIZATION`, `NEGATIVE_CONTROL`, `NOTE`. |
| **stage** | The named unit the fold grades against; bracketed by a `STAGE_ENTER`/`STAGE_EXIT` pair. |
| **pin** | The write-once record fixing the fold rule, stage table and order, async bounds, input digests, falsifier register, declared deviations and declared scope exclusions **before the first observation is appended**. |
| **fold** | The deterministic reduction of the journal to one terminal `outcome`, under the pinned rule. |
| **disposition** | The write-once terminal record carrying the folded `outcome` and its evidence. |
| **candidate** | A git point — `branch`, `head_sha`, `tree_sha`, `base_sha` — plus a `candidate_state` ∈ `MUTATING`, `STABLE_FOR_VALIDATION`, `VALIDATED_EXACT_HEAD`, `ATTESTABLE`, `ATTESTED`. |
| **local head / published head** | Two separate fields. The head committed locally, and the head the pull request carries after the pipeline may have authored fix commits. **Every downstream binding uses the published head.** |
| **qualification** | The mandatory no-mistakes pass over a candidate. Its output is an attested, published, exact-head-bound pull request — never a merge. |
| **policy generation** | The sha256 over the acceptance policy: the branch-protection body, the sorted required contexts, the pinned enforcement-action ref, and the vocabulary digest. **Not** trunk movement. |
| **authorization** | A one-use, head-bound record with states `minted → spending → spent \| refused`, whose **spend constructs the act** from the record rather than receiving one. |
| **landing** | The single merge chokepoint. The only call in the architecture that moves a protected ref. |
| **effect class** | What a mutating act does to the world. Exactly two exist here: **PUBLICATION** (qualification's branch push and PR open) and **LANDING** (the merge). Anything else is out of design. |
| **question** | One compiled, closed-vocabulary engineering decision sent to an external ruler. |
| **ruling** | The external party's typed answer, bound to an exact head, tree and policy generation. |
| **correlation id** | Derived by hash from `(protocol, repo, branch, head_sha, question.key, policy_digest)`, never assigned. A moved head yields a different id. |
| **receipt** | The typed record closing a question in both directions: what was asked, what was ruled, what was done. |
| **watched red** | A control that has been *seen to fail for its own pinned target*. A falsifier records `target` (pinned before the observation) and `observed`; the measurement is valid only when they match. |
| **wrong subject** | The dominant defect class: a verdict credited to something the instrument never examined. The credited claim is usually true, which is what makes it convincing. Resolving one yields **could-not-observe**, not a pass. |
| **D0 / D1 / D2 / D3** | Determinism classes. Owned in full by [`determinism-assessment.md`](determinism-assessment.md) §1. |

---

## 1. The upstream boundary, in one page

**Source: `boundary:` (scout task `cleanroom-upstream-firstmate-boundary`, subject
`kunchenguid/firstmate` at `41d0ab3910ece4e90db0194f756437b3abe8ab8f`).** All seven rows below are
graded OBSERVED *in that report*, by exhaustive grep or line-by-line read; DOCUMENTED here.

| # | Upstream fact | Consequence for this architecture |
|---|---|---|
| 1 | **`yolo` is read by no gate.** It is recorded in `state/<id>.meta`, reported in the fleet snapshot, and consumed only by the LLM's reasoning. `bin/fm-pr-merge.sh` contains zero occurrences of it (`boundary:§2.5`). | Authority must be a **durable artifact a chokepoint spends**, not a metadata field an agent reads. → component **D4**. |
| 2 | **The GitHub merge path has no pre-merge verification at all**, by explicit design (`firstmate:bin/fm-pr-merge.sh:11-13`); GitLab has six live conditions plus `--sha` head binding (`:224-322`, `:677-679`). "Never merge a red PR" is LLM-enforced on GitHub (`boundary:§3.3`). | The merge predicate must be **code, evaluated live, reported in full**, and the merge must be **bound to an expected head**. → §7, components **D3**, **D5**. |
| 3 | **Zero `git push` exists in upstream `bin/`.** Every push and PR-open happens in a worker's free shell or inside `no-mistakes`. There is no chokepoint a push must pass (`boundary:§3.1`, `§3.2`). | Publication is an **effect class with an owner**, not an ambient capability. Here that owner is the qualification pipeline, and the architecture states plainly that it does not re-guard it. → §7.4. |
| 4 | **No retry arithmetic exists.** No durable attempt record, budget, lineage, terminal-state vocabulary or budget-exhaustion state; every `attempt` in `bin/` is a local loop counter (`boundary:§7.1`). | Retry-versus-stop must be **arithmetic against a durable record**, not judgement with no cross-session memory. → component **D6**. |
| 5 | **No external ruling plane exists** — established by exhaustive negative search returning two hits, both ordinary English prose in one skill file (`boundary:§9.1`). Escalation is an LLM writing prose to the captain. | Lane B is a **first build**, not a port, and should be judged as one. → §5. |
| 6 | **`no-mistakes` is an unreproducible external dependency** owning review, fixes, tests, docs, push, PR and CI, and is the largest hidden surface in the subject (`boundary:§1.4`, `§10.6`). | Adopt it as the qualification stage and consume its **typed** surfaces only. → [`no-mistakes-integration.md`](no-mistakes-integration.md). |
| 7 | **The strongest upstream idea is the event-log-versus-current-state split**: `state/<id>.status` is append-only events; `fm-crew-state.sh` is a declared-source deterministic reconciler with no heuristics and no LLM (`boundary:§10.7`). Both guard libraries declare themselves **confused-agent-grade, not adversarial-grade** (`firstmate:bin/fm-lease-lib.sh:38-48`). | Carry both verbatim: the split becomes **journal vs. fold** (§6), and the threat-model honesty is preserved rather than quietly dropped (§9.2). |

**What upstream does not have, checked individually (`boundary:` companion map, `absent_upstream`,
OBSERVED there):** 32 named governance scripts and 4 registry directories are absent, including
`fm-decision-surface.sh`, `fm-landing-authorization-lib.sh`, `fm-publication-guard.sh`,
`fm-outbound-artifact.sh`, `fm-attempt.sh`, `fm-verify.sh`, `fm-status-event-lib.sh`. Every concept
this architecture proposes is therefore **net-new against upstream**, and the retired fork's versions
of them are lessons, never designs (`corpus:` directive, *Import lessons, not architecture*).

---

## 2. What the two proofs established

Both proofs ran. Both were watched by an independent read-only observer that wrote to its own area.
This section states the establishing facts, the **caps** on those facts, and what each teaches the
architecture.

### 2.1 Proof A — the green merged pull request

**Terminal record:** `proof-a:disposition.json`, `outcome: PROVED`, `completed_at 2026-09-01T23:12:39Z`,
sha256 `11dd4ee9…` (DOCUMENTED at `obs-a:§8`; the file's own fold re-derived by me at §0.2).

**Established (OBSERVED in the record and re-verified by me where noted):**

| # | Fact | Evidence |
|---|---|---|
| A1 | The verdict is **folded, not asserted**: 116 gating observations, 0 observed-bad, 0 CNO, under `FAIL > CNO > PASS`, from 152 recorded observations with 33 flagged superseded and 4 non-gating. | `proof-a:disposition.json outcome_fold`; re-derived by me, §0.2 |
| A2 | **The forge refused an unqualified merge itself.** `PUT …/pulls/1/merge` returned **HTTP 405**, `Required status check "PR must be raised via no-mistakes" is failing.` with `enforce_admins: true`, so the owner's own token could not bypass it. | `proof-a:raw/20260901T225152Z-nc2-merge-attempt.{stdout,stderr}` — read by me |
| A3 | **The expected-head bind was watched red at the call site about to be used.** The same endpoint with `sha` set to the base returned **HTTP 409**, `Head branch was modified. Review and try the merge again.`, and a follow-up read confirmed `merged: false`. | `proof-a:raw/20260901T230435Z-nc4-moved-head.*` — read by me |
| A4 | **The landed merge carries the authorized head as its second parent** — identity, not containment. `a7db5c36`, `parents = [2ef121a9, 281e15b2]`, and `281e15b2` is `authorization.expected_head`. Still true on the live forge today. | `proof-a:post-merge.json`; DoD 4b re-run by me, §0.2 |
| A5 | Squash and rebase merges were **disabled at repository level at setup**, precisely so that identity test would exist. | `proof-a:protection-generation.json` |
| A6 | **Qualification was read from the `outcome:` field**, `checks-passed`, never from the exit code, which was 0 — and per `nm-scout:§1.4` is also 0 for a parked gate and for `ci-monitor-interrupted`. `checks-passed` was recorded as **non-terminal** and terminalization confirmed separately, after the merge (`run_status: completed`). | `proof-a:qualification.json`, `proof-a:terminalization.json` |
| A7 | **The landing spent a one-use authorization whose act was constructed from the record.** Eight triggering conditions T1–T8 each carry their own evidence reference; the act digest was re-checked before the call; the record moved `minted → spending → spent`. | `proof-a:authorizations/auth-14593774-….json` |
| A8 | **Two guards genuinely refused mid-run and are retained on a `PROVED` record.** A-S6 `PRECONDITION_UNMET` (pre-gate CNO on G7) and A-S11 `PRECONDITION_UNMET` (the trace-coverage condition T8 **stopped the merge** because a stage was unclosed). | `proof-a:refusals.jsonl` |
| A9 | Positive executed counts, never "no failures": 2 required checks, 8 mergeability conditions, **6 negative controls watched red**, 152 observations, 17 stages covered, 9 mutating forge calls. | `proof-a:disposition.json counts` |
| A10 | **The bootstrap exception held.** `main`'s first-parent chain carries exactly one non-merge commit — the seed. | DoD 6b, re-run by me |

**Caps — what Proof A does not establish, from its own record and its observer:**

- **P-A-CAP-1 — the terminal grade is softer than it reads.** The disposition was written **four
  times**: `REFUSED_AT_A-S11` at 23:06:32Z (fold `good=132/bad=1/cno=1`) → `PROVED` → `PROVED` →
  settled `PROVED` at 23:12:39Z. The outcome changed **because the fold rule was rewritten mid-run
  with the answer in view**, not because any observation changed value. The mechanism — a
  supersession rule plus a non-gating exclusion — appears nowhere in the pre-run design
  (`obs-a:§4 D1`, DOCUMENTED; the executor discloses it as `D-7`/`D-6` in `proof-a:deviations.jsonl`).
  **This is the single most consequential finding in the corpus for this architecture**, and §6.3 is
  the structural answer to it.
- **P-A-CAP-2 — the forge gate is a contributor guardrail, not a forgery-proof boundary.** Its own
  source says so (`no-mistakes:.github/actions/require-no-mistakes/verify.py:21-32`), and NC-2's setup
  demonstrated it: a hand-written PR body reproducing the format turned the check **green** at
  `b02acfe6` (`obs-a:§3`). The disposition records `forge_gate` as evidence the pipeline ran and
  explicitly not as proof it could not have been forged.
- **P-A-CAP-3 — a path fence cannot bound content.** The pipeline's fix commit `281e15b2`, whose
  message reads *"docs already accurate for compare(); no updates needed"*, consists **solely of five
  `.pyc` build artifacts** produced by the post-review test and lint steps. All five sit inside
  `{fmproof/**, tests/**}`, so **T5 and T6 as specified both pass**, and they became the published
  head, the attested head, the head both required checks went green on, and the head that landed
  (`proof-a:deviations.jsonl D-4`; `obs-a:§4 D3`). The published tree `1d88a770` is **not** the pinned
  candidate tree `7a8d4f55`, and the record keeps them as separate fields.
- **P-A-CAP-4 — one negative control was not distinct, and the distinctness test cannot fail.** At
  NC-1's head **both** required checks were red, so the block is attributable to their union rather
  than to `test`. `distinct_match` is computed as `target == observed` where one call supplies both —
  a tautology (`obs-a:§4 D4`). NC-1's own `measured` field records the disconfirming evidence
  (`test=failure gate=failure`) and it is not an input to the verdict.
- **P-A-CAP-5 — observer independence is could-not-observe.** One `sbracewell64` credential serves
  both parties; only *process* independence is established (`proof-a:disposition.json observer`;
  `obs-a:§0`).
- **P-A-CAP-6 — the clean room wrote outside itself.** `no-mistakes init` overwrote
  `~/.claude/skills/no-mistakes/SKILL.md` with the v1.61.0 copy while the host binary stays v1.40.3,
  so the host now carries instructions describing a different binary (`proof-a:deviations.jsonl D-3`;
  `obs-a:§4 D5`). Registered as a captain hold.
- **P-A-CAP-7 — cross-source timestamps cannot establish causal order in this record.** The host clock
  runs ≥18s ahead of GitHub's, so the authorization reads `minted_at 23:04:35Z` against GitHub's
  `merged_at 23:04:14Z` — the record *appears* to show the landing 21 seconds before its own
  authorization. Skew, not a spend before a mint; there is no offset field (`obs-a:§4 D7`).
- **P-A-CAP-8 — the pinned vocabulary was edited mid-run and its history is incomplete.** The observer
  read `vocabulary_digest 681a2621…` at 22:46:05Z; the final file carries `50575d7f…` with history
  `[53c25b89…, ca0d6340…]`, and the digest read first is absent from that history (`obs-a:§4 D6`).
- **P-A-CAP-9 — one falsifier ran inside the stage it falsifies.** NC-4 ran at 23:04:36Z, one second
  after the authorization was minted and four before it was spent — watched red immediately before
  the act, not before the run (`obs-a:§4 D8`).

### 2.2 Proof B — the FirstMate ↔ Browser Sol round trip

**Terminal record:** `proof-b:disposition.json`, `outcome: CNO_AT_B-S3`, written **once** at
`2026-09-02T00:04:55Z`, sha256 `374490eb…` matching its sidecar, `write_once.amendments: 0`
(verified by me, §0.2; independently confirmed across 36 observer poll cycles at `obs-b:§4`).

**Established:**

| # | Fact | Evidence |
|---|---|---|
| B1 | **The round trip closed completely.** Request posted 23:42:41Z; ruling at 23:58:22Z (`ruled_at`), comment `5502255519`; validated, consumed, receipted at 00:04:04Z; issue closed 00:04:26Z. Total forge effect: **one issue, two comments**. | `proof-b:disposition.json control_plane`, `receipt.json`; `obs-b:§3` |
| B2 | **The fold rule was pinned before the first measurement and never moved**, `amendable: false`, `amendments: 0`, and the pin **pre-registers its expected verdict**. The run then graded **stricter** than the pin expected (`CNO_AT_B-S3`, not `CNO_AT_B-S9`) because the same independence fact is first measured one stage earlier, at BP5. A rule bent toward a flattering answer does not produce that direction. | `proof-b:inputs/PINNED.json fold_rule`; `proof-b:disposition.json outcome_fold`; independently confirmed `obs-b:§4` |
| B3 | **Vocabulary drift was made unreachable, not mitigated.** The reply contract was **generated by walking the schema**; the ruler's field names matched on the first attempt with **zero malformed blocks**, from a ruler whose demonstrated native format in that venue is `key: value` prose. | `proof-b:reply-contract.md`; `proof-b:ruling.json`; `obs-b:§8 rec 1` |
| B4 | **The full ladder was evaluated, none skipped.** V1–V10 and L1–L5, 15 predicates plus the completeness predicate; 14 good, **V7 could-not-observe**. | `proof-b:receipt.json validation` (read by me) |
| B5 | **"Correct ruling consumed" is an identity check and it held.** Produced diff bytes identical to the pinned patch; resulting tree `0c0c0cf5…` equal to the pinned tree; changed paths a subset of the declared set; the ruled change's own 50 tests pass. **The observer reproduced the same tree from public artifacts alone.** | `proof-b:receipt.json applied.applied_bytes_identity`; `obs-b:§1`, `§9` |
| B6 | **No model read the rationale and decided what to write.** A closed directive mapped through a **total, pre-registered, byte-pinned** table to one patch. | `proof-b:inputs/PINNED.json directive_action_map` |
| B7 | **The correlation id was derived, not assigned**, and the observer **recomputed it independently** and it matched. | `obs-b:§3 B-S4` |
| B8 | **The evidence was inspectable before anyone was asked.** Six locators probed anonymously before emission. | `proof-b:disposition.json outcome_fold.counts` |
| B9 | **14 falsifiers watched red**, each run twice — before and after the INSTR-3 correction — plus positive controls `F0`/`F0b` and F5b's negative half proving the policy control stays quiet when nothing changed. | `proof-b:disposition.json falsifiers`; `obs-b:§5.7` |
| B10 | **The ruler genuinely inspected.** It cites two workflow-run ids **absent from the evidence set**, which the observer queried and confirmed real at the exact head, `completed`/`success`; and its `evidence_refs_inspected` names **4 of 6** refs — it under-claims. | `obs-b:§5.6` |
| B11 | **The ruling came through a different credential path.** `performed_via_github_app` = `chatgpt-codex-connector` on the ruling comment versus `none` on the request and the receipt, with **zero crossovers** across 373 pre-existing venue comments the observer sampled as a control. | `obs-b:§5.1` |

**Caps — what Proof B does not establish:**

- **P-B-CAP-1 — independence is unmeasured, and that is the terminal grade's whole cause.** One
  account authored the candidate commits, the pull request, the request, the ruling and the receipt.
  The ruler **asserted** its own distinct execution context inside the ruling; the proof declined to
  credit the assertion, because independence is a property of the execution context, not a claim
  about it (`proof-b:disposition.json independence`; the observer files this as a wrong-subject
  finding on axis *stand-in*, `obs-b:§5.4`).
- **P-B-CAP-2 — the staleness ladder was evaluated against a subject that could not go stale.** The
  subject was Proof A's **merged** pull request in an **archived** repository. L1 passed trivially
  (a merged PR's head cannot move); L3 passed against protection nobody could change; and
  **falsifier 4's live half and falsifier 5's positive live half could not be run at all**. The
  proof establishes that the ladder's *comparators* behave correctly and leaves **could-not-observe**
  on whether the ladder catches a real moving candidate (`obs-b:§5.2`). This is the largest gap
  between what Proof B reads like and what it measured.
- **P-B-CAP-3 — the most severe instrument defect is missing from the terminal record's own ledger.**
  `disposition.instrument_defects_found_and_corrected` holds INSTR-1, INSTR-2, INSTR-3. **INSTR-4** —
  the consumer's terminal gate keyed on `observed-bad` alone, so a `RULING_LINEAGE_FORK`, which the
  shared vocabulary classes as **CNO**, fell straight through and consumed `rulings[0]` of two
  contradictory rulings — exists only as a trace `NOTE` and a parenthetical. A write-once record that
  omits its most severe defect teaches the wrong lesson about what write-once buys (`obs-b:§5.3`).
  The defect itself was found by qualifying the consumer against six synthetic universes **before any
  live ruling existed**, and corrected; §5.4 of this document makes the corrected shape structural.
- **P-B-CAP-4 — one evidence locator and its digest name different objects.** Ref 5 declares a sha256
  over a 680-byte extract while its locator returns the 31,121-byte page, so the aggregate
  `resolved=6/6 failures=[]` reads as a clean sweep and one of the six is not clean. The bytes were
  genuinely inspectable — the extract is embedded verbatim in the issue body and does hash to the
  declared value — so the ruler was not misled; what fails is the machine-checkable binding the
  schema's own `$comment` requires (`obs-b:§5.4`, wrong-subject on axis *property*).
- **P-B-CAP-5 — falsifier 1's target was relabelled after the observation.** The pin names its target
  `V2`; the executed record declares `V1`. Distinctness was therefore evaluated against a moved
  target, so **V2 was not watched red as a separately identified control** (`obs-b:§5.4`,
  wrong-subject on axis *instance*; `obs-b:§6.3`).
- **P-B-CAP-6 — the venue already owns the protocol name.** `sbracewell64/firstmate-sol-control` issue
  #1 (2026-08-15) declares `protocol: fm-sol-control/v1` over a **completely different** envelope. One
  version string now names two incompatible protocols in one repository. It did not bite, because the
  schema of record travelled in the issue body — but the mitigation is per-request rather than
  structural (`obs-b:§5.5`).
- **P-B-CAP-7 — economics are untested.** One decision against a frozen candidate says nothing about
  the retired fleet's measured 22 requests / 5 rulings / **45% superseded** (`corpus:§3.2`, OBSERVED
  there). That needs a different experiment, and Proof B says so.
- **P-B-CAP-8 — the guards are confused-agent-grade.** Anyone with the operator's token can post a
  comment that validates. The one thing that cannot be forged is the subject binding *and* the
  live-state predicates *and* the identity of the applied bytes simultaneously — a raised cost, not a
  boundary.
- **P-B-CAP-9 — the request ships a ruling skeleton with placeholder values**, which lowers the cost
  of a schema-valid, evidentially empty ruling. It is the one place the request supplies phrasing that
  can be filled without the underlying fact becoming true — the corpus's own template warning
  (`corpus:§3.4`) pointed back at the design (`obs-b:§5.6`).

### 2.3 The five things execution taught that the designs did not contain

**INFERRED**, and each is answered structurally below rather than by discipline.

1. **A fold rule authored during a run is not a verification contract.** Proof A's outcome flipped on
   a rule written with the answer in view; Proof B pinned the rule first, pre-registered the expected
   verdict, and graded *stricter* than expected. → §6.3, the pinning contract.
2. **A three-valued vocabulary needs a three-valued gate.** INSTR-4 is the transferable finding: a
   terminal gate written against two values silently consumes the exact case it was built to refuse.
   → §5.4 and [`sol-control-v1.md`](sol-control-v1.md) §6.
3. **A path fence bounds paths and cannot bound content.** "Confined to the right directories" is a
   weaker statement than "contains only intended source", and a fence cannot tell them apart.
   → [`no-mistakes-integration.md`](no-mistakes-integration.md) §7.
4. **A distinctness test that computes `target == observed` from one call is a tautology.** The target
   must be **pinned before the observation** and compared against what actually reddened, with the
   neighbour's state a required field. → §6.4.
5. **A record's own defect ledger must be derived from the trace, not typed alongside it.** INSTR-4
   was in the trace and absent from the ledger. → §6.2, the derivation rule.

---

## 3. The eleven load-bearing properties, and who owns each

Working backward from what was **observed to work**, these are the properties the architecture must
reproduce **structurally**. Anything not on this list is not required to reproduce the proofs and is
deliberately out of the first build ([`first-implementation-plan.md`](first-implementation-plan.md) §6).

| # | Property | Established by | Owner component |
|---|---|---|---|
| **L1** | Every observation is three-valued, folds under `FAIL > CNO > PASS`, and cannot be coerced. | A1, B4; `corpus:§2.1` | **K1** |
| **L2** | Every recorded value is derived from a file written **before** the value was parsed. | Proof A's 546 and Proof B's raw captures; `corpus:§3.5` | **K1** |
| **L3** | The verdict's rule, stage order, bounds and input digests are **pinned before the first observation** and never amended. | B2 versus P-A-CAP-1 | **K3** |
| **L4** | The terminal record is **written once**, refuses without stage coverage, and its outcome is folded rather than asserted. | A1, B2; `proof-a:disposition.json trace` | **K4** |
| **L5** | Every field name lives in **exactly one schema file**, and the reply instructions are generated from it. | B3 | **K5** |
| **L6** | Every control has been **watched red for its own pinned target**, with the neighbour's state recorded. | A9, B9 versus P-A-CAP-4, P-B-CAP-5 | **K6** |
| **L7** | Qualification is **mandatory**, its verdict is read from a typed field and never an exit code, and `checks-passed` is non-terminal. | A6 | **D2** |
| **L8** | Green is asserted only **at an exact head**, over a **complete** universe, with each entry recording its own head. | A4, A10; `corpus:§2.2` | **D3** |
| **L9** | An irreversible outward effect **spends a one-use, head-bound authority whose spend constructs the act**, and the post-condition is checked by **identity**. | A2, A3, A4, A7 | **D4**, **D5** |
| **L10** | Retry-versus-stop is **arithmetic against a durable record**, and budget exhaustion is a terminal state. | `boundary:§7.1` (the absence); `proof-a:disposition.json attempt_budget` | **D6** |
| **L11** | An external decision travels as a **typed artifact compiled from machine state**, is validated by a **three-valued** ladder, and is consumed by **byte identity** against a pre-registered action. | B5, B6, B7 | **R1**, **R2**, **R3** |

---

## 4. Lane A — the delivery state machine

Backward-derived from Proof A's observed execution. Each transition names the **evidence required to
enter**, the **evidence required to leave**, and the **refusal** that fires instead. Refusal codes are
drawn from the closed vocabulary in §4.3.

### 4.1 States and transitions

```
                    ┌──────────────┐
                    │ WORLD_UNFIT  │  (initial)
                    └──────┬───────┘
             tool floors, forge auth, pinned inputs, protection PROVED to refuse
                           ▼
                    ┌──────────────┐
                    │ WORLD_READY  │
                    └──────┬───────┘
                    pinned patch applied; tree == pinned tree
                           ▼
              ┌────────────────────────┐
              │ CANDIDATE_LOCAL        │  candidate_state = MUTATING
              └──────────┬─────────────┘
                    pre-gate G0–G11 all observed-good
                           ▼
              ┌────────────────────────┐
              │ CANDIDATE_ADMITTED     │  candidate_state = STABLE_FOR_VALIDATION
              └──────────┬─────────────┘
                    qualification invoked (the first irreversible act follows)
                           ▼
              ┌────────────────────────┐      ask-user finding
              │ QUALIFYING             │─────────────────────────► DECISION_OWED ──► (Lane B, or captain)
              └──────────┬─────────────┘
              outcome ∈ {checks-passed, passed}; attestation head-bound; steps completed
                           ▼
              ┌────────────────────────┐  candidate_state = ATTESTED
              │ QUALIFIED              │  local head and published head are separate fields
              └──────────┬─────────────┘
              every required check success at the published head, over a complete universe
                           ▼
              ┌────────────────────────┐  candidate_state = VALIDATED_EXACT_HEAD
              │ GREEN_AT_EXACT_HEAD    │
              └──────────┬─────────────┘
                    the eight-condition merge predicate, all observed-good
                           ▼
              ┌────────────────────────┐
              │ OBJECTIVELY_MERGEABLE  │
              └──────────┬─────────────┘
                    T1–T8 all observed-good → authorization minted
                           ▼
              ┌────────────────────────┐
              │ LANDING_AUTHORIZED     │  authorization.state = minted
              └──────────┬─────────────┘
                    act constructed from the record; digest re-checked; state → spending
                           ▼
              ┌────────────────────────┐
              │ LANDING                │  authorization.state = spending  (recorded ambiguity)
              └──────────┬─────────────┘
                    HTTP 200, merged: true
                           ▼
              ┌────────────────────────┐  authorization.state = spent
              │ LANDED                 │
              └──────────┬─────────────┘
                    merge_commit.parents[1] == authorization.expected_head
                           ▼
              ┌────────────────────────┐
              │ LANDED_VERIFIED        │
              └──────────┬─────────────┘
                    qualification run reached a terminal status, under a declared bound
                           ▼
              ┌────────────────────────┐
              │ TERMINALIZED           │
              └──────────┬─────────────┘
                    trace covers every stage; fold computed under the pinned rule
                           ▼
              ┌────────────────────────┐
              │ DISPOSED  (write-once) │──► RETAINED (mirror verified AFTER the mutation; archived)
              └────────────────────────┘
```

### 4.2 Transition contracts

| From → To | Evidence required to leave the source state | Refusal instead |
|---|---|---|
| `WORLD_UNFIT` → `WORLD_READY` | Tool floor met (**qualification tool ≥ the version that emits a head-bound attestation**); forge auth with the scopes the effects need; every pinned input digest matches; protection applied **and read back field-for-field**; at least one negative control observed the protection **actually refuse**. | `PRECONDITION_UNMET`; `CNO_TOOL_UNREACHABLE` |
| `WORLD_READY` → `CANDIDATE_LOCAL` | Patch applied to a **clean** worktree; `HEAD^{tree}` equals the pinned candidate tree. | `PRECONDITION_UNMET`; `DIRTY_TREE` |
| `CANDIDATE_LOCAL` → `CANDIDATE_ADMITTED` | The complete pre-gate, all `observed-good`. The predicate set, including the two wrong-subject guards, is owned by [`no-mistakes-integration.md`](no-mistakes-integration.md) §3. **Any CNO refuses**; a CNO here is never read as "no active run". | `WRONG_BRANCH`, `DIRTY_TREE`, `PRECONDITION_UNMET`, `CNO_INDETERMINATE` |
| `CANDIDATE_ADMITTED` → `QUALIFYING` | The recorded invocation contains **no forbidden flag** (`--yes`/`-y`, `--skip`, `--admin`, any force flag, any repo override). Entering this state is the **first irreversible act**: everything before it is local. | `PRECONDITION_UNMET` |
| `QUALIFYING` → `QUALIFIED` | Exactly one `outcome:` field, value ∈ `{checks-passed, passed}`, parsed from the **captured file**; exactly one live attestation marker; `attestation.head_sha` == live published head; `review`, `test`, `document` each `completed` (`skipped` is **not** compliant). | `QUALIFICATION_PARKED`, `QUALIFICATION_FAILED`, `ATTESTATION_ABSENT`, `ATTESTATION_HEAD_MISMATCH`, `CNO_INDETERMINATE` |
| `QUALIFYING` → `DECISION_OWED` | A gate object with no `outcome:`. The implementation worker **never answers its own finding**. Routed by a pre-registered policy table to Lane B, to the captain, or to abort. | — (a state, not a refusal) |
| `QUALIFIED` → `GREEN_AT_EXACT_HEAD` | For each required context, **exactly one** check run whose `name` matches, whose `head_sha` equals the published head, and whose `conclusion` is `success`; the listing's **fetched count equals its reported total**. Each entry records **its own head**. A run not `completed` is CNO and is re-polled under a **declared bound**, then refuses. | `CHECK_RED`, `CNO_INCOMPLETE_UNIVERSE`, `CNO_INDETERMINATE` |
| `GREEN_AT_EXACT_HEAD` → `OBJECTIVELY_MERGEABLE` | The eight-condition merge predicate of §7.1, **every failing condition reported, not just the first**. `mergeable == null` is **CNO, not false**. | `NOT_MERGEABLE`, `CNO_INDETERMINATE` |
| `OBJECTIVELY_MERGEABLE` → `LANDING_AUTHORIZED` | T1–T8 of §7.2, each carrying its own evidence reference. **Any T failing routes to the captain; it never lowers a bar.** | `PRECONDITION_UNMET` |
| `LANDING_AUTHORIZED` → `LANDING` | `authorization.state == minted`; the act is **constructed from the record**; `sha256(canonical(act)) == authorization.act_digest`. | `PRECONDITION_UNMET` |
| `LANDING` → `LANDED` | HTTP 200 with `merged: true`. 409 → `HEAD_MOVED` (**re-enter at `QUALIFIED` with the new head; never retry in place**). 405/422 → `MERGE_REFUSED_BY_FORGE`, quoting the forge's own text **marked as the forge's and kept apart from this system's verdict**. Timeout/unparsable → CNO, and **the PR state is read before any retry**. | `HEAD_MOVED`, `MERGE_REFUSED_BY_FORGE`, `CNO_INDETERMINATE` |
| `LANDED` → `LANDED_VERIFIED` | `merge_commit.parents[1] == authorization.expected_head` **and** `parents[0]` equals the pre-merge default head **and** the default ref now resolves to the merge commit. | `IDENTITY_MISMATCH` (terminal — something else landed; **never reported as success**) |
| `LANDED_VERIFIED` → `TERMINALIZED` | The qualification run reached a terminal status, sampled under a **declared bound**. An immediate sample with no declared bound is **not a result**. A run terminalizing as `ci_monitor_interrupted` is CNO **for terminalization** and is not a failure of the merge. | `CNO_INDETERMINATE` |
| `TERMINALIZED` → `DISPOSED` | Trace coverage complete for every stage in the pinned stage table, with matched `STAGE_ENTER`/`STAGE_EXIT` pairs and no `seq` gap; exactly one declared coverage exemption is permitted, and only for the disposition write itself, which cannot observe its own exit. | `CNO_OBSERVER_GAP` → `CNO_AT_<first uncovered stage>` |
| `DISPOSED` → `RETAINED` | The mirror **resolves the exact landed commit, verified after the mutation** — a backup verified only beforehand is an assumption by the time it matters. | `CNO_INDETERMINATE` |

**Idempotence, per state.** Re-entering a state is a no-op when its key already holds: repo full name
+ seed tree for `WORLD_READY`; post-apply tree for `CANDIDATE_LOCAL`; `(repo, branch, head)` for
`QUALIFYING`; `(pr_number, expected_head)` for `LANDING`. The one expensive case is the merge, and its
rule is fixed: **read PR state before minting or spending**, and `merged == true` with the right second
parent is an **idempotent success** that does not call the API again, while `merged == true` with the
wrong second parent is `IDENTITY_MISMATCH` and terminal.

### 4.3 Closed refusal vocabulary — Lane A

Total over every reachable non-success. **Every FAIL and every CNO stops the lane at that state.**
There is no continue-with-a-warning path.

| Code | Class | Meaning |
|---|---|---|
| `PRECONDITION_UNMET` | FAIL | a pinned floor, pre-gate predicate, or triggering condition is not met |
| `DIRTY_TREE` | FAIL | uncommitted changes where a committed head is required |
| `WRONG_BRANCH` | FAIL | detached HEAD, or the default branch, where a feature branch is required |
| `QUALIFICATION_PARKED` | FAIL | a gate object with no `outcome:` — the run is still owed a decision |
| `QUALIFICATION_FAILED` | FAIL | `outcome: failed` or `outcome: cancelled` |
| `ATTESTATION_ABSENT` | FAIL | no parseable head-bound attestation marker |
| `ATTESTATION_HEAD_MISMATCH` | FAIL | attestation head ≠ live published head |
| `CHECK_RED` | FAIL | a required check concluded anything but `success` at the exact head |
| `NOT_MERGEABLE` | FAIL | a merge-predicate condition failed |
| `HEAD_MOVED` | FAIL | live head ≠ authorized head at the moment of the act |
| `MERGE_REFUSED_BY_FORGE` | FAIL | the forge refused; its text is quoted **as the forge's** |
| `IDENTITY_MISMATCH` | FAIL | the landed second parent ≠ the authorized head |
| `CNO_TOOL_UNREACHABLE` | CNO | daemon, CLI, or forge unreachable |
| `CNO_INDETERMINATE` | CNO | an unreadable or not-yet-computed field, or a bound exhausted |
| `CNO_INCOMPLETE_UNIVERSE` | CNO | a listing's fetched count ≠ its reported total; **no negative claim may be made** |
| `CNO_OBSERVER_GAP` | CNO | a stage lacks trace coverage |
| `BUDGET_EXHAUSTED` | terminal | the attempt budget is spent. A terminal state, not a prompt to try harder. |

---

## 5. Lane B — the decision state machine

Backward-derived from Proof B's observed execution.

### 5.1 States and transitions

```
     ┌──────────────────┐
     │ QUESTION_RAISED  │   a decision exists; its subject is named
     └────────┬─────────┘
        BP1–BP7 (§5.3)
              ├──────────────► CATALOG_MISS        (BP1 fails: refuse; this is D2-B1)
              ├──────────────► CAPTAIN_RESERVED    (BP4 deny list: route to the captain AS A RECORD)
              ▼
     ┌──────────────────────┐
     │ BOUNDARY_CLASSIFIED  │  decision_class = DELEGATED_ENGINEERING
     └────────┬─────────────┘
        every field from a named machine source; correlation id DERIVED
              ▼
     ┌──────────────────┐
     │ COMPILED         │
     └────────┬─────────┘
        every evidence locator resolves ANONYMOUSLY to the exact bytes its digest names
              ▼
     ┌──────────────────┐
     │ DECISION_READY   │
     └────────┬─────────┘
        exactly one issue per correlation id; posted body captured and never edited
              ▼
     ┌──────────────────┐   fetched ≠ reported ──► CNO_INCOMPLETE_UNIVERSE (stop)
     │ EMITTED          │   now ≥ expires_at   ──► NO_ANSWER (terminal, distinct from a ruler's CNO)
     └────────┬─────────┘   two rulings        ──► FORKED (consume NEITHER)
        exactly one ruling selected BY VALIDATED CONTENT, never by containment
              ▼
     ┌──────────────────┐
     │ ANSWERED         │
     └────────┬─────────┘
        V1–V10 (§5.4), three-valued gate
              ▼
     ┌──────────────────┐
     │ VALIDATED        │
     └────────┬─────────┘
        L1–L5 against LIVE state — identity, never ancestry
              ▼
     ┌──────────────────┐
     │ APPLICABLE       │
     └────────┬─────────┘
        directive → pre-registered action; applied bytes verified by IDENTITY
              ▼
     ┌──────────────────┐
     │ CONSUMED         │
     └────────┬─────────┘
        receipt posted; issue closed
              ▼
     ┌──────────────────┐
     │ RECEIPTED        │ ──► if the action produced a code change, hand to Lane A at CANDIDATE_LOCAL
     └──────────────────┘      with a FRESH authorization. A ruling never authorizes a merge.
```

### 5.2 Transition contracts

| From → To | Evidence required to leave | Refusal instead |
|---|---|---|
| `QUESTION_RAISED` → `BOUNDARY_CLASSIFIED` | BP1–BP7 all `observed-good`, except that the independence predicate's value is recorded and **caps the grade** rather than stopping the lane (§5.5). **BP3's reversibility is executed, not asserted.** | `BOUNDARY_CAPTAIN_RESERVED`; catalog miss → stop |
| `BOUNDARY_CLASSIFIED` → `COMPILED` | Every field traceable to a **named command's output or forge read**; none from prose, memory, or a chat message. Correlation id **derived** by hash. The compile **refuses on any absent input**. | compilation refuses |
| `COMPILED` → `DECISION_READY` | Every `evidence_ref` fetched **unauthenticated, from outside the actor's session**, and its sha256 compared to the declared digest. Locator and digest must name **one object** (P-B-CAP-4). A branch or tag URL is refused by schema. | `CNO / DECISION_SUBJECT_NOT_INSPECTABLE` — the request is **not emitted** |
| `DECISION_READY` → `EMITTED` | The envelope validates against the schema; exactly one issue exists for this correlation id; the posted body is captured and is **never edited**. | emission refuses |
| `EMITTED` → `ANSWERED` | `fetched == reported` on the comment listing; **exactly one** comment whose fenced block validates as `kind: ruling` with the matching correlation id. Selection is by **validated content**; a comment that merely mentions the id neither counts nor suppresses. | `CNO_INCOMPLETE_UNIVERSE`, `RULING_LINEAGE_FORK` (CNO), terminal `NO_ANSWER` |
| `ANSWERED` → `VALIDATED` | V1–V10 (§5.4) through the **three-valued** gate of §5.5. | `RULING_MALFORMED`, `RULING_SUBJECT_MISMATCH`, `RULING_SUPERSEDED`, `RULING_LINEAGE_FORK` |
| `VALIDATED` → `APPLICABLE` | L1–L5 against **live** state, all identity comparisons. | `RULING_SUPERSEDED`, `RULING_MALFORMED` |
| `APPLICABLE` → `CONSUMED` | The directive maps through the **total** table to exactly one action; the applied bytes pass the identity check of §5.6. **No step reads the rationale and decides what to write.** | `REFUSED_MISMATCH` |
| `CONSUMED` → `RECEIPTED` | A receipt is posted for **every** terminal state, including refusals and withdrawals, and the issue is closed. A refusal that leaves no receipt is a silently abandoned request. | — |

### 5.3 The boundary predicate set

Owned here because it decides *whether Lane B is entered at all*.

| Id | Predicate | Read from | On failure |
|---|---|---|---|
| **BP1** | `question.key` is in the pre-registered catalog at its pinned digest | catalog file | stop — a novel subject is a catalog **miss**, not a judgement call (**D2-B1**) |
| **BP2** | ≥ 2 options, each with a `reversibility` class from a **closed set** | catalog entry | stop |
| **BP3** | **Reversibility is EXECUTED**: each option applies cleanly in a scratch worktree, reaches its pinned tree, and `git revert --no-commit` returns the tree to the base | `git apply --check`, `git revert --no-commit` | stop — an unrevertible option is not this class of decision |
| **BP4** | The **union** of both options' patches touches no path on the captain-reserved deny list: no `.github/**`, no dependency manifest, no `LICENSE`, no credential path, no new external service or spend | `git diff --name-only` per option | **`BOUNDARY_CAPTAIN_RESERVED`** → route to the captain, never compile a request |
| **BP5** | Maker/checker independence is **measurable** from the actor register | forge-recorded credential path first, author/committer/PR-author logins as the weaker fallback (§5.5) | CNO — **caps the grade**, does not stop the lane |
| **BP6** | `candidate_state` ∈ `{STABLE_FOR_VALIDATION, VALIDATED_EXACT_HEAD, ATTESTED}` — never `MUTATING` | qualification tool's branch-sync state + required checks complete at head | stop |
| **BP7** | Every evidence locator resolves for an unauthenticated third party to the **exact bytes its digest names** | an actual anonymous read | `CNO / DECISION_SUBJECT_NOT_INSPECTABLE` |

**BP4 is the only predicate whose failure routes to a human, and it fails closed.** An option whose
patch touches a workflow file is not a delegated engineering judgement, however innocuous, because
the candidate would then be adjacent to the policy that judges it — the corpus's canonical invariant,
*a candidate may not alter, select, or supply the acceptance-policy generation that judges that same
candidate* (`corpus:§1.7`, DOCUMENTED), applied to the **question** rather than only to the fix.

### 5.4 The validation ladder

The predicate list, its failure codes, and the wire shapes are owned by
[`sol-control-v1.md`](sol-control-v1.md) §§3–5. What is owned **here** is the fact that the ladder
exists as a state transition and that **every failing predicate is reported, not only the first**.

### 5.5 The three-valued terminal gate — the corrected shape

**This is the architecture's answer to INSTR-4 (P-B-CAP-3), and it is structural.**

```
blocking(entries)  :=  { e ∈ entries : e.value ≠ observed-good } \ { the pinned exceptions }
outcome(blocking)  :=  first code carried by an observed-bad entry,      (FAIL outranks CNO)
                       else first code carried by a could-not-observe entry,
                       else CNO_TRANSPORT
consume  iff  blocking(entries) = ∅  ∧  exactly one ruling was selected
```

Three rules make it correct, and each closes a defect that was actually observed:

1. **The gate keys on "not green", never on `observed-bad`.** A `RULING_LINEAGE_FORK` is a **CNO**;
   a gate written against two values let one through and consumed `rulings[0]` of two contradictory
   rulings (P-B-CAP-3).
2. **FAIL outranks CNO when selecting the refusal code**, so a real mismatch is never reported under a
   transport label. The same defect mislabelled a malformed ruling as `CNO_TRANSPORT` instead of
   `REFUSED_MALFORMED` — *a distinction dying at the last step before the operator* (`corpus:§1.4`).
3. **Every exception is pinned by name before the run.** In Proof B exactly one existed — the
   independence CNO caps the terminal grade instead of stopping the lane — and it was resolved
   **before the answer was in view**, and it cannot inflate the verdict because the grade is
   could-not-observe either way (`proof-b:inputs/PINNED.json` DEV-B7). **RECOMMENDED:** an exception
   that is not in the pin does not exist at run time.

### 5.6 "Correct ruling consumed" is an identity check

Three conjuncts, all required:

```
sha256(produced diff bytes)   ==  sha256(the pinned patch for that action)
resulting tree sha            ==  the pinned resulting tree for that action
changed paths                 ⊆   the action's declared path set
```

This is the answer to the corpus's most expensive review round-trip failure — a ruling that differs
from the reviewer's proposed remedy silently does not land, measured **three times on one task in one
day** — whose permanent fix the corpus states as **prose must not be the evidence** (`corpus:§4.2`,
DOCUMENTED). Proof B's F7 held on all three conjuncts and the observer reproduced the tree
independently (B5).

### 5.7 Closed refusal vocabulary — Lane B

**Owned by [`sol-control-v1.md`](sol-control-v1.md) §8**, as a fail-closed matrix mapping each
condition to its code, its class, and what happens next. The transition table in §5.2 above names those
codes; it does not define them. Two vocabulary rules travel with the table and are stated there: a code
is emitted at **exactly one site**, and a state outside the vocabulary must **not fail-close the whole
store** — at the retired fleet's barrier 84% of the landing-authority store was quarantined because one
record carried an out-of-vocabulary value (`corpus:§1.4`, OBSERVED there).

---

## 6. Records: who may write what, and when

### 6.1 Ownership table

**One writer per record.** A record with two writers is two sources of truth that diverge the moment
either moves (`corpus:§3.6`, DOCUMENTED).

| Record | Sole writer | Mutability | Consumer that cannot proceed without it |
|---|---|---|---|
| `inputs/PINNED.json` + its sha256 sidecar | the **pinner**, once, **before the first observation** | **write-once**, `amendable: false` | the fold; the falsifier harness; every digest check |
| `raw/<timestamp>-<tag>.{stdout,stderr,exitcode,argv.json}` | the **capture wrapper**, before any parse | append-only, never rewritten | every `evidence_ref` |
| `observations.jsonl` | the **actor**, append-only | never edited, reordered, or deleted | the fold |
| `trace.jsonl` | the **actor** (Lane A/B) or the **observer** (independent trace) | append-only, `seq` monotonic, gaps are a defect | the disposition write, which **refuses without coverage** |
| `authorizations/auth-<id>.json` | the **authorization owner**, state-machine transitions only | `minted → spending → spent \| refused`, never re-minted over `spending` | the landing chokepoint |
| `request.json` / `ruling.json` / `receipt.json` | compiler / **the external ruler** / consumer, respectively | the ruler's comment is **never edited or deleted by us**; a correction is a **second** record naming the first | the ladder, the action map, the receipt |
| `<id>.attempt` | the **attempt arithmetic owner** | monotonic; retired only by an ordinary teardown | the dispatch decision |
| `disposition.json` + sidecar | the **fold**, once, last | **write-once** | a human, and any downstream reader |

### 6.2 The disposition is write-once, and its ledgers are derived

**RECOMMENDED, and it is the direct answer to P-A-CAP-1 and P-B-CAP-3.**

1. `disposition.json` is written **exactly once**, at the end, and never rewritten. Proof B did this
   and the observer confirmed **zero rewrites across 36 subsequent poll cycles** (`obs-b:§4`). Proof A
   did not, and its `PROVED` reads as *proved under a rule authored during the run*.
2. The write **refuses** unless the trace covers every stage in the pinned stage table. Exactly one
   coverage exemption is permitted, declared in the pin, and only for the disposition write itself.
3. `outcome` is **folded**, never asserted, and the fold must be **reproducible from the record alone
   by a reader with no access to the session**. Both proofs meet this and I re-derived both (§0.2).
4. **Every enumerated ledger in the disposition is derived from the journal or the trace, never typed
   alongside it.** `instrument_defects`, `deviations`, `negative_controls`, `refusals`,
   `github_state_created`, and `d2_fired` are projections. This is the fix for INSTR-4 being present
   in the trace and absent from the ledger: a projection cannot omit what its source contains.
5. Where the rule produces an unflattering verdict, **the verdict is the record**
   (`proof-b:disposition.json write_once.statement`).

### 6.3 The pinning contract

**RECOMMENDED.** Before the first observation is appended, one write-once record fixes:

| Pinned item | Why, with the observation that forced it |
|---|---|
| the **fold rule**, with `amendable: false` and an explicit amendment counter | P-A-CAP-1: the rule was rewritten with the answer in view |
| the **stage table and its order** | the fold grades at the *earliest* non-pass in stage order; the order must not be chosen afterwards |
| **async bounds** — max attempts and interval — for every predicate depending on an external process | P-A-CAP-1's one outcome-changing exclusion was an unbounded sample; *an observation taken before its mechanism's declared bound is not a result* |
| the **digest of every input** | so the run cannot start against edited inputs |
| the **falsifier register**, each entry naming its **target** | P-B-CAP-5: a target relabelled after the observation makes distinctness unmeasurable |
| **declared deviations** from the design | Proof B pinned eleven in advance; only one was discovered during execution |
| **declared scope exclusions** | a limitation the system *could* enforce but chose not to is a **decision not to enforce**, recorded as such, and is **not** a CNO |
| the **pre-registered expected outcome** | it makes the pin falsifiable rather than decorative. Proof B pinned `CNO_AT_B-S9`; the run graded `CNO_AT_B-S3`, **earlier and stricter**. A rule bent toward a flattering answer does not produce that direction. |
| the **exception list for the terminal gate** | §5.5 rule 3 |

**The test that makes this real:** re-run the fold from the journal and the pin, with no access to the
session, and get the same string. Both proofs pass it (§0.2).

### 6.4 Watched-red, with the tautology removed

**RECOMMENDED, closing P-A-CAP-4 and P-B-CAP-5.** A negative control record must carry, as **required
fields**:

```
target        — the control it was pinned to redden, read from PINNED.json, never from this run
observed      — the control that actually reddened
neighbours    — the observed state of every other control at the same head   (required, not optional)
distinct      — computed as (target == observed) AND (every neighbour stayed green)
```

Scoring `distinct` as `target == observed` where **one call supplies both** is a restatement, not a
check. Where a mutation legitimately reddens an upstream control first, the honest record is
`target=X observed=Y distinct=false` **with the reason**, never a moved target.

**And the timing rule:** falsifiers run **before the run**, not immediately before the act they
falsify (P-A-CAP-9). Where a control genuinely cannot be exercised against the live subject — as
Proof B's falsifiers 4 and 5 could not, because the subject was archived — that is a **declared
limit**, recorded in the pin, and the end-to-end control is stated as **not watched red on the live
forge** rather than credited from its comparator (P-B-CAP-2).

---

## 7. The merge predicate and the expected-head gate, exactly as proven

### 7.1 The merge predicate

Evaluated **live**, from the forge, immediately before minting. **Every failing condition is reported,
not just the first.** Observed in `proof-a:mergeability.json`, all eight `observed-good`.

| # | Condition | Field | Three-valued rule |
|---|---|---|---|
| 1 | `state == "open"` | `.state` | — |
| 2 | `draft == false` | `.draft` | — |
| 3 | `mergeable == true` | `.mergeable` | **`null` is CNO, not false** — it means *not yet computed*. Re-poll under a declared bound (Proof A used 6 polls, 5s apart, and needed 1), then `CNO_INDETERMINATE`. |
| 4 | `mergeable_state == "clean"` | `.mergeable_state` | Meaningful **only because protection is on**; without required contexts a red PR is still `clean`. The **policy generation digest** is therefore recorded alongside the state, so a later reader can tell *which policy* the word "clean" was computed under. |
| 5 | `head.sha == published_head_sha` | `.head.sha` | identity |
| 6 | `base.ref == default_branch` | `.base.ref` | — |
| 7 | every required check `success` at that head | check-runs listing | complete universe required (`fetched == total_count`), else `CNO_INCOMPLETE_UNIVERSE` |
| 8 | conversation resolution satisfied | implied by 4 | — |

This is the GitLab ladder upstream already has (`firstmate:bin/fm-pr-merge.sh:224-322`) ported to the
forge where upstream has **nothing** (`boundary:§3.3`). That port is the whole of finding 2 in §1.

### 7.2 The authorization's triggering conditions

Evaluated at mint time, each written as an observation with its own evidence reference. Observed in
`proof-a:authorizations/auth-14593774-….json`, all eight `observed-good`.

| # | Condition |
|---|---|
| **T1** | the repository is the pinned one — **owner and name compared, not a URL substring** |
| **T2** | exactly one open pull request for the candidate branch, and it is the recorded number |
| **T3** | `attestation.head_sha == live PR head == every required check's head_sha` |
| **T4** | every required check `success`, and the whole §7.1 ladder `observed-good` |
| **T5** | **path fence** — the pull request's **own file list**, read from the forge, is inside the allowlist |
| **T6** | no file in the diff is a workflow, a pipeline config, a dependency manifest, or anything under the policy path set |
| **T7** | the **policy generation digest** equals the value recorded when the policy was applied |
| **T8** | the trace carries a good `STAGE_EXIT` for every prior stage |

**T5/T6 are the fixer fence made mechanical**, and they read the forge's own file list rather than
trusting the intent's out-of-scope prose. **T8 is the trace working as a control**: in Proof A it
**stopped the merge** because a stage had been left unclosed (A8). A control nothing refuses without
is decoration; this one refuses.

**Authority.** T1–T8 all `observed-good` authorizes **exactly one merge of exactly one head**. The
authority is scoped by its **triggering conditions**, not by its procedure — *narrow enough to be
useless in the next case rather than broad enough to be wrong once* (`corpus:§4.3`, DOCUMENTED). **Any
T failing routes to the captain; it never lowers a bar.**

### 7.3 The expected-head gate

```python
auth = load(auth_path)                       # the ONLY source of these values
assert auth.state == "minted"
act = { "method": "PUT",
        "path":   f"/repos/{auth.repo.owner}/{auth.repo.name}/pulls/{auth.pr_number}/merge",
        "body":   {"sha": auth.expected_head, "merge_method": auth.merge_method} }
assert sha256(canonical_json(act)) == auth.act_digest      # minted over this exact structure
write_state("spending"); trace(EFFECT_INTENT, act)
resp = http(act)                             # the only landing call in the architecture
trace(EFFECT_RESULT, resp); write_state("spent" if resp.ok else "refused")
```

- **The spend constructs the act.** There is no code path in which the head, repository, pull-request
  number or merge method comes from an ambient variable, so a caller cannot smuggle a different act
  past a valid authorization.
- **`spending` is a state, not a comment.** A crash mid-spend leaves a **recorded ambiguity**, and the
  recovery rule resolves it **from the forge, not from the record**: if not merged, mark `refused` and
  re-enter; **never mint a second authorization on top of a `spending` record**.
- **Watched red at the call site.** Calling the same endpoint with `sha` set to the base returned
  **HTTP 409** and a follow-up read confirmed `merged: false` (A3).
- **`--admin` and every force flag are forbidden and asserted absent** in the recorded invocation.

### 7.4 The post-condition: identity, not containment

```
merge_commit.parents[1]  ==  authorization.expected_head      # the authorized head IS a parent
merge_commit.parents[0]  ==  the pre-merge default head
default_ref              ->  merge_commit
```

Condition 1 is why squash and rebase merges are **disabled at repository level before anything is
built** (A5). Squash and rebase destroy the parent relation and force a patch-id or tree heuristic;
disabling them removes the case rather than detecting it. *Containment is not identity*
(`corpus:§1.1`), and here the relation is structural: the authorized head **is** a parent, or the
landing fails.

### 7.5 What actually enforces this, in descending strength — stated honestly

1. **Server-side.** `enforce_admins: true` plus required status checks means **no actor, including the
   repository owner and any agent holding the owner's token, can land an unqualified candidate.** This
   is the one control that survived a bypass attempt in the proof: HTTP **405** with the owner's own
   token (A2).
2. **Closed effect list.** Exactly two effect classes and a small, enumerated set of mutating calls.
   Any other mutating call is a defect, not a variation.
3. **Constructed acts** (§7.3).
4. **Banned flags**, asserted absent from the recorded invocation.

**Declared limit, preserved rather than dropped:** items 2–4 are **confused-agent-grade, not
adversarial-grade**. An agent with a free shell and the operator's token can call the forge API
directly. Only item 1 survives a deliberate bypass, and only for the merge. Both of upstream's guard
libraries declare exactly this about themselves (`firstmate:bin/fm-lease-lib.sh:38-48`,
`fm-gate-refuse-lib.sh:41-45`), and the honesty is what makes the rest of the claims worth anything.

**And the gap this leaves, named plainly:** the qualification pipeline's **push** reaches the remote
without passing any chokepoint this architecture owns, exactly as upstream's does (§1 finding 3). The
architecture does **not** re-guard it. Server-side branch protection is the defence for the protected
ref; the candidate branch is unprotected by design, and the record says so rather than implying
coverage it does not have.

---

## 8. The minimum component list

Fifteen components. Each has **one responsibility**, and each is on the list because a property in §3
cannot be reproduced without it. Nothing here is a wrapper over a thing that already works. The
retired fleet's own operating contract states the rule this list follows — *"start with the simplest
direct end-to-end path. Do not build wrappers, control planes, policy layers, custom verifiers, or
automation unless the direct path exposes a concrete blocker or repeated need that justifies the added
machinery"* (**OBSERVED** at `AGENTS.md:308-309`, `6d1a000e4e9c836eb120286d63682ca135577dfe`) — and it
is a rule the fleet wrote and did not apply to itself, growing `bin/` from 36,425 to 105,214 lines in
38 days (`corpus:§0`).

### 8.1 Kernel — shared by both lanes

| Id | Component | Single responsibility | Property |
|---|---|---|---|
| **K1** | `observe` | Produce a three-valued observation and the raw capture it derives from. Owns the precedence, the non-coercion rule, and the rule that **every capture is written before its value is parsed**. | L1, L2 |
| **K2** | `journal` | Append an observation or a trace event. Owns append-only-ness, `seq` monotonicity, and the stage-coverage query the disposition write consumes. | L4 |
| **K3** | `pin` | Write the pre-run record once and answer questions about it. Owns the pinning contract of §6.3 and refuses a second write. | L3 |
| **K4** | `fold` | Reduce the journal to one terminal outcome under the pinned rule and write the disposition once. Owns the closed outcome vocabulary and the coverage refusal. | L4 |
| **K5** | `vocabulary` | Be the **single file** defining every field name and enum for one protocol; validate any envelope against it; **generate** the reply contract by walking it; carry its digest in every envelope. | L5 |
| **K6** | `control-harness` | Run a falsifier, record `target`/`observed`/`neighbours`, and compute distinctness the non-tautological way (§6.4). | L6 |

### 8.2 Lane A — delivery

| Id | Component | Single responsibility | Property |
|---|---|---|---|
| **D1** | `candidate` | Own the candidate state machine and the deterministic pre-gate. Answer *may this candidate be admitted to qualification?* | L7 |
| **D2** | `qualify` | Invoke the qualification tool and translate its **typed** surfaces — the `outcome:` field, the attestation, the branch-sync state — into observations. Never interpret its exit code. | L7 |
| **D3** | `forge-observe` | Read the forge and produce observations: check runs at an exact head over a **complete** universe, the merge predicate, and the policy generation digest. **Read-only.** | L8 |
| **D4** | `authorize` | Own the one-use authorization record and its lifecycle, and **construct the act** at spend. Per-record isolation: one malformed record must not blind the store. | L9 |
| **D5** | `land` | Perform the single merge call from a constructed act, and verify the post-condition by **identity**. The only component in the architecture that moves a protected ref. | L9 |
| **D6** | `attempt` | Own the durable attempt count, the budget, and the terminal states. Answer *retry or stop?* as arithmetic. | L10 |

### 8.3 Lane B — decision

| Id | Component | Single responsibility | Property |
|---|---|---|---|
| **R1** | `boundary` | Evaluate BP1–BP7 and answer *is this decision delegated engineering, captain-reserved, or not in the catalog?* Owns the executed reversibility test and the deny list. | L11 |
| **R2** | `compile` | Build the request envelope **entirely from machine state**, derive the correlation id, probe every evidence locator anonymously, emit exactly one issue, and retrieve its comments **completely**. | L11 |
| **R3** | `consume` | Run V1–V10 and L1–L5, apply the three-valued terminal gate, map the directive through the **total** table to one pre-registered action, verify the applied bytes by identity, and post the receipt. | L11 |

### 8.4 Why nothing else is on the list

**RECOMMENDED.** Each of the following was considered and left out because no property in §3 needs it
to reproduce the proofs; several are on the explicit do-not-import list
([`first-implementation-plan.md`](first-implementation-plan.md) §6).

- **A decision surface / control-plane read layer.** Both lanes read their own state directly from
  records that have one writer each. A surface composing them is worth building when there are enough
  owners to compose, not before.
- **A route/capacity/qualification registry.** Nothing in either proof dispatches to a pool.
- **A commitment register, a loopspec registry, a vocabulary-collision register.** These are remedies
  for problems a clean start avoids by naming things once (`corpus:R9`).
- **A supervision watcher, wake queue, or pane model.** Neither proof supervises a live worker.
- **A publication guard.** The push happens inside the qualification tool; a guard around a call this
  architecture does not make would be a control credited to something it never examines — the exact
  wrong-subject class the proofs exist to avoid.
- **A second reviewer stage.** The selected qualification path owns its own rigor; adding an
  independent reviewer around it is the anti-double-review error upstream is emphatic about
  (`boundary:§6.2`).

---

## 9. Boundaries this architecture keeps

### 9.1 Agent cognition is bounded, and where

Agents appear in exactly three places, each with declared inputs, outputs, authority and acceptance:

| Phase | Input | Output | Authority bound | Acceptance |
|---|---|---|---|---|
| **Qualification's internal turns** (review, fix, test, document, lint, PR prose) | the candidate diff plus the intent bytes | typed findings, fix commits, PR body | the tool's fixed nine-step order, its typed findings schema, and the review-approved-head binding at push | the `outcome:` field and the head-bound attestation |
| **The ruler** (Lane B) | the request envelope and its content-addressed evidence | one ruling in a **closed** directive vocabulary, bound to an exact head/tree/policy | the schema; no field exists for a third option | V1–V10 and L1–L5 |
| **Intake** — deciding *what* to build and *which* question is being asked | the captain's request | a task with a pinned candidate patch or a catalog key | the catalog is finite; a miss refuses | the pre-gate and BP1 |

Everything else is code. The complete classification, including every avoidable cognition and the
machinery that removes it, is owned by [`determinism-assessment.md`](determinism-assessment.md).

### 9.2 The threat model, declared

**RECOMMENDED, carried from the corpus deliberately.** Every guard in this architecture except
server-side branch protection is **confused-agent-grade, not adversarial-grade**. Naming this is not
modesty; it is what stops a reader crediting the forge gate with forgery resistance it explicitly
disclaims (P-A-CAP-2), and it is the reason the disposition records `forge_gate` as *evidence the
pipeline ran* rather than *proof it could not have been forged*.

### 9.3 The bootstrap exception, decided before the gate is built

**RECOMMENDED.** The corpus's largest self-inflicted architectural wound was a gate that governed its
own delivery path: the publication guard was itself unlanded, so no candidate could be published, and
359 items queued while roughly a dozen validated candidates sat parked (`corpus:§3.1`, OBSERVED
there). The ruled lesson is to decide the exception **before** the gate exists.

> **BOOTSTRAP-EXCEPTION.** Exactly one commit — the seed, whose tree equals a pinned digest — may be
> pushed directly to the protected branch **while it is still unprotected**. Expiry: immediate;
> protection is applied in the same sequence and a negative control proves it refuses. Every later
> commit arrives through a landed pull request. The exception is **recorded in the disposition**, not
> merely honoured, and it is falsifiable: the default branch's first-parent chain must carry exactly
> **one** non-merge commit.

Proof A used it exactly once and the check confirms it (A10).

---

## 10. Could-not-observe register for this synthesis

Stated as results, not omitted.

| # | Question | Value | Why |
|---|---|---|---|
| 1 | Does the staleness ladder catch a genuinely **moving** candidate? | **could-not-observe** | The only executed subject was archived; the two live-forge falsifiers could not be run (P-B-CAP-2). |
| 2 | Is the ruling party a **distinct principal**? | **could-not-observe** | One account owns candidate, request, ruling and receipt. The forge-recorded credential path shows a distinct execution context (B11); the account holder authorized that app, so one human could still drive both. |
| 3 | Would Proof A's `PROVED` hold under a **pre-registered** fold rule? | **could-not-observe** | Not attempted. Every observation's value was unchanged by the amendment; only the rule moved (P-A-CAP-1). Resolving it needs attempt 2 under a pinned rule — a registered captain decision. |
| 4 | Does a declared verifier cover any of this? | **observed-bad** | `fm-verify.sh --list` declares five, none applicable. Every grade here except §0.2's two re-derivations is hand-made (**D2-S1**). |
| 5 | Does this architecture's throughput close where the retired fleet's did not? | **could-not-observe** | One landing and one round trip say nothing about volume against a moving trunk (P-B-CAP-7). The measuring experiment is named in [`first-implementation-plan.md`](first-implementation-plan.md) §5 and is a registered captain decision. |
| 6 | Is the qualification tool's behaviour on this host as its pinned source describes? | **partially observed** | Proof A ran it end to end at v1.61.0 and its typed surfaces behaved as `nm-scout:` describes. Claims about paths Proof A did not exercise — every `--skip` case, Bitbucket, crash recovery — remain DOCUMENTED from the pinned source. |
| 7 | Would Machinist behave as its source describes? | **could-not-observe** | No Go toolchain on this host; the scout could not build or run it (`machinist-scout:§0`). See [`machinist-integration-plan.md`](machinist-integration-plan.md). |
| 8 | Is this synthesis itself independent of the parties that produced the proofs? | **could-not-observe at the identity level** | Same host, same commissioning firstmate, same account. Process independence only. The same rule that caps the ruler's independence caps mine. |
