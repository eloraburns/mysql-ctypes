import contextlib
import datetime

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

    def test_iterable(self, connection):
        with self.create_table(connection, "users", uid="INT"):
            with contextlib.closing(connection.cursor()) as cur:
                cur.executemany("INSERT INTO users (uid) VALUES (%s)", [(i,) for i in xrange(5)])
                cur.execute("SELECT * FROM users")
                x = iter(cur)
                row = cur.fetchone()
                assert row == (0,)
                row = x.next()
                assert row == (1,)
                rows = cur.fetchall()
                assert rows == [(2,), (3,), (4,)]
                with py.test.raises(StopIteration):
                    x.next()

    def test_lastrowid(self, connection):
        with self.create_table(connection, "users", uid="INT NOT NULL AUTO_INCREMENT", primary_key="uid"):
            with contextlib.closing(connection.cursor()) as cur:
                cur.execute("INSERT INTO users () VALUES ()")
                assert cur.lastrowid

    def test_longlong(self, connection):
        with contextlib.closing(connection.cursor()) as cur:
            cur.execute("SHOW COLLATION")
            cur.fetchone()

    def test_datetime(self, connection):
        with contextlib.closing(connection.cursor()) as cur:
            cur.execute("SELECT SYSDATE()")
            row = cur.fetchone()
            now = datetime.datetime.now()
            assert row[0].date() == now.date()
            assert row[0].hour == now.hour
            # ~1 in 60 chance of spurious failure, i'll take those odds
            assert row[0].minute == now.minute

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
                cur.executemany("INSERT INTO users (uid) VALUES (%s)", [(i,) for i in xrange(10)])
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