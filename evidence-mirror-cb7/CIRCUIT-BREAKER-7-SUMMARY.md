# Authority-resolver circuit breaker (round 7) — owner-level identity decision

Redacted, verifiable evidence for one bounded engineering decision under Browser Sol's
circuit-breaker condition (ruling 5548458921 §6). The narrow authority-continuation
resolver (ruling 5546939246) is parked at review round 7; the combined adversarial round
surfaced one materially-new defect whose root cause is again the programme-fact ↔
backlog-answer rebinding abstraction.

## Candidate / evidence identity
- Repo: sbracewell64/firstmate-cleanroom. Branch: fm/authority-continuation-resolver.
- Committed head: 22d9b380c133 (resolver = bin/fm-continuation-lib.sh + bin/fm-continuation-resolve.sh; typed hold binding in bin/fm-captain-hold.sh; consumers closed).
- Parked no-mistakes run: 01M1QEAGWYG2S2W9P2M21XMESX (review round 7, risk medium).
- Prior decisions (control#3): rounds 2-5 remedies + Astra A#2 + owner-map + auto-fix all applied; ruling 5548458921 PROCEED_WITH_CONDITIONS + circuit breaker.

## Round-7 defect (id=axis-covered-fact-never-materializes-then-refires-after-answer, warning)
Materialize SUPPRESSION is keyed by AXIS while retirement/answer is keyed by TASK identity.
Trace: a captain hold `foo` bound action=proof-b axis=new_paid_spend, plus a proof-b fact
{axis:new_paid_spend, decision_key:runner-b}. The hold wins the rank tie and its shared
axis drops the fact from materialize, so `runner-b` is never created and the render shows
`foo` as the gate. The captain answers `foo`. Next resolve: `foo` is closed/gone; the
fact's live-hold check and fact_answered look up only `runner-b` (which never existed), so
the fact re-fires and materialize now creates `runner-b` — the captain is asked a SECOND
time for the same action/programme/axis they just answered. The exact defect class this
repair targets, reached from typed state.

## Root cause
A fact carries TWO identities in code — its AXIS (used to decide whether an existing hold
covers it) and its TASK id (used to decide whether it was answered) — and backlog holds
carry a third (arbitrary task id + binding). Coverage and retirement key on different
ones, so they disagree. Rounds 2-7 were successive edges of this same dual-identity.

## Options for the decision (see policy)
- A (recommended): OWNER-LEVEL SIMPLIFICATION — a fact is identified ONLY by its own task
  identity (fact_task_id) EVERYWHERE (coverage, retirement, materialize). A foreign hold
  sharing the axis never stands in for a fact; each distinct fact materializes and is
  answered through its own task. Drops the axis-coverage suppression (two distinct facts on
  one axis are genuinely distinct decisions and each should own its gate). Collapses the
  dual-identity that produced the recurrence. Plus the load-time reserved-axis auto-fix.
- B: keep axis-coverage; continue edge-by-edge (not recommended — it is the recurrence source).
- C: a different bounded owner-level identity model Browser Sol prefers.

Under any option: preserve the canonical captain-hold answer/durability owner (no
fact+answer co-location — that stays in the Manager Loop study, 5547318616). No proof
evidence or control history is edited.
