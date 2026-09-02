# Current control plane — `fm-sol-control/v2`, and why it is not usable yet

    generated:      2026-09-02
    projection_of:  artifacts/control/ and runtime/firstmate/config/  (NOT authoritative; see ../README-FIRST.md)
    drawn_from:
      - artifacts/control/bootstrap-report.md                    (executor)
      - artifacts/control/observer/observer-report.md            (independent read-only observer)
      - artifacts/control/policy/architecture-review-acceptance-v1.md
      - artifacts/control/evidence/captain-addendum-control-config-generation.md
      - artifacts/control/evidence/ruler-credential-path-reachability.md
      - artifacts/control/evidence/verifier-coverage.md
      - artifacts/control/schema/  (frozen schema, FREEZE.json, generated reply contracts)
      - artifacts/plans/sol-control-v1.md                        (the wire contract this v2 derives from)
      - runtime/firstmate/config/control-plane.yaml              (THE canonical owner)
      - runtime/firstmate/state/cleanroom-control-v2.listener.json

---

## 1. The bottom line

**The plane was built, frozen and proven; the round trip did not complete, and
the failure was preserved honestly rather than bypassed.**

Twenty-three guards and controls were exercised, every refusal writing **zero**
side-effect records, with four positive controls proving the plane also stays
quiet when the input is genuinely valid. Then the first real transaction reached
a terminal **`NO_ANSWER`**: no ruling arrived inside its 90-minute bound.

**The machinery being sound and the channel being usable are different claims,
and only the first has evidence.**

## 2. The facts

| | |
|---|---|
| Venue | `https://github.com/sbracewell64/firstmate-cleanroom-control` (public, issues on) |
| Protocol | `fm-sol-control/v2` |
| Schema of record | `artifacts/control/schema/fm-sol-control-v2.schema.json`, sha256 `23e828b2…` |
| Frozen | 2026-09-02T11:35:41Z — **before** any envelope was compiled |
| Canonical config | `runtime/firstmate/config/control-plane.yaml` |
| Config generation | `58235a9229b99afb82a3b7b43e9cebf5d53cbe4dc63edf9f0e7c5c0cb562a336` |
| Evidence mirror | commit `ee7aa5c3…`, one commit, 25 files |
| Acceptance policy | commit `ac78e35a…` — pinned **before** the request was compiled |
| Request | `fscr2-c7757a26…` on issue **#1** |
| Correlation | `fsc2-3f10d80b…` |
| **Outcome** | **`NO_ANSWER`**, verdict `CNO`; receipt `fscp2-ec0ee3cd…` posted, issue closed `completed` |
| Writes to the retired venue | **zero**, verified on nine axes plus a set difference |
| Retired venue | `sbracewell64/firstmate-sol-control` — private, read-only historical evidence, **untouched and unmigrated** |

## 3. The law it runs under — the captain's nine rules

The captain's addendum of 2026-09-02 made control-plane identity a **single
canonical effective configuration generation**. Protocol, control repository,
logical Browser Sol project and routing metadata live in one file and **only**
there; no emitter, watcher, consumer, receipt writer, prompt, diagnostic or
document may carry an independent copy. Every one resolves through one
deterministic resolver, which normalizes the file and computes the generation
digest.

The consequences that bite:

- **Request binding.** Every request carries the applicable config generation.
- **Ruling applicability.** At consumption the config is *freshly re-resolved*; a
  mismatch makes the ruling historical evidence — `STALE/INAPPLICABLE`, zero
  action.
- **Venue isolation.** Comparison is **exact string equality everywhere**,
  because `fm-sol-control/v2` *contains* `fm-sol-control`, so a consumer matching
  by word overlap would happily consume retired-venue traffic. Watched red three
  ways.
- **Projection, not duplicate truth.** The venue's README is *generated from the
  resolver* rather than typed, so it cannot drift from the configuration it
  describes.
- **Routing metadata is never authority.** `browser_sol_project` is diagnostic
  only; authority stays in the typed ruling, exact parentage, forge identity
  evidence, and fresh applicability.

## 4. What was independently confirmed

The observer **arrived before the venue existed** and built its instruments with
negative controls *first*, so a silent instrument could never be mistaken for a
clean result: an anonymous probe (private repo must 404, bogus repo must 404,
public repo 200); an independent schema validator (a deliberately broken v1
envelope produced 23 errors); an anonymous evidence resolver (true digest / wrong
digest / 404 → GOOD / BAD / BAD); a generation-change detector (comment-only edit
→ digest unchanged, so it is value-sensitive and format-insensitive); a secret
scanner (planted token, AWS key, private key, home path → 7 hits, then 0 when
removed); a listener predicate (fires on 5 hits, silent on 0).

It then confirmed: the venue was created and configured as directed; the schema
was frozen **once**, before any transaction; the canonical config owner exists
with a third-party-reproducible generation digest; **every identity in the
protocol is genuinely derived and reproducible by an independent party**;
evidence is anonymously resolvable at immutable locators; venue isolation holds
by construction rather than convention; the guard set discriminates in **both**
directions; the timeout was honest; and **nothing was written to the retired
venue**.

## 5. Why `NO_ANSWER` is an honest result and not a shrug

