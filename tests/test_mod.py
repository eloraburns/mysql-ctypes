import MySQLdb


class TestModule(object):
    def test_string_literal(self):
        assert MySQLdb.string_literal(2) == "'2'"
