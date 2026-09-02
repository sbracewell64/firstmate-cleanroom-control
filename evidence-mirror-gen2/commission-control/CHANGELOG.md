# fm-sol-control/v2 - SCHEMA GENERATION 2

The protocol string is **unchanged**. A generation is distinguished by
`vocabulary_digest`, which every envelope already carries, so no third party has to
learn a second protocol name and the venue-isolation law's exact-equality
comparisons keep working.

| | |
|---|---|
| Generation 1 schema | `23e828b27d5c8d44e7c23ac67ddfe74ab3ba71783726f5e67304dd7c58fafbd3` |
| **Generation 2 schema** | **`bbe6ce89744ef03901cd5823a75670db86293bdc1f55bff4f4095b0ced446908`** |
| Frozen at | 2026-09-02T21:40:14Z |
| Frozen artifacts | 12 |
| Control config at freeze | `912f6238d94dfdf8afd672bc7f28a445b66138c14a5a08fa266a77837346c2aa` |
| Watched-red arms | 82, all observed-good |

Generation 1 stays frozen, published and untouched. The completed NO_ANSWER
transaction on issue #1 was emitted under it and is never revalidated under
generation 2.

## Changes

### G2-0 - lineage

generation 2 declared, generation 1 digest recorded in $defs.schema_generation

### G2-1 - observer 4.3 / recommendation 1

receipt.consumption_identity (and applied, replay_check) conditional on outcome == CONSUMED; forbidden for every other outcome

### G2-2 - observer tooling constraint / recommendation 7; captain directives 4 and 5

$defs.read_mechanism and $defs.authoritative_read added; observation.read added with two structural laws forcing could-not-observe on a truncated or truncating read; receipt outcome CNO_TRUNCATED_RESPONSE added

### G2-3 - observer 4.5 / recommendation 4

$defs.digest_basis added with per-kind laws; evidence_ref.digest_basis optional and law-bound; request.evidence_refs items require it via $defs.evidence_ref_declared

### G2-4 - observer 4.6 / recommendation 5

request.routing_labels required, resolved from the canonical config, with the atomic-creation law

### G2-5 - observer 4.4 / captain directive 2

$defs.redaction_class and $defs.redaction_policy added covering POSIX, WSL-Windows, native Windows, macOS and UNC user-profile paths; request.publication_redaction required with residue_count structurally pinned to 0

### G2-6 - captain directive 6

control_config.listener required (id, record_path, check_script_path, all FM_HOME-relative)

## Frozen artifacts

| Artifact | sha256 | bytes |
|---|---|---|
| `bin/fsc2-consume.py` | `02aad67e80679626f91597d2aa348a4e2c41282a2af2ffe66b3d31a5695c2851` | 26693 |
| `bin/fsc2-emit-request.py` | `4883f0bcbcf5a83ed7c40a6c1dd6194db6632c89f75c2afa86566f1ae50a4e08` | 6068 |
| `bin/fsc2-listener.py` | `261994f1ec6c393b7b19228a352fd180c1500d542b67749bf7df6cebd3a91bfd` | 9756 |
| `bin/fsc2-redact.py` | `373aa3537521467475a6de763a10905bb3e4fa4b8d8e791279e58a6b9e5c7cf5` | 6249 |
| `bin/fsc2.py` | `09fc2d0f8dfbf0717ecbf0352507f5a8ffc14d0bc3498aa8906d60db496f0642` | 11533 |
| `schema/reply-contract.receipt.txt` | `cc77349afec84ad321aa7ee212eef5043e0d7bd79cf802fef941f2d3a30402af` | 4466 |
| `schema/reply-contract.request.txt` | `23455c198d9cbd1f2dffc7a4db86b262befdb69d256de224e5fc4ead3bdc4402` | 10347 |
| `schema/reply-contract.ruling.txt` | `6fec16aba4cdb96c3ec63085165bee34c7bc1142445f0bad4a6ceb6147112671` | 6285 |
| `bin/fsc2_config.py` | `f12a623d61e72aaf0d5e264c08006a8454bba64011e59e44a79d4fd1cdcdc918` | 8613 |
| `schema/fm-sol-control-v2.schema.json` | `bbe6ce89744ef03901cd5823a75670db86293bdc1f55bff4f4095b0ced446908` | 60409 |
| `bin/build-gen2-schema.py` | `62dfb6d7dfe8fef0359154dd185a9552e8de4cdc74a957e226f81e345ee87d19` | 21227 |
| `reds/watched-reds.py` | `00a100d92d996ebc72c392fde627ee238e9a3eec614a72780270eae64da18bc5` | 26047 |

Verify with `bin/fsc2-verify-freeze.sh`: exit 0 unchanged, 6 drifted, 4 could-not-observe.
Enforcement is digest comparison only - detective, not preventive - because this tree
is on a mount that carries no file modes.
