# Pre-activation generation-transition contract (gen-3 -> gen-4)

Browser Sol control#15 required the smallest explicit typed contract that can authorize the
atomic gen-3 -> gen-4 control-tooling transition WITHOUT pre-activating gen-4 or bootstrapping
by prose. Implemented in `bin/fsc4-transition.py`; seam proven by
`reds/TRANSITION-ROUNDTRIP-RESULTS.txt` (10/10 green).

## The contract
A gen-3-vocabulary transition request (no gen-4 vocabulary is used before activation) with:
- `from_generation`: {generation 3, vocabulary_digest = gen-3 schema sha, control_config_digest = current}
- `to_generation`: {generation 4, vocabulary_digest = gen-4 schema sha, manifest_digest = gen-4 FREEZE sha,
  candidate_commit = the immutable control-repo commit that carries the published candidate}
- `subject_identity_line`: `generation_transition:<gen3vocab>-><gen4vocab>@<manifest>`
- `evidence_refs`: the published gen-4 candidate files; `evidence_digest` computed under the gen-3
  SCHEMA law (the 3-tuple the gen-3 schema declares — the value Browser Sol's gen-3 processor
  accepts, as it did for #15), NOT the gen-3 producer's 4-tuple.
- **effect**: on an applicable Browser Sol ruling ONLY, atomically advance the active generation
  to 4 by writing a digest-bound activation record; no other effect.

## Who validates / who applies
- **Validates**: Browser Sol (rules on the transition request, gen-3 law).
- **Applies**: the dedicated applier in `fsc4-transition.py apply` — NOT the deadlocked gen-3
  consumer. It re-checks the effect boundary and writes the activation record atomically.

## Effect-boundary revalidation (apply time; any failure refuses, zero effect)
- ruling `applies_to.subject_identity_line` equals the exact transition subject (else REFUSED_MISMATCH);
- replay: an activation record for this exact target already exists -> REPLAY_NOOP, zero effects;
- the current active generation is still 3 (else REFUSED_STALE: old-config moved);
- the target gen-4 manifest still verifies byte-for-byte (else REFUSED_STALE: target-manifest moved);
- evidence set still digests to `valid_while.evidence_digest` under the declared gen-3 law.

## THE OBSERVED BOOTSTRAP DEFECT (why step 5 holds rather than emits)
The canonical gen-3 tooling cannot emit a Browser-Sol-acceptable activation request:
1. A standard gen-3 `request` emitted by the canonical producer (`fsc3-emit-request.py`) carries the
   4-tuple evidence_digest, which Browser Sol's gen-3 processor refuses. The canonical producer is
   itself the broken component — it cannot author the request that would fix it.
2. Representing the transition as a distinct envelope kind (`generation_transition_request`) is not
   defined in the frozen gen-3 schema, so the gen-3 validator/processor does not know it — using it
   is effectively introducing gen-4 semantics before activation.

So a real activation request cannot be emitted without either a bespoke non-canonical builder (a
bypass) or pre-activating gen-4 — both of which Browser Sol forbade. Per control#15 step 5, this is
reported as an observed bootstrap defect and the system is KEPT HELD. This contract + its green seam
round trip are the proposed resolution, offered for Browser Sol's disposition: if Browser Sol adopts
the transition contract (its dedicated builder honors the gen-3 schema law; its applier revalidates
the effect boundary), the activation request may then be emitted and ruled under that sanctioned
mechanism, and only a consumed applicable ruling advances `control_config_generation`.

Nothing here activates gen-4, moves `control_config_generation`, or modifies gen-1/2/3.
