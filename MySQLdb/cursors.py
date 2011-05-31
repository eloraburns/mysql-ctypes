import weakref

from MySQLdb import libmysql


class Cursor(object):
    def __init__(self, connection):
        self.connection = weakref.proxy(connection)
        self._result = None

    def _check_closed(self):
        if not self.connection:
            raise ProgrammingError("cursor closed")

    def _clear(self):
        if self._result is not None:
            self._result = None

    def _query(self, query):
        self._executed = query
        r = libmysql.c.mysql_real_query(self.connection._db, query, len(query))
        if r:
            self.connection._exception()

    def close(self):
        if not self.connection:
            return

        self.connection = None

    def execute(self, query, args=None):
        self._check_closed()
        self._clear()

        if isinstance(query, unicode):
            query = query.encode(db.character_set_name())
        if args is not None:
            raise NotImplementedError
        self._query(query)

    def fetchall(self):
        return []