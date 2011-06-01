import contextlib

from MySQLdb.cursors import DictCursor

from .base import BaseMySQLTests


class TestCursor(BaseMySQLTests):
    def test_basic_execute(self, connection):
        with self.create_table(connection, "things", name="VARCHAR(20)"):
            with contextlib.closing(connection.cursor()) as cur:
                cur.execute("INSERT INTO things (name) VALUES ('website')")
                cur.execute("SELECT name FROM things")
                results = cur.fetchall()
                assert results == [("website",)]

class TestDictCursor(BaseMySQLTests):
    def test_fetchone(self, connection):
        with self.create_table(connection, "people", name="VARCHAR(20)", age="INT"):
            with contextlib.closing(connection.cursor(DictCursor)) as cur:
                cur.execute("INSERT INTO people (name, age) VALUES ('guido', 50)")
                cur.execute("SELECT * FROM people")
                rows = cur.fetchall()
                assert rows == [{"name": "guido", "age": 50}]