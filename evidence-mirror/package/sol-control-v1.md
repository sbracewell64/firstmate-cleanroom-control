# The control plane, as proven — `fm-sol-control/v1`

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: knowledge-work
product_contract_source: Captain clean-room directive, 2026-09-01, section 10
authored_by: scout task cleanroom-architecture-synthesis, 2026-09-02
status_of_this_document: DESIGN ONLY - the schemas below were EXECUTED in proof-b attempt-1;
                         the changes this document proposes on top of them were not
owns: the control-plane wire schemas and lifecycle - request envelope, generated reply contract,
      V1-V10 and L1-L5, correlation and stale-state protection, the fail-closed refusal vocabulary,
      the receipt, and the one-issue-per-question rule
```

**Master document:** [`architecture-synthesis.md`](architecture-synthesis.md) owns the shared
vocabulary (§0.3), the Lane B state machine (§5), the boundary predicate set (§5.3), the three-valued
terminal gate (§5.5), and the consumption identity check (§5.6). This document owns the **wire** —
every field name, every predicate's exact comparison, and the refusal vocabulary. It does not restate
the state machine.

Grading legend and citation forms: [`architecture-synthesis.md`](architecture-synthesis.md) §0.1.

---

## 0. Status of every claim in this document

Everything in §§1–7 was **executed** in `proof-b/attempt-1` on 2026-09-01, against a live external
ruler, and the resulting records are on disk. Where this document changes what was executed, the
change is marked **CHANGE** with the observation that forced it. There are five such changes and they
are collected in §9.

---

## 1. The venue: one issue per question

| Term | Value |
|---|---|
| Venue unit | **one issue per `correlation_id`**, opened by the compiler, closed at consumption |
| Issue body | the validated `request` envelope in a fenced JSON block, followed by the **generated** reply contract and the **schema of record**, both as further fenced blocks |
| Ruling | exactly one issue comment carrying one fenced JSON block with `kind: "ruling"` |
| Receipt | exactly one issue comment with `kind: "receipt"`, then the issue is closed |
| Total control-plane state per round trip | **one issue, two comments** |

**OBSERVED (`proof-b:disposition.json control_plane`, `obs-b:§7`):** the executed round trip created
exactly that and nothing else — issue #47, the ruler's comment `5502255519`, the consumer's receipt
`5502291831`, then closed. The observer confirmed `{"comments": 2, "state": "closed"}` on a final
re-read, that **no comment was edited after posting** (`updated_at == created_at` on both), and that of
47 issues in the venue **exactly one** names the correlation id.

### 1.1 Why an issue, and why one per question

| Alternative | Why not |
|---|---|
| a pull-request review comment | it binds to the pull request, and the head is exactly what moves; a review thread survives a head change and would then address a subject that no longer exists |
| a file in the subject repository | it requires the ruler to hold write access to the subject, which grants far more than the ability to answer a question |
| a long-lived thread | the retired fleet's ruling poll froze at page one and **every newer ruling was invisible for six days**; separately, an unpaginated comment read returned only the first 30, and firstmate repeatedly reported *"Browser Sol has not replied"* while **three rulings sat unread on a later page**, including an approval that had left a worker parked for hours (`corpus:§3.7`, DOCUMENTED) |

**One issue per correlation id bounds the comment universe at about three**, so the completeness
predicate is cheap and always satisfiable. **Pagination is still used**, because a structural answer
and a correct read are not alternatives.

And the venue carries **no state that is not in an envelope**: no labels, no assignees, no milestones,
no projects. **Nothing parses the issue title.**

---

## 2. One vocabulary source, and the generated reply contract

### 2.1 The rule

1. **Exactly one file** defines every field name and every enum value: `fm-sol-control-v1.schema.json`.
2. **Every producer validates against it before emitting. Every consumer validates against the same
   file before acting.** Validation failure is `observed-bad`, never a warning.
3. **The reply contract handed to the ruler is generated from that same file** by walking
   `properties`, `required`, `$defs` and every `enum`. **No field name is typed by a human or an agent
   anywhere** — not in a request body, not in an issue body, not in a brief, not in a prompt.
4. The renderer **self-checks**: after posting, re-render and byte-compare against what was posted. A
   mismatch is a build failure, not a diff to eyeball.
5. Every envelope carries `vocabulary_digest`, the sha256 of the schema file's exact bytes. A consumer
   whose digest differs from the producer's **refuses**.

### 2.2 It worked, first time, and that is the measurement

**OBSERVED (`proof-b:reply-contract.md`, `proof-b:ruling.json`, both read by me; `obs-b:§8` rec 1):**
the ruler's field names matched on the **first attempt**, with **zero malformed blocks** — from a party
whose demonstrated native format in that same repository is `key: value` prose rather than fenced JSON.

This is the direct answer to the corpus's costliest transport defect: *multiple Browser Sol rulings
failed to attach because reply field spelling was manually reconstructed; FirstMate also relayed the
wrong required field list once* (`corpus:§1.4`, from the captain's own throughput directive).

> **The defect is not mitigated; it is unreachable. There is no second place for a field name to live.**

**And its limits, stated:** the mechanism makes *field-name drift* unreachable. It does **not** make a
ruler answer correctly, and it does **not** make a ruler answer at all.

### 2.3 The generated block, as it was actually posted

Reproduced from `proof-b:reply-contract.md` (read by me). Every line below was **produced by walking
the schema**, including the enum lists and the conditional-companion table:

```
Required fields (10):
  - schema: exactly "fm-sol-control/v1"
  - kind: exactly "ruling"
  - vocabulary_digest: string matching ^[0-9a-f]{64}$
  - correlation_id: string matching ^fsc1-[0-9a-f]{32}$
  - ruled_at: string matching ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$
  - ruler: object{login=string, kind=one of: "human" | "agent" | "automation"} optional:session_ref
  - applies_to: object{repo=..., head_sha=<40hex>, tree_sha=<40hex>, policy_digest=<64hex>}
  - inspection: object{evidence_refs_inspected=array, observations=array}
  - directive: one of: "ADOPT_OPTION" | "REJECT_ALL_WITH_CONSTRAINT"
                     | "INSUFFICIENT_EVIDENCE" | "OUT_OF_SCOPE_CAPTAIN_RESERVED"
  - single_writer_assertion: exactly true

