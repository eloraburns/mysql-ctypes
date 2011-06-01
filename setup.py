from setuptools import setup, find_packages


setup(
    name="mysql-ctypes",
    description=("A MySQL wrapper that uses ctypes, aims to be a drop-in "
        "replacement for MySQLdb"),
    packages=find_packages(),
)