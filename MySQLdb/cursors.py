import weakref


class Cursor(object):
    def __init__(self, connection):
        self.connection = weakref.proxy(connection)

    def close(self):
        if not self.connection:
            return

        self.connection = None

    def execute(self, query, args=None):
        pass

    def fetchall(self):
        return []