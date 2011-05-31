import contextlib


class BaseMySQLTests(object):
    @contextlib.contextmanager
    def create_table(self, connection, table_name):
        with contextlib.closing(connection.cursor()) as cursor:
            cursor.execute("CREATE TABLE %s (name VARCHAR(100))" % table_name)
        try:
            yield
        finally:
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute("DROP TABLE %s" % table_name)