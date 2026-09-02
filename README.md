# firstmate-cleanroom-control

**Transport only. This repository is never canonical engineering state.**

It carries control-plane messages and an evidence mirror, and nothing else. No
decision, no design, no record and no source of truth lives here: everything
here is a copy published so that an independent party can inspect the exact
bytes a decision was made about. Deleting this repository would lose transport
history and lose nothing else.

## Browser Sol project binding

| | |
|---|---|
| Logical project | `FirstMate-Cleanroom` |
| Thread | `Cleanroom Control` |
| Protocol | `fm-sol-control/v2` |
| Control repository | `sbracewell64/firstmate-cleanroom-control` |
| Routing | `firstmate` -> `browser-sol` |

`FirstMate-Cleanroom` is routing and diagnostic metadata only. It is
never proof of a ruler's identity or authority. Authority is grounded in the
typed ruling, the exact request parentage, the forge's own venue and identity
evidence, and a fresh applicability check at the moment of consumption.

## How a decision travels

One issue per question. The issue body carries the validated request envelope,
then the reply contract generated from the schema of record, then the schema's
own digest. A ruling is exactly one comment. A receipt is exactly one comment.
Then the issue is closed. One issue, two comments, per round trip.

Every field name in every envelope comes from one authored file,
[`schema/fm-sol-control-v2.schema.json`](schema/fm-sol-control-v2.schema.json),
which is frozen: [`schema/FREEZE.json`](schema/FREEZE.json) records its digest.
The same file produces the producer's validation, the consumer's validation and
the human reply contract, so a field name has no second place to live.

## Venue isolation

This venue's consumer reads `sbracewell64/firstmate-cleanroom-control` and nothing else. Comparison is
`exact_string_equality` throughout, never substring and never prefix: `fm-sol-control/v2`
contains `fm-sol-control`, so a consumer matching on word overlap would consume
traffic from the retired venue. These are denied outright:

- repository `sbracewell64/firstmate-sol-control`
- protocol `fm-sol-control/v1`

## Control configuration generation

The protocol, repository, project and routing above have exactly one canonical
owner, held privately in the clean-room runtime home, and exactly one resolver.
Every request seals the generation it was compiled against; at consumption the
generation is freshly re-resolved and compared. A mismatch means the ruling
stays historical evidence and nothing is acted on.

Current generation: `58235a9229b99afb82a3b7b43e9cebf5d53cbe4dc63edf9f0e7c5c0cb562a336`
Normalized projection: [`control-config/control-plane.normalized.json`](control-config/control-plane.normalized.json)

## What is in here

| Path | What it is |
|---|---|
| `schema/` | the frozen schema of record, its freeze record, and the generated reply contracts |
| `control-config/` | the normalized control-configuration projection the generation digest is taken over |
| `evidence-mirror/` | byte-exact copies of documents under review, published so a ruling can cite immutable locators |

Every document in `evidence-mirror/` is a COPY. The source of truth is the
clean-room artifact tree on the operator's machine, and is named in the mirror's
own manifest.
