from datetime import datetime, date, time, timedelta
from decimal import Decimal


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
    if field[1] not in [field_types.BLOB]:
        return

    # Magic binary charset
    if field.charsetnr == 63:
        return str

    charset = connection.character_set_name()
    return lambda value: value.decode(charset)

def datetime_decoder(value):
    date_part, time_part = value.split(" ", 1)
    return datetime.combine(
        date_decoder(date_part),
        time(*[int(part) for part in time_part.split(":")])
    )

def date_decoder(value):
    return date(*[int(part) for part in value.split("-")])

def time_decoder(value):
    return timedelta(*[int(part) for part in value.split(":")])

def timestamp_decoder(value):
    if " " in value:
        return datetime_decoder(value)
    raise NotImplementedError

_simple_field_decoders = {
    field_types.TINY: int,
    field_types.LONG: int,
    field_types.LONGLONG: int,
    field_types.YEAR: int,

    field_types.FLOAT: float,
    field_types.DOUBLE: float,

    field_types.NEWDECIMAL: Decimal,

    field_types.VAR_STRING: str,
    field_types.STRING: str,

    field_types.DATETIME: datetime_decoder,
    field_types.DATE: date_decoder,
    field_types.TIME: time_decoder,
    field_types.TIMESTAMP: timestamp_decoder,
}

def fallback_decoder(connection, field):
    return _simple_field_decoders.get(field[1])

DEFAULT_DECODERS = [
    unicode_decoder,
    fallback_decoder,
]