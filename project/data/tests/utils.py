# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import cql
import datetime
import os
import time

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from pycallgraph import Config
try:
    from pycassa.pool import ConnectionPool
    from pycassa.columnfamily import ColumnFamily
    PYCASSA_TESTS = True
except ImportError:
    PYCASSA_TESTS = False
from django.db import connection


def clear_tables(*tables):
    """
    Deletes all data from database tables
    
    Args:
        tables - list of table names
    """
    cursor = connection.cursor()
    for table_name in tables:
        try:
            cursor.execute("TRUNCATE %s" % (table_name,))
        except Exception:
            pass


def count_rows(table_name, limit=200000):
    """
    Count rows
    
    Args:
        table_name - str - table name
        limit - int - limit counted rows
        
    Return:
        int
    """
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM %s LIMIT %d;' % (table_name, limit))
    return cursor.fetchall()[0][0]
