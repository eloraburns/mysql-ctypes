import contextlib


class BaseMySQLTests(object):
    @contextlib.contextmanager
    def create_table(self, connection, table_name, **fields):
        pk = fields.pop("primary_key", None)
        with contextlib.closing(connection.cursor()) as cursor:
            # TODO: this could return data unexpectadly because the fields are
            # in arbitrary order, you have been warned.
            fields = ", ".join(
                "%s %s" % (name, field_type)
                for name, field_type in fields.iteritems()
            )
            if pk is not None:
                fields += ", PRIMARY KEY (%s)" % pk
            cursor.execute("CREATE TABLE %s (%s)" % (table_name, fields))
        try:
            yield
        finally:
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute("DROP TABLE %s" % table_name)