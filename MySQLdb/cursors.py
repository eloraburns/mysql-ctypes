import weakref

from MySQLdb import libmysql


class Cursor(object):
    def __init__(self, connection):
        self.connection = weakref.proxy(connection)
        self._result = None

    def _check_closed(self):
        if not self.connection:
            raise ProgrammingError("cursor closed")

    def _check_executed(self):
        if not self._executed:
            raise ProgrammingError("execute() first")

    def _clear(self):
        if self._result is not None:
            self._result = None

    def _query(self, query):
        self._executed = query
        self.connection._check_closed()
        r = libmysql.c.mysql_real_query(self.connection._db, query, len(query))
        if r:
            self.connection._exception()
        self._result = Result(self)

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
        self._check_executed()
        if not self._result:
            return []
        return self._result.fetchall()

class Result(object):
    def __init__(self, cursor):
        self.cursor = cursor
        self._result = libmysql.c.mysql_store_result(self.cursor.connection._db)
        if not self._result:
            return
        self._nfields = libmysql.c.mysql_num_fields(self._result)

        self.rows = []

    def _get_row(self):
        row = libmysql.c.mysql_fetch_row(self._result)
        if not row:
            if self.cursor.connection._has_error():
                self.cursor.connection.exception()
            return
        n = libmysql.c.mysql_num_fields(self._result)
        lengths = libmysql.c.mysql_fetch_lengths(self._result)
        r = [None] * n
        for i in xrange(n):
            if not row[i]:
                r[i] = None
            else:
                r[i] = "".join([row[i][j] for j in xrange(lengths[i])])
        return tuple(r)

    def flush(self):
        if self._result:
            while True:
                row = self._get_row()
                if row is None:
                    break
                self.rows.append(row)

    def fetchall(self):
        if self._result:
            self.flush()
        return self.rows