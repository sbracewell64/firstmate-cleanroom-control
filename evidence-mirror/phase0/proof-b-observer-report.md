# Proof B — independent observer report

```yaml
observer_task: cleanroom-proof-b-observer
role: read-only independent observer (no repository writes, no comments, no messages)
observed_run: artifacts/proofs/proof-b/attempt-1
window: 2026-09-01T23:21:27Z .. 2026-09-02T00:46Z (executor terminal disposition written 00:04:55Z)
observer_trace: artifacts/proofs/proof-b/observer/trace.jsonl (330 lines, seq 1..330, 0 gaps, 0 duplicates)
raw_captures: artifacts/proofs/proof-b/observer/raw/ (291 files, every capture written before any parse)
slot_base_for_fleet_citations: 6d1a000e4e9c836eb120286d63682ca135577dfe
```

## 1. Verdict

**The round trip happened, end to end, and the part that matters most survived independent
reproduction.** A schema-valid escalation left the executor, an outside party answered it, the answer was
validated on fifteen predicates and consumed by byte identity, and a receipt closed the loop. I rebuilt the
consumption from public artifacts alone and got the same tree.

**The executor's terminal grade `CNO_AT_B-S3` is correct, and I re-derived it independently.** Under the
fold rule pinned before the run, 141 observations fold to `CNO_AT_B-S3` — the earliest could-not-observe in
pinned stage order. My own fold, computed from `observations.jsonl` and `inputs/PINNED.json` without reading
`disposition.outcome`, produced the identical string.