Conditionally required companion field, by directive:
  - when directive == "ADOPT_OPTION":                  option_id is REQUIRED
  - when directive == "REJECT_ALL_WITH_CONSTRAINT":    constraint is REQUIRED
  - when directive == "INSUFFICIENT_EVIDENCE":         missing_evidence is REQUIRED
  - when directive == "OUT_OF_SCOPE_CAPTAIN_RESERVED": reserved_reason is REQUIRED

Rules the consumer enforces mechanically (a violation is refused, never repaired):
  - additionalProperties is false on every object: an unknown or misspelled field name is
    REFUSED_MALFORMED and the refusal names the field.
  - vocabulary_digest MUST equal the schema of record's sha256, quoted below.
  - applies_to.head_sha / .tree_sha / .policy_digest MUST be copied from this request's candidate
    and policy_generation. Identity is checked, never ancestry.
  - Exactly ONE ruling per correlation_id. Two rulings that do not name each other in supersedes
    are a lineage fork: NEITHER is consumed and the newer is not picked.
  - There is no field for a third option.
```

**CHANGE 1 — drop the pre-filled skeleton.** The executed body also shipped a **ruling skeleton with
placeholder values**. The observer's caution is correct and worth acting on: *the skeleton is the one
place the request supplies phrasing that can be filled without the underlying fact becoming true*
(`obs-b:§5.6`), which is exactly the corpus's template warning — *supplying the phrasing supplies a
TEMPLATE, and a template can be filled without the underlying fact ever becoming true*
(`corpus:§3.4`). **Keep the generated required-field contract; remove the pre-filled envelope.** A
ruler that cannot assemble ten named fields from a typed contract is not a ruler this plane should be
consuming.

---

## 3. The request envelope

Field-for-field as executed (`proof-b:request.json`, read by me). `$defs` — `sha1_hex`, `sha256_hex`,
`rfc3339_utc`, `three_valued`, `candidate_state`, `repo_ref`, `git_point`, `evidence_ref`, `actor`,
`observation` — are shared with the disposition schema so there is **one** definition of each across
the whole architecture.

```jsonc
{ "schema": "fm-sol-control/v1", "kind": "request",
  "vocabulary_digest": "<sha256 of the schema file's exact bytes>",
  "correlation_id": "fsc1-<32hex>",              // DERIVED, never assigned - §4
  "created_at": "<rfc3339_utc>",
  "requester": { "login": "...", "kind": "agent", "session_ref": "..." },
  "repo": { "owner": "...", "name": "...", "url": "https://github.com/<o>/<n>",
            "default_branch": "main", "node_id": "..." },
  "candidate": { "branch": "...", "head_sha": "<40hex>",
                 "tree_sha": "<40hex>", "base_sha": "<40hex>" },
  "candidate_state": "ATTESTED",                 // never MUTATING
  "pull_request": { "number": 2, "url": "...", "head_sha": "<40hex>",
                    "state": "closed", "merged": true, "merge_commit_sha": "<40hex>" },
  "policy_generation": { "digest": "<64hex>",
                         "inputs": ["branch-protection.json", "sorted-required-contexts",
                                    "pinned-require-no-mistakes-action-ref",
                                    "fm-sol-control-v1.schema.json"] },
  "decision_class": "DELEGATED_ENGINEERING",     // | CAPTAIN_RESERVED
  "boundary_evidence": [ <observation>, ... ],   // the BP1-BP7 results, IN FULL
  "question": {
    "key": "<from the pre-registered catalog; free text is refused>",
    "title": "...",
    "body_rendered": "...",                      // a catalog template with MACHINE-VALUE slots
    "options": [ { "id": "A", "summary": "...", "consequence": "...",
                   "reversibility": "<closed set>", "paths": ["..."],
                   "patch_sha256": "<64hex>", "resulting_tree_sha": "<40hex>" }, ... ] },
  "evidence_refs": [ { "kind": "blob|commit|diff|check_run|pull_request|workflow_run|file|api_capture",
                       "locator": "<content-addressed or immutable>", "sha256": "<64hex>" }, ... ],
  "valid_while": { "pr_head": "<40hex>", "pr_state": "closed",
                   "policy_digest": "<64hex>", "vocabulary_digest": "<64hex>" },
  "reply_contract": { "schema_locator": "...", "schema_sha256": "<64hex>",
                      "required_fields": [ ... ],   // GENERATED
                      "renderer_digest": "<64hex>" },
  "expires_at": "<rfc3339_utc>" }