- **The negative claim rests on a complete universe.** 89 polls over 90 minutes,
  every one recording `fetched == reported`. "No ruling arrived" is an
  observation, not an absence of looking. The consumer re-evaluated completeness
  at consumption.
- **`NO_ANSWER` is deliberately kept apart from `INSUFFICIENT_EVIDENCE`**, which
  would have been an *answer*.
- **The bound was pinned before emission and honoured**, not extended once the
  silence was visible.
- **The receipt is typed**, validated against the frozen schema *before* posting,
  and never edited (`created_at == updated_at`). The observer validated it
  against its **own pinned copy** of the schema — valid, 0 errors — and re-derived
  both the receipt id and the consumption key independently.
- **The closure is clean.** One comment, closed `completed`, no second receipt, no
  reopen, no edit.

## 6. Two defects the machinery found in its own author

Both found by **running** it, not by reading it.

1. **The schema refused this author's own receipt** — `'replay_check' is a
   required property`. The consumer was claiming a consumption without having
   demonstrated the replay. The fix is not to add the field: the consumer now
   *executes* the second consumption, fingerprints the durable store before and
   after, and **refuses to emit a receipt at all** unless the replay really
   performed zero actions. That gate is itself watched red.
2. **Expiry shared a refusal code with a late ruling** — "nobody answered" and
   "somebody answered too late" collapsed into one token, one repair standing in
   for two. Now resolved at fold time. **Eighteen fixtures missed it**, because
   every fixture ran while the request was still live: *a fixture suite that never
   advances the clock cannot see a bug in the clock's own branch.*

**And the consumer changed between emission and consumption.** That is stated
rather than left to be discovered: the frozen surface — schema, renderer,
resolver — is unchanged and re-verified by digest afterwards; the receipt was
validated against that unchanged schema before posting; the change corrected a
code-selection defect without touching any predicate's verdict. **The consumer is
deliberately not part of the frozen surface; what is frozen is the vocabulary
both sides validate against.**

## 7. Open defects on the plane

| # | Defect | Severity |
|---|---|---|
| 1 | **The schema cannot express "nothing was consumed."** `consumption_identity` is required regardless of outcome, so a `NO_ANSWER` receipt must still carry consumption shape. A **design gap**, not a slip; the conditional mechanism already exists in the schema. Needs a new generation. | moderate |
| 2 | **Evidence-mirror redaction is exact but incomplete.** The `/home/OPERATOR` substitution is perfect (6/3/3 → 6/3/3, zero residue), but the **Windows** form `/mnt/c/Users/<operator>/…` survives into three files on the public venue whose declared class says operator-local paths are replaced. Not a credential disclosure — the same name is already public as the git author — but the contract is not met on its own terms. Registered as a captain decision, because scrubbing rewrites the commit **21 evidence references are pinned to by sha256**. | low |
| 3 | **The commit-kind evidence digest is self-referential.** | low |
| 4 | **Routing labels were applied 10m25s late** rather than atomically with issue creation. | low |
| 5 | **`gh-axi` silently truncates at ~4 KB** (`original_length: 40306` cut to 4 KB). **Every envelope in this protocol exceeds it.** Any agent reading an issue, ruling or PR body through that path and believing it saw the whole document is exposed. Treat as a fleet-wide hazard. | hazard |
| 6 | **No declared verifier covers anything on this plane.** `fm-verify.sh --list` offers `browser, pr-checks, merge-clean, review-exec, review-mutation`; none covers schema validation, config generation, locator readiness, universe completeness or replay. Every grade was reached by hand, **and no green was trusted before its negative control was watched going red.** | reported gap |

## 8. Two limits worth stating plainly

- **The plane is not adversarially resistant, and says so.** Anyone holding the
  operator's token can post a comment that validates. What cannot be forged
  *simultaneously* is the subject binding, the live-state predicates, the config
  generation and the applied-bytes identity. **That is a raised cost, not a
  boundary.**
- **The authenticated watcher mechanism is unavailable on this filesystem.**
  `fm-check-register.sh` refuses because a 9p mount cannot hold a file mode. A
  documented listener config plus a bounded poll ran instead — and the listener
  record states which mechanism ran rather than implying it. The check script is
  written to the upstream contract and is ready to register unchanged on any
  filesystem that carries modes.

## 9. What happens next

1. **Settle the return path** — the blocking captain decision. Until a ruling can
   physically arrive, a timeout is **not** evidence that the ruler declined.
2. **Re-run the handshake unchanged.** Nothing needs rebuilding: a new request at
   `request_generation: 2` recompiles from the same frozen schema, the same config
   generation and the same evidence mirror commit.
3. **Do not retire the old venue.** The retirement plan was deliberately **not**
   drafted, because drafting it now would be the more damaging half of a
   wrong-subject error: retiring a listener that *works*, on the strength of a
   plane that has never completed a round trip, because the new plane's
   *machinery* is sound. The precondition is stated so the plan can be written
   the moment it is met — **one ruling received on the new venue without relay,
   validated, consumed once, and receipted.**

## 10. What this plane does not establish

That Browser Sol received, read, or declined the request — transport and ruler
remain unseparated. That at-most-once holds for non-`CONSUMED` outcomes. That the
reviewed architecture package is sound, **since no review took place**. That the
ruling party is an independent principal, which one shared forge account makes
unobservable here.
