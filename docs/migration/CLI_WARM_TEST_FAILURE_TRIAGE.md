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

## Source inspection result (strong candidate root cause; fix not yet verified)

Inspected the exact pinned upstream files directly:

- `whatsapp-plugin/src/server/services/cli-engine.ts` at `30928c297646597fd7d52ee15ca93236bf0bd2e5`.
- `whatsapp-plugin/tests/cli-warm.test.ts` at the same revision.

The strongest candidate is a lifecycle race from a **previous warm-enabled test**, rather than the warm-disabled test starting two processes itself:

1. In `CliEngine.run()`, the `finally` block destroys the used worker and starts background replenishment via `void this.ensureWarm(model, effort)`.
2. `ensureWarm()` awaits `spawnWarm()`; `spawnWarm()` first awaits `ensureWorkspace()` before spawning the child.
3. The worker is only added to `this.booting` after `spawnWarm()` resolves. If test teardown calls `dispose()` while that await is in flight, `dispose()` cannot see/cancel that not-yet-registered operation. The async replenishment can therefore spawn after teardown.
4. The test fake process reads `process.env.FAKE_WARM_LOG` when the child starts. The next test changes that process-global variable to its own log path. A late child from the previous test can consequently write a second `start` entry into the next test's log, even though the warm-disabled engine's own `runCold()` only spawns one child.

This fits both the assertion shape (two `start` entries in a per-test log) and the source's asynchronous lifecycle. It is a source-supported hypothesis, not yet proven by an instrumented run that correlates both PIDs/log paths.

## Recommended fix and verification

1. Add lifecycle cancellation/generation state to `CliEngine`. `dispose()` should mark the engine disposed and invalidate in-flight warmup/replenishment operations; check that state after each awaited boundary and before spawning/registering a worker. Track in-flight operations from before the first await, not only after a worker is created.
2. Ensure a late `spawnWarm()` result is immediately killed if its originating generation was cancelled. Avoid changing the process-global fake logger as a workaround; optionally inject the log destination into the fake child environment for test isolation.
3. Add a regression test: start a warm-enabled request, trigger teardown while replenishment is paused at workspace setup, then prove no late child starts after `dispose()`. Keep the warm-disabled assertion at exactly one start.
4. Repeat the single test, then run the full WhatsApp plugin suite and root suite; record the exact run and commit.

## Current status and limitation

The source inspection materially narrows the likely cause, but no upstream code fix has been applied or tested. The validation workflow checks out an external source pinned to a fixed SHA; Hephaestus currently stores migration tooling and evidence rather than a writable copy of that implementation. No assertion was weakened and no production resources were touched.


## Candidate fix staged in migration validation workflow

A fail-closed patch applicator was added at `scripts/migration/apply_cli_warm_lifecycle_patch.py` and wired into `.github/workflows/goodjob-source-validation.yml`. In the CI temporary checkout only, it adds a disposed flag, prevents `ensureWarm()` from starting after disposal, and checks the flag after `ensureWorkspace()` resolves but before spawning a child. The applicator requires each source snippet to match exactly once and fails rather than patching an unexpected upstream revision.

This is a candidate fix, not yet a verified fix: the workflow must pass the patch step, build, the isolated warm test, and the full suite. The patch does not modify the upstream repository or production resources. The existing test assertion remains unchanged. A dedicated deterministic teardown-race test is still desirable even if the existing test becomes green.
