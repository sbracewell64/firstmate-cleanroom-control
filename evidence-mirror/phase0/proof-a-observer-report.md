# Proof A — independent observer report

**Observer:** task `cleanroom-proof-a-observer`, a separate worker process, read-only throughout.
**Window observed:** 2026-09-01T22:38:42Z to 2026-09-01T23:12Z.
**Subject:** the Proof A execution by task `cleanroom-proof-a-executor`.
**Machine-readable trace:** `trace.jsonl` — 90 lines, `fm-proof-trace/v1`, seq 1–90, no gaps.
**Raw captures:** `raw/` — 216 files, each written before the value in it was parsed.

## 0. What this observer did and did not do

Every GitHub interaction was a `GET`. No push, no comment, no review, no API mutation, no message to the
executor. The only writes are `trace.jsonl` and `raw/` under this directory.

Observations carry the three-valued grade. My own tally:
**56 observed-good, 16 observed-bad, 9 could-not-observe.** A could-not-observe is a result here, never a pass.

**Independence, honestly stated.** I ran as a separate process with separate state, so process independence is
`observed-good`. Identity independence is **`could-not-observe`**: I authenticate to GitHub with the same
`sbracewell64` token the executor uses. `proofs-shared-contracts.md` §3.2 names the stronger form and this run
does not meet it.

## 1. Verdict

**The designed pathway was executed end to end, and its mechanical core is independently confirmed.** I re-derived
from GitHub, not from the executor's record: the seed tree digest, branch protection field-for-field, three
negative controls reddening on GitHub's own check runs, the trusted `.no-mistakes.yaml` on `main`, both required
checks green at the exact published head, the eight-condition mergeability ladder, the merge commit's second
parent, the default-branch ref, and the protection generation before and after the merge. A declared verifier
(`bin/fm-verify.sh pr-checks`) returned `PASS / verified` on the candidate PR.

**The terminal grade is where the proof is weaker than it reads.** The disposition says `PROVED`. It first said
`REFUSED_AT_A-S11`, and the outcome changed because the *fold rule* was rewritten mid-run — with the answer in
view — not because any observation changed value. Every amendment is disclosed and the final fold is
reproducible (I reproduced it exactly against the settled record: 152 observations, 33 flagged superseded, 4 flagged
non-gating, leaving good=116/bad=0/cno=0), but a verification contract's value is that its criteria are fixed
before the result. Read `PROVED` as *proved under a fold rule authored during the run and disclosed*, not as
*proved under the fold rule the design pre-registered*.

## 2. The observed pathway

| Stage | What GitHub shows | Time (GitHub) |
|---|---|---|
| A-S1 | `sbracewell64/fm-cleanroom-proof` created, public, default `main` | 22:49:00Z |
| A-S2 | seed commit `2ef121a9`, tree `d162bf8f` = pinned `seed_tree_sha`, zero parents, author `Shane Bracewell <sbracewell64@gmail.com>` | 22:49:27Z |
| A-S2 | `ci` run green on the seed push | 22:49:18Z |
| A-S3 | protection on `main` exactly as designed; squash/rebase off, merge commits on | 22:49:3xZ |
| A-S4 | PR #1, three heads, three controls, closed unmerged, branch retained | 22:51:05–22:53:40Z |
| A-S7 | candidate branch pushed; PR #2 opened | 22:59:46 / 23:00:08Z |
| A-S9 | both required checks `success` at `281e15b2`; `total_count` 2 = 2 fetched | 23:00:21–22Z |
| A-S10 | `state=open, draft=false, mergeable=true, mergeable_state=clean, base=main` | 23:02Z |
| A-S12 | merged; merge commit `a7db5c36` | 23:04:14Z |
| A-S13 | `parents = [2ef121a9, 281e15b2]`; `refs/heads/main → a7db5c36` | 23:04:14Z |
| A-S16 | repository archived, retained, publicly readable | 23:06Z |

Two heads, kept apart exactly as the design requires: the locally committed candidate `d29527ed` (tree
`7a8d4f55` = pinned `candidate_tree_sha`) and the published head `281e15b2` the pipeline authored on top of it.
Every downstream binding used the published one.

The bootstrap exception held: after the merge, `main` carries four commits and only the seed is a non-merge
commit with no pull request behind it.

## 3. Negative controls — what was actually watched red

Verified by re-reading GitHub's check runs at each head, not by reading the executor's record.

| Control | Target | Reddened | Neighbour |
|---|---|---|---|
| NC-2 unsigned body | `PR must be raised via no-mistakes` | failure 22:51:14Z at `b02acfe6` | `test` **green** — isolated |
| NC-3 stale attestation | `PR must be raised via no-mistakes` | failure 22:52:08Z at `13f1b3e2` | `test` **green** — isolated |
| NC-1 broken unit test | `test` | failure 22:52:34Z at `1e9172a5` | gate **also red** — **not isolated** |
| NC-4 wrong merge sha | forge head bind | executor-captured: *"Head branch was modified. Review and try the merge again."* 23:04:36Z | not observer-verified |
| NC-5 / NC-6 | executor's own parser and comparator | offline unit checks | not forge-side |

