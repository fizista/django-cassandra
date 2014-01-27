# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db.backends import BaseDatabaseIntrospection, FieldInfo
from django.utils.encoding import force_text


class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Maps type codes to Django Field types.
    data_types_reverse = {
        16: 'BooleanField',
        17: 'BinaryField',
        20: 'BigIntegerField',
        21: 'SmallIntegerField',
        23: 'IntegerField',
        25: 'TextField',
        700: 'FloatField',
        701: 'FloatField',
        869: 'GenericIPAddressField',
        1042: 'CharField',  # blank-padded
        1043: 'CharField',
        1082: 'DateField',
        1083: 'TimeField',
        1114: 'DateTimeField',
        1184: 'DateTimeField',
        1266: 'TimeField',
        1700: 'DecimalField',
    }

    ignored_tables = []

    def get_table_list(self, cursor):
        "Returns a list of table names in the current database."
        cursor.execute(b"""
            SELECT columnfamily_name 
            FROM system.schema_columnfamilies 
            WHERE keyspace_name = '%s';
        """ % (cursor.db.get_connection_params()[1]['keyspace'],))
        query_out = cursor.fetchall()
        if query_out:
            tables = zip(*query_out)[0]
            return tables
        else:
            return []

