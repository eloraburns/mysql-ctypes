from datetime import datetime

from MySQLdb.constants import field_types


def object_to_quoted_sql(connection, obj):
    if hasattr(obj, "__unicode__"):
        return unicode_to_sql(connection, obj)
    return connection.string_literal(str(obj))

def none_encoder(obj):
    if obj is None:
        return lambda connection, obj: "NULL"

def fallback_encoder(obj):
    return object_to_quoted_sql

DEFAULT_ENCODERS = [
    none_encoder,
    fallback_encoder,
]


def datetime_decoder(value):
    date, time = value.split(" ", 1)
    return datetime(*[int(part) for part in date.split("-") + time.split(":")])

_simple_field_decoders = {
    field_types.LONG: int,
    field_types.LONGLONG: int,
    field_types.VAR_STRING: str,
    field_types.BLOG: unicode,
    field_types.DATETIME: datetime_decoder,
}

def fallback_decoder(field):
    return _simple_field_decoders.get(field[1])

DEFAULT_DECODERS = [
    fallback_decoder,
]