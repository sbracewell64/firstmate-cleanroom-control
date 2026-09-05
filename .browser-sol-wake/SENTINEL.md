# Browser Sol Wake — sentinel PR (NON-AUTHORITATIVE)

This PR is a durable doorbell surface ONLY. It carries NO authority. The canonical
fm-sol-control/v2 issue is the sole authority; Browser Sol re-reads and validates it before ruling.
A GitHub Action rings this PR (a comment) when a routed control issue is opened/labeled; a ChatGPT
Work PR-activity event task watches this PR and wakes Browser Sol, who then reads the canonical issue.
Editing this PR grants nothing. control#3 accepted design (v2); implementation authorized on control#3.
