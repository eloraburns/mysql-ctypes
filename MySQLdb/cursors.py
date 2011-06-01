import collections
import re
import weakref

from MySQLdb import libmysql


INSERT_VALUES = re.compile(
    r"(?P<start>.+values\s*)"
    r"(?P<values>\(((?<!\\)'[^\)]*?\)[^\)]*(?<!\\)?'|[^\(\)]|(?:\([^\)]*\)))+\))"
    r"(?P<end>.*)",
    re.I
)



class Cursor(object):
    def __init__(self, connection, encoders):
        self.connection = weakref.proxy(connection)
        self.arraysize = 1
        self.encoders = encoders

        self._result = None
        self._executed = None

    def _check_closed(self):
        if not self.connection:
            raise ProgrammingError("cursor closed")

    def _check_executed(self):
        if not self._executed:
            raise self.connection.ProgrammingError("execute() first")

    def _clear(self):
        if self._result is not None:
            self._result = None
        del self.rowcount

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

    def _escape_data(self, args):
        if isinstance(args, tuple):
            return tuple(
                self._get_encoder(arg)(self.connection, arg)
                for arg in args
            )
        elif isinstance(args, collections.Mapping):
            return {
                key: self._get_encoder(value)(self.connection, value)
                for key, value in args.iteritems()
            }
        raise self.connection.NotSupportedException("Unexpected type to "
            "execute/executemany for args: %s" % args)


    @property
    def description(self):
        if self._result is not None:
            return self._result.description
        return None

    @property
    def rowcount(self):
        if hasattr(self, "_rowcount"):
            return self._rowcount
        if self._result is not None:
            return self._result.rowcount
        return -1

    @rowcount.setter
    def rowcount(self, rowcount):
        self._rowcount = rowcount

    @rowcount.deleter
    def rowcount(self):
        if hasattr(self, "_rowcount"):
            del self._rowcount

    def close(self):
        if not self.connection:
            return

        self.connection = None

    def execute(self, query, args=None):
        self._check_closed()
        self._clear()

        if isinstance(query, unicode):
            query = query.encode(self.connection.character_set_name())
        if args is not None:
            query %= self._escape_data(args)
        self._query(query)

    def executemany(self, query, args):
        self._check_closed()
        self._clear()
        if not args:
            return

        if isinstance(query, unicode):
            query = query.encode(self.connection.character_set_name())
        matched = INSERT_VALUES.match(query)
        if not matched:
            rowcount = 0
            for arg in args:
                self.execute(query, arg)
                rowcount += self.rowcount
            self.rowcount = rowcount
        else:
            start, values, end = matched.group("start", "values", "end")
            sql_params = [
                values % self._escape_data(arg)
                for arg in args
            ]
            multirow_query = start + ",\n".join(sql_params) + end
            self._query(multirow_query)

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
        self.rowcount = -1
        self.rows = None
        self.row_index = 0
        if not self._result:
            return

        self._nfields = libmysql.c.mysql_num_fields(self._result)
        self.description = self._describe()
        self.rowcount = libmysql.c.mysql_affected_rows(self.cursor.connection._db)

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
        if self.rows is None:
            raise self.cursor.connection.ProgrammingError("Can't fetchall() "
                "from a query with no result rows")
        if self._result:
            self.flush()
        rows = self.rows[self.row_index:]
        self.row_index = len(self.rows)
        return rows