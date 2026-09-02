# Acceptance policy — clean-room architecture review

    policy_generation: cleanroom-architecture-review-v1
    status: PINNED BEFORE the request was compiled and BEFORE any ruling was in view

This policy states what a ruling on the clean-room architecture package must
establish before its answer is consumed. It is pinned in advance so that no
criterion can be adjusted after an answer arrives. Its digest is sealed into the
request and compared by identity at consumption; if this file changes, the
digest changes, the ruling no longer applies, and a new request is compiled.

## 1. What the ruler is being asked to do

Rule on whether the six-document architecture package is sound enough to build
the first implementation from, given the Phase 0 evidence it rests on. The
package is design only: nothing in it has been executed except where a document
explicitly cites an executed proof.

## 2. What a consumable ruling must contain

1. **Parentage.** `in_reply_to` equal to this request's `request_id`, exactly.
2. **A unique ruling identity.** `ruling_id` unique across the ruler's lineage.
3. **Applicability.** Every field of `applies_to` copied from this request and
   equal to it by identity, including the control-configuration generation.
4. **Inspection actually performed.** `evidence_refs_inspected` naming which
   locators the ruler resolved and read. Naming fewer than all of them is the
   honest shape; naming all of them without having read them is not.
5. **Three-valued observations.** `inspection.observations` recording what the
   ruler could not observe as well as what it could.
6. **One directive from the closed set**, with its required companion field.

## 3. What this policy will NOT accept

1. **A self-authenticated provenance narrowing.** A `narrowed_from:
   could-not-observe` on any actor, independence or authority axis that cites
   only a `session_ref`, a role label, an authority string or the transport
   account. This is the canonical provenance ruling of 2026-09-02: an
   acceptance-bearing artifact must not bootstrap its own provenance from fields
   its own producer controls. The schema makes this unspellable; this policy
   states it so the refusal is not a surprise.
2. **A third option.** The offered options are the reachable answers. Rejecting
   all of them is `REJECT_ALL_WITH_CONSTRAINT`, which produces no change and
   hands the constraint back.
3. **A ruling on a subject this request did not name.** Applicability is
   identity, never ancestry and never plausibility.
4. **An edited ruling.** A changed mind is a new comment naming the prior
   `ruling_id` in `supersedes`. Two rulings that do not name each other are a
   lineage fork, which is a could-not-observe: neither is consumed.

## 4. Independence, stated in advance

Maker/checker independence on this venue is expected to be
**could-not-observe at the principal level**, because one forge account fronts
both sides of the transport. It is a **grade cap and not a blocking gate** for
this transaction: the cap cannot inflate a verdict, because the grade is
could-not-observe either way. This disposition is pinned here, before the answer
is in view, which is what makes it legitimate rather than convenient.

The forge-recorded credential path is the stronger axis and is read where it is
available. It can establish a distinct credential path. It cannot establish a
distinct principal, and this policy does not pretend otherwise.

## 5. Terminal handling

Every terminal produces a receipt, refusals included. A ruling is consumed at
most once, keyed by the consumption identity; a second consumption performs
exactly zero actions and returns the first outcome unchanged. No answer before
the request expires is recorded as `NO_ANSWER`, which is a preserved failure and
is kept apart from `INSUFFICIENT_EVIDENCE`, which is an answer.
