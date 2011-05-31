import contextlib

from .base import BaseMySQLTests


class TestCursor(BaseMySQLTests):
    def test_basic_execute(self, connection):
        with self.create_table(connection, "things"):
            with contextlib.closing(connection.cursor()) as cur:
                cur.execute("INSERT INTO things (name) VALUES ('webite')")
                cur.execute("SELECT name FROM things")
                results = cur.fetchall()
                assert results == [("website",)]