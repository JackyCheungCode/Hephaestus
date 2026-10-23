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

## Current validation status

Run #58: both dependency installs and both audit steps succeeded; all upstream package builds succeeded. The complete suite failed with 359 passed, 1 failed, 9 skipped; the isolated retry reproduced the CLI warm test failure at `whatsapp-plugin/tests/cli-warm.test.ts:210` (expected one process start, observed two). Dependency triage is now evidence-backed but **not complete**. No dependency upgrades have been applied by this register.
