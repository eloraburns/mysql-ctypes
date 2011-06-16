from setuptools import setup


setup(
    name="mysql-ctypes",
    description=("A MySQL wrapper that uses ctypes, aims to be a drop-in "
        "replacement for MySQLdb"),
    packages=["MySQLdb", "MySQLdb.constants"],
)
