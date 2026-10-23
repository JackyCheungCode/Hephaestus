# CLI warm-pool test failure triage

## Latest reproducible failure

Run #74: https://github.com/JackyCheungCode/Hephaestus/actions/runs/39924298660
Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

The complete test suite reports 359 passed, 1 failed, and 9 skipped. The failing test is:

- File: `whatsapp-plugin/tests/cli-warm.test.ts`
- Case: `常驻预热池 > warm 关闭时走老路径：参数里没有 --input-format，行为与之前完全一致`
- Assertion: line 210 expects exactly one `start` event, but observes two.
- Isolated rerun in the same CI job reproduces the same failure (5 passed, 1 failed).

The failure is specifically in the warm-disabled legacy path: the test expects one CLI process start and verifies that the start does not use `--input-format`. Do not change the assertion to accept two starts; that would weaken the behavioral contract.

## Investigation plan

1. Inspect `whatsapp-plugin/src/server/services/cli-engine.ts` around `run()`, `ensureWarm()`, worker disposal, and any post-request replenishment. Trace whether a warm/replenishment process is spawned even when warm mode is disabled, or whether a delayed asynchronous spawn races with the test's process log.
2. Inspect test setup/teardown and the fake process logger. Determine whether the second start is a real extra child process, a delayed event written into a reused log, or both.
3. Add a regression test that proves warm-disabled mode creates exactly one process and does not start replenishment. If an async warm operation can outlive disposal, add cancellation/generation protection at the lifecycle owner rather than sleeping in the test.
4. Run the single test repeatedly, then the full WhatsApp plugin test suite and full root suite. Record exact commands, counts, and commit SHA.

## Current status and limitation

The validation workflow checks out the upstream source at a fixed external SHA; Hephaestus currently stores migration tooling and evidence rather than a writable copy of that upstream implementation. The diagnosis above is a test-backed investigation plan, not a verified root cause or a claimed source fix. No assertion was weakened, no upstream source was modified by this triage, and no production resources were touched.
