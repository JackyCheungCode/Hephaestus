# Licensing and distribution gate

Pinned upstream: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`

## Confirmed repository declarations

- Root `LICENSE` is Apache License 2.0.
- `whatsapp-plugin/package.json` declares `GPL-3.0-only`; `whatsapp-plugin/LICENSE` contains GNU GPL version 3.
- The WhatsApp plugin depends on `@whiskeysockets/baileys` version `7.0.0-rc13` and includes project-specific license notices under `whatsapp-plugin/LICENSES/`.
- The upstream root package and WhatsApp package are separate package boundaries. A combined distribution/deployment must not assume every component has the same license.

## Required before distribution or private/closed-source reuse

1. Generate a complete SBOM and direct/transitive license inventory from the pinned lockfiles, including the separately locked WhatsApp plugin.
2. Preserve upstream LICENSE/NOTICE and bundled third-party notices when copying code or building artifacts.
3. Have qualified counsel review whether packaging or linking the GPL-3.0-only WhatsApp plugin with other components triggers source-disclosure or other obligations for the intended distribution model.
4. Review the selected WhatsApp integration implementation and applicable provider/platform terms separately; a library license is not platform permission.
5. Document whether the WhatsApp plugin remains a separately deployed service, whether it is modified, and how corresponding source and build materials will be made available if required.
6. Do not strip license files or silently replace the Baileys integration with a different implementation.

## CI evidence

The first pinned-source CI dependency install completed with npm reporting 36 vulnerabilities (7 moderate, 25 high, 4 critical). This is a raw install-time audit summary, not a triaged finding list. The validation workflow now captures `npm audit --json` reports for both the root workspace and standalone WhatsApp plugin as artifacts (`npm-audit-root.json` and `npm-audit-whatsapp.json`) when dependency installation succeeds. Review the next completed run's reports, classify production reachability and exploitability, and document accepted risks or upgrades. Avoid automatic `npm audit fix --force` because it can introduce breaking dependency changes.

## Safety boundary

This is a release gate, not legal advice. No upstream license files or dependencies have been changed. No deployment or production resources have been modified.
