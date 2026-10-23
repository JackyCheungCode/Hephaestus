# Supabase migration workspace

This directory is reserved for reviewed PostgreSQL migrations for the GoodJob port.

**No production migration has been applied.** The connected Hephaestus Supabase project is treated as production until its purpose and data ownership are confirmed. Do not run migrations against it during prototyping.

## Required workflow

1. Finish the full MySQL schema inventory from `../` source.
2. Develop against local PostgreSQL or an explicitly approved isolated development database.
3. Create ordered migration files using the Supabase CLI's documented migration command.
4. Apply the complete chain from an empty database; run schema and authorization tests.
5. Review RLS policies for every table exposed through the Data API. Check tenant/team authorization, not only signed-in status.
6. Run Supabase advisors and inspect query plans.
7. Only after written approval, plan production backup, migration, row-count/checksum reconciliation and rollback.

Do not put service-role/secret keys in frontend environment variables or commit credentials. Pin package versions and commit lockfiles.

The first real migration must be generated from the complete `backend/schema.mysql.sql` plus ORM/query usage, not a hand-picked subset of tables. A partial schema would silently break GoodJob features.
