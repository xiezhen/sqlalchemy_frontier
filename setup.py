#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'sqlalchemy_frontier',
    version = '2.8.19',
    description = 'sqlalchemy driver for frontier_client',    
    data_files = [('site-packages/sqlalchemy/connectors',['connectors/frontier.py']),('site-packages/sqlalchemy/dialects/oracle',['dialects/oracle/__init__.py','dialects/oracle/frontier_client_ctypes.py','dialects/oracle/frontier_dbapi.py','dialects/oracle/frontier.py'])]
)

