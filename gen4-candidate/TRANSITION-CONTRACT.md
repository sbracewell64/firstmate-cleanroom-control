# Pre-activation generation-transition contract (gen-3 -> gen-4)

Corrected per Browser Sol's transition-contract review (control#15). The transition is an
ORDINARY frozen-gen-3 `fm-sol-control/v2` request — NOT a custom envelope kind — authored by a
quarantined one-use recovery compiler and applied by a dedicated full-applicability applier.
Adoption of generation 4 and of the 4-tuple law is PENDING Browser Sol's typed ruling; nothing
here asserts that authority.

## The activation request (ordinary gen-3 request; `bin/fsc4-activation-compiler.py`)
- `kind` = `request`; validates against the UNCHANGED gen-3 schema (root `oneOf` request/ruling/receipt).
- `work_id` = `cleanroom-gen4-activation-transition`; `question` options **A** = activate exactly this
  successor gen-4 candidate via the dedicated applier, **B** = keep generation 3, return for revision.
- `subject` = a `document_package` over the gen-4 candidate files. The member for
  `schema/fm-sol-control-v2.schema.json` binds the target gen-4 **vocabulary**; the member for
  `schema/FREEZE.json` binds the target **manifest**. `identity_line` is the sorted `sha256  path`
  manifest digest and is verified to recompute from the members.
- `evidence_refs` = the candidate files at immutable `raw.githubusercontent` locators at the exact
  candidate commit, plus the commit locator. `valid_while.subject_head_sha` = that commit;
  `valid_while.control_config_generation_digest` = the still-current source config digest.
- `valid_while.evidence_digest` = the gen-3 SCHEMA 3-tuple (`kind\tlocator\tsha256`) — the value
  Browser Sol's gen-3 processor accepts. This is the ONLY intentional correction relative to the
  broken canonical gen-3 producer (which computes the 4-tuple); the differential proof shows every
  other schema-derived identity is byte-identical.

## The recovery compiler is quarantined + effect-incapable
`fsc4-activation-compiler.py` reads candidate bytes and writes only the request JSON + a differential
proof. It changes no `control_config_generation`, applies no ruling, lands no code, and publishes to
no venue. It is one-use: it exists only to author the authority request that breaks the emitter
bootstrap.

## The applier requires FULL exact applicability (`fsc4-transition.py apply`)
Accepts ONLY a full schema-valid gen-3 ruling with `directive=ADOPT_OPTION` and `option_id=A`, and
requires exact equality on: `in_reply_to`==request_id, `correlation_id`, `vocabulary_digest`,
`control_config_generation_digest`, `applies_to.{venue,repo,work_id,work_generation,request_generation,
subject_identity_line,policy_digest,evidence_digest}`, and `single_writer_assertion==true`. It obtains
the complete non-truncated ruling universe and refuses ambiguity / lineage forks (more than one ruling
for the request). Then at the effect boundary it revalidates: source active generation still 3; source
control-config digest unchanged; target manifest + vocabulary byte-match the bound members; the whole
candidate freeze-verifies green; the subject identity recomputes from its members. Only then, ONE
atomic advance of the active generation to 4. Replay (exact target already activated) is zero-effect.

## Proven
`reds/TRANSITION-ROUNDTRIP-RESULTS.txt`: 19/19 activation-seam checks green over the REAL gen-3
request + REAL gen-3 ruling shapes, only schema-admitted immutable locators, and the exact successor
candidate commit — including every mutated-binding negative (in_reply_to, correlation, applies_to
bindings, config/vocabulary/policy/evidence mutation), duplicate rulings, truncated universe, replay,
old-config movement, target-manifest movement, 3-tuple/4-tuple both ways, and historical gen-1/2/3
freeze verification byte-unchanged.

## Bootstrap note
The canonical gen-3 producer emits the 4-tuple Browser Sol refuses, so it cannot author this request;
that is why a quarantined schema-law-honoring compiler exists. This is NOT a bypass by prose: the
output is an ordinary gen-3 request, the correction is exactly the schema-mandated digest law, and the
differential proof isolates it. Nothing activates gen-4 or moves `control_config_generation` until an
applicable typed Browser Sol ruling on this request is consumed by the applier.
