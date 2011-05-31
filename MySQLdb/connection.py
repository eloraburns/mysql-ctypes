from ctypes import byref, pointer

from MySQLdb import cursors, libmysql
from MySQLdb.exceptions import OperationalError


class Connection(object):
    MYSQL_ERROR_MAP = {}

    def __init__(self, host=None, user=None, db=None):
        self._db = libmysql.c.mysql_init(None)
        res = libmysql.c.mysql_real_connect(self._db, host, user, None, db, 0, None, 0)
        if not res:
            self._exception()

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
                err_cls = OperationalError
        raise err_cls(err, libmysql.c.mysql_error(self._db))

    def cursor(self):
        return cursors.Cursor(self)

def connect(*args, **kwargs):
    return Connection(*args, **kwargs)