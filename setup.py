from setuptools import setup


setup(
    name="mysql-ctypes",
    version = "0.5",
    author = "Alex Gaynor and Quora",
    author_email = "alex.gaynor@gmail.com",
    description=("A MySQL wrapper that uses ctypes, aims to be a drop-in "
        "replacement for MySQLdb"),
    packages=["MySQLdb", "MySQLdb.constants"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database",
    ],
)
