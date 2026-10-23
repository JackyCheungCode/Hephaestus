#!/usr/bin/env python3
"""Apply the reviewed CLI warm-pool teardown guard to the pinned validation checkout.

This deliberately fails closed if upstream source context changes; it never edits the
upstream repository or any production resource. The patch is applied only in CI's
temporary checkout before build/tests.
"""
from pathlib import Path

SOURCE = Path("goodjob-source/whatsapp-plugin/src/server/services/cli-engine.ts")
text = SOURCE.read_text(encoding="utf-8")

replacements = [
    (
        "  private warming = 0;\n",
        "  private warming = 0;\n  /** Prevent asynchronous warm spawns after dispose() has begun. */\n  private disposed = false;\n",
    ),
    (
        "  dispose(): void {\n    if (this.warmTimer) clearInterval(this.warmTimer);",
        "  dispose(): void {\n    this.disposed = true;\n    if (this.warmTimer) clearInterval(this.warmTimer);",
    ),
    (
        "  private async ensureWarm(model: string, effort: string): Promise<void> {\n    if (!this.options.warm) return;",
        "  private async ensureWarm(model: string, effort: string): Promise<void> {\n    if (!this.options.warm || this.disposed) return;",
    ),
    (
        "  private async spawnWarm(model: string, effort: string): Promise<WarmWorker> {\n    const workspace = await this.ensureWorkspace();\n    const args = [",
        "  private async spawnWarm(model: string, effort: string): Promise<WarmWorker> {\n    const workspace = await this.ensureWorkspace();\n    // dispose() may run while ensureWorkspace() is pending. Do not spawn after teardown.\n    if (this.disposed) throw new Error(\"CLI warm engine disposed during workspace setup\");\n    const args = [",
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Refusing patch: expected exactly one match, found {count}: {old[:90]!r}")
    text = text.replace(old, new, 1)

SOURCE.write_text(text, encoding="utf-8")
print(f"Applied teardown guard to {SOURCE}")