```

### 3.1 Every field's machine source

**The captain is never transport.** No input to any stage may be a chat message, and no output may
require a human to carry it. **OBSERVED (`obs-b:§3 B-S4`):** the executed compile recorded **52
predicates each naming the command it came from**, across three compile passes.

| Field | Machine source |
|---|---|
| `repo.*` | the remote URL, canonicalised; the forge's repository record |
| `candidate.branch / head_sha / tree_sha` | `git rev-parse --abbrev-ref HEAD`, `git rev-parse HEAD`, `git rev-parse HEAD^{tree}` |
| `candidate.base_sha` | `git merge-base HEAD origin/<default>` — **and see INSTR-1 in §3.2** |
| `pull_request.*` | the forge's pull-request record |
| `candidate_state` | the qualification tool's branch-sync state plus required-check completion at head |
| `policy_generation.digest` | sha256 over the canonical protection body ‖ sorted required contexts ‖ the pinned enforcement-action ref ‖ the vocabulary digest |
| `question.key`, `question.options` | the pinned catalog entry, verbatim |
| `question.body_rendered` | a catalog template whose slots are **machine values**; the compiler **refuses if any slot is unfilled** |
| `evidence_refs` | `git rev-parse`, raw blob fetches at a pinned commit, plus the sha256 of each captured byte range |
| `boundary_evidence` | the BP1–BP7 observation objects, in full |
| `correlation_id` | derived (§4) |
| `reply_contract` | generated by the renderer (§2) |

**`question.body_rendered` is the one prose-shaped field**, and the corpus's warning cuts the right
way: the *decision* rests on `evidence_refs`, not on the prose; the prose's slots are machine values;
and the compiler refuses an unfilled slot.

### 3.2 `evidence_ref` — the locator law, and the defect it did not catch

The schema's own comment states it:

> `locator` MUST be content-addressed or immutable: a commit URL, a blob-at-commit URL, a numeric
> check-run id, or a captured-response file path. **A branch or tag URL is refused** — it is a name
> that can be re-pointed between two lookups (`corpus:§1.3`).

**Two executed findings sharpen this.**

**INSTR-1 — a true green observation about the wrong question.** `candidate.base_sha` was first sourced
from `git merge-base head origin/main`, but the default branch now **contained** the candidate, so it
returned the head itself and the diff locator would have resolved to an **empty range**. The
observation *"`candidate.base_sha` came from machine state"* was **true and green** while saying
nothing about whether the field answered the right question. The observer independently confirmed the
symptom from outside: request v0's diff ref carried sha256 `e3b0c442…`, which is the digest of the
**empty string** (`obs-b:§4`).

> **CHANGE 2 — two gating predicates, added and executed:** `base != head`, and *the diff resolves
> non-empty*. Both are in the corrected record.

**INSTR-2 — a fail-closed refusal for the wrong reason is still a wrong answer.** Blob digests were
first taken over stripped output, so they could never equal the sha256 of the bytes an anonymous reader
receives; the readiness probe would have refused on an **instrument artifact** rather than on genuine
inspectability, and the request would never have been emitted
(`proof-b:disposition.json instrument_defects_found_and_corrected`, read by me).

**P-B-CAP-4 — the defect that survived.** Evidence ref 5 declares a sha256 over a **680-byte extract**
while its locator returns the **31,121-byte** page. The aggregate observation read `resolved=6/6
failures=[]`, and one of the six was not clean. The bytes were genuinely inspectable — the extract is
embedded verbatim in the issue body and does hash to the declared value, which the observer confirmed —
so the ruler was not misled. What failed is the machine-checkable binding the schema's own comment
requires, and the locator additionally **mixes a URL with prose** (`obs-b:§5.4`).

> **CHANGE 3 — the locator must name the object its digest names, and must be a locator.** Two
> mechanical additions: (a) the readiness probe compares digests **per ref** and the aggregate is a
> **conjunction of per-ref observations**, never a count; (b) `locator` is refused if it contains
> whitespace-separated prose. Where the addressable object and the hashed object genuinely differ —
> as with a normative extract from a larger page — the honest form is an `api_capture` locator naming
> the captured bytes, which do hash to the declared value.

---

## 4. Correlation and stale-state protection

### 4.1 The correlation id is derived

```
correlation_id := "fsc1-" || first32hex( sha256( protocol_version "\n"
                                                 owner "/" name     "\n"
                                                 branch             "\n"
                                                 head_sha           "\n"
                                                 question.key       "\n"
                                                 policy_digest ) )
