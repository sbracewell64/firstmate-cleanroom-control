# control-emission-lease (NON-MERGED transport branch)

A mechanically-exclusive single-writer emission lease for fm-sol-control/v2 terminal
ruling emission. NOT a decision store, authority store, scheduler, or programme-state
owner — a transport mutex only. A lease carries ZERO engineering authority by itself.

Every authority-capable Browser Sol execution surface MUST acquire the lease for a
request before emitting any terminal ruling for it. Acquisition is GitHub-contents CAS
(create-if-absent, or sha-guarded generation-advance takeover of an EXPIRED lease). After
acquiring, the holder MUST re-read the complete canonical issue universe immediately
before emission; if an applicable terminal ruling already exists, emit nothing and release.

Never merge this branch into main. Leases live under leases/<request_id>.json.
