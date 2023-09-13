#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'sqlalchemy_frontier',
    version = '2.10.2',
    description = 'sqlalchemy driver for frontier_client',    
    data_files = [('connectors',['connectors/frontier.py']),('dialects/oracle',['dialects/oracle/frontier_client_ctypes.py','dialects/oracle/frontier_dbapi.py','dialects/oracle/frontier.py'])],
    py_modules = []
)

