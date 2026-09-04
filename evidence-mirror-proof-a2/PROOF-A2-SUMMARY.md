# Fresh Proof A attempt-2 — qualified clean, landing held at the path fence

This is the redacted, digest-verifiable evidence for one bounded engineering decision:
whether the no-mistakes pipeline's own documentation edit belongs inside the Proof A
landing scope. Every identifier below is a public forge identity, verifiable directly.

## Subject
- Fresh candidate: `fmproof.semver.bump(version, part)` — increment a core part, reset
  lower parts, drop pre-release; out-of-scope seam = pre-release-sequence bumping /
  finalisation. Distinct from attempt-1's `compare()`.
- Immutable pre-registration sealed BEFORE the first grading observation. Seal
  `083ea1b97e24a21930efbd903d4749c3f49efe714c881221685b4507b7465716`; two pre-grading
  amendments recorded in the seal (manifest completion, then tree-sha file-mode
  convention). Candidate source/tests/intent bytes unchanged across amendments.
- Bound contract documents (exact bytes): proof-a-green-pr-design.md
  `2dc1b3f483b30d0d1507c4cbf74e5a9135faa899195014430f2596f6494aaf9d`;
  proofs-shared-contracts.md `9964415d3313c528e3ba5985dee6b8474f31d2fdc481c6f494ae35da6b422dcf`.

## World and candidate identities
- Proof repo (fresh, public, protected): `sbracewell64/fm-cleanroom-proof-a2`.
- Seed commit `4359b4c` (one commit, bootstrap exception). Branch protection:
  enforce_admins on, strict, required contexts [`test`, `PR must be raised via
  no-mistakes`], linear_history false, force-push/deletions refused, squash/rebase
  disabled, merge-commit only. Protection generation `6c6af4e1`.
- Candidate branch `fm-proof-a2/bump`; local head `6a71531`; pinned candidate tree
  `be4cb786`; base `4359b4c`.

## Qualification (clean)
- no-mistakes v1.61.0 (`0af0be6`), run `01M1PF3QDX0BCWV7BNVXSZ0369`, `outcome:
  checks-passed`, findings **none**; review/test/document/lint/push/pr all completed.
- Published head `0313d8e8` (the pipeline authored one fix commit over the candidate).
  Attestation head-bound to `0313d8e8`.
- PR #2 https://github.com/sbracewell64/fm-cleanroom-proof-a2/pull/2 — both required
  checks `success` at `0313d8e8`; full 8-condition mergeability ladder `clean`.
- All five falsifiers watched red first (red-blocked, bypass-405, stale-attestation,
  moved-head, exit-0 parser), each with distinct target==observed.

## Where it stopped (honest three-valued state)
Held at A-S11 (authorization). The merge API was **never called**. The path fence (T5)
refused because the pipeline's `document` step edited `README.md` — see
`readme-change.diff`: it appended ", and core-part bumping" to the module capability
row. That file is outside the pinned landing allowlist `{fmproof/**, tests/**}`.
attempt-2 evidence is preserved; nothing merged, no teardown, pre-registration
unchanged.

## Root cause (why a fresh candidate hits this)
The seed README already described "parsing, and version precedence comparison", so
attempt-1's `compare()` needed no README change. A genuinely fresh capability is
documented by the pipeline into README, which the strict allowlist rejects. The design's
stated fixer-fence purpose (proof-a-green-pr-design.md §9.5) is to stop a candidate
editing the POLICY that judges it (workflows, `.no-mistakes.yaml`) — already enforced by
the separate T6 predicate. Documentation is not that policy.
