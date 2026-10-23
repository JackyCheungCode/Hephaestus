# Migration validation checklist

## Source baseline
- [ ] Record upstream GoodJob commit SHA and license files.
- [ ] Record Node.js/npm versions and `npm ci` output.
- [ ] `npm run build`
- [ ] `npm test`
- [ ] `npm run test:e2e` (confirm script exists before relying on it)
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
- [ ] Worker build/compatibility check and `wrangler deploy --dry-run`.
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