```

Three properties fall out, and all three are load-bearing:

1. **Idempotence for free.** Recompiling the same subject yields the same id, so "have I already asked
   this?" is a lookup, not a judgement.
2. **Staleness protection is partly structural.** A moved head yields a **different** id, so a stale
   ruling cannot even *address* the new subject.
3. **It is verifiable by a third party.** **OBSERVED (`obs-b:§3 B-S4`):** the independent observer
   **recomputed the id** from public artifacts and it matched.

**And the gap the observer found, recorded rather than inferred:** the id hashes only
`(protocol, repo, branch, head_sha, question.key, policy_digest)`. It stayed constant across all three
request versions **while the evidence set changed materially**. Nothing went wrong, because only v2 was
ever emitted — *but a ruling bound to a correlation id is not thereby bound to the evidence its ruler
was shown* (`obs-b:§4`).

> **CHANGE 4 — bind the evidence set.** Add `evidence_digest` to `valid_while`: the sha256 over the
> canonical, sorted list of `(kind, locator, sha256)` triples. The correlation id keeps its current
> inputs, so idempotence over a subject survives; the ruling is additionally bound to **what the ruler
> was shown**. This is the observer's highest-value structural recommendation after the independence
> axis (`obs-b:§8` rec 4).

### 4.2 The staleness ladder — L1 to L5

V1–V10 validate the **ruling**. L1–L5 validate that the **world has not moved** since the request was
compiled. All five are identity comparisons against **live** reads.

| # | Predicate | Failure code |
|---|---|---|
| **L1** | live pull-request head **equals** `valid_while.pr_head` | `RULING_SUPERSEDED` |
| **L2** | live pull-request state **equals** the state recorded at compile time | `RULING_SUPERSEDED` |
| **L3** | recomputed `policy_generation.digest` equals `valid_while.policy_digest` | `RULING_SUPERSEDED` |
| **L4** | the schema of record still hashes to `valid_while.vocabulary_digest` | `RULING_MALFORMED` |
| **L5** | `now < expires_at` | `RULING_SUPERSEDED` |

**L1 is identity, never ancestry.** *An ancestor relation is not an identity check, and it fails in the
direction that looks safe. Requiring the recorded candidate to be the immediate parent is the repair;
broadening to an older ancestor is not* (`corpus:§2.2`, DOCUMENTED). A ruling made about `abc123` does
not apply to a descendant of `abc123`.

**L3 is deliberately narrow.** The policy digest covers the protection body, the required contexts, the
pinned action ref and the schema bytes — and **not** the movement of the default branch. That is the
corpus's ruled fix: *unrelated main movement with byte-identical authoritative policy must not
invalidate a review solely by chronology* (`corpus:§3.2`, DOCUMENTED). Where trunk movement genuinely
matters it reaches the ladder through **L1** anyway, because protection is `strict: true` and a moved
base forces the candidate head to move. **The two mechanisms do not double-count.**

**Watched red, and honestly capped.** Falsifier 5 ran **both halves**: the positive half (a changed
required context must trip L3) as a comparator, and — importantly — **the negative half live**: the
default branch had already moved after protection was set, and L3 **stayed green**
(`proof-b:inputs/PINNED.json falsifiers n=5`, read by me). *A design that only ever proves its refusals
fire has not shown that it can also stay quiet*, and a control that fires on everything is the
permanently-red shape the corpus already ruled gets ignored and then removed (`corpus:§3.6`).

**P-B-CAP-2, stated as a result, not a footnote:** the ladder was evaluated against a **merged pull
request in an archived repository**. L1 passed trivially — a merged head cannot move. L3 passed against
protection nobody could change. **Falsifier 4's live half and falsifier 5's positive live half could
not be run at all.** So the proof establishes that the **comparators** behave correctly and leaves
**could-not-observe** on whether the ladder catches a real moving candidate (`obs-b:§5.2`). The next
attempt must run against a **live, open** candidate; that is the first named increment in
[`first-implementation-plan.md`](first-implementation-plan.md) §4.

### 4.3 A superseded ruling is never carried forward

The repair is a **new** correlation id compiled at the new head — which §4.1 produces automatically.
The old issue receives a `WITHDRAWN` receipt and is **closed, never edited**. That is the corpus's rule
for wedged external state: *move forward into a new identity rather than mutating the wedged one*
(`corpus:§2.7`, DOCUMENTED).

---

## 5. The ruling, and the validation ladder V1–V10

### 5.1 The ruling envelope

```jsonc
{ "schema": "fm-sol-control/v1", "kind": "ruling",
  "vocabulary_digest": "<64hex>", "correlation_id": "fsc1-<32hex>",
  "ruled_at": "<rfc3339_utc>",
  "ruler": { "login": "...", "kind": "human|agent|automation", "session_ref": "..." },
  "applies_to": { "repo": {...}, "head_sha": "<40hex>",
                  "tree_sha": "<40hex>", "policy_digest": "<64hex>" },
  "inspection": { "evidence_refs_inspected": [ <evidence_ref>, ... ],
                  "observations": [ <observation>, ... ] },     // three-valued, including its own CNOs
  "directive": "ADOPT_OPTION",
  //   ADOPT_OPTION                  -> option_id        required
  //   REJECT_ALL_WITH_CONSTRAINT    -> constraint       required
  //   INSUFFICIENT_EVIDENCE         -> missing_evidence required   (this is the ruler's CNO)
  //   OUT_OF_SCOPE_CAPTAIN_RESERVED -> reserved_reason  required   (the ruler declining the boundary)
  "option_id": "A",
  "rationale": "...", "confidence": "high|medium|low",
  "supersedes": null,
  "single_writer_assertion": true }