**On Proof A's provenance lesson the answer is unambiguous and positive.** Proof A's disposition was written
four times and its fold rule changed mid-run with the answer in view. Proof B's disposition was written
**once**, at 00:04:55Z, and never rewritten across the 36 subsequent observer poll cycles; the fold rule was
pinned at 23:35:00Z, before the first measurement, marked `amendable: false`, and carries `amendments: 0`.
The pin even **pre-registers the expected verdict** (`CNO_AT_B-S9`, "PROVED is not reachable in this attempt
and is not being aimed at"). The actual grade came out *stricter* than the pin expected, not softer.

**What the run does not establish is narrower than the run reads.** The subject was Proof A's already
**merged** candidate in an **archived** repository. A head that cannot move cannot go stale, so the L1/L2/L3
staleness ladder passed against a subject incapable of failing it, and the two live-forge falsifiers that
would have watched those controls red could not be run at all. Independence remains unmeasured at the
principal level. And one instrument defect — the most severe of the four found — is missing from the terminal
record's own defect ledger.

| Question | Value | Basis |
|---|---|---|
| Round trip completed request → ruling → validated consumption → receipt | **observed-good** | issue #47 closed with exactly 2 comments; receipt `outcome: CONSUMED` |
| Terminal disposition written once, fold rule pinned first | **observed-good** | 1 creation, 0 rewrites; `PINNED.json` at 23:35:30Z, `amendments: 0` |
| Applied bytes are the ruled bytes | **observed-good** | observer reproduced tree `0c0c0cf5…` from the public repo |
| Escalation compiled from machine state | **observed-good** | 52 `C:` predicates each naming a command; correlation id recomputed by observer |
| Sol independently inspected the evidence | **observed-good** | ruling cites two workflow-run ids absent from the evidence set; both verified real at the exact head |
| Ruler is a distinct execution context | **observed-good** (credential path) | `performed_via_github_app` differs between ruling and request/receipt |
| Ruler is a distinct principal | **could-not-observe** | one account owns candidate, request, ruling and receipt |
| Stale-state controls exercised against a subject that could go stale | **could-not-observe** | subject repo archived; falsifiers 4 and 5 live halves unrunnable |
| Terminal record lists every instrument defect found | **observed-bad** | INSTR-4 present in the trace, absent from the disposition ledger |
| Every evidence locator resolves to the bytes its digest names | **observed-bad** | 5 of 6 verified by the observer; ref 5 does not |
| Any human decided anything inside the round trip | **observed-bad** (i.e. none did) | two decision records, both `CAPTAIN_DEFERRED`; no captain input before terminal |

## 2. How I observed, and the limit on my own independence

Separate process, separate worktree (`…/5/`), separate pane (`wF4:p2`) from the executor (`…/4/`, `wF3:p2`).
I wrote only under `artifacts/proofs/proof-b/observer/` and this report; I made no forge write of any kind.

A background poller ran on a 60-second cadence from 23:25Z, and on every cycle it: hashed every file under
`artifacts/proofs/proof-b/` outside my own directory and emitted a trace event for each appearance, rewrite
(with **before and after digests**) and deletion; polled both candidate venues plus the subject repo; fetched
each issue and its comments with `--paginate` and recorded the completeness predicate `fetched == reported`
on every read; and tailed the executor's status file. Every capture was written to `raw/` before any parse.

**My independence is `could-not-observe` at the identity level and `observed-good` at the process level.** I
am a different process with different state, but I share the host and the same `gh` credential as the
executor, and I was commissioned by the same firstmate. Corpus §2.5's rule applies to me as much as to the
ruler: independence is a property of the execution context, not of a name.

**No declared verifier covers any of this.** `bin/fm-verify.sh --list` returns exactly `browser`,
`pr-checks`, `merge-clean`, `review-exec`, `review-mutation`; none is declared for a clean-room proof. Every
observation below is hand-graded, and the undeclared verifier is reported here as a gap rather than absorbed.

## 3. Designed pathway versus observed execution

| Stage | Design | Observed | Grade |
|---|---|---|---|
| B-S1 control repo | new repo `sbracewell64/fm-cleanroom-control`, issues enabled | **never created** — HTTP 404 on every poll from 23:22Z to 00:36Z. Venue was one new issue on the pre-existing private `sbracewell64/firstmate-sol-control` | deviation, pre-registered `DEV-B1` |
| B-S2 candidate prep | a fresh **open** qualified candidate PR | Proof A's **merged, closed** PR #2 at head `281e15b2`, in an **archived** repo | deviation, pre-registered `DEV-B5` |
| B-S3 boundary | BP1–BP7, all `observed-good` | 6 predicates evaluated; BP1–BP4, BP6–BP7 good; **BP5 could-not-observe**; BP3 reversibility genuinely executed (apply + `git revert --no-commit`, recorded as a `NEGATIVE_CONTROL`) | as designed, one CNO |
| B-S4 compile | every field from machine state | 52 `C:` predicates across three compile passes, each naming its command. Correlation id derived, not assigned — **I recomputed it independently** and it matches | observed-good |
| B-S5 readiness | anonymous third-party resolution of every locator | 6 probed; I re-probed all 6 myself: 5 byte-identical, 1 not (see §5.4) | mixed |
| B-S6 emit | one issue, body = validated envelope | issue #47 created 23:42:41Z; posted envelope is canonically identical to `request.json`; schema of record and the reply contract embedded in the body | observed-good |
| B-S7 ruling | one comment, `kind: ruling` | comment 5502255519 at 23:59:40Z, `ruled_at` 23:58:22Z, `ADOPT_OPTION/A`, `single_writer_assertion: true`, `supersedes: null` | observed-good |
| B-S8 retrieve | complete comment universe | 5 poll attempts of a pinned 18×300s bound; `fetched=1 reported=1` on the terminating read; my own polls agreed on every cycle | observed-good |
| B-S9 ladder | V1–V10 | all ten recorded; nine good, **V7 could-not-observe** | as designed |
| B-S10 live state | L1–L5 | all five recorded, all good — but see §5.2 | see §5.2 |
| B-S11 consume | directive → byte-pinned patch, identity check | `ADOPT_OPTION/A → ACT-A-IGNORE-BUILD-METADATA`; diff bytes identical, tree matches pin, paths a subset, tests pass — **reproduced by me** | observed-good |
| B-S12 receipt | receipt comment then close | comment 5502291831 at 00:04:04Z, issue closed 00:04:26Z | observed-good |
| B-S13 land | land through Proof A's path | **not attempted** — applied in a local scratch clone, nothing pushed, repo never unarchived | deviation, pre-registered `DEV-B6`, declared out of scope |
| B-S14 disposition | written once, last | written once at 00:04:55Z, digest matches its sidecar | observed-good |

## 4. The provenance question, answered directly

This is what the observation was commissioned for, and it is the run's strongest result.

**The fold rule was pinned before the first measurement and never moved.** `inputs/PINNED.json`, mtime
23:35:30Z, `pinned_at: 2026-09-01T23:35:00Z`, `fold_rule.amendable: false`, `fold_rule_defects: []`. Its
digest matches the `PINNED.sha256` sidecar written beside it, and I observed **zero** rewrites of either file
across the whole run. The first request compile was at 23:39:52Z, the issue went up at 23:42:41Z, and the
ruling arrived at 23:59:40Z — every measurement is after the pin.

**The pin is falsifiable rather than decorative**, because it names the expected answer in advance:

> the EXPECTED terminal outcome of this attempt, pinned here before execution, is `CNO_AT_B-S9`. PROVED is
> not reachable in this attempt and is not being aimed at.

The run then graded `CNO_AT_B-S3` — earlier and stricter than the pin expected, because BP5's independence CNO
precedes V7's in pinned stage order. A rule bent toward a flattering answer does not produce that direction.

**The terminal record was written once.** `disposition.json` appeared once, at observer cycle 00:05:48Z (file
mtime 00:04:55Z), sha256 `374490eb08be434b…`, matching `disposition.sha256`. Across the 36 further poll cycles that ran while it existed, to
00:46Z, I observed **no rewrite**. `write_once.amendments` is 0 and its own statement reads: *"Where the rule
produces an unflattering verdict, the verdict is the record."*

**The journals are append-only, and I proved it rather than accepting it.** I hold 10 captured versions of
`observations.jsonl` (3,397 → 41,919 bytes) and 11 of the executor's `trace.jsonl` (6,065 → 86,410 bytes).
Each version is a strict byte-prefix of the next. Nothing was edited or reordered.

**The one record that was genuinely rewritten was rewritten before it left the machine.** `request.json` has
three versions — 23:39:52Z, 23:40:42Z, 23:41:56Z — all before the 23:42:41Z issue creation. I diffed them:

- v0 → v1 corrected `candidate.base_sha` from the head itself to the true merge-base. In v0 the diff evidence
  ref carried sha256 `e3b0c442…`, which is the digest of the **empty string** — the compare range was empty.
- v1 → v2 moved blob locators from `github.com/blob/` to `raw.githubusercontent.com`, the commit locator to
  `.patch`, and dropped two `check_run` refs.

Both are disclosed by the executor as `INSTR-1`, `INSTR-2` and `DEV-B12`, and its accounts match what I saw
from outside. That correspondence is itself evidence: the disclosure was not reconstructed after the fact.

**One structural gap, recorded rather than inferred.** The correlation id hashes only
`(protocol, repo, branch, head_sha, question.key, policy_digest)`. It stayed constant across all three request
versions while the evidence set changed materially. Nothing went wrong here, because only v2 was ever emitted
— but a ruling bound to a correlation id is not thereby bound to the evidence its ruler was shown.

## 5. Findings

### 5.1 The forge held a better independence instrument than the ladder asked for — and nobody read it

The design measures independence as `ruler.login ∉ {commit author, committer, PR author}` (V7). With one
account that returns could-not-observe, which the design pre-registers as its weakest joint (`D2-B2`).

GitHub records a second, stronger fact that neither the design nor the executor consulted:

| Object | `performed_via_github_app` |
|---|---|
| issue #47 (the request) | `none` |
| comment 5502255519 (**the ruling**) | **`chatgpt-codex-connector`** — OpenAI's GitHub App, id 1144995 |
| comment 5502291831 (the receipt) | `none` |

I ran a control over 373 pre-existing comments in venue issues #9, #19, #36 and #40. Every comment whose
in-body `from:` names `firstmate` carries `app=none` (138 sampled). Every comment whose `from:` names
`browser-sol*` or `captain*` carries `app=chatgpt-codex-connector` (168 sampled). **Zero crossovers.** The
field is a credential-path fact the forge writes, not a self-declared string, and it separates the two parties
cleanly in this venue's whole history.

**What this does and does not establish.** It establishes `observed-good` that the ruling was written through
a different credential path — a genuinely different execution context, and a different model vendor
altogether. It does **not** establish a distinct principal: the account holder authorized that app, so one
human could still drive both. Principal-level independence stays could-not-observe. But the design's own
citation — independence is a property of the execution context, not of a name — is exactly the axis this field
measures and the login does not.

**Recommendation.** V7 should read `performed_via_github_app` (and the app slug) as a first-class axis
alongside the login, three-valued, with the login retained as the weaker fallback. That single change would
have moved this attempt's independence from unmeasured to measured-on-the-axis-that-matters.

### 5.2 The staleness ladder was evaluated against a subject that could not go stale

`L2` in the design is `live PR state == "open"`, failing to `RULING_SUPERSEDED`. The executor's L2 reads
`live PR state EQUALS the state recorded at compile time`, measured `closed vs closed`. The subject is Proof
A's merged PR in a repository that is `archived: true`, `pushed_at 2026-09-01T23:04:14Z` and unchanged since.

The executor pre-registered this as `DEV-B5` before the run, and named exactly what it costs. I confirm the
cost is real and larger than one predicate:

- L1's identity check passed trivially — a merged PR's head cannot move.
- L3 passed against protection nobody could change — an archived repo is read-only.
- Falsifier 4's live half (push a commit after the ruling) and falsifier 5's positive live half (change a
  required context after the ruling) **could not be run at all**. Their comparators were exercised with
  synthetic inputs, so the end-to-end staleness controls were never watched red on the live forge.

So the proof establishes that the ladder's *comparators* behave correctly, and leaves
**could-not-observe** on whether the ladder catches a real moving candidate. That is the single largest gap
between what Proof B reads like and what it measured, and it follows from the choice of subject rather than
from any defect in the machinery.

### 5.3 The most severe instrument defect is missing from the terminal record's own ledger

`disposition.instrument_defects_found_and_corrected` holds `INSTR-1`, `INSTR-2`, `INSTR-3`. A fourth exists —
`INSTR-4` — recorded only as a `NOTE` at trace seq 154 (23:48:21Z) and as a parenthetical inside the F12
predicate text. In the executor's own words:

> The terminal-branch gate keyed on observed-bad ALONE, so a `RULING_LINEAGE_FORK` — which the shared refusal
> vocabulary classes as CNO, not FAIL — fell straight through to consumption and CONSUMED `rulings[0]` of two
> contradictory rulings. That is exactly the corpus failure design §6.1 exists to prevent, reproduced inside
> the consumer built to prevent it.

It was found by self-qualification against synthetic universes **after** the request was emitted but **before**
any live ruling existed, and it was corrected; F12 now watches it red. The handling is exemplary. The record
is not: a reader of `disposition.json` alone learns of three defects, and the one it omits is the one where
the consumer once consumed a forked ruling. This is a completeness defect in a write-once record, not a
rewrite — the record was never altered, it was incomplete when written.

### 5.4 Three wrong-subject findings

```
wrong-subject finding (axis: property)
  check:       proof-b attempt-1 B-S5 aggregate observation: BP7 EVERY evidence locator is third-party inspectable
  examined:    the semver.org page at the ref-5 locator returns HTTP 200 and contains the anchor sentence, and its own fetched digest was recorded
  credited:    every evidence_ref resolves for an unauthenticated third party to the exact bytes its sha256 names (resolved=6/6 failures=[])
  credited-as: pass
  gap:         ref 5 declares sha256 683f9e2920b262cf... over a 680-byte extract while its locator returns the 31121-byte HTML page hashing f9d4b8b1a5e9a0de..., so locator and digest name different objects
  therefore:   the credited claim is could-not-observe, not pass
  remedy:      hash the object the locator actually returns, or make the locator address the extract - the extract is embedded verbatim in the issue body and does hash to the declared value, so an api_capture locator naming that body would close it
  evidence:    artifacts/proofs/proof-b/attempt-1/observations.jsonl B-S5 entries
  evidence:    artifacts/proofs/proof-b/observer/trace.jsonl OBS-EVIDENCE

wrong-subject finding (axis: stand-in)
  check:       proof-b attempt-1 ruling.inspection.observations[5], authored by the ruler
  examined:    requester.session_ref and ruler.session_ref hold different strings inside the ruling envelope
  credited:    the ruling execution context is distinct from the maker and executor context despite the shared GitHub identity
  credited-as: pass
  gap:         both session_ref values are authored by the party whose independence they assert, so any single actor can write two different strings
  therefore:   the credited claim is could-not-observe, not pass
  remedy:      read the forge's own credential-path record: the ruling comment carries performed_via_github_app=chatgpt-codex-connector while the request issue and the receipt comment carry none
  evidence:    artifacts/proofs/proof-b/observer/raw/obs-issue47-comments-final.json

wrong-subject finding (axis: instance)
  check:       proof-b attempt-1 falsifier 1 distinctness record
  examined:    a ruling body with corelation_id reddens control V1 and the schema refusal names the misspelt field
  credited:    falsifier 1 watched control V2 schema validation red for its own reason, with target matching observed
  credited-as: pass
  gap:         inputs/PINNED.json pins falsifier 1's target as V2 while the executed record declares its target V1, so distinctness was evaluated against a target relabelled after the observation
  therefore:   the credited claim is could-not-observe, not pass
  remedy:      record pinned-target V2 against observed-control V1 and grade distinctness false, or add a mutation that reddens V2 while leaving V1 green
  evidence:    artifacts/proofs/proof-b/attempt-1/inputs/PINNED.json falsifiers n=1
```

The first is the one with a practical consequence: the aggregate `resolved=6/6 failures=[]` reads as a clean
sweep, and one of the six is not clean. The bytes are genuinely inspectable — the 680-byte SemVer §10 extract
is embedded verbatim in the issue body and does hash to the declared digest, which I confirmed — so the ruler
was not misled. What fails is the machine-checkable binding between `locator` and `sha256` that the schema's
own `$comment` requires, and locator 5 additionally mixes a URL with prose.

### 5.5 The venue the design specified was never built, and the venue used already owns the protocol name

`sbracewell64/fm-cleanroom-control` returned 404 on every poll for 74 minutes. The run used a new issue on the
retired fleet's private `sbracewell64/firstmate-sol-control` — pre-registered as `DEV-B1`, with the
`CLEANROOM-PROOF-B:` title prefix, touching no existing issue.

That venue **already declares `fm-sol-control/v1`**. Issue #1 (2026-08-15) carries `protocol: fm-sol-control/v1`
over a completely different YAML envelope — `classification`, `firstmate_recommendation`,
`captain_required_by_firstmate` — and Sol's routine replies there use `kind: control-evidence-update`, not the
clean room's `kind: ruling`. One version string now names two incompatible protocols in one repository.

It did not bite here: the executor embedded the schema of record in the issue body, generated the reply
contract from it, and the ruler answered in the new shape on the first attempt. But it is the corpus's own
costliest transport failure — rulings that failed to attach because reply vocabulary was reconstructed — sitting
one mistake away, and the mitigation is entirely per-request rather than structural. **This belongs in
`docs/vocabulary-collisions.md`** as a ruled disposition, and a clean-room protocol should carry a version
string the retired fleet does not already own.

### 5.6 What the round trip genuinely proved about the ruler

Three independent signals, and the third is the one a sceptic should want:

1. **Timing.** Issue posted 23:42:41Z; `ruled_at` 23:58:22Z; comment posted 23:59:40Z. Fifteen minutes and
   forty-one seconds — not an echo, and the 78-second gap between ruling and posting is the shape of composing
   a document and then sending it.
2. **Self-limited inspection claim.** `inspection.evidence_refs_inspected` names **4 of 6** refs — the three
   raw blobs and the anchor — and does not claim the diff or the commit patch. It under-claims, which is the
   opposite of what a fabricated ruling does.
3. **Evidence the request never supplied.** The ruling cites workflow runs `33568974962` (ci) and
   `33568974944` (Require no-mistakes). Those are not in the evidence set — the `check_run` refs were dropped
   at request v2. I queried both: real, at head `281e15b2`, `completed`/`success`. A ruler filling the reply
   skeleton could not have invented them.

Against that, one caution: the issue body ships a **ruling skeleton with placeholder values**. It lowers the
cost of a schema-valid, evidentially empty ruling. The design anticipated this and the consumer records what
was inspected — but the skeleton is the one place the request supplies phrasing that can be filled without the
underlying fact becoming true.

### 5.7 Smaller observations

- **Byte identity versus content identity.** Definition of Done §2 asks that the local envelopes be
  byte-identical to what the control plane holds. They are canonically identical but not byte-identical
  (posted request block `14c3639e…` vs local file `0034fa33…`; posted ruling block `6172a009…` vs local
  `66b14758…`). The digest that actually travels — `receipt.ruling_sha256` — is taken over the **posted**
  bytes, and I reproduced it independently, so third-party joinability is intact.
- **`vocabulary_digest` is reproducible from the control plane alone.** The schema of record is embedded as
  the issue body's third fenced block; sha256 of those bytes plus the trailing newline is
  `72bcfa5253c0db59…`, equal to the declared digest and to the local schema file. Verified by me.
- **Effect logging is complete.** The executor's trace holds exactly three `EFFECT_INTENT`/`EFFECT_RESULT`
  pairs, matching its three mutating acts, each intent written before the call.
- **Falsifier coverage is better than the trace suggests.** All ten design falsifiers ran, plus `F0`/`F0b`
  positive controls, `F5b` (the negative half — L3 stays quiet when nothing changed), `F8b`/`F8c`, `F11` and
  `F12`; 14 distinct falsifier observations, each run twice, before and after the `INSTR-3` correction. Only 7
  carry a `NEGATIVE_CONTROL` trace event; the rest are `OBSERVATION` entries, so a reader counting trace
  events would undercount them.
- **B-S14 coverage exemption is declared, not silent** — "the disposition write cannot observe its own exit",
  and coverage gates `PROVED` only.

## 6. Could-not-observe register

Stated as results.

| # | Question | Value | Why |
|---|---|---|---|
| 1 | Is the ruling's principal distinct from the maker's? | could-not-observe | one account owns every artifact; the app installation is authorized by that same account |
| 2 | Does the staleness ladder catch a genuinely moving candidate? | could-not-observe | archived repo; falsifiers 4 and 5 live halves unrunnable |
| 3 | Was control V2 watched red as a separately identified control? | could-not-observe | falsifier 1's pinned target V2 was relabelled to V1 after the observation |
| 4 | Does evidence ref 5 resolve for a third party to the bytes its digest names? | observed-bad, and the credited aggregate is could-not-observe | locator returns the 31,121-byte page; digest is over the 680-byte extract |
| 5 | Was a human in the loop of the ruling itself? | could-not-observe | the forge records a credential path, not who drove it |
| 6 | Is my own observation independent of the executor? | could-not-observe at identity level | shared host, shared `gh` credential, same commissioning firstmate |
| 7 | Does a declared verifier cover any of this? | observed-bad | `fm-verify.sh --list` declares five, none applicable; every grade here is hand-made |
| 8 | Would the round trip work against a live open candidate? | could-not-observe | never attempted; `B-S13` declared out of scope |

## 7. Interventions, distinguished

- **No captain input reached the executor before its terminal disposition.** Two decision records exist —
  `control-plane-economics-experiment` and `sol-ruling-identity` — both with disposition `CAPTAIN_DEFERRED`,
  and both are live captain holds under origin `cleanroom-proof-b-executor`, which I verified.
- **The executor did not author the ruling.** Its complete instrumented command inventory (26 `meta.json`
  records) contains exactly one `gh issue create` (23:43:04Z, the request) and exactly one `gh issue comment`
  (00:04:28Z, the receipt). No command posts a ruling, and its trace holds no fourth effect pair.
- **The ruling came from a distinguishable actor** — the ChatGPT Codex Connector app, §5.1.
- **No comment in the venue was edited after posting.** Both comments carry `updated_at == created_at`, and my
  poller watched for edits on every cycle.
- **No third issue, no second ruling, no lineage fork.** Of 47 issues in the venue, exactly one names the
  correlation id; it is the only issue created after 23:00Z; its comment count was `fetched=2 reported=2` on
  every read.

## 8. Recommendations

1. **Make `performed_via_github_app` a first-class independence axis in V7**, three-valued, with the login as
   the weaker fallback. It is forge-recorded, third-party readable, and it discriminated the two parties
   perfectly across 373 control comments. This is the highest-value change the observation surfaced.
2. **Run the next attempt against a live, open candidate**, so L1/L2/L3 and falsifiers 4 and 5 can be watched
   red on the live forge. Until then, the staleness claim rests on comparators, not on the control.
3. **Add `INSTR-4` to the disposition's instrument-defect ledger**, or state in the ledger that the trace is
   its authoritative superset. A write-once record that omits its most severe defect teaches the wrong lesson
   about what write-once buys.
4. **Bind the evidence set into the correlation id**, or add a separate `evidence_digest` to `valid_while`, so
   a ruling is bound to the evidence its ruler was shown and not only to the head.
5. **Fix evidence ref 5** so `locator` and `sha256` name one object, and refuse a locator carrying prose.
6. **Grade falsifier distinctness against the pinned target**, never against a target relabelled after the
   observation. Where a mutation legitimately reddens an upstream control first, record
   `target=V2 observed=V1 distinct=false` and say why, rather than moving the target.
7. **Rule the `fm-sol-control/v1` collision in `docs/vocabulary-collisions.md`**, and give clean-room protocols
   a version string the retired fleet does not already own.
8. **Drop the reply skeleton, or bind it.** Keep the generated required-field contract; the pre-filled
   placeholder envelope is the one affordance that makes an evidentially empty ruling cheap.

## 9. Positive executed counts

Never "no failures found" — here is what actually ran.

| Measure | Count |
|---|---|
| Observer trace events written | 330 (seq 1..330, 0 gaps, 0 duplicates) |
| Observer raw captures, all written before parse | 291 |
| Observer poll cycles completed | 71 |
| Executor observations independently re-folded | 141 (139 good, 0 bad, 2 CNO) |
| Executor artifact appearances / rewrites / deletions observed | 142 / 35 / 0 |
| Terminal-record rewrites observed | **0** (`disposition.json`, `PINNED.json`, `ruling.json`, `receipt.json`, `validation.json`) |
| Append-only journal versions verified prefix-extending | 21 (10 observations, 11 trace) |
| Evidence locators re-resolved anonymously by the observer | 6 (5 byte-identical, 1 mismatched) |
| Comment universes checked for completeness (`fetched == reported`) | every poll; always equal |
| Venue comments sampled for the independence control | 373 across 4 pre-existing issues |
| Ladder predicates recorded by the executor | 15 (V1–V10, L1–L5), 14 good, 1 CNO |
| Falsifier observations recorded | 14 distinct, each run twice |
| Workflow runs cited by the ruler and verified by the observer | 2 (both real, at the exact head, success) |
| Consumption reproduced independently by the observer | 1 (tree `0c0c0cf5…`, 3 paths, 50 tests passing) |
| Correlation ids recomputed independently by the observer | 1 (matches) |
| Mutating forge calls made by the observer | **0** |

## 10. Evidence index

| Artifact | Path |
|---|---|
| Observer trace | `artifacts/proofs/proof-b/observer/trace.jsonl` |
| Change journal (appearance / rewrite / venue events) | `artifacts/proofs/proof-b/observer/raw/change-journal.log` |
| Issue #47 body as fetched | `…/observer/raw/obs-issue47-body.md` |
| Both comments as fetched | `…/observer/raw/obs-issue47-comments-final.json` |
| Ruling comment body | `…/observer/raw/obs-ruling-comment-5502255519.txt` |
| Captured executor artifact versions (before/after) | `…/observer/raw/*-exec-attempt-1__*` |
| Executor terminal record | `artifacts/proofs/proof-b/attempt-1/disposition.json` (sha256 `374490eb08be434b…`) |
| Pinned fold rule | `artifacts/proofs/proof-b/attempt-1/inputs/PINNED.json` (sha256 `276ccf45a7444e7e…`) |
| Control plane | `https://github.com/sbracewell64/firstmate-sol-control/issues/47` (closed, 2 comments) |
| Subject | `https://github.com/sbracewell64/fm-cleanroom-proof` PR #2, head `281e15b292d0e604d7aac4c1f15413efaf8ee8ed` |
