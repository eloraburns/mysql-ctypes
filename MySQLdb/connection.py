from ctypes import byref, pointer

from MySQLdb import cursors, libmysql


class Connection(object):
    MYSQL_ERROR_MAP = {}

    from MySQLdb.exceptions import (Warning, Error, InterfaceError,
        DatabaseError, OperationalError, IntegrityError, InternalError,
        ProgrammingError, NotSupportedError)

    def __init__(self, host=None, user=None, db=None):
        self._db = libmysql.c.mysql_init(None)
        res = libmysql.c.mysql_real_connect(self._db, host, user, None, db, 0, None, 0)
        if not res:
            self._exception()

    def __del__(self):
        if self._db:
            self.close()

    def _check_closed(self):
        if not self._db:
            raise ProgrammingError("closing a closed connection")

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


    def cursor(self):
        return cursors.Cursor(self)

def connect(*args, **kwargs):
    return Connection(*args, **kwargs)