import py

import MySQLdb

from . import dbapi20


class MySQLDBAPI20Tests(dbapi20.DatabaseAPI20Test):
    driver = MySQLdb

    def setUp(self):
        from pytest import config

        option = config.option
        self.connect_kw_args = {
            "host": option.mysql_host,
            "user": option.mysql_user,
            "passwd": option.mysql_passwd,
            "db": option.mysql_database,
        }

    def is_table_does_not_exist(self, exc):
        return exc.args[0] == 1051

    def test_nextset(self):
        py.test.skip("No idea what this is, skipping for now")

    def test_setoutputsize(self):
        py.test.skip("No idea what this is, skipping for now")