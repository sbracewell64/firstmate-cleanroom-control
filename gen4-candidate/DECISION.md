# Generation-4 evidence_digest law: 3-tuple vs 4-tuple decision

Browser Sol (control#15) required the choice be made deliberately and schema-visible,
not by implementation accident. This records both options and the adopted one. Browser
Sol dispositions the final choice; the watched-reds prove **both** directions of mismatch
regardless of the default.

## The two options

### Option 3T — three-tuple `kind\tlocator\tsha256`
- Matches the generation-3 schema *text* (`$defs.valid_while` prose) and Browser Sol's
  queue-processor recomputation.
- **Regresses observer finding 4.5:** a single evidence ref could silently change its
  `digest_basis` from `fetched_bytes` (a real independent byte digest) to
  `locator_identity` (a digest of the locator's own identity string, which adds no
  independent binding) **without moving** `evidence_digest`. The ruler would have been
  shown a materially weaker kind of binding under an unchanged aggregate.

### Option 4T — four-tuple `kind\tlocator\tsha256\tdigest_basis`  (RECOMMENDED)
- Matches the generation-3 *code* (`fsc3.evidence_digest`, used at emit and at consume L3).
- **Binds `digest_basis` into the aggregate**, closing observer 4.5: any change to a ref's
  basis moves `evidence_digest` (watched-red R2 proves this).
- Requires `digest_basis` to be **schema-visible and load-bearing** — which generation 4
  makes explicit in `$defs.evidence_digest_derivation`, rather than leaving it hidden in
  code as generation 3 did.

## Why 4T is recommended (Browser Sol dispositions)

The generation-3 defect was **not** that the 4-tuple was wrong; it was that the 4-tuple
lived only in code while the schema text still declared the 3-tuple, and `evidence_digest`
was not verifier-covered, so the disagreement was invisible at emit and only surfaced at
consume (REFUSED_STALE on #15). The 4-tuple is the *stronger* law (it preserves the
observer-4.5 binding); the 3-tuple would throw that protection away to match stale prose.

Generation 4 therefore adopts 4T and removes the ambiguity at the source: `evidence_digest`
is ONE declared canonical law (`$defs.evidence_digest_derivation`) that the producer, the
as-fetched envelope verifier, the applicability recomputation, the consumer staleness
ladder (L3), and the receipt path all read from and nothing else. A producer/schema
disagreement now fails closed at **emit** (verifier coverage, watched-red R3) as well as at
consume.

## If Browser Sol prefers 3T instead

Re-run `build-gen4-schema.py` with the derivation const's `tuple` set to 3 and `row` to
`kind\tlocator\tsha256`, and set `digest_basis_load_bearing` false. The single-owner
property and verifier coverage are unchanged; only the adopted default moves. This is a
one-line change precisely because the law now has one owner. Adopting 3T would knowingly
regress observer 4.5, which is why it is not the recommended default.
