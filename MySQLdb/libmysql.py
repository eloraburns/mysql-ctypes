import ctypes


class MYSQL(ctypes.Structure):
    _fields_ = []
MYSQL_P = ctypes.POINTER(MYSQL)

class MYSQL_RES(ctypes.Structure):
    _fields_ = []
MYSQL_RES_P = ctypes.POINTER(MYSQL_RES)

MYSQL_ROW = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))

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

c.mysql_real_query.argtypes = [MYSQL_P, ctypes.c_char_p, ctypes.c_ulong]
c.mysql_real_query.restype = ctypes.c_int

c.mysql_query.argtypes = [MYSQL_P, ctypes.c_char_p]
c.mysql_query.restype = ctypes.c_int

c.mysql_store_result.argtypes = [MYSQL_P]
c.mysql_store_result.restype = MYSQL_RES_P

c.mysql_num_fields.argtypes = [MYSQL_RES_P]
c.mysql_num_fields.restype = ctypes.c_uint

c.mysql_fetch_row.argtypes = [MYSQL_RES_P]
c.mysql_fetch_row.restype = MYSQL_ROW

c.mysql_fetch_lengths.argtypes = [MYSQL_RES_P]
c.mysql_fetch_lengths.restype = ctypes.POINTER(ctypes.c_ulong)