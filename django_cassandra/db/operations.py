# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db.backends import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):

    compiler_module = "django_cassandra.db.compiler"

    def __init__(self, connection):
        super(DatabaseOperations, self).__init__(connection)

    def quote_name(self, name):
        if name.startswith(b'"') and name.endswith(b'"'):
            return name  # Quoting once is enough.
        return b'"%s"' % name

    def start_transaction_sql(self):
        """
        Returns the SQL statement required to start a transaction.
        """
        return ""

    def end_transaction_sql(self, success=True):
        """
        Returns the SQL statement required to end a transaction.
        """
        return ""

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        if tables:
            sql = []
            for table in tables:
                sql = ['%s %s;' % (
                    style.SQL_KEYWORD('TRUNCATE'),
                    style.SQL_FIELD(self.quote_name(table)),
                )]
            sql.extend(self.sequence_reset_by_name_sql(style, sequences))
            return sql
        else:
            return []

#    def bulk_insert_sql(self, fields, num_values):
#        items_sql = "(%s)" % ", ".join(["%s"] * len(fields))
#        return "VALUES " + ", ".join([items_sql] * num_values)