```

**The directive vocabulary is closed and total over the reachable answers.** There is **no field for a
third option**; the only way to reject both is `REJECT_ALL_WITH_CONSTRAINT`, which produces **no code
change** and hands the constraint back. A consumer inventing a third option would be the consumer
deciding, which is the thing the round trip exists to avoid.

**Two of the four directives are the ruler correcting us, and both are successful round trips:**
`INSUFFICIENT_EVIDENCE` is the ruler's could-not-observe; `OUT_OF_SCOPE_CAPTAIN_RESERVED` is the ruler
telling us our boundary predicate was wrong. *Rulings are not exempt from the laws they establish*
(`corpus:§4.3`).

### 5.2 The actor contract

**Must:** resolve and read each evidence locator and record **exactly which** it read; emit **exactly
one** comment; set `single_writer_assertion: true`; copy `head_sha`, `tree_sha` and `policy_digest`
from the request; record its own observations **three-valued**, including anything it could not
observe.

**May not:** propose a third option; edit or delete an earlier ruling. A changed mind is a **new**
comment naming the prior id in `supersedes`.

**OBSERVED — the executed ruling met all five musts** (`proof-b:ruling.json`, read by me), and three
independent signals say it genuinely inspected (`obs-b:§5.6`):

1. **Timing.** Issue posted 23:42:41Z, `ruled_at` 23:58:22Z, comment posted 23:59:40Z — fifteen minutes
   and forty-one seconds, with a 78-second gap between ruling and posting: the shape of composing a
   document and then sending it, not an echo.
2. **It under-claims.** `evidence_refs_inspected` names **4 of 6** refs and does not claim the diff or
   the commit patch — the opposite of what a fabricated ruling does.
3. **It cites evidence the request never supplied.** Two workflow-run ids absent from the evidence set,
   which the observer queried and found real, at the exact head, `completed`/`success`.

### 5.3 V1–V10

Ordered; each writes an observation; each failure has **exactly one** code. **Every failing predicate
is reported, not only the first.**

| # | Predicate | Failure code |
|---|---|---|
| **V1** | exactly one valid ruling for this correlation id | 0 → wait or terminal `NO_ANSWER`; >1 → `RULING_LINEAGE_FORK` (**CNO**) |
| **V2** | the comment body validates against the schema | `RULING_MALFORMED` — and **the refusal names the offending field** |
| **V3** | `ruling.vocabulary_digest == request.vocabulary_digest` | `RULING_MALFORMED` (drift, caught mechanically) |
| **V4** | `ruling.correlation_id == request.correlation_id` | `RULING_SUBJECT_MISMATCH` |
| **V5** | `applies_to.repo`, `.head_sha`, `.tree_sha` equal the request's candidate | `RULING_SUBJECT_MISMATCH` |
| **V6** | `applies_to.policy_digest == request.policy_generation.digest` | `RULING_SUPERSEDED` |
| **V7** | the ruler is **assignment-distinct** from the maker | three-valued — see §6 |
| **V8** | `single_writer_assertion == true`, and `supersedes` is null or names a known prior id | `RULING_LINEAGE_FORK` |
| **V9** | the directive's required companion field is present | `RULING_MALFORMED` |
| **V10** | if `ADOPT_OPTION`: `option_id` ∈ the offered option ids | `RULING_SUBJECT_MISMATCH` |

**V5 and V6 are kept apart on purpose.** A head mismatch and a policy mismatch are different facts with
different repairs — the first needs a new request, the second needs a policy reconciliation. The
corpus's vocabulary lesson is that *a distinction that dies at the last step before the operator* is
more dangerous than a missing control, because every layer is correct in isolation (`corpus:§1.4`). The
two conditions never share a code.

**OBSERVED:** all sixteen predicates (V1–V10, L1–L5, plus the completeness predicate) were evaluated in
the executed run, **none skipped**; fifteen `observed-good`, **V7 could-not-observe**
(`proof-b:receipt.json validation`, read by me).

### 5.4 Selection is by validated content, never by containment

For each comment: extract the fenced JSON, validate against the schema, and keep it **only if**
`kind == "ruling"` and the correlation id matches.

**Never select by substring.** The corpus's sharpest instance of the wrong-subject class was exactly
this: a presence check matched any comment *body containing* a request id, *"so a comment merely
mentioning a request suppressed its emission… the mechanism got quieter the more anyone discussed a
request"* (`corpus:§1.1`, DOCUMENTED). **The failure direction is the sharp part.**

**Watched red:** falsifier 7 posted a comment that merely mentions the correlation id in prose and
asserted it was **ignored** — it neither counted as a ruling nor suppressed the real one
(`proof-b:inputs/PINNED.json falsifiers n=7`, read by me).

### 5.5 The completeness predicate

```
require len(fetched comments) == issue.comments        # the reported total
```

A disagreement is **`CNO_INCOMPLETE_UNIVERSE`** — the lane stops rather than concluding "no ruling yet".
*Zero findings is not evidence of cleanliness unless the verifier also establishes its completeness
predicate* (`corpus:§1.2`, the ruled law). The corpus's own six-day blindness was exactly a negative
claim made over an unbounded universe.

**OBSERVED:** the executed run recorded `fetched == reported` on **every** read across 5 poll attempts
of a pinned bound of 18, and the independent observer's own polls agreed on every cycle
(`obs-b:§3 B-S8`).

### 5.6 Lineage forks — the structural answer, plus the gate

The corpus recorded the external automation emitting *"two or three authoritative-looking rulings for
one decision subject within minutes, sometimes contradictory"*, with the ruled handling: *never pick the
latest by timestamp and never merge them; record the fork, preserve every comment, and ask for explicit
supersession* (`corpus:§3.7`).

Three structural defences, plus one gate rule:

1. **one issue per correlation id**, so a fork is confined to one place and is trivially countable;
2. **`single_writer_assertion`**, so a second ruling contradicts an explicit claim rather than merely
   existing;
3. **`supersedes`**, so an intentional replacement is distinguishable from an accidental duplicate;
4. **the gate keys on "not green", not on `observed-bad`** — because `RULING_LINEAGE_FORK` is a **CNO**.
   This is INSTR-4, and it is the transferable finding of the whole proof: **a three-valued vocabulary
   needs a three-valued gate.** A gate written against two values silently consumes the exact case it
   was built to refuse. The corrected gate is owned by
   [`architecture-synthesis.md`](architecture-synthesis.md) §5.5.

**How INSTR-4 was found is itself the method worth importing:** the consumer was **qualified against
six synthetic comment universes** after the request was posted but **before any live ruling existed**.
All six now resolve correctly — valid → `CONSUMED`; wrong head → `REFUSED_MISMATCH`; malformed →
`REFUSED_MALFORMED`; fork → `REFUSED_AMBIGUOUS` **with nothing consumed**; prose mention → `CONSUMED`
(neither counted nor suppressed); no ruling → `CNO_TRANSPORT`
(`proof-b:disposition.json`, executor's own account, DOCUMENTED).

> **CHANGE 5 — the disposition's defect ledger is derived from the trace.** INSTR-4 is recorded in the
> trace and in a predicate's text, and is **absent from `instrument_defects_found_and_corrected`**
> (`obs-b:§5.3`). A write-once record that omits its most severe defect teaches the wrong lesson about
> what write-once buys. The fix is not "remember to add it" — it is that **every enumerated ledger in
> the disposition is a projection of the journal or the trace**, so a projection cannot omit what its
> source contains ([`architecture-synthesis.md`](architecture-synthesis.md) §6.2 rule 4).

---

## 6. Independence — the gap, measured honestly

### 6.1 What V7 measured, and why it returned could-not-observe

**The executed V7** compares `ruler.login` against the candidate's commit author, committer and
pull-request author. **OBSERVED:** one account, `sbracewell64`, authored the candidate commits, the
pull request, the request, the ruling and the receipt, so the login proxy **cannot discriminate a
distinct execution context from a maker**. V7 returned **could-not-observe**, and the terminal grade
`CNO_AT_B-S3` is caused by exactly that fact, first measured one stage earlier at BP5
(`proof-b:receipt.json validation V7`; `proof-b:disposition.json independence`, both read by me).

**The ruler asserted its own independence, and the proof declined to credit it.** Its inspection
carried *"Ruling execution context is distinct from the maker/executor context despite the shared
GitHub transport login"*, narrowing a CNO with its own reason. The consumer did not accept the
narrowing. The independent observer files this as a **wrong-subject finding on axis *stand-in***:
*both session_ref values are authored by the party whose independence they assert, so any single actor
can write two different strings* (`obs-b:§5.4`).

> **Independence is a property of the execution context, not a claim about it, and not a property of a
> name.**

### 6.2 The stronger axis the forge already records — and nobody read

**OBSERVED (`obs-b:§5.1`), and this is the observation's highest-value finding.** GitHub records a
second, stronger fact:

| Object | `performed_via_github_app` |
|---|---|
| the request issue | `none` |
| **the ruling comment** | **`chatgpt-codex-connector`** (OpenAI's GitHub App, id 1144995) |
| the receipt comment | `none` |

The observer ran a **control over 373 pre-existing comments** in four venue issues: every comment whose
in-body `from:` names firstmate carries `app=none` (138 sampled); every comment whose `from:` names the
ruling party carries `app=chatgpt-codex-connector` (168 sampled). **Zero crossovers.**

**What this establishes and does not:**

- **observed-good**: the ruling was written through a **different credential path** — a genuinely
  different execution context, and a different model vendor altogether. The field is a fact **the forge
  writes**, not a self-declared string.
- **could-not-observe**: a distinct **principal**. The account holder authorized that app, so one human
  could still drive both.

> **CHANGE 6 — V7 reads the forge-recorded credential path as its first-class axis**, three-valued,
> with the login retained as the weaker fallback:
>
> ```
> V7 := observed-good        if credential_path(ruling) ∉ credential_paths(maker artifacts)
>                               AND ruler.login ∉ {commit author, committer, PR author}
>       observed-bad         if ruler.login ∈ {commit author, committer, PR author}
>                               AND credential_path(ruling) ∈ credential_paths(maker artifacts)
>       could-not-observe    otherwise, with `measured` naming WHICH axis was unavailable
> ```
>
> That single change would have moved this attempt's independence from **unmeasured** to
> **measured-on-the-axis-that-matters**, at the principal level still could-not-observe.

**And INSTR-3 must not recur.** V7 originally had **no `observed-bad` branch**, so its falsifier could
only ever redden the could-not-observe path; crediting it with *"the ruler-is-a-maker refusal was
watched red"* would have been the same wrong-subject failure. V7 gained an explicit `identities_distinct`
input and **all three values**, and two falsifiers now watch **both** branches with a positive control
re-confirming the green path (`proof-b:disposition.json` INSTR-3, read by me). **Any three-valued
predicate whose falsifier can reach only one non-green branch is not yet watched red.**

### 6.3 The captain's decision, stated as options

**This is not an engineering choice and this document does not make it.** It is registered as a durable
captain decision (`sol-ruling-identity`, disposition `CAPTAIN_DEFERRED`), and the two prior clean-room
tasks that raised it are `cleanroom-proof-designs` (`proof-sol-identity`) and
`cleanroom-proof-b-executor`.

| Option | What it buys | What it costs |
|---|---|---|
| **A — a second GitHub principal** for the ruling party (a distinct account, or an installation token owned separately) | V7 becomes **measurable at the principal level**; the round trip's core property stops being unmeasured | account provisioning; possibly spend; a second credential to hold |
| **B — adopt CHANGE 6 and accept principal-level CNO** | measured on the credential-path axis, which the forge writes and a third party can read; **no spend, no new credential** | independence at the principal level remains **could-not-observe** forever, and every landing that depends on it inherits that grade |
| **C — accept unmeasured independence** (the status quo) | nothing changes | the plane demonstrates transport, schema and consumption correctly and leaves **the one property it is for** unmeasured |

**RECOMMENDED, and only as a recommendation:** adopt **CHANGE 6 unconditionally** — it is free, it is
forge-recorded, and it discriminated the two parties perfectly across 373 control comments — and treat
option A as the captain's separate call about whether principal-level independence is required before
this plane governs a landing.

### 6.4 The enforcement question the captain also owns

**A second, sharper form of the same decision, and it is genuinely the captain's** because it decides
whether the fleet can ship at all while independence is unmeasured:

> **Is the independence predicate a *grade cap* or a *blocking gate*?**

In the executed proof it was a **cap**, pinned in advance as `DEV-B7`: the independence CNO caps the
terminal grade and does not stop the lane, and it **cannot inflate the verdict** because the grade is
could-not-observe either way. That was resolved *before the answer was in view*, which is what makes it
legitimate (`proof-b:inputs/PINNED.json`, read by me).

Making it **blocking** in production means **no ruled change lands until a second principal exists**.
That is a real product consequence, not an engineering preference, and it is registered as a new
captain decision by this synthesis (`cleanroom-independence-enforcement`).

---

## 7. Consumption and the receipt

### 7.1 The directive → action map is total and byte-pinned

Pre-registered before the run, **total over the directive enum**, with **no default branch and no
fallback**.

| Directive | `action_id` | Mechanical action | Code change? |
|---|---|---|---|
| `ADOPT_OPTION` / `<id>` | the option's pinned action | apply the **byte-pinned patch**; assert the resulting tree equals the pinned tree | **yes** |
| `REJECT_ALL_WITH_CONSTRAINT` | record-constraint | append the constraint **verbatim** to a decision record in the control plane; open nothing in the subject | no |
| `INSUFFICIENT_EVIDENCE` | recompile | add the named `missing_evidence[]` to the evidence set; post a `WITHDRAWN` receipt; close; compile a **new** request with a **new** correlation id | no |
| `OUT_OF_SCOPE_CAPTAIN_RESERVED` | route-to-captain | post a receipt recording the reserved reason; close; the question reaches the captain **as a record**, never as a paraphrase | no |

**No step reads the rationale and decides what to write.** The identity check that makes that claim
checkable is owned by [`architecture-synthesis.md`](architecture-synthesis.md) §5.6, and it held on all
three conjuncts in the executed run, with the observer reproducing the resulting tree independently
from public artifacts alone (`obs-b:§1`).

### 7.2 The receipt closes the loop in both directions

```jsonc
{ "schema": "fm-sol-control/v1", "kind": "receipt",
  "vocabulary_digest": "<64hex>", "correlation_id": "fsc1-<32hex>",
  "consumed_at": "<rfc3339_utc>", "consumer": { ... },
  "ruling_comment_id": 5502255519,
  "ruling_sha256": "<64hex over the POSTED bytes>",
  "validation": [ <observation>, ... ],        // the WHOLE ladder, pass or fail
  "applied": { "directive": "...", "option_id": "...", "action_id": "...",
               "applied_bytes_identity": <observation> },
  "resulting": { "tree_sha": "<40hex>", "pull_request": null, "scope": "..." },
  "note": "...",                               // e.g. the independence cap, stated plainly
  "outcome": "CONSUMED" }
  // CONSUMED | REFUSED_MALFORMED | REFUSED_MISMATCH | REFUSED_STALE | REFUSED_AMBIGUOUS
  // | CNO_TRANSPORT | CNO_INCOMPLETE_UNIVERSE | WITHDRAWN
