# SBOM and license metadata triage — pinned GoodJob source

Run #74: [GitHub Actions run 39924298660](https://github.com/JackyCheungCode/Hephaestus/actions/runs/39924298660), artifact ID `12488164989`.
Pinned source: `huangguojia/GoodJob@30928c297646597fd7d52ee15ca93236bf0bd2e5`.

## Evidence verified

Both CycloneDX 1.5 files were generated, parsed as JSON, and passed the workflow's basic `components` array check:

| Scope | Components | Components with license metadata missing |
|---|---:|---:|
| Root workspace | 514 | 2 |
| Standalone WhatsApp plugin | 384 | 1 |

License labels recorded in the SBOMs (component counts by label, not legal approval):

- Root: MIT 391; Apache-2.0 43; ISC 43; BSD-2-Clause 16; BSD-3-Clause 9; 0BSD 3; plus individual entries for `(MIT OR EUPL-1.1+)`, Python-2.0, CC-BY-4.0, LGPL-3.0-or-later, MIT-0, `(MIT AND Zlib)`, and Unlicense. Two components lack license metadata: `async@0.2.10` and `qrcode-terminal@0.12.0`.
- WhatsApp: MIT 326; ISC 26; BSD-3-Clause 16; Apache-2.0 10; plus individual entries for `Apache-2.0 AND LGPL-3.0-or-later AND MIT`, BlueOak-1.0.0, CC-BY-4.0, BSD-2-Clause, and GPL-3.0. One component lacks license metadata: `xmlhttprequest-ssl@2.1.2`.

## Interpretation and open actions

1. This is a metadata triage, not a complete legal license audit. SBOM license fields can be missing, stale, normalized imperfectly, or fail to represent bundled assets, notices, dual licensing choices, or source-level license files.
2. Resolve the three missing metadata entries by inspecting their exact package metadata and shipped license/notice files; record evidence and the resulting conclusion.
3. Review the WhatsApp plugin's declared `GPL-3.0-only` license and its GPL license file alongside the root Apache-2.0 license. Legal review must determine distribution/combined-work obligations, source-offer requirements if applicable, notices, and whether the planned deployment boundary changes the analysis.
4. Review the unusual/reciprocal license entries and every dependency that may be distributed with the product. Preserve attribution and third-party notices as required.
5. Re-run SBOM and license review after any dependency/lockfile changes. Do not treat component counts or this document as approval to deploy.

No dependency upgrade, license exception, or production change was made as part of this triage.
