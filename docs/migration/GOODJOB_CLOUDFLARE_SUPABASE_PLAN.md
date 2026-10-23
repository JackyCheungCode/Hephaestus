# GoodJob → Cloudflare + Supabase migration

Status: **Phase 0 — isolated migration branch; no production resources changed.**

- Source: https://github.com/huangguojia/GoodJob (master)
- Target: https://github.com/JackyCheungCode/Hephaestus
- Target branch: `migration/goodjob-cloudflare-supabase`
- Existing Supabase project: `Hephaestus` (`fhvixzgvebyojdvymijl`, region `ap-northeast-1`)
- Existing Cloudflare application: Hephaestus. Preserve current Worker, bindings, secrets, routes and deployment until a reviewed cutover.

## Safety boundary

This branch contains migration documentation only. Do not run production DDL, import data, rotate secrets, overwrite the current Worker, change DNS, or replace the existing deployment workflow as part of early migration work. All schema development should first run against a disposable local PostgreSQL database or a separately approved Supabase development branch/project.

## Findings verified from source manifests/schema

- GoodJob root npm workspace scripts build/test the connector SDK, backend, frontend, integration worker, local runner and WhatsApp plugin.
- The backend schema is a large MySQL schema (`backend/schema.mysql.sql`) with tenant/team-scoped CRM data, prospecting, approvals, audit records, JSON fields, generated columns, indexes, constraints and MySQL-specific syntax.
- Root package declares Apache-2.0; WhatsApp plugin has a separate GPL-3.0-only licensing concern. Preserve all source notices and complete a distribution/licensing review before shipping a closed-source combined product.
- Current Hephaestus repo is a Next.js/Prisma application with a Cloudflare Worker and D1 configuration. Its application stack is not yet the same as GoodJob's Vite/Node workspace. Do not assume the existing Worker can run the whole monorepo without an adapter/refactor.
- The connected Supabase Hephaestus project is active, but inspection returned no tables in `public` and no recorded migrations. This is not permission to assume the database is unused; check all schemas and connected services before any production schema changes.

## Target architecture

1. **Frontend:** GoodJob frontend hosted on Cloudflare Pages (or Workers static assets after compatibility validation).
2. **Request API:** split Express/server-only backend modules into Cloudflare Workers-compatible handlers. Keep domain logic independent from HTTP/runtime APIs.
3. **System of record:** Supabase PostgreSQL. Use Supabase Auth only after mapping GoodJob's existing user/team/role/auth-version semantics; do not blindly replace application authorization with `auth.uid()`.
4. **Durable jobs:** Cloudflare Queues for dispatch/retries and Workflows for multi-step, resumable jobs. Keep task state, lease state, idempotency keys, approvals and reconciliation records in PostgreSQL; queue delivery alone is not the source of truth.
5. **Scheduled jobs:** Cron Triggers for bounded schedules; Queues/Workflows for long-running or retryable work. Do not use `waitUntil` as the durable job system.
6. **Files/assets:** Supabase Storage or R2 after identifying access controls, signed URL needs, retention and current asset URL assumptions.
7. **External integrations:** isolate provider adapters and OAuth token lifecycle. Keep secrets encrypted at rest, validate OAuth state/PKCE and webhook signatures, enforce host allowlists, deduplicate webhooks and require explicit approvals for side-effecting acquisition actions.
8. **WhatsApp:** keep as a separate compatibility workstream. Baileys/WhatsApp Web depends on persistent auth/session state and long-lived socket behavior. Verify runtime and provider terms before choosing Workers; if incompatible, use the official WhatsApp Business Platform or a small separately hosted bridge, documenting feature differences. Do not promise full compatibility before a reconnect/session/send/receive test suite passes.

## File-level implementation sequence

### A. Baseline and inventory
- `package.json`, all workspace `package.json`: record Node engine, scripts, dependency versions and deployable entrypoints.
- `backend/schema.mysql.sql`: parse all tables, indexes, constraints, generated columns, JSON columns, triggers and MySQL-specific expressions into a migration inventory.
- `backend/src/**`: locate SQL calls, transaction boundaries, `FOR UPDATE`, advisory/lease logic, `ON DUPLICATE KEY`, `INSERT IGNORE`, date handling and connection-pool assumptions.
- `integration-worker/src/**`, `goodjob-runner/**`: enumerate BullMQ/Redis usage, retry semantics, leases, queue names and side effects.
- `whatsapp-plugin/**`: map Baileys, Socket.IO, session persistence, crypto key handling and plugin license/dependencies.
- `frontend/**`: identify API base URL, auth/session storage, uploads, streaming/WebSocket calls and build output.
- `deploy/**`, `scripts/**`, `.github/workflows/**`, `.env.example`: separate local Docker/MySQL deployment from Cloudflare deployment and identify every secret/binding.

### B. PostgreSQL port
- Create ordered, versioned SQL migrations only after the complete schema inventory.
- Convert MySQL types/DDL deliberately: `DATETIME(3)` → chosen `timestamptz` policy; `JSON` → `jsonb`; `AUTO_INCREMENT` → identity/sequence; `ON DUPLICATE KEY UPDATE` → `ON CONFLICT`; generated columns and collations require explicit review.
- Preserve primary/unique constraints, tenant scoping, foreign keys, check constraints and query-critical indexes.
- Audit every exposed table for RLS. Avoid generic policies: encode actual team/tenant membership and role permissions. Keep privileged integration secrets out of browser-visible tables.
- Implement data migration as a repeatable, resumable process with row counts, checksums, rejected-row logs and a rollback/restore plan. Do not dual-write until idempotency and reconciliation are tested.

### C. Workers and integrations
- Replace direct Express server startup with runtime-neutral route handlers plus a Workers adapter.
- Replace BullMQ/Redis workers with queue consumers/workflows only after documenting ordering, retries, concurrency, dead-letter handling and idempotency.
- Preserve external API rate limits, OAuth refresh behavior, webhook verification, approval freeze parameters and unknown-outcome reconciliation.
- Store large blobs in object storage; keep metadata and authorization in PostgreSQL.

### D. Rollout gates
1. Baseline build/test on the source revision.
2. PostgreSQL schema applies from an empty disposable database.
3. Backend integration tests pass against PostgreSQL; no MySQL-only SQL remains in migrated paths.
4. Queue replay, retry, duplicate webhook, lease expiry and crash/restart tests pass.
5. OAuth/credential encryption/approval tests pass.
6. WhatsApp session persistence/reconnect and inbound/outbound tests pass on the selected runtime.
7. Cloudflare preview deploy and Supabase dev integration pass with isolated credentials.
8. Restore drill, monitoring, rollback and data reconciliation reviewed.
9. Explicit approval before any production data migration, production Worker change, secret/DNS change or cutover.

## Commands to run at baseline

Run from the GoodJob checkout, record commit SHA and Node/npm versions first:

```bash
node --version
npm --version
npm ci
npm run build
npm test
npm run test:e2e
```

If any script is absent or a command fails, record the exact failure; do not label it passed. Capture test logs and lockfile integrity. Then run PostgreSQL-specific tests and Cloudflare dry-run checks on the migration branch.

## Current execution status

- [x] Confirm source and target repositories.
- [x] Create isolated target branch.
- [x] Inspect source root scripts, the MySQL schema, target stack manifest, and connected Supabase project metadata.
- [ ] Full table/SQL/ORM/worker/license inventory.
- [ ] PostgreSQL migrations and automated tests.
- [ ] Cloudflare adapter, queue/workflow implementations, preview deployment.
- [ ] WhatsApp compatibility decision.
- [ ] Production cutover (requires separate explicit approval).
