# PostgreSQL port risk register

Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

This document records implementation risks found in source inspection. It is not a PostgreSQL schema conversion and must not be treated as a migration script.

## Confirmed dialect coupling

- Root and backend packages currently default to `CRM_STORE=mysql` and `DATABASE_URL=mysql://...`; production deployment scripts explicitly set `CRM_STORE=mysql`.
- Backend code imports `Pool` / `RowDataPacket` from `mysql2/promise` across many domain modules. Changing the connection driver alone will not make SQL portable.
- Direct MySQL syntax is present, e.g. `backend/src/app-settings.ts` uses `VALUES (?, ?, NOW(3)) ON DUPLICATE KEY UPDATE ... VALUES(setting_value)`; `backend/src/iam/platform-mfa.ts` uses the same upsert form.
- `backend/src/iam/iam-business-tenant-migration.ts` queries `information_schema.columns` and `DATABASE()`, so schema introspection/migration utilities also require a PostgreSQL implementation.
- The WhatsApp plugin config parser accepts `pglite`, `postgres`, and `mysql`, and a PostgreSQL adapter exists, but its production deployment guide explicitly requires `DATABASE_CLIENT=mysql` and the same MySQL 8 database as the CRM. The plugin's production runtime rejects PostgreSQL. Treat PostgreSQL support as local/dev or migration tooling, not a production-ready Supabase adapter.

## Prioritized implementation gates

| Priority | Confirmed issue | Required engineering action | Exit evidence |
|---|---|---|---|
| P0 | WhatsApp plugin production runtime requires MySQL; its PostgreSQL adapter is not a supported production configuration | Choose and document either a real PostgreSQL port or an isolated service/database contract before designing a shared Supabase schema | Architecture decision record plus production-like adapter tests |
| P0 | Backend domain modules directly depend on `mysql2/promise` types and pool behavior | Define the minimum store/transaction interface from actual call sites; inventory every direct driver import before changing runtime wiring | Import inventory and contract tests covering transactions, errors, connection lifecycle and row types |
| P0 | Task execution, approval freeze, webhook dedupe and lease recovery depend on transaction/locking semantics | Map each critical flow and its invariants before translating SQL; add concurrent PostgreSQL tests for duplicate delivery, retries, lease expiry and ambiguous provider outcomes | Repeatable concurrency tests against disposable PostgreSQL |
| P1 | MySQL upserts use `ON DUPLICATE KEY UPDATE` and legacy `VALUES(column)` semantics | Identify the exact unique constraint and intended behavior for every statement; use explicit `ON CONFLICT` targets only after verifying constraints | Per-query disposition, matching unique constraint, regression test |
| P1 | Schema introspection uses `DATABASE()` and MySQL `information_schema` assumptions | Replace with PostgreSQL catalog queries or portable migration metadata; do not mechanically rename catalog fields | Introspection tests on a fresh PostgreSQL database |
| P1 | `DATETIME(3)`, JSON, unsigned numeric declarations, generated columns and collation behavior may not preserve semantics directly | Complete column-level mapping and data round-trip tests before producing target DDL | Reviewed mapping register, boundary-value tests and count/invariant reconciliation |
| P1 | Supabase RLS and API exposure are not yet modeled against actual authorization rules | Derive policies from tenant/team checks in application code; test each exposed table with anonymous, authenticated and service roles | Automated positive and cross-tenant negative RLS tests |
| P2 | Install-time npm audit reported 36 vulnerabilities across the root dependency install; no triage has been recorded | Capture machine-readable audit reports for root and WhatsApp lockfiles separately; classify direct/transitive dependency, runtime reachability and fix availability | Reviewed SBOM/license report and vulnerability disposition; no blind force-upgrades |

These priorities describe ordering, not proof that every item has the same exploitability or implementation cost. The scanner is a lead generator; each source finding must be manually classified as executable runtime SQL, test-only, migration code, dead code or false positive before estimating effort.

## Immediate next actions

1. Obtain a non-cancelled CI run for the current scanner and inspect its artifact before quoting any match counts.
2. Extract the complete source table/column/index/constraint inventory and reconcile it with the mapping register.
3. Build the source SQL disposition list from real runtime call sites, beginning with transaction-critical code and upserts.
4. Do not create executable Supabase migrations until schema mapping and authorization/RLS review are approved.

## Required compatibility layers

1. **Store abstraction:** define a narrow database interface and implement PostgreSQL pool/transaction semantics separately from MySQL; do not mechanically replace `mysql2` imports.
2. **SQL translation inventory:** enumerate placeholder conventions, `NOW(3)`, `ON DUPLICATE KEY UPDATE`, `VALUES(col)`, `INSERT IGNORE`, `REPLACE`, `LIMIT` patterns, JSON operators, date arithmetic, information_schema queries, and MySQL-specific locking. Every occurrence needs an explicit disposition and tests.
3. **Upserts:** translate each upsert to `INSERT ... ON CONFLICT (...) DO UPDATE` using the correct unique constraint; never infer a conflict target from table names alone.
4. **Transactions/concurrency:** inspect task claim/lease, provider limits, approval freezes, webhook dedupe, job reconciliation and worker lifecycle. Verify isolation levels and row-lock behavior under concurrent PostgreSQL transactions.
5. **Types and precision:** map `DATETIME(3)`, `JSON`, unsigned/numeric fields, generated columns and collation-dependent unique constraints with round-trip tests.
6. **Security:** model tenant/team membership from actual authorization logic, then test RLS policies for every exposed table using anonymous, authenticated, and service roles. Avoid blanket tenant policies.
7. **Migration repeatability:** create migrations only after a normalized schema model is reviewed; apply against a disposable fresh database, compare table/constraint/index counts, and rerun from a clean state.

## Implementation order

- [ ] Inventory all MySQL-specific SQL and module-level driver imports.
- [ ] Define a table-by-table schema mapping and conflict/locking behavior.
- [ ] Implement PostgreSQL store behind a feature flag; keep MySQL path unchanged.
- [ ] Run repository/domain tests against disposable PostgreSQL, including concurrent and cross-tenant cases.
- [ ] Add Supabase RLS and API-exposure checks.
- [ ] Only after preview evidence, request separate authorization for any production cutover.

## Safety boundary

No SQL in this document has been executed. No Supabase schema/data, Cloudflare resources, production secrets, DNS, or deployment workflows have been changed.

## WhatsApp-specific runtime gate

The pinned plugin's production deployment guide explicitly mandates `DATABASE_CLIENT=mysql` and a shared GoodJob CRM MySQL database. Therefore, moving the CRM to Supabase PostgreSQL also requires a deliberate WhatsApp production redesign; simply setting `DATABASE_CLIENT=postgres` is not supported. Preserve the existing WhatsApp provider interface and evaluate two isolated options: (a) port/test its repository, schema migrations, transaction behavior and production config for PostgreSQL; or (b) keep it as a separately deployed, private Node.js service with a controlled adapter while CRM data ownership is redesigned. The second option still needs an explicit cross-database contract and cannot pretend both systems share one transaction.

The source architecture also documents an official Meta Cloud API provider alongside Baileys. For production-critical messaging, evaluate Meta's official channel separately from Baileys' non-official WhatsApp Web protocol; this is a product/runtime decision, not something the Cloudflare Worker runtime automatically solves.
