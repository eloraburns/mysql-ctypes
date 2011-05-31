def object_to_quoted_sql(connection, obj):
    if hasattr(obj, "__unicode__"):
        return unicode_to_sql(connection, obj)
    return connection.string_literal(str(obj))


def fallback_encoder(obj):
    return object_to_quoted_sql


DEFAULT_ENCODERS = [
    fallback_encoder,
]