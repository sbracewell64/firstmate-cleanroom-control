# One bounded synthetic round-trip plan (offline, for Browser Sol disposition)

Purpose: prove, on activation, that the gen-4 evidence_digest law consumes cleanly where
gen-3 dead-locked — WITHOUT touching the live control repo, gen-1/2/3, or any historical
transaction. This plan is described here and NOT executed; it is bounded, offline, and
uses the fake-forge fixture (`reds/fixture-fake-gh.sh`), never GitHub.

## Preconditions
- Browser Sol has dispositioned gen-4 activation.
- `bash bin/fsc4-verify-freeze.sh` is green (17 artifacts) and gen-2/gen-3 freeze-verify green.
- Run entirely under a scratch dir; write no state under gen4/state or the live control repo.

## Steps
1. **Emit (synthetic).** Compile a gen-4 request over the existing published evidence bundle
   (mirror commit `4828d023`, same owner-identity decision), through the gen-4 producer. The
   producer computes `valid_while.evidence_digest` via the ONE canonical owner (4-tuple).
   Assert: `fsc4-verify-envelope.py file request <req>` is observed-good on ALL checks,
   INCLUDING the new "valid_while.evidence_digest recomputes from evidence_refs" check. This
   is the emit-time gate gen-3 lacked.
2. **Rule (synthetic).** Construct a gen-4 ruling fixture that copies the request's 4-tuple
   `evidence_digest` into `applies_to`, `single_writer_assertion=true`, Option A. (In the
   live flow Browser Sol authors this; offline it is a fixture the fake-forge serves.)
3. **Consume.** Run `fsc4-consume.py <req> <receipt>` against the fake-forge ruling universe.
   Assert outcome `CONSUMED`, `actions_performed>=1`: L3 (`fsc4.evidence_digest == valid_while`)
   and V10 (`applies_to.evidence_digest == valid_while.evidence_digest`) both pass because
   all three are the 4-tuple. This is the exact step that returned REFUSED_STALE under gen-3.
4. **Replay.** Re-run consume; assert the exclusive-create claim refuses a second consumption
   (no duplicate receipt), per `$defs.receipt.consumption_identity.claim_mechanism`.
5. **Negative controls (both directions).** (a) Hand-edit the request's carried digest to the
   3-tuple; assert emit-time verifier folds observed-bad AND consume folds REFUSED_STALE.
   (b) Mutate one ref's `digest_basis` only; assert `evidence_digest` moves and both gates
   fail closed. These mirror watched-reds R1/R2/R3/R4 end-to-end.
6. **Immutability.** After all steps, `fsc2-verify-freeze.sh`, `fsc3-verify-freeze.sh`, and
   `fsc4-verify-freeze.sh` all return exit 0 (nothing drifted).

## Expected result
Every step green: the gen-4 law consumes cleanly where gen-3 dead-locked, both mismatch
directions fail closed at emit and at consume, replay is refused, and no historical
generation was modified. Only then is a real (non-synthetic) fresh gen-4 request emitted to
the live venue for the parked owner-identity decision.
