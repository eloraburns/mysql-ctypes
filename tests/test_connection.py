import contextlib

import py

from MySQLdb.cursors import DictCursor

from .base import BaseMySQLTests


class TestConnection(BaseMySQLTests):
    def test_custom_cursor_class(self, connection):
        with contextlib.closing(connection.cursor(DictCursor)) as cur:
            assert type(cur) is DictCursor

    def test_closed_rollback(self, connection):
        connection.close()
        with py.test.raises(connection.InterfaceError):
            connection.rollback()

    def test_closed_property(self, connection):
        assert not connection.closed
        connection.close()
        assert connection.closed

    def test_string_literal(self, connection):
        assert connection.string_literal(3) == "'3'"

    @py.test.mark.connect_opts(sql_mode="ANSI")
    def test_sql_mode(self, connection):
        with self.create_table(connection, "people", age="INT"):
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute('SELECT "people"."age" FROM "people"')
                rows = cursor.fetchall()
                assert rows == []