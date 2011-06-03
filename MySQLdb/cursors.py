import collections
import itertools
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
    def __init__(self, connection, encoders, decoders):
        self.connection = weakref.proxy(connection)
        self.arraysize = 1
        self.encoders = encoders
        self.decoders = decoders

        self._result = None
        self._executed = None
        self.rowcount = -1

    def __del__(self):
        self.close()

    def _check_closed(self):
        if not self.connection or not self.connection._db:
            raise self.connection.ProgrammingError("cursor closed")

    def _check_executed(self):
        if not self._executed:
            raise self.connection.ProgrammingError("execute() first")

    def _clear(self):
        if self._result is not None:
            self._result.close()
            self._result = None
        self.rowcount = -1

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

    def _get_decoder(self, val):
        for decoder in self.decoders:
            res = decoder(self.connection, val)
            if res:
                return res

    def _escape_data(self, args):
        self._check_closed()
        if isinstance(args, tuple):
            return tuple(
                self._get_encoder(arg)(self.connection, arg)
                for arg in args
            )
        elif isinstance(args, collections.Mapping):
            return dict(
                (key, self._get_encoder(value)(self.connection, value))
                for key, value in args.iteritems()
            )
        raise self.connection.NotSupportedError("Unexpected type to "
            "execute/executemany for args: %s" % args)

    @property
    def description(self):
        if self._result is not None:
            return self._result.description
        return None

    def __iter__(self):
        return iter(self.fetchone, None)

    def close(self):
        self.connection = None
        if self._result is not None:
            self._result.close()
            self._result = None

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
            for arg in args:
                self.execute(query, arg)
        else:
            start, values, end = matched.group("start", "values", "end")
            sql_params = [
                values % self._escape_data(arg)
                for arg in args
            ]
            multirow_query = start + ",\n".join(sql_params) + end
            self._query(multirow_query)

    def callproc(self, procname, args=()):
        self._check_closed()
        self._clear()

        query = "SELECT %s(%s)" % (procname, ",".join(["%s"] * len(args)))
        if isinstance(query, unicode):
            query = _query.encode(self.connection.character_set_name())
        query %= self._escape_data(args)
        self._query(query)
        return args


    def fetchall(self):
        self._check_executed()
        if not self._result:
            return []
        return self._result.fetchall()

    def fetchmany(self, size=None):
        self._check_executed()
        if not self._result:
            return []
        if size is None:
            size = self.arraysize
        return self._result.fetchmany(size)

    def fetchone(self):
        self._check_executed()
        if not self._result:
            return None
        return self._result.fetchone()

    def setinputsizes(self, *args):
        pass

    def setoutputsize(self, *args):
        pass

class DictCursor(Cursor):
    def _make_row(self, row):
        return dict(
            (description[0], value)
            for description, value in itertools.izip(self._result.description, row)
        )

    def fetchall(self):
        rows = super(DictCursor, self).fetchall()
        return [self._make_row(row) for row in rows]

    def fetchmany(self, size=None):
        rows = super(DictCursor, self).fetchmany(size)
        return [self._make_row(row) for row in rows]

    def fetchone(self):
        row = super(DictCursor, self).fetchone()
        if row is not None:
            row = self._make_row(row)
        return row

_Description = collections.namedtuple("Description", [
    "name", "type_code", "display_size", "internal_size", "precision", "scale", "null_ok"
])
class Description(_Description):
    def __new__(cls, *args, **kwargs):
        charsetnr = kwargs.pop("charsetnr")
        self = super(Description, cls).__new__(cls, *args, **kwargs)
        self.charsetnr = charsetnr
        return self

class Result(object):
    def __init__(self, cursor):
        self.cursor = cursor
        self._result = libmysql.c.mysql_store_result(self.cursor.connection._db)
        self.description = None
        self.rows = None
        self.row_index = 0
        # TOOD: this is a hack, find a better way.
        if self.cursor._executed.upper().startswith("CREATE"):
            cursor.rowcount = -1
        else:
            cursor.rowcount = libmysql.c.mysql_affected_rows(cursor.connection._db)
        if not self._result:
            cursor.lastrowid = libmysql.c.mysql_insert_id(cursor.connection._db)
            return


        self.description = self._describe()
        self.row_decoders = [
            self.cursor._get_decoder(field)
            for field in self.description
        ]

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
        for i, decoder in enumerate(self.row_decoders):
            if not row[i]:
                r[i] = None
            else:
                val = "".join([row[i][j] for j in xrange(lengths[i])])
                r[i] = decoder(val)

        return tuple(r)

    def _describe(self):
        n = libmysql.c.mysql_num_fields(self._result)
        fields = libmysql.c.mysql_fetch_fields(self._result)
        d = [None] * n
        for i in xrange(n):
            d[i] = Description(
                fields[i].name,
                fields[i].type,
                fields[i].max_length,
                fields[i].length,
                fields[i].length,
                fields[i].decimals,
                None,
                charsetnr=fields[i].charsetnr
            )
        return tuple(d)

    def _check_rows(self, meth):
        if self.rows is None:
            raise self.cursor.connection.ProgrammingError("Can't %s from a "
                "query with no result rows" % meth)

    def close(self):
        if self._result:
            libmysql.c.mysql_free_result(self._result)
        self._result = None

    def flush(self):
        if self._result:
            while True:
                row = self._get_row()
                if row is None:
                    break
                self.rows.append(row)

    def fetchall(self):
        self._check_rows("fetchall")
        if self._result:
            self.flush()
        rows = self.rows[self.row_index:]
        self.row_index = len(self.rows)
        return rows

    def fetchmany(self, size):
        self._check_rows("fetchmany")
        if self._result:
            for i in xrange(size - (len(self.rows) - self.row_index)):
                row = self._get_row()
                if row is None:
                    break
                self.rows.append(row)
        if self.row_index >= len(self.rows):
            return []
        row_end = self.row_index + size
        if row_end >= len(self.rows):
            row_end = len(self.rows)
        rows = self.rows[self.row_index:row_end]
        self.row_index = row_end
        return rows

    def fetchone(self):
        self._check_rows("fetchone")

        if self.row_index >= len(self.rows):
            row = self._get_row()
            if row is None:
                return
            self.rows.append(row)
        row = self.rows[self.row_index]
        self.row_index += 1
        return row