import tempfile
import unittest
from pathlib import Path

from scripts.migration.audit_mysql_dialect import inventory


class MysqlDialectAuditTests(unittest.TestCase):
    def test_finds_known_mysql_coupling_with_paths_and_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "backend" / "sample.ts"
            source.parent.mkdir()
            source.write_text(
                'import { Pool } from "mysql2/promise";\n'
                'await db.query("INSERT IGNORE INTO jobs (id) VALUES (?)");\n'
                'await db.query("SELECT id FROM jobs FOR UPDATE");\n',
                encoding="utf-8",
            )
            result = inventory(root)
            self.assertEqual(result["files_scanned"], 1)
            found = {(item["pattern"], item["line"]) for item in result["findings"]}
            self.assertIn(("mysql_driver_import", 1), found)
            self.assertIn(("insert_ignore", 2), found)
            self.assertIn(("mysql_placeholder", 2), found)
            self.assertIn(("for_update_lock", 3), found)

    def test_ignores_generated_dependency_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dependency = root / "node_modules" / "dep"
            dependency.mkdir(parents=True)
            (dependency / "index.js").write_text('db.query("INSERT IGNORE INTO t VALUES (?)")', encoding="utf-8")
            result = inventory(root)
            self.assertEqual(result["files_scanned"], 0)
            self.assertEqual(result["finding_count"], 0)


if __name__ == "__main__":
    unittest.main()
