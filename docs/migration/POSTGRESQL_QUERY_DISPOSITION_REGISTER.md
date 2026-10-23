# PostgreSQL query disposition register — verified source examples

Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

This register captures concrete SQL examples verified directly in the pinned source. It is intentionally a first slice, not a claim that all repository queries have been inventoried. No SQL has been executed and no production database was changed.

## Verified findings

| ID | Source location | MySQL-specific behavior | Required PostgreSQL disposition | Priority / validation |
|---|---|---|---|---|
| SQL-001 | `backend/src/iam/platform-mfa.ts:139` | MFA challenge row read with `FOR UPDATE` inside a transaction | Preserve single-use challenge semantics and row-lock scope. Verify competing challenge verification attempts cannot both succeed; test rollback on invalid/expired challenge. | P0; concurrent transaction test |
| SQL-002 | `backend/src/iam/platform-mfa.ts:142` | MFA record read with `LIMIT 1 FOR UPDATE` | Confirm PostgreSQL locking syntax/order and lock scope; ensure recovery-code and TOTP state updates remain atomic with challenge consumption. | P0; concurrency + failure rollback |
| SQL-003 | `backend/src/iam/platform-mfa.ts:118` | `ON DUPLICATE KEY UPDATE ... VALUES(secret_encrypted)` | Identify unique key (expected operator identity, verify schema) and convert to explicit `ON CONFLICT (operator_id) DO UPDATE` only if matching unique constraint exists. Preserve disabled/reset/failed-attempt semantics. | P0; duplicate enrollment regression |
| SQL-004 | `backend/src/iam/platform-mfa.ts:152` | `DATE_ADD(NOW(3), INTERVAL 10 MINUTE)` | Use an explicit UTC timestamp expression or parameterized deadline; preserve 10-minute lockout and millisecond precision. Avoid implicit session-time-zone drift. | P1; expiry boundary/time-zone tests |
| SQL-005 | `backend/src/iam/iam-business-tenant-migration.ts:6,11,20` | `information_schema.columns/statistics` filtered by `table_schema = DATABASE()` | Replace with PostgreSQL catalog queries or migration metadata; distinguish current schema vs explicit schema and check indexes/columns/identity properties accurately. | P1; fresh DB introspection tests |
| SQL-006 | `backend/src/iam/approval-service.ts:78,148-149` | Approval schema introspection uses MySQL `information_schema` and `DATABASE()` | Replace schema checks without assuming MySQL catalog fields. Confirm idempotent schema bootstrap on an empty PostgreSQL database and on a database with partially applied migrations. | P1; migration repeatability |
| SQL-007 | `backend/src/iam/approval-service.ts:297` | Approval task row selected `FOR UPDATE` | Preserve task decision serialization and tenant predicate. Test two concurrent approve/reject decisions; only one may win and related instance/outbox writes must commit atomically. | P0; concurrent approval test |
| SQL-008 | `backend/src/iam/approval-service.ts:340-342` | `INSERT IGNORE INTO approval_outbox_events` | Determine exact unique constraint and whether duplicate outbox event is expected; use `INSERT ... ON CONFLICT (...) DO NOTHING` only with the verified conflict key. Verify outbox event cannot be silently dropped for unrelated constraint errors. | P0; duplicate-event/idempotency test |
| SQL-009 | `backend/src/iam/approval-service.ts:312,339` | MySQL `JSON_ARRAY()` | Replace with PostgreSQL JSONB array literal/expression consistent with the column type and node code. Verify empty-array vs SQL NULL semantics. | P1; serialization/read-back test |
| SQL-010 | `backend/src/iam/approval-service.ts:502,513,520,551` | MySQL `JSON_OBJECT()` | Replace with `'{}'::jsonb` or `jsonb_build_object()` according to the target column type and required shape. | P1; JSON round-trip test |
| SQL-011 | `backend/src/iam/approval-service.ts:214-222,306+` | `NOW(3)` timestamps across validity checks, task decisions and instance state transitions | Define timestamp source and UTC/precision policy; replace consistently, preferably with explicit application-provided timestamps or a documented DB clock. Test validity boundary and ordering. | P1; time precision tests |
| SQL-012 | `backend/src/app-settings.ts:41-42` | `ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)` | Inspect schema unique key for `setting_key`; translate to `ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value` only after verifying unique constraint and update semantics. | P1; concurrent upsert regression |
| SQL-013 | `backend/src/iam/platform-mfa.ts:171-183` | MFA DDL uses `DATETIME(3)`, `ENGINE=InnoDB`, `DEFAULT CHARSET`, `COLLATE`, `UNIQUE KEY`, `INDEX` inline syntax | Re-express table, timestamp precision, indexes, and uniqueness in PostgreSQL migrations; review collation/case sensitivity rather than dropping it. | P1; DDL apply + type round-trip |
| SQL-014 | `backend/src/iam/approval-service.ts:67-128` | Approval bootstrap DDL uses MySQL inline `INDEX`/`UNIQUE KEY`, `ENGINE=InnoDB`, `JSON`, `DATETIME(3)` | Normalize DDL into versioned PostgreSQL migrations; verify all FKs, unique constraints, indexes, JSONB and timestamp types against the mapping register. | P1; schema reconciliation |

## Important cautions

- Line references refer to the pinned source commit above and must be rechecked if the source revision changes.
- `LIMIT 1 FOR UPDATE` should be normalized to a valid PostgreSQL query form during implementation; the semantic goal is row locking, not literal syntax preservation.
- Do not mechanically replace every `NOW(3)`, `JSON_OBJECT()`, `JSON_ARRAY()`, or placeholder in the repository. First classify the statement, schema type, transaction, and runtime call path.
- A query-level syntax conversion is insufficient where correctness depends on unique constraints, transaction boundaries, row locks, idempotency, or tenant isolation.
- No migration SQL should be generated from this register alone.

## Completion criteria

For each row, implementation is complete only after: target schema/constraint is verified; PostgreSQL statement is implemented behind an isolated adapter or migration; regression tests pass against a disposable PostgreSQL database; and transaction/concurrency behavior is tested where marked P0. Keep the MySQL production path unchanged until the separate cutover authorization gate is approved.