```

**One record serves both directions.** From a request you reach what was ruled and what was done; from
a landed commit you reach the ruling that authorized its shape.

**Every terminal state produces a receipt**, including refusals and withdrawals. *A refusal that leaves
no receipt is a silently abandoned request*, which is how the retired fleet accumulated **six requests
still `emitted` and waiting at the barrier** (`corpus:§3.2`, OBSERVED there).

**The digest that travels is taken over the POSTED bytes.** **OBSERVED (`obs-b:§5.7`):** the local
envelopes and the posted blocks are **canonically identical but not byte-identical** — the local
`request.json` hashes `0034fa33…` while the posted block hashes `14c3639e…`. Because
`receipt.ruling_sha256` is taken over the **posted** bytes, third-party joinability is intact, and the
observer reproduced that digest independently. **A definition-of-done clause asking for byte identity
between a local file and a forge-rendered body is asking for the wrong thing;** ask for canonical
identity locally and **byte identity on the wire digest**.

---

## 8. Fail-closed matrix — the closed refusal vocabulary for the control plane

Total over every reachable non-success. **Precedence `FAIL > CNO > PASS` throughout.** There is no
continue-with-a-warning row.

| Condition | Code | Class | What happens next |
|---|---|---|---|
| ruling body is not valid JSON, or fails schema | `RULING_MALFORMED` | FAIL | receipt naming the failing **field**; close; recompile |
| `vocabulary_digest` differs | `RULING_MALFORMED` | FAIL | as above — this is drift caught mechanically |
| correlation id, repo, head or tree disagree | `RULING_SUBJECT_MISMATCH` | FAIL | receipt; close; recompile at the live head |
| `option_id` not among the offered options | `RULING_SUBJECT_MISMATCH` | FAIL | as above |
| policy digest moved | `RULING_SUPERSEDED` | FAIL | **new** correlation id |
| pull-request head moved, state changed, or expired | `RULING_SUPERSEDED` | FAIL | **new** correlation id |
| two rulings, neither naming the other in `supersedes` | `RULING_LINEAGE_FORK` | **CNO** | consume **neither**; preserve both; require explicit supersession |
| the ruler is a maker of the candidate | independence `observed-bad` | FAIL | consume nothing |
| independence unmeasurable | independence **CNO** | **CNO** | **caps the grade** (or blocks — the open captain decision of §6.4) |
| fetched comment count ≠ reported total | `CNO_INCOMPLETE_UNIVERSE` | **CNO** | stop; **no negative claim may be made** |
| an evidence locator does not resolve to the bytes its digest names | `CNO / DECISION_SUBJECT_NOT_INSPECTABLE` | **CNO** | the request is **not emitted** |
| the boundary deny list is hit | `BOUNDARY_CAPTAIN_RESERVED` | FAIL | route to the captain **as a record**; never compile a request |
| the forge is unreachable | `CNO_TOOL_UNREACHABLE` | **CNO** | stop; retry is bounded by the attempt budget |
| no ruling before `expires_at` | terminal `NO_ANSWER` | terminal | receipt; close; **recorded apart from** a ruler answering `INSUFFICIENT_EVIDENCE`, which is an answer |
| no ruling reached the consumer and no more specific code applies | `CNO_TRANSPORT` | **CNO** | stop |

**Two vocabulary rules that make this table safe:**

1. **A code is emitted at exactly one site.** The corpus's measured failure was a multiple-candidates
   condition detected at two live sites and reported under **two different tokens**, one of them a
   neighbour's (`corpus:§1.4`). When a token is declared and never emitted, the question is not *is the
   case reachable* but **is the case already detected somewhere and labelled as something else**.
2. **A state outside the vocabulary must not fail-close the whole store.** At the retired fleet's
   barrier, **84% of the landing-authority store was quarantined** because one record carried a value
   outside the vocabulary, and an unrelated item could not even ask for a ruling (`corpus:§1.4`,
   `§2.3`, OBSERVED there). **Per-record isolation is mandatory**: set a malformed record aside the
   moment it is found, and never delete it.

---

## 9. The six changes this document makes to what was executed

| # | Change | Forced by |
|---|---|---|
| **1** | Drop the pre-filled ruling skeleton; keep the generated required-field contract | `obs-b:§5.6`, `corpus:§3.4` — a template can be filled without the fact becoming true |
| **2** | Two gating predicates: `base != head`, and the diff resolves non-empty | INSTR-1 — a true green observation about the wrong question |
| **3** | Per-ref digest observations, never an aggregate count; refuse a locator carrying prose | P-B-CAP-4 — locator and digest named different objects while the aggregate read clean |
| **4** | Add `evidence_digest` to `valid_while` | `obs-b:§4` — a ruling bound to a correlation id is not thereby bound to the evidence its ruler was shown |
| **5** | The disposition's defect ledger is a **projection** of the journal and trace | P-B-CAP-3 / `obs-b:§5.3` — the most severe defect was in the trace and absent from the ledger |
| **6** | V7 reads the forge-recorded credential path as its first-class axis, three-valued | `obs-b:§5.1` — the forge held a better independence instrument than the ladder asked for |

**And one thing this document deliberately does not change:** the protocol version string. The venue
that was used **already declares `fm-sol-control/v1`** over a completely different envelope
(`obs-b:§5.5`). It did not bite, because the schema of record travelled in the issue body — but the
mitigation is per-request rather than structural.

> **RECOMMENDED:** give the clean-room protocol a version string the retired fleet does not already
> own, and note the collision where a reader will meet it. This is an engineering choice, not a captain
> decision, and it costs one string.

---

## 10. What the control plane does not establish

| # | Question | Value |
|---|---|---|
| 1 | Is the ruler **correct**? | **Out of scope by construction.** Every mechanism here constrains a ruling's *form*, its *subject binding* and its *consumption*. **None makes the answer right.** The schema gives the ruler a place to put its evidence; it cannot compel it. |
| 2 | Is the plane **economical**? | **could-not-observe.** One decision against a frozen candidate says nothing about the retired fleet's measured 22 requests / 5 rulings / 45% superseded — a property of **volume against movement** (`corpus:§3.2`). The measuring experiment is a registered captain decision (`control-plane-economics-experiment`). |
| 3 | Does the staleness ladder catch a **moving** candidate? | **could-not-observe** (§4.2, P-B-CAP-2). |
| 4 | Is the plane **adversarially** resistant? | **observed-bad, and stated.** The guards are confused-agent-grade. Anyone with the operator's token can post a comment that validates. What cannot be forged is the subject binding *and* the live-state predicates *and* the applied-bytes identity **simultaneously** — a raised cost, not a boundary. |
| 5 | Does a ruled change **survive a pipeline and land**? | **not attempted** — a declared decision not to enforce, recorded as such, and explicitly **not** a could-not-observe (`proof-b:inputs/PINNED.json stages_out_of_scope` B-S13). |
