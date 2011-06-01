import contextlib

import py

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

    def test_fetchmany_insert(self, connection):
        with self.create_table(connection, "things", name="VARCHAR(20)"):
            with contextlib.closing(connection.cursor()) as cur:
                cur.execute("INSERT INTO things (name) VALUES ('website')")
                with py.test.raises(connection.ProgrammingError):
                    cur.fetchmany()

class TestDictCursor(BaseMySQLTests):
    def test_fetchall(self, connection):
        with self.create_table(connection, "people", name="VARCHAR(20)", age="INT"):
            with contextlib.closing(connection.cursor(DictCursor)) as cur:
                cur.execute("INSERT INTO people (name, age) VALUES ('guido', 50)")
                cur.execute("SELECT * FROM people")
                rows = cur.fetchall()
                assert rows == [{"name": "guido", "age": 50}]

    def test_fetchmany(self, connection):
        with self.create_table(connection, "users", uid="INT"):
            with contextlib.closing(connection.cursor(DictCursor)) as cur:
                for i in xrange(10):
                    cur.execute("INSERT INTO users (uid) VALUES (%s)", (i,))
                cur.execute("SELECT * FROM users")
                rows = cur.fetchmany()
                assert rows == [{"uid": 0}]
                rows = cur.fetchmany(2)
                assert rows == [{"uid": 1}, {"uid": 2}]

    def test_fetchone(self, connection):
        with self.create_table(connection, "salads", country="VARCHAR(20)"):
            with contextlib.closing(connection.cursor(DictCursor)) as cur:
                cur.execute("INSERT INTO salads (country) VALUES ('Italy')")
                cur.execute("SELECT * FROM salads")
                row = cur.fetchone()
                assert row == {"country": "Italy"}
                row = cur.fetchone()
                assert row is None