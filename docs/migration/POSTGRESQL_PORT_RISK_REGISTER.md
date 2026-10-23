# PostgreSQL port risk register

Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

This document records implementation risks found in source inspection. It is not a PostgreSQL schema conversion and must not be treated as a migration script.

## Confirmed dialect coupling

- Root and backend packages currently default to `CRM_STORE=mysql` and `DATABASE_URL=mysql://...`; production deployment scripts explicitly set `CRM_STORE=mysql`.
- Backend code imports `Pool` / `RowDataPacket` from `mysql2/promise` across many domain modules. Changing the connection driver alone will not make SQL portable.
- Direct MySQL syntax is present, e.g. `backend/src/app-settings.ts` uses `VALUES (?, ?, NOW(3)) ON DUPLICATE KEY UPDATE ... VALUES(setting_value)`; `backend/src/iam/platform-mfa.ts` uses the same upsert form.
- `backend/src/iam/iam-business-tenant-migration.ts` queries `information_schema.columns` and `DATABASE()`, so schema introspection/migration utilities also require a PostgreSQL implementation.
- The WhatsApp plugin has a PostgreSQL adapter, but its documented production deployment shares the CRM's MySQL 8 database. That adapter is not evidence that all schema, SQL, session, or transaction behavior is compatible with Supabase.

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
