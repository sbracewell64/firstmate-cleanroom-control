# Determinism assessment — every operation, classified

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: knowledge-work
product_contract_source: Captain clean-room directive, 2026-09-01, section 10
authored_by: scout task cleanroom-architecture-synthesis, 2026-09-02
status_of_this_document: DESIGN ONLY
owns: the D0/D1/D2/D3 classification of every operation in the proposed architecture,
      each D2's eliminating machinery, and the zero-D3 enforcement argument
headline: 78 operations classified. D0 = 66. D1 = 3. D2 = 9. D3 = 0.
```

**Master document:** [`architecture-synthesis.md`](architecture-synthesis.md) owns the component list
(§8) and the shared vocabulary (§0.3) this document classifies against. Grading legend and citation
forms: §0.1 there.

---

## 1. The four classes

| Class | Definition |
|---|---|
| **D0** | **Deterministic.** Code decides. Given the same machine state, the same result. No model turn. |
| **D1** | **Deterministic orchestration around bounded cognition.** A model turn happens, but its authority is bounded by a typed schema, a closed vocabulary, or an external gate, and the orchestration around it is D0. |
| **D2** | **Avoidable cognition compensating for missing machinery.** A model does something a machine could do, because the machine does not exist. **Every D2 names the machinery that would eliminate it.** |
| **D3** | **Unbounded agent workflow authority.** An agent decides what happens next with no typed bound on the set of outcomes. **Target: zero.** |

**Two rules that keep the classification honest, both learned from execution:**

1. **Pinning moves authorship out of the run, not out of the world.** Where bytes are authored once and
   then **pinned and hashed before the first observation**, the *execution* is D0 and the *authorship*
   remains D2. Both facts are recorded. Proof A states this exactly for its intent bytes
   (`proof-a:disposition.json d2_fired` D2-A1, read by me).
2. **A D2 that fired must appear in the record.** Proof A's definition-of-done required it and my
   re-run of its independent verifier confirms it: *"every D2 that fired is recorded in
   `observations[]` with its cognition and eliminating machinery — D2 fired: `['D2-A1', 'D2-S1']`"*
   (DoD 8, PASS, re-run by me 2026-09-02). A proof's honesty about what it did **not** automate has to
   survive into the record, or the classification is decoration.

---

## 2. Kernel components — K1 to K6

| # | Operation | Class | Note |
|---|---|---|---|
| K1.1 | Capture a command's stdout, stderr, exit code and argv to files **before any parse** | **D0** | the raw-first rule; every `evidence_ref` points at one of these |
| K1.2 | Produce a three-valued observation from a captured file | **D0** | fixed comparison; no interpretation |
| K1.3 | Refuse to coerce a could-not-observe into either neighbour | **D0** | non-coercion is a code path, not a habit |
| K1.4 | Apply `FAIL > CNO > PASS` precedence | **D0** | |
| K2.1 | Append an observation to the journal | **D0** | append-only; nothing edits or reorders |
| K2.2 | Append a trace event with a monotonic `seq` | **D0** | gaps are a defect, detected not assumed |
| K2.3 | Answer *does the trace cover every stage in the pinned table?* | **D0** | the query the disposition write consumes |
| K3.1 | Write the pin once and refuse a second write | **D0** | |
| K3.2 | Verify every pinned input digest before the run starts | **D0** | the run cannot begin against edited inputs |
| K3.3 | Answer *what is the pinned bound for this predicate?* | **D0** | |
| **K3.4** | **Author the pinned material** — the fold rule, the stage table, the bounds, the falsifier targets, the candidate patch | **D2-K1** | §4 |
| K4.1 | Fold the journal to one outcome under the pinned rule | **D0** | reproducible by a reader with no session access; I re-derived both proofs' outcomes (`architecture-synthesis.md` §0.2) |
| K4.2 | Refuse the disposition write without stage coverage | **D0** | |
| K4.3 | Project the journal and trace into the disposition's ledgers | **D0** | a projection cannot omit what its source contains — the fix for P-B-CAP-3 |
| K4.4 | Emit a code from the closed outcome vocabulary | **D0** | total over reachable end states; no `PARTIAL`, no `PROVED_WITH_CAVEATS` |
| K5.1 | Validate an envelope against the one schema file | **D0** | |
| K5.2 | Generate the reply contract by walking the schema | **D0** | **no field name is typed anywhere** |
| K5.3 | Self-check: re-render and byte-compare against what was posted | **D0** | a mismatch is a build failure, not a diff to eyeball |
| K5.4 | Compare `vocabulary_digest` between producer and consumer | **D0** | drift is caught mechanically |
| K6.1 | Run a falsifier and record `target`, `observed`, `neighbours` | **D0** | the target is **read from the pin**, never from this run |
| K6.2 | Compute distinctness as `(target == observed) ∧ (neighbours stayed green)` | **D0** | the tautology of P-A-CAP-4 removed |
| **K6.3** | **Choose which falsifiers exist, and what each targets** | **D2-K2** | §4 |
| **K6.4** | **Author the deviation register** | **D2-K3** | §4 |

**Subtotal: 20 D0, 0 D1, 3 D2, 0 D3.**

---

## 3. Lane A and Lane B operations

### 3.1 Lane A — delivery

| # | Operation | Class | Note |
|---|---|---|---|
| A.1 | Host and tool preflight probes, compared to pinned floors | **D0** | |
| A.2 | Create the repository | **D0** | fixed flags |
| A.3 | Seed commit under the bootstrap exception | **D0** | fixed file set, pinned bytes, exactly one commit |
| A.4 | Apply repository merge settings and branch protection | **D0** | one PATCH, one PUT, pinned bodies |
| A.5 | Read protection back field-for-field and digest it | **D0** | the policy generation |
| A.6 | Negative control: prove protection actually refuses | **D0** | watched red; **HTTP 405 observed** |
| A.7 | Apply the pinned candidate patch; assert the resulting tree | **D0** | no authoring step exists |
| A.8 | Pre-gate G0–G5, G7, G8, G10, G11 | **D0** | every input a command's output |
| A.9 | Pre-gate **G6/G6b** — validate the config that will actually execute | **D0** | a wrong-subject guard |
| A.10 | Pre-gate **G9** — required contexts vs real job display names at the default branch | **D0** | a wrong-subject guard |
| A.11 | Pre-gate **G12** — no generated or build output in the diff | **D0** | new; anchored to trusted ignore rules the candidate cannot edit |
| **A.12** | **The qualification run's internal agent turns** — review, fix, test, document, lint, PR prose | **D1** | §5.1 |
| A.13 | Parse the `outcome:` field from the captured file | **D0** | field-keyed; never `$?` |
| A.14 | Extract and validate the attestation; bind it to the live published head | **D0** | exactly one live marker; three named steps `completed` |
| A.15 | Read required check runs at the exact head, over a **complete** universe | **D0** | each entry records its own head |
| A.16 | Evaluate the eight-condition merge predicate | **D0** | `mergeable == null` is CNO, re-polled under a declared bound |
| A.17 | Evaluate triggering conditions T1–T8 | **D0** | each carries its own evidence reference |
| A.18 | Mint the one-use authorization and compute its act digest | **D0** | |
| A.19 | **Construct** the merge act from the authorization record | **D0** | no ambient variable reaches the act |
| A.20 | Perform the merge; classify 200 / 409 / 405 / 422 / timeout | **D0** | the forge's text is quoted **as the forge's** |
| A.21 | Verify `merge_commit.parents[1] == expected_head` | **D0** | identity, not containment |
| A.22 | Confirm pipeline terminalization under a **declared** bound | **D0** | an unbounded sample is not a result |
| A.23 | Mirror, verify it resolves the landed commit **after** the mutation, archive | **D0** | |
| A.24 | Attempt arithmetic: spend, budget, terminal state | **D0** | |
| A.25 | Merge idempotence: read PR state before minting or spending | **D0** | the one place a wrong answer is expensive |
| **A.26** | **Author the `--intent` bytes** | **D2-A1** | §4 |
| **A.27** | **Attribute a red required check to flake or defect** | **D2-A2** | §4 |
| **A.28** | **Answer a qualification gate outside the pre-registered catalog** | **D2-A3** | §4 |

**Subtotal: 24 D0, 1 D1, 3 D2, 0 D3.**

### 3.2 Lane B — decision

| # | Operation | Class | Note |
|---|---|---|---|
| B.1 | BP1 — the question key is in the catalog at its pinned digest | **D0** | a miss **refuses**; it is not a judgement |
| B.2 | BP2 — ≥ 2 options, each with a reversibility class from a closed set | **D0** | |
| B.3 | BP3 — **execute** reversibility: apply, reach the pinned tree, revert to base | **D0** | measured, not asserted |
| B.4 | BP4 — the captain-reserved deny list over the union of both patches | **D0** | the only predicate whose failure routes to a human |
| B.5 | BP5 / V7 — independence, on the credential-path axis with the login as fallback | **D0 producing a three-valued result** | the *measurement* is code; what it can measure is capped by §4's D2-B2 |
| B.6 | BP6 — `candidate_state` is never `MUTATING` | **D0** | |
| B.7 | BP7 — every locator resolves anonymously to the bytes its digest names | **D0** | per-ref observations, never an aggregate count |
| B.8 | Compile every request field from a named machine source | **D0** | 52 such predicates in the executed run |
| B.9 | Derive the correlation id by hash | **D0** | recomputed independently by the observer |
| B.10 | Emit exactly one issue; capture the posted body | **D0** | idempotent on the derived id |
| B.11 | Retrieve comments with the completeness predicate | **D0** | `fetched == reported`, else CNO |
| B.12 | Select rulings by **validated content**, never by containment | **D0** | a prose mention neither counts nor suppresses |
| **B.13** | **The ruler's judgement** | **D1** | §5.2 |
| B.14 | Evaluate V1–V10 | **D0** | every failing predicate reported, not just the first |
| B.15 | Evaluate L1–L5 against live state | **D0** | identity, never ancestry |
| B.16 | The three-valued terminal gate | **D0** | keys on "not green"; FAIL outranks CNO; exceptions pinned by name |
| B.17 | Map directive → pre-registered action through a **total** table | **D0** | no default branch, no fallback |
| B.18 | Apply the byte-pinned patch; verify the three-conjunct identity check | **D0** | no step reads the rationale and decides what to write |
| B.19 | Post the receipt; close the issue | **D0** | every terminal state produces a receipt |
| B.20 | Hand a code change to Lane A with a **fresh** authorization | **D0** | authority is minted, never transferred |
| **B.21** | **Author a catalog entry for a subject the catalog does not contain** | **D2-B1** | §4 |
| **B.22** | **Establish independence beyond what the forge records** | **D2-B2** | §4 |

**Subtotal: 19 D0, 1 D1, 2 D2, 0 D3.**

### 3.3 Cross-cutting

| # | Operation | Class | Note |
|---|---|---|---|
| X.1 | Grade every observation, in the absence of a declared verifier | **D2-S1** | §4 — shared by both lanes |
| X.2 | Route a `DECISION_OWED` gate: Lane B, captain, or abort | **D0** *once the policy table exists*; **D2-A3** until then | the table is keyed on `(step, category, action, review_scope)` and is **total** |
| X.3 | Decide whether a decision is captain-reserved | **D0** | BP4's deny list is mechanical; the captain-reserved classes are a closed list |
| X.4 | **Intake: turn a captain request into a pinned candidate or a catalog key** | **D1** | §5.3 |
| X.5 | Re-enter a stage after an instrument repair | **D0** | §6 — **this was a D2 in Proof A and is D0 now** |

**Subtotal: 3 D0, 1 D1, 1 D2 (X.1; X.2's D2 is A.28 already counted), 0 D3.**

---

## 4. Every D2, with the machinery that eliminates it

Nine. Each names a machine that could do the job, and what it would cost.

| Id | The avoidable cognition | Why it exists today | Machinery that eliminates it | Cost |
|---|---|---|---|---|
| **D2-S1** | Every observation is graded by hand rather than by a declared verifier. | **OBSERVED:** `bin/fm-verify.sh --list` declares five verifiers — `browser`, `pr-checks`, `merge-clean`, `review-exec`, `review-mutation` — and none covers a clean-room proof record or a control-plane round trip. Both proofs' designs predicted this and both executions confirmed it. | Two **declared verifiers** in the registry — one for a delivery stage, one for a control-plane round trip — each returning `PASS` / `FAIL` / `NO_VERIFIER_RAN` for a named stage id, so the actor **consumes a verdict instead of forming one**. | small: two verifier definitions plus their registration. **This is the highest-value D2 to close, because it is the only one that touches every other operation.** |
| **D2-K1** | Authoring the pinned material: the fold rule, the stage table, the async bounds, the candidate patch, the falsifier targets. | The pin has to be written by someone before the first observation; there is no upstream typed artifact for it to compile from. | A **typed plan artifact** the pinner compiles into the pin mechanically — stage ids, bounds and falsifier targets rendered from a declared verification contract rather than typed. The candidate patch stays authored, but its *execution* is already D0 because it is hashed. | medium. Note this is the **same shape** as D2-A1 and closing one closes most of the other. |
| **D2-K2** | Choosing which falsifiers exist, and what each targets. | A guard set does not currently enumerate its own mutations. | A **mutation register derived from the predicate table**: for every declared refusal code, the mutation that reddens it, generated mechanically, with the target read from the generated register rather than typed. Then P-B-CAP-5's relabelled target is unreachable rather than discouraged. | medium, and it removes a whole defect class rather than one instance. |
| **D2-K3** | Authoring the deviation register. | A deviation is currently a sentence a human writes. | Generate it as the **diff between the pinned contract and the executed stage record**: where a stage's actual inputs, bounds or scope differ from the pin, the deviation is emitted with both values. A *reason* still needs a human sentence; the *existence* and the *delta* do not. | small, and it converts an inventory that can be forgotten into one that cannot. |
| **D2-A1** | Authoring the `--intent` bytes that become enforceable review acceptance criteria. | **DOCUMENTED (`nm-scout:§2.5`, OBSERVED there):** `--intent` is *"the only channel by which caller-side evidence reaches the reviewer. There is no structured-criteria input port."* | A **structured criteria port** on the qualification tool taking a typed verification contract, **or** a deterministic serializer that renders that contract into intent bytes. Either makes the transformation total and mechanical. In this architecture the *execution* is already D0 because the bytes are pinned and hashed; the *authorship* remains D2. | the serializer is small and entirely ours; the input port is an upstream change. |
| **D2-A2** | Judging whether a red required check is a flake or a real defect. | The forge reports a **conclusion, not a cause**. | A **base-commit control runner**: re-run the identical workflow N times on the base commit and N times on the candidate, and decide from the two rates. Without it, an agent judges from one red. | small, and it is a general instrument, not a one-off. |
| **D2-A3** | Answering a qualification gate whose subject is not in the pre-registered catalog. | The pipeline parks by design — an unclassified finding resolves to `ask-user` (`no-mistakes:internal/types/findings.go:409-414`), which is it failing **closed to the human**, working correctly. | A **total decision-policy table** keyed on `(step, finding.category, finding.action, review_scope)` mapping to one of `{escalate-to-Lane-B, abort, adopt-pinned-response}`. The catalog-covered case becomes D0; the **uncovered case still refuses**, which is the correct behaviour rather than a gap. | medium; the closed vocabularies for all four key fields already exist (`nm-scout:§5.3`). |
| **D2-B1** | Recognising that a decision exists, and choosing which catalog entry it is, for a subject the catalog does not contain. | The catalog is finite. | A **typed decision detector bound to the pipeline's own `Findings` objects** rather than to prose, emitting `question.key` mechanically from `(category, review_scope, action)`. Then a novel subject is a catalog **miss that refuses**, not a judgement call. | medium; depends on the same typed surfaces as D2-A3. |
| **D2-B2** | Establishing that the ruling party is assignment-distinct from the maker. | **Partly eliminated already.** The forge records `performed_via_github_app`, which the observer showed discriminates the two parties **perfectly across 373 control comments, with zero crossovers** (`obs-b:§5.1`). Adopting it as V7's first-class axis moves independence from *unmeasured* to *measured on the axis that matters*. | **Full** elimination needs a **second principal** — a distinct account or a separately-owned installation token — plus a two-line actor register the validator reads, so distinctness is **measured** rather than asserted. | the credential-path axis is **free**; the second principal is a captain decision with provisioning cost. |

### 4.1 The D2 that was eliminated between the two proofs

**OBSERVED, and it is the package's clearest evidence that the classification is actionable.**

In Proof A, **deciding to re-enter a stage after an instrument repair, and deciding how the fold should
treat the superseded evaluations, was semantic cognition by the executing agent**, performed **during
the run with the answer in view** (`obs-a:§6`, listing exactly this among the agent's semantic acts;
`proof-a:deviations.jsonl D-7`).

In Proof B the same situation is **D0**, because the pin decides it in advance:

> *"If a stage cannot be evaluated because the measuring instrument is broken, the recorded observation
> is could-not-observe and it gates. Re-measuring after a fix appends a SECOND observation which also
> gates, so the outcome after any instrument defect is at best `CNO_AT_<that stage>`. This is
> deliberately unforgiving; it is the price of a rule fixed before the answer is in view."*
> — `proof-b:inputs/PINNED.json fold_rule.rules[4]`, read by me

**Four instrument defects were then found and corrected in Proof B, and none of them moved the
verdict**, because the rule that graded them was already fixed. That is what eliminating a D2 looks
like: the same event, no longer requiring a judgement.

---

## 5. The three D1s — where cognition happens, and what bounds it

Every D1 has a **machine-readable input, a machine-readable output, a declared authority bound, and a
machine-checkable acceptance contract.** Anything that lacks one of the four is D3, not D1.

### 5.1 A.12 — the qualification pipeline's internal turns

| | |
|---|---|
| **Input** | the candidate diff, the pinned intent bytes, the trusted default-branch configuration |
| **Output** | typed findings (`id`, `severity`, `file`, `line`, `description`, `action`, `source`, `user_instructions`, `review_scope`, `category`), fix commits, a PR body carrying a head-bound attestation |
| **Authority bound** | a **hardcoded nine-step order with no configuration path** to add, remove or reorder steps (`nm-scout:§1.1`); closed vocabularies on every finding field; the review gate's auto-fix budget defaulting to **0**, so blocking findings park rather than self-fix; and the **review-approved-head binding at push**, which is written only when a full review round completes and refuses a head that is not equal-or-descendant |
| **Acceptance** | the `outcome:` field ∈ `{checks-passed, passed}`, plus a head-bound attestation with `review`/`test`/`document` all `completed`, plus every required check `success` at the exact published head |
| **Anti-collusion** | reviewer and fixer are **structurally separated**: every review turn runs **session-free**, because resuming the session that prescribed a fix *"would seat the prescriber of those fixes as their certifier"*; only the fixer keeps a durable session, *"because it certifies nothing"* (`nm-scout:§5.2`) |

**And the one step with zero agent involvement is the one that performs the irreversible outward
effect.** Push is entirely deterministic: reload the durable review-approved commit and refuse if
missing or unreachable; anchor the force-with-lease to an explicit SHA; verify by `ls-remote` that the
remote head **equals** the pushed head; settle the mirror before recording publication
(`nm-scout:§5.1`). That is the shape this architecture copies at its own landing chokepoint.

### 5.2 B.13 — the ruler's judgement

| | |
|---|---|
| **Input** | the request envelope and its content-addressed evidence |
| **Output** | one ruling in a **closed, total** directive vocabulary, bound to an exact head, tree and policy generation, with its own three-valued inspection observations |
| **Authority bound** | the schema: `additionalProperties: false` on every object; **no field exists for a third option**; the only way to reject both is a directive that produces **no code change** |
| **Acceptance** | V1–V10, L1–L5, and the applied-bytes identity check |

**The ruling does not authorize a landing.** It answers *what the code should do*; a landing spends a
freshly minted authorization. Authority is **minted, never transferred**.

### 5.3 X.4 — intake

| | |
|---|---|
| **Input** | the captain's request, in natural language — the one genuinely unstructured input in the architecture |
| **Output** | either a task carrying a **pinned candidate patch** and pinned intent, or a **catalog key** |
| **Authority bound** | the catalog is finite and a miss **refuses**; the deny list is mechanical; the pinned material is hashed before the first observation |
| **Acceptance** | the pre-gate (Lane A) or BP1–BP7 (Lane B) |

**INFERRED:** this is the only place where a human sentence enters the system, and it is bounded on the
way out by two independent mechanical gates. Everything downstream of it is typed.

### 5.4 The one D1 this architecture does **not** have

There is **no "supervisor agent" D1**. Nothing decides what to dispatch next, what to retry, when to
escalate, or whether a lane is healthy. Those are D0 (component **D6**, and the state machines) or they
do not exist. That absence is the largest single difference from the retired fleet, whose
governing machinery grew to 105,214 lines of shell around exactly those questions (`corpus:§0`).

---

## 6. Zero D3 — the enforcement argument, and its declared limit

**Claim: no operation in this architecture is D3.** An operation is D3 if an agent decides what happens
next **with no typed bound on the set of outcomes**. Four independent mechanisms make that unreachable,
in descending strength.

| # | Mechanism | What it forecloses |
|---|---|---|
| **1** | **Server-side enforcement.** `enforce_admins: true` plus required status checks on the protected branch. | **No actor — including the repository owner and any agent holding the owner's token — can land an unqualified candidate.** **OBSERVED:** HTTP 405 with the owner's own token (`proof-a:raw/…-nc2-merge-attempt.stderr`, read by me). This is the one control that survives a deliberate bypass. |
| **2** | **A closed effect list.** Exactly two effect classes, and a small enumerated set of mutating calls. Proof A made **9** mutating forge calls and its ledger accounts for all nine; Proof B made **3** and its trace holds exactly three `EFFECT_INTENT`/`EFFECT_RESULT` pairs, each intent written before the call (`obs-b:§5.7`). | Any other mutating call is **out of design** — a defect, not a variation. |
| **3** | **Constructed acts.** The landing act is built from the authorization record and its digest re-checked; the consumption act is a byte-pinned patch selected by a **total** map. | A caller cannot smuggle a different head, repository, method, or patch past a valid authority. There is no code path where these come from an ambient variable. |
| **4** | **Closed vocabularies with total maps.** The outcome vocabulary, both refusal vocabularies, the directive enum and its action map, the finding-action enum. **Every state transition names its refusal.** | An outcome outside the vocabulary is unreachable **by schema**, not by convention. There is no default branch and no fallback anywhere in the directive map. |

**And the structural test:** for every state in both machines, the set of successor states is finite and
enumerated ([`architecture-synthesis.md`](architecture-synthesis.md) §§4.1–4.2, §§5.1–5.2), and each
transition names the evidence required to leave and the refusal that fires instead. **There is no state
whose successor is "whatever the agent decides next."**

### 6.1 The declared limit — stated, not glossed

**Mechanisms 2, 3 and 4 are confused-agent-grade, not adversarial-grade.** An agent with a free shell
and the operator's token can call the forge API directly, bypassing all three. **Only mechanism 1
survives a deliberate bypass, and only for the merge.**

This is the same honesty both of upstream's guard libraries apply to themselves —
*"a deliberately forging shell running as the same uid … can evade any in-process discriminator …
adversarial-grade separation is explicitly out of scope"* (`firstmate:bin/fm-lease-lib.sh:38-48`,
OBSERVED in `boundary:§6.6`) — and preserving it is what makes the zero-D3 claim worth anything. A
zero-D3 claim that quietly assumed adversarial resistance would be **the wrong-subject class applied to
the architecture's own safety argument**.

### 6.2 Two places where the claim is narrower than it looks

Named here rather than left for a reader to find.

1. **The qualification pipeline's push reaches the remote without passing any chokepoint this
   architecture owns.** It is D1's own irreversible effect, deterministic *inside* the tool
   (`nm-scout:§5.1`), and this architecture does not re-guard it. The candidate branch is unprotected
   by design; the protected ref is defended server-side. **Stated, not implied.**
2. **The forge gate proves the pipeline ran; it does not prove the evidence could not have been
   forged.** `verify.py:21-32` says so, and Proof A's NC-2 setup demonstrated it by turning the check
   green on a hand-written body. Every D0 downstream of that gate is deterministic **about a signal
   that is author-editable**. The disposition records `forge_gate` as evidence of a run and never as
   proof of integrity.

---

## 7. Totals, and where the remaining cognition lives

| Class | Count | Share |
|---|---|---|
| **D0** | 66 | 85% |
| **D1** | 3 | 4% |
| **D2** | 9 | 12% |
| **D3** | **0** | **0%** |

**78 rows total**, counted mechanically over the four tables in §§2–3 rather than tallied by hand.

**Where the D2s cluster, and what that says.** Six of the nine — D2-S1, D2-K1, D2-K2, D2-K3, D2-A1,
plus D2-A2 — are about **the evidence apparatus itself**, not about the work. They exist because the
architecture instruments itself by hand: it grades its own observations, authors its own pin, chooses
its own falsifiers, writes its own deviation register, and serialises its own acceptance criteria.

**INFERRED:** that is the right place for the remaining cognition to be, and it is the cheapest place to
remove it from. **One piece of machinery — a declared verifier plus the typed plan artifact it grades
against — closes or shrinks five of the nine**, and none of the five requires an upstream change to any
external tool.

The other three are genuinely bounded by the world: **D2-A3** and **D2-B1** shrink to a catalog miss as
soon as their typed detectors exist and then **refuse rather than judge**, and **D2-B2** is half-closed
free of charge by reading the credential path the forge already records, with the remaining half a
captain decision about a second principal ([`sol-control-v1.md`](sol-control-v1.md) §6.3).

---

## 8. Could-not-observe register for this classification

| # | Question | Value |
|---|---|---|
| 1 | Is the D0 share above measured, or asserted? | **Asserted by enumeration, not measured.** Every row is classified from the executed record or the proposed contract; no operation was run and timed. A row classified D0 whose implementation later calls a model is a **defect against this table**, and the table is the artifact that makes that checkable. |
| 2 | Are there operations neither proof exercised that this table therefore misses? | **Likely, and stated.** The table covers the architecture's proposed components. Operations that appear only under load — concurrency, multi-lane dispatch, capacity — are **not in the architecture** and so are not classified. If they are added, they are classified then. |
| 3 | Does the classification survive the D2 eliminations? | **UNPROVEN.** Closing a D2 usually adds D0 operations; the share moves, the count grows. That is the intended direction, not a regression. |
| 4 | Is D1 genuinely bounded in the qualification pipeline, or bounded in prompt only? | **Partly prompt.** The tool's own source states that its fixer's verification discipline *"is a contract, not an enforced sandbox — the agent has free shell access — so the pinned regression tests guard the wording, not the runtime"* (`nm-scout:§5.4`). The **structural** bounds — the fixed step order, the typed findings, the review-approved-head binding at push — are code. The behavioural ones are prompt. Both facts are recorded. |
