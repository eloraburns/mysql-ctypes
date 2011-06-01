from MySQLdb.constants import field_types


def object_to_quoted_sql(connection, obj):
    if hasattr(obj, "__unicode__"):
        return unicode_to_sql(connection, obj)
    return connection.string_literal(str(obj))


def fallback_encoder(obj):
    return object_to_quoted_sql


DEFAULT_ENCODERS = [
    fallback_encoder,
]


_simple_field_decoders = {
    field_types.LONG: int,
}

def fallback_decoder(field):
    return _simple_field_decoders.get(field[1])

DEFAULT_DECODERS = [
    fallback_decoder,
]