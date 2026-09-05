# Generation 3 -> Generation 4 migration / compatibility rule

Generation 4 is an **unactivated candidate**. Nothing below takes effect until Browser Sol
separately dispositions activation. Generation-3 authority-bearing delivery remains
fail-closed in the meantime (control#15).

## What changes (only the evidence_digest law's ownership)
- `$defs.evidence_digest_derivation` is added: the ONE canonical law, the 4-tuple
  `kind\tlocator\tsha256\tdigest_basis`, LF-terminated, sorted, sha256.
- `$defs.valid_while` prose no longer restates a divergent inline rule; it points at the
  derivation const.
- `$defs.envelope_verifier` gains an evidence_digest recomputation check, so the law is
  verifier-covered at emit.
- The tools (`fsc4*`) resolve their schema relative to `gen4/`, so they validate against the
  gen-4 schema automatically.
- Nothing else in the protocol changes: field names, id-derivations, venue publication,
  redaction, listener, reply contracts are byte-inherited from generation 3.

## What does NOT change
- **Protocol string** stays `fm-sol-control/v2`; generations are distinguished by
  `vocabulary_digest` (gen-4 = `baa9d2d0033a51131306308d7edc477dcece5b0a8798457578a35e02626950c3`).
- **control_config_generation** does NOT move for this candidate. Activation is separate.
- Generations 1, 2, 3 stay frozen and historical. Nothing emitted under them is revalidated
  under gen-4. Freeze-verify of gen-2 (12 artifacts) and gen-3 (17 artifacts) passes
  byte-unchanged (watched-red R7).

## Compatibility rule (once activated)
- A generation is selected by the `vocabulary_digest` an envelope carries. A gen-3 envelope
  is verified only by gen-3 tooling; a gen-4 envelope only by gen-4 tooling. The gen-4
  verifier returns could-not-observe (never a pass) for an envelope of another generation.
- No cross-generation revalidation. The historical #15 REFUSED_STALE receipt stays as-is.
- On activation, the clean path for the parked owner-identity decision is a **fresh gen-4
  request** (request_generation 3, supersedes #15) carrying the 4-tuple; Browser Sol
  re-affirms the existing Option A ruling on it; the gen-4 consumer consumes it cleanly.
  #15's ruling remains the decision of record; only a consumable request was missing.
