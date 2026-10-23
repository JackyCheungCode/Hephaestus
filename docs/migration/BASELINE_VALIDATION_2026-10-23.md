# GoodJob source baseline validation — 2026-10-23

## Scope

- Target repository: `JackyCheungCode/Hephaestus`
- Migration branch: `migration/goodjob-cloudflare-supabase`
- Pull request: https://github.com/JackyCheungCode/Hephaestus/pull/2
- Upstream source: `huangguojia/GoodJob`
- Pinned revision: `30928c297646597fd7d52ee15ca93236bf0bd2e5`
- Workflow run: https://github.com/JackyCheungCode/Hephaestus/actions/runs/39918669046

## Results

| Check | Result | Notes |
|---|---|---|
| Pinned source checkout | PASS | Checked out the exact pinned SHA above. |
| MySQL schema inventory script | PASS | Script completed and emitted the JSON inventory artifact. |
| Schema inventory unit tests | PASS | 2 tests passed. |
| Root dependency install | PASS | `npm ci --ignore-scripts=false` completed. npm audit reported 36 vulnerabilities (7 moderate, 25 high, 4 critical); these are untriaged findings, not a migration sign-off. |
| Standalone WhatsApp dependency install | PASS | `whatsapp-plugin/npm ci --ignore-scripts=false` completed. |
| Monorepo build | NOT VERIFIED | The build step was cancelled; do not treat this as a source build failure or a pass. |
| Full upstream test suite | FAIL | Workflow reports a test failure; see the isolated CLI warm test below. |
| Isolated WhatsApp CLI warm test | FAIL | `tests/cli-warm.test.ts:210`: expected one CLI start, observed two. The test's assertion is reproducibly failing in the isolated retry; do not alter upstream expectations just to make CI green. |
| End-to-end tests | NOT RUN | Browser/system prerequisites have not been verified. |

## Interpretation

The baseline is **not green**. Dependency installation and schema inventory are verified; build completion is not verified, and the test suite currently has a reproducible failure in the WhatsApp CLI warm test. Diagnose the duplicate process start and determine whether it is an existing upstream defect, an environment interaction, or a workflow issue before changing runtime behavior.

## Migration gates still open

- Complete the table/constraint/index/generated-column inventory and map MySQL-specific SQL/transaction semantics.
- Produce PostgreSQL migrations and apply them only to a disposable development database first.
- Test tenant/team authorization and RLS, timezone/decimal behavior, transaction and lease semantics, idempotency, retries and duplicate webhooks.
- Validate Cloudflare Worker compatibility, Queue retry/dead-letter behavior and resumable Workflows in preview only.
- Validate WhatsApp session persistence, restart/reconnect and inbound/outbound behavior on the selected runtime.
- Complete dependency vulnerability triage and license review (including the separately licensed GPL-3.0-only WhatsApp plugin).
- Do not deploy, alter production data, secrets, bindings, DNS or the existing deployment workflow without separate explicit authorization.

## Safety

This report and the validation workflow do not deploy the application or modify production resources. Existing Cloudflare Worker, D1, Supabase project, secrets and DNS remain outside this migration step.