The gate's declared limit was exercised deliberately and is worth keeping in view: **a hand-written attestation
in the PR body passed the required check** at `b02acfe6` (success 22:51:41Z). `verify.py:21-32` says the gate is a
contributor guardrail, not a forgery-proof boundary. A green `PR must be raised via no-mistakes` is evidence
consistent with the pipeline having run; it is not proof that it ran.

## 4. Divergences from the design

**D1 — the terminal record was rewritten, and the fold rule with it.** `proofs-shared-contracts.md` §2 says the
disposition is *"written once, at the end"*. I read four versions: `REFUSED_AT_A-S11` (23:06:32Z, fold
good=132/bad=1/cno=1), then `PROVED` (23:08:36Z), `PROVED` (23:09:57Z), and the settled record
(23:12:39Z, sha256 `11dd4ee9…`, fold good=116/bad=0/cno=0). The difference is a **supersession rule** and a
**non-gating exclusion**, neither of which appears in the design.
Exactly one exclusion changes the outcome: A-S14's `observed-bad` ("run status = running"), set aside because it
was sampled with no declared bound while the CI reconciler polls at 30/60/120s, then replaced by a bounded
16×30s re-observation that returned `completed`. That reasoning is sound and cites code. The problem is
provenance, not arithmetic.

**D2 — `REFUSED_AT_A-S11` was a guard doing its job.** The first A-S11 attempt failed T8 with `missing=['A-S7']`:
it refused to mint a landing authorization while the trace was incomplete. A-S7 closed at 23:03:52Z, A-S11
re-ran at 23:04:31Z and passed. The design's own §2 already says refusals coexist with `PROVED`; what it never
supplied was the mechanism, which is why one had to be written mid-run.

**D3 — the pipeline committed build artifacts, and the fence let them through.** Commit `281e15b2`, messaged
*"docs already accurate for compare(); no updates needed"*, adds five `.pyc` files and touches no documentation.
They are inside `{fmproof/**, tests/**}`, so **T5 and T6 as specified both pass**, and they landed on `main`. The
PR body itself says *"build artifacts, likely unintended"* while the Review section reports *"No issues found"*.
The same body's Test section still reads *"git diff --stat shows only fmproof/semver.py and tests/test_compare.py
changed"* — true of the head Test ran on, no longer true of the head the PR carries. The executor recorded all of
this as deviation D-4 and declined to add a new gate mid-run, which is the right call; the finding is that
*"the diff is confined to fmproof/ and tests/"* is a weaker statement than *"the diff contains only intended
source"*, and a path fence cannot tell them apart.

**D4 — NC-1 was not distinct, and the distinctness test cannot fail.** Both required checks were red at NC-1's
head, so the block is attributable to their union, not to `test`. The executor's `distinct_match` is computed as
`target == observed` where the same call supplies both — a tautology. Its own `measured` field records
`test=failure gate=failure`, so the disconfirming evidence is present but is not an input to the verdict. NC-2
and NC-3 carry a real neighbour-stayed-green observation; NC-1 does not.

**D5 — the clean room wrote outside itself.** `~/.claude/skills/no-mistakes/SKILL.md` was rewritten at 22:55Z
(the only file in a directory otherwise dated 2026-07-25). The isolated `NM_HOME` scopes run state but not the
skill install. The host binary is untouched and still reports v1.40.3, so the host now carries v1.61.0
*instructions* describing a v1.40.3 *binary*. The executor disclosed this as D-3.

**D6 — the pinned vocabulary was edited mid-run and its history is incomplete.** I read
`vocabulary_digest 681a2621…` from `PINNED.json` at 22:46:05Z. The final file carries `50575d7f…` with a history
of `[53c25b89…, ca0d6340…]` — at least three changes, and the digest I read first is not in the recorded history.
`proofs-shared-contracts.md` §1.1 exists precisely so this cannot happen. The final record does validate cleanly
against the final schema (I re-ran `jsonschema`: zero errors).

**D7 — cross-source timestamps in this record cannot establish causal order.** The host clock runs at least 18s
ahead of GitHub's: the `ci` run for the seed push was created by GitHub at 22:49:09Z for a commit whose host-set
author date is 22:49:27Z. Consequently the authorization reads `minted_at 23:04:35Z` and `spent_at 23:04:40Z`
while GitHub records `merged_at 23:04:14Z` — the record *appears* to show the landing 21 seconds before its own
authorization. It is skew, not a spend before a mint, and the record carries no offset field to correct for it.

