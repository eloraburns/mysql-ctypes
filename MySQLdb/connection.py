from ctypes import byref, pointer, create_string_buffer, string_at

from MySQLdb import cursors, libmysql, converters


class Connection(object):
    MYSQL_ERROR_MAP = {}

    from MySQLdb.exceptions import (Warning, Error, InterfaceError,
        DatabaseError, OperationalError, IntegrityError, InternalError,
        ProgrammingError, NotSupportedError)

    def __init__(self, host=None, user=None, db=None, port=0, client_flag=0, encoders=None, decoders=None):
        self._db = libmysql.c.mysql_init(None)
        res = libmysql.c.mysql_real_connect(self._db, host, user, None, db, port, None, client_flag)
        if not res:
            self._exception()
        if encoders is None:
            encoders = converters.DEFAULT_ENCODERS
        if decoders is None:
            decoders = converters.DEFAULT_DECODERS
        self.encoders = encoders
        self.decoders = decoders

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

    def cursor(self, cursor_class=None, encoders=None, decoders=None):
        if cursor_class is None:
            cursor_class = cursors.Cursor
        if encoders is None:
            encoders = self.encoders[:]
        if decoders is None:
            decoders = self.decoders[:]
        return cursor_class(self, encoders=encoders, decoders=decoders)

    def string_literal(self, obj):
        buf = create_string_buffer(len(obj) * 2)
        length = libmysql.c.mysql_real_escape_string(self._db, buf, obj, len(obj))
        return "'%s'" % string_at(buf, length)

    def get_server_info(self):
        self._check_closed()
        return libmysql.c.mysql_get_server_info(self._db)

def connect(*args, **kwargs):
    return Connection(*args, **kwargs)