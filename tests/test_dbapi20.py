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
            "db": option.mysql_database,
        }