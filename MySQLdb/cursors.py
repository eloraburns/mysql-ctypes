import collections
import weakref

from MySQLdb import libmysql


class Cursor(object):
    def __init__(self, connection, encoders):
        self.connection = weakref.proxy(connection)
        self.arraysize = 1
        self.rowcount = -1
        self.encoders = encoders

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

    def _get_encoder(self, val):
        for encoder in self.encoders:
            res = encoder(val)
            if res:
                return res


    @property
    def description(self):
        if self._result is not None:
            return self._result.description
        return None

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
            if isinstance(args, tuple):
                query %= tuple(
                    self._get_encoder(arg)(self.connection, arg)
                    for arg in args
                )
            elif isinstance(args, collections.Mapping):
                query %= {
                    key: self._get_encoder(value)(self.connection, value)
                    for key, value in args.iteritems()
                }
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
        self.description = None
        if not self._result:
            return
        self._nfields = libmysql.c.mysql_num_fields(self._result)
        self.description = self._describe()

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

    def _describe(self):
        n = libmysql.c.mysql_num_fields(self._result)
        fields = libmysql.c.mysql_fetch_fields(self._result)
        d = [None] * n
        for i in xrange(n):
            d[i] = (
                fields[i].name,
                fields[i].type,
                fields[i].max_length,
                fields[i].length,
                fields[i].length,
                fields[i].decimals,
                None
            )
        return tuple(d)

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