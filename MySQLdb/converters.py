from datetime import datetime, date

from MySQLdb.constants import field_types


def literal(value):
    return lambda conn, obj: value

def unicode_to_quoted_sql(connection, obj):
    return connection.string_literal(obj.encode(connection.character_set_name()))


def object_to_quoted_sql(connection, obj):
    if hasattr(obj, "__unicode__"):
        return unicode_to_sql(connection, obj)
    return connection.string_literal(str(obj))

def none_encoder(obj):
    if obj is None:
        return literal("NULL")

def literal_encoder(obj):
    if isinstance(obj, int):
        return literal(str(obj))

def unicode_encoder(obj):
    if isinstance(obj, unicode):
        return unicode_to_quoted_sql

def fallback_encoder(obj):
    return object_to_quoted_sql

DEFAULT_ENCODERS = [
    none_encoder,
    literal_encoder,
    unicode_encoder,
    fallback_encoder,
]


def unicode_decoder(connection, field):
    if field[1] == field_types.BLOB:
        char_set = connection.character_set_name()
        return lambda value: value.decode(char_set)

def datetime_decoder(value):
    date, time = value.split(" ", 1)
    return datetime(*[int(part) for part in date.split("-") + time.split(":")])

def date_decoder(value):
    return date(*[int(part) for part in value.split("-")])

_simple_field_decoders = {
    field_types.TINY: int,
    field_types.LONG: int,
    field_types.LONGLONG: int,

    field_types.VAR_STRING: str,
    field_types.STRING: str,

    field_types.DATETIME: datetime_decoder,
    field_types.DATE: date_decoder,
}

def fallback_decoder(connection, field):
    return _simple_field_decoders.get(field[1])

DEFAULT_DECODERS = [
    unicode_decoder,
    fallback_decoder,
]