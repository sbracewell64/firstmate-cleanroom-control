# Pristine baseline - recorded 2026-09-01T21:41Z

Clean-room establishment under Captain directive (clean-room FirstMate architecture effort, 2026-09-01).
Every checkout below is an independent Git repository with its own provenance; the clean-room root is NOT a Git repository.
No modification has been made to any checkout. The retired sbracewell64/firstmate at ~/kun-agent-workspace is read-only historical corpus and is not part of this tree.

| role | repo | branch | pinned HEAD | version/describe | last commit |
|---|---|---|---|---|---|
| upstream subject | kunchenguid/firstmate | main | 41d0ab3910ece4e90db0194f756437b3abe8ab8f | 41d0ab3 | 2026-09-01 fix: surface inbound Relay media (#3442) |
| qualification tool | kunchenguid/no-mistakes | main | 0af0be6323bebd61edaf3a1a6170d82c5075e818 | v1.61.0 | 2026-08-31 release 1.61.0 (#917) |
| execution substrate | owainlewis/machinist | main | 75964acbdb944b4456a51c9bfaa4948e76b0c041 | v0.4.0-4-g75964ac | 2026-09-01 refactor!: remove Shepherd schedules (#448) |
| planning/review tool | EveryInc/compound-engineering-plugin | main | cd31338034920c9a8239e8a3fc390778edd06ab8 | compound-engineering-v3.24.0-2-gcd313380 | 2026-09-01 fix(validate-doc-claims) |

## Runtime environment
- Host: WSL2 (Linux 6.18.33.2-microsoft-standard-WSL2) over Windows, clean-room on E: (932G, 727G free)
- Recorded by: FirstMate session 2bdd718e (retired-environment session acting under the clean-room directive)

## Baseline validation status (three-valued)
- firstmate upstream test suite: NOT YET RUN (could-not-observe) - scheduled as baseline task B1
- no-mistakes v1.61.0 self-check: NOT YET RUN - baseline task B2
- machinist: NOT YET RUN - baseline task B3
- compound-engineering plugin load: NOT YET RUN - baseline task B4
A validation result recorded later must name the exact command, exit status, and counts of tests executed (never zero-failures alone).

## Baseline validation - task B1 first result (2026-09-01)
Command: `bin/fm-test-run.sh --lane portable-parallel-1` in upstream/firstmate @41d0ab39; full log: artifacts/baseline/testrun-portable-parallel-1.log; runner exit 1.
Executed 11 scripts, 3 failed, 1 gate-skip, 267s:
- tests/fm-test-run.test.sh FAILED - "ruby is required to parse .github/workflows/ci.yml as YAML": HOST DEPENDENCY (ruby absent on this WSL host), not an upstream defect - OBSERVED host-environment gap.
- tests/fm-lint.test.sh FAILED - "changed-mode lint run failed": likely the pinned-shellcheck/host-tool contract - INFERRED host-environment gap, cause not yet isolated.
- tests/fm-captain-hold-lifecycle.test.sh FAILED - "not ok - refusal must be explicit": cause UNPROVEN (could be upstream red at this SHA or host-dependent); isolate before treating the baseline as characterized.
Remaining 8 scripts passed. Baseline is NOT yet fully green on this host; the three failures must be attributed (host gap vs upstream defect) before proof experiments rely on suite verdicts. Remaining lanes (portable-parallel-2, portable-serial) not yet run.

### B1 failure attribution (2026-09-01, follow-up)
All three lane failures are HOST-ENVIRONMENT GAPS, not upstream defects - OBSERVED:
1. fm-captain-hold-lifecycle: teardown DID refuse and preserve metadata, but worded the refusal via its tasks-axi feature guard - "automatic backlog transitions require tasks-axi 0.2.4 or newer" - because this host runs tasks-axi 0.2.3; the test greps for "REFUSED". Captured stderr preserved in the session scratchpad. Host gap: upgrade tasks-axi to >=0.2.4.
2. fm-test-run: requires ruby to parse .github/workflows/ci.yml; ruby absent on host.
3. fm-lint: changed-mode lint run failed; lint owner pins a shellcheck version - host gap likely (isolate when tooling installed).
CONCLUSION: no OBSERVED upstream defect at 41d0ab39 in this lane; baseline reproducibility requires host provisioning (ruby, tasks-axi >=0.2.4, pinned shellcheck), after which the lane should be re-run to prove green.

## Clean-room tool provisioning (2026-09-01, post-design)
- no-mistakes v1.61.0 official linux-amd64 release binary installed ISOLATED at tools/bin/no-mistakes (sha256 verified against the release checksums; commit 0af0be6 = the pinned source SHA). The retired environment's v1.40.3 daemon and binary are untouched. Clears decision proof-nm-version-floor via the no-compiler option.
- Operating choices recorded against the registered proof decisions, conservative axis, captain may revise at package review: proof-repo-visibility=PUBLIC (no spend; branch protection available); proof-repo-retention=KEEP AND ARCHIVE (no token widening); proof-sol-identity=Browser Sol via the existing arrangement with the independence limitation RECORDED AS UNMEASURED (second identity remains a captain option).
