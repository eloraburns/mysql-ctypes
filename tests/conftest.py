import MySQLdb


def pytest_addoption(parser):
    group = parser.getgroup("MySQL package options")
    group.addoption(
        "--mysql-host",
        default = "localhost",
        dest = "mysql_host",
    )
    group.addoption(
        "--mysql-user",
        default = "root",
        dest = "mysql_user",
    )
    group.addoption(
        "--mysql-database",
        default = "test_mysqldb",
        dest = "mysql_database",
    )

def pytest_funcarg__connection(request):
    option = request.config.option
    extra_kwargs = {}
    if hasattr(request.function, "connect_opts"):
        extra_kwargs = request.function.connect_opts.kwargs.copy()
    conn = MySQLdb.connect(
        host=option.mysql_host, user=option.mysql_user, db=option.mysql_database, **extra_kwargs
    )

    def close_conn():
        if not conn.closed:
            conn.close()

    request.addfinalizer(close_conn)
    return conn