# Dependency audit triage — pinned GoodJob source

Audit run: GitHub Actions run #58, run ID `39923215892`, artifact ID `12488427607`.
Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`.
Reports: `npm-audit-root.json` and `npm-audit-whatsapp.json` in artifact `goodjob-validation-metadata`.

## Results

| Lockfile/install scope | Critical | High | Moderate | Total reported package findings |
|---|---:|---:|---:|---:|
| Root workspace | 4 | 25 | 7 | 36 |
| Standalone WhatsApp plugin | 5 | 7 | 6 | 18 |

These are separate npm audit scopes. Findings overlap between scopes and **must not be added together as 54 unique vulnerabilities**. They are dependency-tree findings, not confirmed exploitable vulnerabilities in this application. The reports must be retained with the source revision and regenerated after dependency changes.

## First remediation queue

### P0 — immediate review before any production use

- `concurrently`: critical, direct in root and WhatsApp; report indicates a compatible fix at `9.2.5`. Verify lockfile changes and run CLI/process tests.
- `proxy-addr`: critical transitive finding in both scopes; determine which dependency introduces it and verify the resolved fixed version and runtime exposure.
- `shell-quote`: critical transitive finding in both scopes; root report indicates a fix through `concurrently@9.2.5`. Verify no unexpected behavior change.
- `dompurify`: critical in root scope; report indicates a fix is available. Determine actual usage and whether sanitization boundaries are security-sensitive.
- `tinypool` / `vitest`: critical in WhatsApp test dependency tree; report indicates the fix requires `vitest@5.0.5` (major-version change). Validate test compatibility before adopting.
- Root `xlsx`: high severity with `fixAvailable: false` in this report. Identify product use, input trust boundary and alternative/mitigation; do not claim it is fixed by a generic audit fix.
- WhatsApp `undici`: high direct finding, report suggests `6.29.1`; confirm engine/runtime constraints and test HTTP integration behavior.
- Direct root `@modelcontextprotocol/client` and `@modelcontextprotocol/server`: high, report indicates `2.3.1` as a compatible fix. Upgrade together and run protocol/integration tests.
- Direct root `mailparser`, `nodemailer`, and `vite`: high findings; review the exact fixed versions in the full JSON, test mail parsing/sending and production build paths.

### P1 — transitive findings with major-upgrade or broad dependency implications

- `whatsapp-web.js` family (including Puppeteer-related packages, `basic-ftp`, `extract-zip`, `get-uri`, `pac-proxy-agent`, `proxy-agent`): the audit suggests a `whatsapp-web.js` major-version change. This is not a routine patch; check supported WhatsApp session behavior, browser compatibility and provider terms before considering it.
- Root `whatsapp-web.js` is itself high severity in the captured tree. Verify the installed version and lockfile resolution; the report's suggested fix version is lower than the affected range in the advisory, so do not blindly apply it without inspecting the full advisory and npm resolution.
- WhatsApp `vite`, `browserslist`, `engine.io`, `nanoid`, `sharp`, and `source-map-js`: inspect exact dependency paths, fixed versions and whether the affected code reaches production bundles or server runtime.

## Required remediation protocol

1. Create a dedicated dependency-remediation commit on the migration branch only; preserve the original lockfiles and audit JSON as evidence.
2. Run targeted upgrades first where npm identifies a non-major fix. Do not run blanket `npm audit fix --force`.
3. Treat major upgrades (notably `whatsapp-web.js` and `vitest`) as separate changes with explicit compatibility tests.
4. After every change, run root and standalone plugin install, build, full test suite, isolated CLI warm test, and regenerate both audit JSON files.
5. Review each remaining critical/high item by advisory, dependency path, runtime reachability, exposure and compensating control. Record accepted risk with owner and rationale; no silent suppression.
6. Produce an SBOM and direct/transitive license inventory for both dependency scopes. Separately review root Apache-2.0 and WhatsApp plugin GPL-3.0-only distribution obligations, including combined-work boundaries and third-party/provider terms.
7. Do not deploy or modify production resources as part of this queue.

## Follow-up validation — run #74

Run #74 (`39924298660`, [workflow](https://github.com/JackyCheungCode/Hephaestus/actions/runs/39924298660), artifact `12488164989`) confirms that both audit JSON files and both CycloneDX 1.5 SBOMs were generated and passed JSON/structure checks. The SBOMs contain 514 root-scope components and 384 standalone WhatsApp components. License metadata is absent for 2 root components (`async@0.2.10`, `qrcode-terminal@0.12.0`) and 1 WhatsApp component (`xmlhttprequest-ssl@2.1.2`); see `docs/migration/SBOM_LICENSE_TRIAGE.md`. These results validate artifact production, not vulnerability remediation or legal compliance.

## Current validation status

Run #58: both dependency installs and both audit steps succeeded; all upstream package builds succeeded. The complete suite failed with 359 passed, 1 failed, 9 skipped; the isolated retry reproduced the CLI warm test failure at `whatsapp-plugin/tests/cli-warm.test.ts:210` (expected one process start, observed two). Dependency triage is now evidence-backed but **not complete**. No dependency upgrades have been applied by this register.


## Follow-up validation — run #99 (2026-10-23)

Run #99 (`39926659632`, [workflow](https://github.com/JackyCheungCode/Hephaestus/actions/runs/39926659632), artifact `12489673430`) completed successfully against pinned source `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`. Both dependency installs, audit reports, CycloneDX SBOM generation/validation, all package builds, and the full WhatsApp plugin test suite succeeded. The full suite reported **360 passed, 9 skipped** across 32 test files (30 passed, 2 skipped). The isolated `tests/cli-warm.test.ts` rerun also passed **6/6**. The temporary-checkout lifecycle guard and isolated-test workflow change therefore pass this run; this is not a production deployment and does not mean the upstream source or dependency vulnerabilities are fully remediated.

The run regenerated and retained `npm-audit-root.json`, `npm-audit-whatsapp.json`, `sbom-root.cdx.json`, `sbom-whatsapp.cdx.json`, `mysql-schema-inventory.json`, and `mysql-dialect-audit.json` in artifact `goodjob-validation-metadata` (artifact expires 2026-10-30). The audit counts remain root: 4 critical, 25 high, 7 moderate (36 findings); standalone WhatsApp: 5 critical, 7 high, 6 moderate (18 findings). These scopes overlap. **No dependency remediation was applied by run #99.** Continue by reviewing exact advisories and applying narrowly scoped upgrades in a dedicated migration-branch commit, then repeat build/full/isolated tests and regenerate reports. PostgreSQL compatibility and production readiness remain separate open gates.


## Run #99 artifact review — exact direct findings

Reviewed the actual JSON files from artifact `12489673430` rather than relying only on prior summaries. Root scope direct findings include: `concurrently` (critical; compatible suggested fix 9.2.5), `@modelcontextprotocol/client` and `@modelcontextprotocol/server` (high; suggested 2.3.1), `mailparser` and `nodemailer` (high; npm reports a fix but exact lockfile-resolved versions must be checked), `vite` (high; fix available), `express` (moderate; fix available), and `mysql2` (moderate; suggested 3.24.6). Root `whatsapp-web.js` remains high with a confusing suggested downgrade to 1.34.2 while the reported affected range is 1.34.4–1.34.7; do not apply that suggestion. Root `xlsx` is high and has no fix available in the captured report; it needs an explicit replacement/mitigation assessment.

Standalone WhatsApp direct findings include `concurrently` (critical; 9.2.5), `undici` (high; 6.29.1), `vite` (high; fix available), and `mysql2` (moderate; 3.24.6). `vitest` is critical but npm suggests 5.0.5 as a major upgrade; keep it separate from the compatible patch batch. Transitive critical `proxy-addr` can be updated by compatible dependency resolution (affected through 2.0.7; fixed line starts 2.0.8), while `shell-quote` is tied to `concurrently` and is expected to be addressed by 9.2.5. These are audit recommendations, not yet applied changes.

### Safe remediation order

1. In a dedicated temporary-checkout patch, update `concurrently` to 9.2.5 in each affected package scope and refresh each relevant lockfile; verify `shell-quote` and `proxy-addr` resolved versions from the lockfiles, rather than assuming direct upgrades fixed the tree.
2. Apply compatible, isolated fixes for `undici` 6.29.1 in WhatsApp and `mysql2` 3.24.6 where engine/API compatibility checks pass.
3. Resolve exact patched versions for root MCP client/server, `mailparser`, `nodemailer`, and `vite` from npm's advisory output and lockfiles; upgrade paired MCP client/server packages together.
4. Keep `vitest` 5, `whatsapp-web.js`, and `xlsx` out of the first patch batch pending major-upgrade or replacement/mitigation plans. Do not use blanket `npm audit fix --force`.
5. Re-run installs, builds, the full suite, isolated CLI warm test, audit and SBOM generation. Compare counts and resolved package versions before claiming remediation.
