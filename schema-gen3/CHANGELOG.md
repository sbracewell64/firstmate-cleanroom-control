# fm-sol-control/v2 - SCHEMA GENERATION 3

The protocol string is **unchanged**. A generation is distinguished by
`vocabulary_digest`, exactly as generation 2 was distinguished from generation 1.

Ruled by Browser Sol on control issue #3 (`tooling_supersession: PROCEED_WITH_CONDITIONS`,
authority `BROWSER_SOL_NOT_CAPTAIN`): "cut a new frozen control tooling/schema generation
before the next authority-bearing transaction; call it generation 3 rather than 2.1 because
schema-visible semantics and identity derivation change; keep the wire protocol name."

| | |
|---|---|
| Generation 2 schema | `bbe6ce89744ef03901cd5823a75670db86293bdc1f55bff4f4095b0ced446908` |
| **Generation 3 schema** | **`43c1faa9ff8485ac7392b363a4d83729cd84ae4c1ab1a606e128ca20781342a8`** |
| Control config at freeze | `912f6238d94dfdf8afd672bc7f28a445b66138c14a5a08fa266a77837346c2aa` (UNCHANGED by this generation) |
| Watched-red arms | 129, all observed-good (`reds/watched-reds.log`, `reds/watched-reds.tsv`) |

Generations 1 and 2 stay frozen, published and untouched (required repair 7). Nothing
emitted under them is revalidated here.

## Required repairs, each mapped to its change and its red

| # | Ruling text | Change | Red |
|---|---|---|---|
| 0 | published request must validate as fetched; one structural representation | G3-1 `question.body_rendered` removed, `question.body_markdown` required, `$defs.venue_publication` pins `issue_body == render(envelope)`; emitter renders through it | RB12 |
| 1 | frozen emitter performs the single atomic issue+labels creation without a bridge | `fsc3-emit-request.py`: title, labels and body are fields of ONE JSON POST body (no `-f` query fields); post-condition also checks `body == render(envelope)` | RB5, RB16 |
| 2 | outcome in `receipt_id` derivation | G3-2 `$defs.id_derivation.receipt_id.inputs` += `outcome` | RB13 |
| 3 | preserve truncating-read uncertainty as `CNO_TRUNCATED_RESPONSE`; never fold to `NO_ANSWER` | G3-4 receipt law (any truncated/truncating read forces the outcome); consumer fold order TRUNCATED > FAIL > CNO > PASS | RB8, RB11, RB15 |
| 4 | atomic first-consumption claim on ext4, exclusive create | G3-3 `consumption_identity.claim_mechanism` const `exclusive_create`; consumer claims with `O_CREAT|O_EXCL` | RB4, RB14 (8-way race: one winner) |
| 5 | declared verifier for envelope-against-frozen-schema | `bin/fsc3-verify-envelope.py` (`issue`, `comment`, `file`, `render-check`), declared in `$defs.envelope_verifier` | RB12 |
| 6 | preserve generation-1 and generation-2 frozen bytes | never edited; `gen2/bin/fsc2-verify-freeze.sh` still exit 0 | - |

## Unattended monitoring (`unattended_monitoring: REQUIRED_FOLLOW_ON`)

G3-5 `$defs.inbound_item`; `bin/fsc3-listener.py` now generates, from the same canonical
owner and without changing it, an inbound `process-event-adapter/1` extension
(`listener/`, id `org.firstmate.cleanroom.control-listener`, adapter and source id
`<listener.id>-inbound`) bound through upstream's supported trusted-extension seam. A
registered source is what upstream's supervision predicate counts, so the Stop-owned
auto-arm keeps a watcher alive for an empty fleet and every fresh qualified Browser Sol
request or ruling is surfaced exactly once (RB17: fresh-once, idempotent replay, no
re-announce, FirstMate-authored filter, loud could-not-observe, retired-venue denial).

## Frozen artifacts

See `schema/FREEZE.json`; verify with `bin/fsc3-verify-freeze.sh` (exit 0 unchanged,
6 drifted, 4 could-not-observe). Enforcement remains digest comparison only on this mount.
