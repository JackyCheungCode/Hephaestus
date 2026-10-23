# PostgreSQL SQL compatibility triage — first pass

Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

## Scope and confidence

This is a **triage queue**, not a conversion plan or estimate. It is derived from the run #38 static audit artifact (`549` files, `5,095` text matches). Static matching does not prove that a line executes SQL, and a filename containing `mysql` does not automatically mean every query is incompatible. Each query must be reviewed with its transaction boundary, schema constraint, and caller.

The existing artifact was generated before the later workflow change that captures npm audit JSON. Run #56 is pending and should be used to verify the new workflow and refresh artifacts.

## Recommended review order

| Priority | Area / source files surfaced by audit | Why review early | Required disposition |
|---|---|---|---|
| P0 | `backend/src/mysql-store.ts`; `backend/src/iam/approval-service.ts`; `backend/src/iam/platform-operations-service.ts`; `backend/src/integrations/integration-control-repository.ts`; `integration-worker/src/repository.ts`; `backend/src/prospect-coverage-memory-mysql.ts` | Locking, lease/approval state, repository writes and concurrent worker behavior can change correctness under PostgreSQL | For each critical flow, record transaction boundaries, isolation assumptions, lock intent, retry/idempotency behavior, and a concurrent PostgreSQL regression test |
| P0 | `backend/src/iam/iam-foundation.ts`; `backend/src/iam/iam-management-service.ts`; `backend/src/iam/platform-mfa.ts`; `backend/src/organization-strong-identity-mysql.ts`; `whatsapp-plugin/src/server/db/repository.ts`; `integration-worker/src/repository.ts` | Upsert and `INSERT IGNORE` semantics are not a mechanical syntax substitution; conflict target and duplicate handling must match actual unique constraints | Record each statement, expected duplicate behavior, target unique key, `ON CONFLICT` candidate, and test |
| P1 | `backend/src/iam/iam-business-tenant-migration.ts`; `backend/src/mysql-store.ts`; `backend/src/mysql-data-import.ts`; `whatsapp-plugin/src/server/db/mysql-migrate.ts`; `backend/src/integrations/integration-mysql-schema.ts` | `DATABASE()` and MySQL `information_schema` assumptions affect migration, introspection and import tooling | Replace with PostgreSQL catalogs or portable migration metadata; test on a clean disposable database |
| P1 | `backend/src/iam/iam-management-service.ts`; `backend/src/iam/platform-operations-service.ts`; `backend/src/iam/approval-service.ts`; `backend/src/iam/iam-foundation.ts`; `whatsapp-plugin/src/server/db/mysql-migrate.ts` | Millisecond time functions and `DATETIME(3)` affect ordering, expiry, lease and audit timestamps | Define UTC/time-zone and precision semantics; test expiry boundaries, ordering and round trips |
| P1 | `backend/schema.mysql.sql` and all application SQL referencing JSON columns | Schema JSON type matches alone do not reveal required operators, indexes or shape constraints | Map each JSON column, query/operator use, index needs and null/missing-key semantics; add round-trip and query tests |
| P1 | All actual backend and worker repository call sites using `?` placeholders | Placeholder counts are high and include non-runtime/prototype/test content; PostgreSQL uses different parameter syntax | Enumerate executable queries by call site and adapt through a reviewed database abstraction rather than broad text replacement |
| P2 | `frontend/src/prototype-api.ts` and files suffixed `*-test.ts` | Audit shows large placeholder and driver-related match counts here; prototype/test code may not be production data access | Classify as production, development-only, test-only, dead code or false positive before including in implementation scope |

## Snapshot details from run #38

- Audit: 549 files scanned, 5,095 raw matches.
- 70 `FOR UPDATE` matches; top non-test paths included `backend/src/prospect-coverage-memory-mysql.ts` (19), `backend/src/integrations/integration-control-repository.ts` (8), `backend/src/organization-strong-identity-mysql.ts` (8), and `integration-worker/src/repository.ts` (8).
- 59 `ON DUPLICATE KEY UPDATE` matches; `whatsapp-plugin/src/server/db/repository.ts` (16), `backend/src/iam/iam-foundation.ts` (11), and `backend/src/iam/iam-management-service.ts` (6) were the largest surfaced locations.
- 26 `INSERT IGNORE` matches; the WhatsApp repository (6), its MySQL migration module (4), and backend IAM foundation (3) were surfaced.
- 67 `information_schema` matches overall; notable non-test locations include `backend/src/mysql-store.ts` (8), `backend/src/iam/iam-business-tenant-migration.ts` (3), and `whatsapp-plugin/src/server/db/mysql-migrate.ts` (3).
- 150 millisecond-time matches; the largest groups were IAM management (41), platform operations (31), approval service (27), and IAM foundation (16).
- 4,091 placeholder matches are **not** 4,091 distinct SQL statements; `frontend/src/prototype-api.ts` alone accounts for 748 raw matches in the current static scan.

Counts above are audit leads, not authoritative runtime query counts. Some `*-mysql-test.ts` files appeared in non-document scans; they must remain explicitly classified as test-only unless call-site evidence proves otherwise.

## Acceptance rule for each query

Do not mark a finding complete until the register records: (1) source file and line, (2) runtime/test/prototype classification, (3) query purpose and caller, (4) relevant schema constraints, (5) PostgreSQL disposition, (6) transaction/locking behavior if applicable, and (7) a regression test. No executable Supabase migration should be generated from this triage alone.

## Next actions

1. Download and review the next completed validation artifact, including both npm audit JSON files if present.
2. Turn P0 source locations into a query-by-query disposition register, beginning with approval/lease/worker locking and upsert uniqueness.
3. Keep the PostgreSQL schema, RLS, concurrency and import gates unchecked until disposable-database tests exist.
