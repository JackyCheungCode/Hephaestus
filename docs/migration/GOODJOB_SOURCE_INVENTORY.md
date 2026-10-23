# GoodJob source inventory — schema and runtime

The schema measurements below were re-run against upstream `huangguojia/GoodJob` at pinned revision `30928c297646597fd7d52ee15ca93236bf0bd2e5` on 2026-10-23. The schema file blob SHA is `e833e94fcdcd765d930d6439d66302374b3ebe18`. Counts are lexical inventory aids, not a normalized DDL model.

## Schema measurements

The fetched `backend/schema.mysql.sql` is 121,675 characters and declares:

| Construct | Count |
|---|---:|
| `CREATE TABLE` | 132 |
| Lines beginning with `KEY` / `INDEX` / `UNIQUE KEY` | 217 |
| Foreign-key declarations | 109 |
| Check constraints | 99 |
| Lines mentioning `GENERATED ALWAYS` or `STORED` | 13 |
| JSON column/type references | 76 |
| `DATETIME(3)` occurrences | 178 |

The schema is not a safe one-shot find-and-replace conversion. It includes many tenant/team-scoped CRM, prospecting, integration and operational records, generated tenant columns, and substantial relational integrity. The file has 3,260 lines and 132 table starts. Counts are produced by simple regex/line matching: the 217 index lines and 13 generated/STORED lines are not guaranteed to equal semantic index/column counts. A normalized DDL parser/model is still required before generating PostgreSQL DDL.

## Runtime/package evidence

- Root `package.json` defines workspaces for `backend`, `frontend`, `integration-worker`, `integration-sdk`, and `goodjob-runner`; the WhatsApp plugin is invoked separately by root scripts.
- Root `build` compiles SDK, backend, frontend, integration worker, local runner and WhatsApp plugin. Root `test` runs each package's tests, and `test:e2e` delegates to the frontend workspace.
- Backend package has a MySQL-specific migration command (`db:migrate:mysql`), MySQL worker startup and a MySQL test suite. The schema file is therefore only one part of the migration; application query/repository code and test fixtures must also be ported.
- Integration worker pins BullMQ and mysql2. Queue processing must be moved with retry/concurrency/idempotency semantics, not just swapped to a new queue API.
- WhatsApp package declares GPL-3.0-only and depends on Baileys 7.0.0-rc13, Express 5, Socket.IO 4, mysql2, pg and PGlite. Its README describes PGlite for local use and MySQL 8 shared with the GoodJob CRM in production. This is a real database/runtime boundary to resolve, not merely a frontend integration.
- Target Hephaestus has `wrangler.toml` for Worker `hephaestus`, `cloudflare/worker.js` entrypoint and D1 binding `DB`. The existing GitHub Actions deployment workflow explicitly deploys from `main`; do not change it to deploy this migration branch.

## Additional code-level findings (important for implementation order)

- The upstream source revision used by the isolated CI workflow is `30928c297646597fd7d52ee15ca93236bf0bd2e5`; the workflow checks out this exact SHA and runs `npm ci`, `npm run build`, and `npm test`. The workflow has been committed but its run result must be checked separately; no pass is claimed yet.
- `backend/src/prospect-bullmq-backend.ts` defines the prospect execution queue `goodjob-prospect-execution-v1` and dead-letter queue `goodjob-prospect-dead-letter-v1`, validates Redis URLs and configures retry/connection behavior. Queue migration must preserve both normal and dead-letter behavior.
- `integration-worker/src/queue.ts` defines separate control, tool-call and event workers, including OAuth prepare/complete, credential refresh/revoke, webhook sync, health checks, disconnect/terminate, and webhook-event processing. A single generic queue would risk losing operation-specific concurrency/retry semantics.
- The README explicitly documents a **single-backend-instance production constraint**: some candidate-cleaning, global provider rate-limit and worker-lifecycle paths are not yet cross-process atomic. The migration must not scale API/worker replicas horizontally until these paths are redesigned and race-tested.
- WhatsApp `src/server/db/database.ts` already contains a database abstraction for PGlite, PostgreSQL (`pg`) and MySQL (`mysql2`), plus transaction wrappers. That makes a PostgreSQL path plausible, but the production README still documents MySQL 8 as the shared CRM database. Existing SQL compatibility, migrations, query parameter conventions, auth/session encryption and transaction semantics still need a full audit before switching production.
- WhatsApp production documentation says its database/session master key must be backed up together and requires a fixed `SESSION_MASTER_KEY`; it describes the plugin as single-tenant, single-instance and privately deployed behind the CRM auth gateway. These constraints must remain explicit until a tested replacement design exists.

## PostgreSQL port decisions required before writing migrations

1. **Identity/auth:** GoodJob `users` currently stores email/password hash, role, team_id and auth_version. Decide whether existing authentication remains app-managed initially or is migrated to Supabase Auth. A naïve Auth swap could break password/session semantics and integrations.
2. **Tenant isolation:** map team_id, owner_id, tenant_id and cross-team relationships; define RLS policies from actual authorization code. Do not use a generic “authenticated users can read/write” policy.
3. **Generated tenant columns:** 8 stored generated columns need expression-by-expression review and PostgreSQL equivalents; avoid duplicating team_id if uniqueness or query behavior depends on the generated column.
4. **Timestamps:** 178 DATETIME(3) occurrences need explicit timezone policy and tests. Preserve millisecond precision where behavior depends on it.
5. **JSON:** 76 JSON references need jsonb decisions, validation/indexes and compatibility tests for query operators.
6. **Referential integrity:** translate 109 foreign-key declarations and 99 CHECK declarations; verify constraint names and delete/update behavior.
7. **Indexing:** normalize 219 index/key declarations and compare with query access patterns; don't blindly carry over MySQL collation/index assumptions.
8. **Concurrency:** inspect task claim, lease, approval, webhook and reconciliation code for transaction/locking assumptions. Test race behavior under PostgreSQL.
9. **Secret handling:** SMTP/IMAP credentials and external provider tokens need a clear encryption/key-rotation strategy. Do not copy plaintext values into browser-accessible tables or commit secrets.
10. **WhatsApp:** keep an isolated bridge/runtime until Baileys session persistence, long-lived connections, crypto compatibility and terms are validated. Cloudflare Workers may host webhook/API components without necessarily hosting the entire socket/session engine.

## Next implementation artifacts

- [x] Pin upstream GoodJob commit SHA and add a non-deploying validation workflow (execution result still pending).
- [ ] Build a normalized schema inventory (table/column/type/nullability/default/PK/unique/FK/check/index/generated expression).
- [ ] Inspect backend repository/store code and every direct SQL dialect assumption.
- [ ] Create versioned Supabase migrations only after schema inventory is complete.
- [ ] Add disposable PostgreSQL tests, including tenant/RLS and concurrency cases.
- [ ] Add Cloudflare adapter and queue/workflow consumers behind preview-only configuration.
- [ ] Keep WhatsApp deployment separate until compatibility tests pass.

## Safety

No production schema/data has been changed. No Cloudflare Worker, D1 binding, secret, DNS or deployment workflow has been changed. This document is an inventory, not a claim that a PostgreSQL port or build has passed.
