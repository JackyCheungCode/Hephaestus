# PostgreSQL schema mapping register

Status: **template only; no production schema changes**  
Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

Use one row per source table and a separate column-level register before writing Supabase migrations. Do not treat the lexical inventory JSON as a normalized schema or as executable DDL.

## Table-level register

| Field | Required review |
|---|---|
| Source table / target table | Preserve stable names where practical; document every rename |
| Ownership and tenant keys | Identify team/tenant/owner relationships from application authorization code |
| Primary key | Type, generation strategy, sequence/identity behavior |
| Unique constraints | Exact columns, collation/case sensitivity, nullable-column semantics |
| Foreign keys | Referenced table/columns, ON DELETE/UPDATE behavior, deferrability |
| Check constraints | Translate expression semantics, not just syntax |
| Indexes | Columns/order, partial/expression indexes, query evidence, uniqueness |
| Generated columns | Expression-by-expression PostgreSQL equivalent and stored/virtual behavior |
| RLS | Policies by operation and role; anonymous/authenticated/service-role tests |
| Migration order | Dependency ordering and backfill requirements |
| Verification | Expected row counts, invariant queries, rollback/re-run behavior |

## Column-level register

Record every column with these fields:

- Source table and column; source declaration verbatim
- Target type and rationale (including unsigned numeric ranges)
- Nullable, default, identity/sequence and generated-expression behavior
- Timestamp policy: `timestamp with time zone` versus `timestamp without time zone`, UTC assumptions, and millisecond precision
- JSON versus JSONB decision, validation and indexes
- Text collation/case sensitivity and unique-index implications
- Foreign-key/check participation
- Data conversion/backfill expression and handling of invalid legacy values
- Round-trip test and sign-off status

## SQL compatibility disposition register

For each finding emitted by `audit_mysql_dialect.py`, record:

| Field | Meaning |
|---|---|
| File, line, pattern | Stable pointer to the source finding |
| Runtime path | Production code, test, migration, docs, or dead code (verified manually) |
| Semantic intent | Idempotency, lock/lease, dedupe, metadata introspection, etc. |
| PostgreSQL implementation | Proposed SQL/API change and conflict target where applicable |
| Concurrency implications | Locking/isolation/retry implications |
| Test | Regression test and disposable-PostgreSQL test |
| Disposition | Open / accepted / rejected / not applicable, with reviewer and date |

Important examples that require semantic review include `ON DUPLICATE KEY UPDATE` plus `VALUES(column)`, `INSERT IGNORE`, `REPLACE INTO`, `NOW(3)`, `DATABASE()`, `information_schema` queries, `?` placeholders, JSON functions, and `FOR UPDATE`. A text match is only a lead; a missing match does not prove portability.

## Acceptance gates

- [ ] Every table and column from the pinned schema is represented.
- [ ] Primary/unique/foreign/check constraints and indexes are reconciled against parsed DDL and application queries.
- [ ] Generated columns are reviewed individually.
- [ ] All dialect-audit findings have a disposition; high-risk query paths have tests.
- [ ] Fresh disposable PostgreSQL migration succeeds twice from clean state.
- [ ] Data conversion tests preserve counts, relationships, uniqueness and timestamp precision.
- [ ] RLS tests prove cross-tenant reads and writes are denied for all unprivileged roles.
- [ ] Task claims, leases, retries, duplicate webhooks and unknown external outcomes pass concurrent tests.
- [ ] No production cutover until a separate explicit authorization is given.

## Safety boundary

This register is planning/review material. It contains no credentials and does not execute SQL. Do not point migration tests at the existing Supabase project; use a disposable local or preview database.
