import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "migration" / "inventory_mysql_schema.py"
SPEC = importlib.util.spec_from_file_location("inventory_mysql_schema", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class InventoryMysqlSchemaTests(unittest.TestCase):
    def test_splits_nested_commas_and_quoted_commas(self):
        sql = """
        CREATE TABLE example (
          id VARCHAR(64) NOT NULL,
          note VARCHAR(100) DEFAULT 'it''s, still one column',
          payload JSON DEFAULT (JSON_OBJECT('x', 'a,b')),
          derived VARCHAR(100) GENERATED ALWAYS AS (CONCAT(id, ',', 'x')) STORED,
          PRIMARY KEY (id),
          UNIQUE KEY uq_payload (payload(20)),
          CONSTRAINT fk_example_parent FOREIGN KEY (id) REFERENCES parent (id),
          CHECK (CHAR_LENGTH(id) > 0)
        ) ENGINE=InnoDB;
        """
        result = MODULE.inventory(sql)
        self.assertEqual(result["counts"]["tables"], 1)
        self.assertEqual(result["counts"]["columns"], 4)
        self.assertEqual(result["counts"]["primary_keys"], 1)
        self.assertEqual(result["counts"]["unique_constraints"], 1)
        self.assertEqual(result["counts"]["foreign_keys"], 1)
        self.assertEqual(result["counts"]["checks"], 1)
        self.assertTrue(next(c for c in result["tables"][0]["columns"] if c["name"] == "derived")["generated"])

    def test_handles_multiple_tables_and_comments(self):
        sql = """
        -- comma in a comment, should not split columns
        CREATE TABLE first_table (
          id BIGINT PRIMARY KEY,
          note TEXT /* a comma, inside a comment */
        );
        CREATE TABLE second_table (
          id BIGINT NOT NULL,
          KEY ix_second_id (id)
        );
        """
        result = MODULE.inventory(sql)
        self.assertEqual([t["name"] for t in result["tables"]], ["first_table", "second_table"])
        self.assertEqual(result["counts"]["tables"], 2)
        self.assertEqual(result["counts"]["indexes"], 1)


if __name__ == "__main__":
    unittest.main()
