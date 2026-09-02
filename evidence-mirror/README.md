# Evidence mirror

**These files are copies. This directory is not a source of truth.**

Every file here is published for one reason: a control-plane request must cite
evidence at an immutable locator that any third party can fetch and hash, and
the reviewed documents live on the operator's local machine where no third
party can reach them. Publishing them here makes the review independently
inspectable. It does not make this repository their home.

- **Source of truth:** the clean-room artifact tree, path recorded per file in
  [`MANIFEST.tsv`](MANIFEST.tsv).
- **Binding:** each row of the manifest carries the sha256 of the exact bytes at
  that path in this commit. A locator here always names the object its digest
  names.
- **Never edit in place.** A corrected document is a new commit and a new
  request generation, never an amendment to a published one.

## Classes

| Class | Meaning |
|---|---|
| `byte-exact` | identical, byte for byte, to the source-of-truth file |
| `redacted-derivative` | identical except that operator-local filesystem paths are replaced, because this venue is public; the digest in the manifest is over the REDACTED bytes, and the source file's own digest is carried separately in the request |

A `redacted-derivative` is deliberately NOT byte-exact and is never presented as
though it were.

Control configuration generation at publication: `58235a9229b99afb82a3b7b43e9cebf5d53cbe4dc63edf9f0e7c5c0cb562a336`
Protocol: `fm-sol-control/v2`
