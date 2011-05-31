from datetime import date as Date
from time import localtime

from MySQLdb.connection import connect
from MySQLdb.exceptions import (Warning, Error, InterfaceError, DatabaseError,
    OperationalError, IntegrityError, InternalError, ProgrammingError,
    NotSupportedError)
from MySQLdb.types import BINARY, DATETIME, NUMBER


def Binary(x):
    return str(x)

def DateFromTicks(ticks):
    return Date(*localtime(ticks)[:3])