# Generation 2 evidence mirror

This tree is **additive**. It adds nothing to, and removes nothing from, the
generation 1 mirror published at commit
`ee7aa5c35655e41793b9be01ecac4eacb11ac554`. That commit is not rewritten, not
amended and not force-pushed: it carries the twenty-one sha256-pinned evidence
locators of a completed transaction, and rewriting it would invalidate every one
of them.

## Why this tree exists

Three files in the generation 1 mirror still carried an operator-local Windows
profile path (`/mnt/c/Users/<operator>/...`) after redaction, because generation
1's redaction covered `/home/<user>` and nothing else. Generation 2 declares five
operator-path classes in the schema of record and implements exactly those five,
and it pins `publication_redaction.residue_count` to a structural `0`, so a
request whose published evidence still carries such a path cannot be expressed at
all.

`phase0-redacted-v2/` therefore republishes those three files, and **only** those
three, with the corrected redaction applied. Each was produced by fetching the
exact published bytes from commit `ee7aa5c3` and running the generation 2
redactor over them, so the difference between the generation 1 copy and the copy
here is **one line per file** and that line differs only in the operator
identity. Nothing else in the generation 1 evidence package was reissued: where a
locator is still exact and current, the generation 2 request points at
`ee7aa5c3`.

## What else is here

* `commission-runtime/` -- the runtime evidence the 2026-09-02 commission itself
  produced: the measured filesystem mode semantics that forced the operational
  home onto ext4, the listener registration with its own failure reproduced as a
  control, the venue-exclusivity refusals, the migration ledger, the untouched
  pinned upstream checkout at both ends of the window, and a clean session start.
* `commission-exchange/` -- the human-readable projection of where the effort
  stands. It is a projection: where it disagrees with the evidence it cites, the
  evidence is right.
* `commission-control/` -- the generation 2 change register and the 82-arm
  watched-red result table.
* `../schema-gen2/` -- the frozen generation 2 schema of record and its three
  generated reply contracts.
* `../control-config/control-plane.normalized.gen2.json` -- the canonical
  normalized control-plane bytes whose sha256 is
  `control_config_generation.digest`.

## Redaction

Every file in this tree was passed through the generation 2 redactor and then
through its scanner, which reports an unreadable target as could-not-observe
rather than as clean. The scanner was first run against a deliberately dirty
fixture exercising all five classes and observed to go red, so a clean result
here is a discrimination and not a silent pass.

One file is a **projection rather than a copy**: `../schema-gen2/FREEZE.redacted.json`.
The frozen freeze record names the configuration owner's absolute path, which is
an operator home path. Redacting it necessarily changes its bytes, so it is
published under a different name and does **not** hash to the frozen record. The
frozen record's own binding is over the twelve artifacts it names, and each of
those digests is reproduced here unchanged; the redacted field is the freeze
record's explicitly non-binding configuration snapshot.
