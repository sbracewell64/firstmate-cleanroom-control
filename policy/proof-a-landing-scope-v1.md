# Proof A landing-scope decision — acceptance policy v1

One bounded engineering question, three total options. This policy fixes the exact scope
of each option and the consequence of adopting it, so a ruling binds to a known effect.
It does not weaken any test, validator, no-mistakes, maker/checker, exact-head,
provenance, immutable-proof, or landing-authority requirement.

## The question
The fresh Proof A attempt-2 candidate qualified clean, but the no-mistakes `document`
step edited `README.md` (documenting the new capability). The pinned Proof A landing
path-fence (predicate T5) requires the published diff to be a subset of
`{fmproof/**, tests/**}`, so it refused the landing. Should the pipeline's own
documentation edit be inside the Proof A landing scope?

## Options (total; exactly one is adopted)

### Option A — include README.md in the landing allowlist
- Scope of the revision: the path allowlist becomes `{fmproof/**, tests/**, README.md}`.
  The separate fixer-fence predicate (T6) is UNCHANGED and still refuses any edit to a
  workflow, `.no-mistakes.yaml`, a dependency manifest, or anything under `.github/`.
  Rationale: documentation is not the acceptance policy the fixer-fence protects.
- Consequence, stated explicitly: this changes a value bound in the immutable Proof A
  pre-registration, so it CANNOT be applied to attempt-2. It requires a FRESH proof
  generation — a new pre-registration sealed before grading, on a fresh proof repo
  (`fm-cleanroom-proof-a3`), re-running every stage from bootstrap through the real
  expected-head protected merge to PROVED. attempt-2 is preserved as adverse evidence.

### Option B — keep the strict allowlist; record attempt-2 as REFUSED
- Scope: no contract change. attempt-2's disposition is written `REFUSED_AT_A-S11`
  (the fence demonstrably fired), the repo is archived as evidence, and Proof A stops
  without ever demonstrating the green protected landing.

### Option C — keep the strict allowlist; re-run with a README-neutral candidate
- Scope: no contract change. A fresh candidate whose capability the seed README already
  describes (e.g. version precedence comparison in a form distinct from attempt-1) is
  chosen so the document step stays out of README, on a fresh proof repo, re-run to
  PROVED. Risk: the document step's behaviour is not fully predictable, so a README edit
  cannot be guaranteed absent.

## Recommendation
Option A. It is faithful to the design's stated fixer-fence purpose (policy files,
enforced by T6), it lets Proof A demonstrate its actual goal (the green protected
landing), and its cost — a fresh proof generation — is honest and bounded.
