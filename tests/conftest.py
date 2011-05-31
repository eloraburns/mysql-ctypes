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

def pytest_funcarg__connection(request):
    option = request.config.option
    return MySQLdb.connect(host=option.mysql_host, user=option.mysql_user)