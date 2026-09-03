# Acceptance policy: generation-3 conformance transaction (fm-sol-control/v2, schema generation 3)

    policy_id:     cleanroom-gen3-conformance-v1
    ruled_by:      control issue #3, tooling_supersession.qualification[1]
                   ("run one bounded synthetic/conformance transaction through generation 3
                   before relying on it for later proof/control work")
    scope:         TRANSPORT SEMANTICS ONLY. This transaction qualifies the generation-3 tooling;
                   it does not re-review the architecture package (qualification[2]).
    pinned:        before the request envelope is compiled. Write-once.

## What is being asked

The ruling party is asked to fetch the request envelope from the venue item that carries it,
validate it against the generation-3 schema of record named by its `vocabulary_digest`
(published at `schema-gen3/`), and rule ADOPT_OPTION A if it validates as fetched, or
INSUFFICIENT_EVIDENCE naming the failing predicate if it does not. Any ruling that validates
against the schema of record and names this request is consumed; the transaction is bounded
by `expires_at` (90 minutes) and a NO_ANSWER is a preserved terminal, not a failure of the tooling.

## Acceptance predicates (three-valued, all measured, none skipped)

| # | Predicate | Instrument |
|---|---|---|
| Q1 | the venue item was created carrying its routing labels in ONE call, by the frozen emitter itself, and its body equals `render(envelope)` | `fsc3-emit-request.py check` against the creation response |
| Q2 | the envelope fetched whole from the venue validates against the schema of record and its ids recompute | `fsc3-verify-envelope.py issue <n>` |
| Q3 | the ongoing inbound monitor surfaces the ruling comment exactly once, as a `ruling_candidate` for this request id | `state/procevent-inbox/<source>.<seq>.result`, `bin/fm-procevent.sh handled` |
| Q4 | the consumer yields a receipt that validates against the schema of record with an outcome-bearing `receipt_id`, claiming through an exclusive create when CONSUMED | `fsc3-consume.py --with-replay-proof`, `fsc3-verify-envelope.py file receipt` |
| Q5 | a second consumption performs zero actions and returns the first outcome unchanged | `replay_check` in the receipt |
| Q6 | every published mirror byte carries no operator-local user-profile path | `fsc3-redact.py scan` before the mirror commit |
| Q7 | the generation-1, generation-2 and generation-3 frozen bytes are unchanged throughout | the three `verify-freeze` tools, exit 0 |

A predicate that could not be measured is could-not-observe and is never narrowed to observed-good.

## Fold

`observed-bad` on any of Q1, Q2, Q4, Q5, Q6, Q7 -> generation 3 is NOT qualified; the defect is recorded and a
generation 4 is cut rather than a frozen byte edited. `could-not-observe` on Q3 (no ruling arrived) leaves Q3
unmeasured and the transaction terminal at NO_ANSWER; the remaining predicates still qualify the transport.
