import ctypes


class MYSQL(ctypes.Structure):
    _fields_ = []
MYSQL_P = ctypes.POINTER(MYSQL)

c = ctypes.CDLL("libmysqlclient.so")

c.mysql_init.argtypes = [MYSQL_P]
c.mysql_init.restype = MYSQL_P

c.mysql_real_connect.argtypes = [
    MYSQL_P,            # connection
    ctypes.c_char_p,    # host
    ctypes.c_char_p,    # user
    ctypes.c_char_p,    # password
    ctypes.c_char_p,    # database
    ctypes.c_int,       # port
    ctypes.c_char_p,    # unix socket
    ctypes.c_ulong      # client_flag
]
c.mysql_real_connect.restype = MYSQL_P

c.mysql_error.argtypes = [MYSQL_P]
c.mysql_error.restype = ctypes.c_char_p