**D8 — falsifier timing.** Design §17 requires all five falsifiers watched red *before the real run*. NC-4 ran at
23:04:36Z, inside A-S12, one second after the authorization was minted and four before it was spent. It was
watched red immediately before the act it falsifies, but not before the run.

## 5. Could-not-observe register

Nine, none narrowed into a pass:

1. **Observer identity independence** — one credential serves both parties.
2. **Account plan** (`.plan.name` empty; token lacks `user` scope). Matches the design's PR-3.
3. **The merge request's `sha` binding** — a mutating call I do not make, and GitHub keeps no readable record of
   it. What I *can* establish is the outcome the binding is for: the landed second parent is exactly the head
   that was green. That an admin bypass was not used is **inference** from `enforce_admins=true` plus both checks
   already green, and is graded as inference.
4. **The forge refusing NC-2's merge attempt** — same structural limit. I confirmed the state that makes such a
   call fail (`mergeable_state=blocked`, two red required contexts, `enforce_admins=true`).
5. **Agent versus human attribution** — every commit, the PR, the merge and every event carry the single account
   `sbracewell64`. GitHub cannot separate the executor agent, the pipeline and a person at the keyboard. Step
   attribution in §6 rests on the local artifact tree and process timing, not on forge evidence.
6. **Local pre-gate results G0–G5, G7, G10, G11** — properties of the executor's private worktree and invocation.
   I independently confirmed three of the twelve gates (G6/G6b, G8, G9) and claim no more.
7. **Pipeline terminalization at A-S14** — I have no read into the executor's isolated no-mistakes home. The
   executor's first measurement was `observed-bad`; its bounded re-observation was `observed-good`. Reported as
   both, adopted as neither.
8. **A negative control at A-S4 before any PR existed** — an empty pull-request list is not a passing control.
   Resolved later by observation.
9. **One observer transport failure.** A poll of `/users/sbracewell64/events` at 23:04:44Z returned
   `decode-failed` and was recorded as could-not-observe rather than as data. Cause, inferred: `gh-axi` truncates
   bodies past ~3000 characters, so I pull large responses as base64 slices; that feed changed between two slice
   fetches. No graded observation in this trace rests on that label. Recorded because a transport that *can*
   silently produce a wrong answer must be reported even when it did not.

## 6. Semantic cognition versus deterministic execution

**Deterministic** — repository creation, the seed push, the protection PUT and read-back, the pinned-patch apply,
the twelve pre-gate predicates, check-run conclusions, the attestation head bind, the mergeability ladder, the
authorization act digest, the merge call, the parent identity check, the mirror verification. Everything here
that I could re-derive, I re-derived, and nothing it measured turned out to be wrong.

**Semantic, inside no-mistakes** — the Review verdict, the Document step's decision to write no documentation,
the risk rating, and the PR prose, including the sentence disclosing the artifacts it had just committed.

**Semantic, by the executing agent** — which negative controls to run and how to score distinctness; re-entering
A-S6, A-S11 and A-S14 rather than stopping; authoring and applying the supersession and non-gating rules;
treating build artifacts inside the allowlist as a finding rather than a refusal; writing the deviation register.

**Every divergence in §4 sits in one of the two semantic layers.** The deterministic layer held.

## 7. What the executor got right, plainly

The deviation register is real and self-incriminating: D-3 (host side effect), D-4 (the artifacts), D-5 (the
re-pin), D-6 (the unbounded A-S14 sample), D-7 (the fold). Superseded observations are flagged and retained, not
deleted. The `forge_gate` is recorded as evidence the pipeline ran and explicitly not as proof it could not have
been forged. `exit_code: 0` is recorded and is not an input to the verdict. The refusal that fired at A-S11 is
kept in `refusals[]` on a `PROVED` record. A proof that hides its own bruises is worth less than this one.

## 8. Record state at close of observation

Settled record: `attempt-1/disposition.json`, `completed_at 2026-09-01T23:12:39Z`, sha256
`11dd4ee96b7b4f90e60df79e9b720f84976e04ec3e4f8b0571e54436d6c70462`, `outcome: PROVED`, seven disclosed
deviations `D-1`…`D-7`, two retained refusals (`A-S6`, `A-S11`), trace 231 lines with zero seq gaps and one
declared coverage exemption for `A-S15` (the disposition write cannot observe its own exit). I re-ran the fold
against this exact file and reproduced `{observed-good: 116, observed-bad: 0, could-not-observe: 0}`.

Two of the seven deviations were also found independently by this observer before reading the register: `D-2`
(the eighth seed file, `tests/__init__.py`, which the design's §4.1 list omits and which Python 3.14's
`unittest discover` needs) and `D-4` (the committed build artifacts). Agreement on those raises confidence that
the register is a real inventory rather than a formality.

The proof repository remains publicly readable and archived at
<https://github.com/sbracewell64/fm-cleanroom-proof>; PR #2 is <https://github.com/sbracewell64/fm-cleanroom-proof/pull/2>.
