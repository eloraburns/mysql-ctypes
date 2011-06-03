import ctypes
from ctypes.util import find_library


class MYSQL(ctypes.Structure):
    _fields_ = []
MYSQL_P = ctypes.POINTER(MYSQL)

class MYSQL_RES(ctypes.Structure):
    _fields_ = []
MYSQL_RES_P = ctypes.POINTER(MYSQL_RES)

MYSQL_ROW = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))

class MYSQL_FIELD(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("org_name", ctypes.c_char_p),
        ("table", ctypes.c_char_p),
        ("org_table", ctypes.c_char_p),
        ("db", ctypes.c_char_p),
        ("catalog", ctypes.c_char_p),
        ("def", ctypes.c_char_p),
        ("length", ctypes.c_ulong),
        ("max_length", ctypes.c_ulong),
        ("name_length", ctypes.c_uint),
        ("org_name_length", ctypes.c_uint),
        ("table_length", ctypes.c_uint),
        ("org_table_length", ctypes.c_uint),
        ("db_length", ctypes.c_uint),
        ("catalog_length", ctypes.c_uint),
        ("def_length", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("decimals", ctypes.c_uint),
        ("charsetnr", ctypes.c_uint),
        ("type", ctypes.c_int),
        ("extension", ctypes.c_void_p),
    ]
MYSQL_FIELD_P = ctypes.POINTER(MYSQL_FIELD)

c = ctypes.CDLL(find_library("mysqlclient"))

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

c.mysql_errno.argtypes = [MYSQL_P]
c.mysql_errno.restype = ctypes.c_uint

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

c.mysql_fetch_fields.argtypes = [MYSQL_RES_P]
c.mysql_fetch_fields.restype = MYSQL_FIELD_P

c.mysql_escape_string.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong]
c.mysql_escape_string.restype = ctypes.c_ulong

c.mysql_real_escape_string.argtypes = [MYSQL_P, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong]
c.mysql_real_escape_string.restype = ctypes.c_ulong

c.mysql_affected_rows.argtypes = [MYSQL_P]
c.mysql_affected_rows.restype = ctypes.c_ulonglong

c.mysql_get_server_info.argtypes = [MYSQL_P]
c.mysql_get_server_info.restype = ctypes.c_char_p

c.mysql_insert_id.argtypes = [MYSQL_P]
c.mysql_insert_id.restype = ctypes.c_ulonglong

c.mysql_autocommit.argtypes = [MYSQL_P, ctypes.c_char]
c.mysql_autocommit.restype = ctypes.c_char

c.mysql_commit.argtypes = [MYSQL_P]
c.mysql_commit.restype = ctypes.c_char

c.mysql_rollback.argtypes = [MYSQL_P]
c.mysql_rollback.restype = ctypes.c_char

c.mysql_set_character_set.argtypes = [MYSQL_P, ctypes.c_char_p]
c.mysql_set_character_set.restype = ctypes.c_int

c.mysql_close.argtypes = [MYSQL_P]
c.mysql_close.restype = None

c.mysql_free_result.argtypes = [MYSQL_RES_P]
c.mysql_free_result.restype = None

c.mysql_character_set_name.argtypes = [MYSQL_P]
c.mysql_character_set_name.restype = ctypes.c_char_p