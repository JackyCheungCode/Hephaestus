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
- [x] Re-run validation after the dialect-audit workflow changes (run #25, run ID `39919928750`): root and WhatsApp dependency installs passed; schema inventory step passed; **all upstream packages built successfully**. The full suite still failed: 359 passed, 1 failed, 9 skipped (369 total). `whatsapp-plugin/tests/cli-warm.test.ts:210` expected one CLI process start but observed two; isolated retry failed identically (5 passed, 1 failed). Artifact `goodjob-validation-metadata` was uploaded (artifact ID `12486104218`). Both `migration-artifacts/mysql-schema-inventory.json` and `migration-artifacts/mysql-dialect-audit.json` were present in the downloaded artifact. Their contents were reviewed; the dialect scan was found to overcount prose/config text, so those initial counts are retained only as historical evidence, not as a migration estimate. Do not alter the upstream expectation merely to green the workflow.
- [x] Reviewed run #25 artifact. The first static scan included many irrelevant matches from documentation, URLs, and configuration files, so its raw counts are not suitable for estimating migration effort.
- [x] Refined the scanner to focus on source/SQL files and SQL-like lines, and added regression tests for irrelevant documentation/config matches. Commits: `34f258b692bdd1c61d0d8254f09d8b524b8b61a8`, `98d952d8dd0e0cba825fbcd4f35fc2e088e135d3`, `c4c5b6343a0203f6446a17024bc3f86619327e48`. Run #29 for commit `c4c5b6343a0203f6446a17024bc3f86619327e48` was cancelled before jobs were available (`conclusion: cancelled`), so it provides no validation of the refined scanner. Trigger a fresh non-deploying run and review its artifacts before using the findings.
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
