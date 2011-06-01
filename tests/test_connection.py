import contextlib

from MySQLdb.cursors import DictCursor

from .base import BaseMySQLTests


class TestConnection(BaseMySQLTests):
    def test_custom_cursor_class(self, connection):
        with contextlib.closing(connection.cursor(DictCursor)) as cur:
            assert type(cur) is DictCursor