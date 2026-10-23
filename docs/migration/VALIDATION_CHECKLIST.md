# Migration validation checklist

## Source baseline
- [x] Pin upstream GoodJob revision: `30928c297646597fd7d52ee15ca93236bf0bd2e5`.
- [x] Add isolated GitHub Actions workflow at `.github/workflows/goodjob-source-validation.yml`. It checks out the pinned upstream source, records toolchain versions, runs `npm ci`, `npm run build`, and `npm test`.
- [x] Run the workflow against the pinned revision. First run: root `npm ci` succeeded (638 packages added; audit reported 36 vulnerabilities: 7 moderate, 25 high, 4 critical); build failed in the separately-installed WhatsApp frontend because its dependencies were not installed by root workspaces. This exposed a workflow setup issue, not yet a confirmed upstream source defect.
- [x] Correct the workflow to install `whatsapp-plugin/package-lock.json` separately and to run tests even when the build step fails (provided both installs succeed).
- [x] Add `scripts/migration/audit_mysql_dialect.py` to produce path/line-level matches for driver imports, MySQL upserts, `INSERT IGNORE`, timestamp functions, metadata queries, row locks, JSON functions, and placeholders; add unit tests and retain its JSON output as a workflow artifact.
- [x] Disable concurrency cancellation for the validation workflow so a new documentation commit does not automatically cancel an expensive build/test run.
- [x] Confirm corrected workflow run #16: the schema inventory extractor and its two unit tests passed; root and standalone WhatsApp dependency installation is in progress.
- [x] Record workflow #16 outcome: build was cancelled, full test suite failed, and isolated `whatsapp-plugin/tests/cli-warm.test.ts` retry failed. The warm test expected one CLI start but observed two.
- [ ] Re-run validation after the dialect-audit workflow changes; confirm build, full suite, and isolated retry. Do not claim test-suite pass until it finishes.
- [ ] Record upstream license files and dependency/license report.
- [ ] Run `npm run test:e2e` separately after confirming browser/system prerequisites.
- [ ] Record all failures without masking or changing expected behavior.

## PostgreSQL
- [ ] Migrations apply to a fresh disposable PostgreSQL database.
- [ ] Every table, index, foreign key, unique constraint, check constraint and generated column has a disposition.
- [ ] Test timezone and decimal precision behavior.
- [ ] Test concurrent task claim/lease expiry, retries, idempotency and duplicate webhooks.
- [ ] Test tenant/team isolation and RLS as anonymous, authenticated, and privileged service roles.
- [ ] Test OAuth PKCE/state, encrypted credential read/write/rotation and revocation.
- [ ] Test approval freeze parameters and reconciliation of unknown external execution outcomes.
- [ ] Test import counts/checksums and repeatability.

## Cloudflare
- [ ] Worker build/compatibility check and `wrangler deploy --dry-run` in a preview-only workflow.
- [ ] Queues retry/backoff/dead-letter and duplicate-delivery tests.
- [ ] Workflow resume/retry/timeout tests.
- [ ] Cron idempotency and overlapping invocation tests.
- [ ] Verify secrets and bindings in a preview environment only.
- [ ] Validate logs, alerting, rate limits and rollback.

## WhatsApp and external integrations
- [ ] Verify the selected WhatsApp API is allowed for intended use.
- [ ] Test pairing/session persistence, process restart, reconnect and key rotation.
- [ ] Test inbound/outbound messages, delivery status, webhook verification and deduplication.
- [ ] Test provider throttling, timeout, retry and ambiguous outcome reconciliation.

## Cutover
- [ ] Backup and restore drill.
- [ ] Reconciliation report approved.
- [ ] Rollback steps rehearsed.
- [ ] Written authorization for production database, Worker, DNS, secrets and deployment changes.

## Safety boundary
The source-validation workflow does not deploy anything and does not access production secrets. The existing `deploy-hephaestus.yml` workflow remains unchanged and explicitly deploys `main`.
