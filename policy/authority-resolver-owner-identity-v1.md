# Authority-resolver owner-identity decision — acceptance policy v1

One bounded engineering decision under the circuit breaker (ruling 5548458921 §6): how a
reserved-axis fact is identified across coverage, retirement, and materialization, so an
answered captain gate is never re-manufactured. Options are total; exactly one is adopted.
No option co-locates the answer with the fact (that stays in the Manager Loop study), and
none edits proof evidence or control history.

## Option A (recommended) — single task identity
A fact is identified ONLY by its own task identity (fact_task_id) everywhere: coverage,
retirement/answer, and materialization all key on that one id. A foreign hold that merely
shares the fact's axis never suppresses the fact's materialization or stands in as its
gate; each distinct fact materializes exactly one canonical hold and is answered through
that same task. The axis-coverage suppression is removed. Rationale: two distinct facts on
one axis are genuinely distinct decisions and each must own its gate; unifying the identity
collapses the dual-identity (axis vs task) that produced review rounds 2-7.
Includes the load-time auto-fix: the decision_key identity check filters to reserved axes
(a non-reserved fact never owns a durable binding), with watched-reds proving an optional
record cannot overwrite/alias/retire a required fact's binding.
Consequence: one final combined adversarial round + fixtures, then exact-head no-mistakes
qualification and delegated landing.

## Option B — keep axis-coverage, continue edge-by-edge
Retain the axis-coverage suppression and patch the round-7 edge only (filter the
suppression by fact_task_id at that one site). Not recommended: axis-coverage is the
recurrence source; this risks a further same-abstraction edge.

## Option C — a different bounded owner-level identity model
Browser Sol specifies a different bounded identity law for coverage/retirement/materialize.

## Required watched-reds before qualification (any adopted option)
answered fact + later external/non-captain hold → no CAPTAIN re-fire, external hold intact;
live applicable captain hold for the exact unanswered fact → fact stays outstanding;
a foreign hold sharing only the axis → does NOT suppress or stand in for the fact;
materialize/retry/replay converges on one stable binding (no ping-pong);
two required facts sharing a key (same step or across steps) → load refusal;
optional key reuse cannot overwrite/alias/retire a required binding;
newer in-flight attempt without terminal disposition → no older-PROVED fallback;
positive non-vacuity: one genuinely new unanswered reserved-axis fact → CAPTAIN + exactly one canonical hold.
