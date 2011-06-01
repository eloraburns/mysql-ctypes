from ctypes import byref, pointer, create_string_buffer, string_at

from MySQLdb import cursors, libmysql, converters


class Connection(object):
    MYSQL_ERROR_MAP = {}

    from MySQLdb.exceptions import (Warning, Error, InterfaceError,
        DatabaseError, OperationalError, IntegrityError, InternalError,
        ProgrammingError, NotSupportedError)

    def __init__(self, host=None, user=None, db=None, encoders=None):
        self._db = libmysql.c.mysql_init(None)
        res = libmysql.c.mysql_real_connect(self._db, host, user, None, db, 0, None, 0)
        if not res:
            self._exception()
        if encoders is None:
            encoders = converters.DEFAULT_ENCODERS
        self.encoders = encoders

    def __del__(self):
        if self._db:
            self.close()

    def _check_closed(self):
        if not self._db:
            raise self.ProgrammingError("closing a closed connection")

    def _has_error(self):
        return libmysql.c.mysql_errno(self._db) != 0

    def _exception(self):
        err = libmysql.c.mysql_errno(self._db)
        if not err:
            err_cls = InterfaceError
        else:
            if err in self.MYSQL_ERROR_MAP:
                err_cls = self.MYSQL_ERROR_MAP[err]
            elif err < 1000:
                err_cls = InternalError
            else:
                err_cls = self.OperationalError
        raise err_cls(err, libmysql.c.mysql_error(self._db))

    def close(self):
        self._check_closed()
        libmysql.c.mysql_close(self._db)
        self._db = None

    def commit(self):
        self._check_closed()
        res = libmysql.c.mysql_query(self._db, "COMMIT")
        if res:
            self._exception()

    def rollback(self):
        self._check_closed()
        res = libmysql.c.mysql_query(self._db, "ROLLBACK")
        if res:
            self._exception()

    def cursor(self, encoders=None):
        if encoders is None:
            encoders = self.encoders[:]
        return cursors.Cursor(self, encoders=encoders)

    def string_literal(self, obj):
        buf = create_string_buffer(len(obj) * 2)
        length = libmysql.c.mysql_real_escape_string(self._db, buf, obj, len(obj))
        return "'%s'" % string_at(buf, length)

def connect(*args, **kwargs):
    return Connection(*args, **kwargs)