# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

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

    def value_to_db_date(self, value):
        if value is None:
            return None
        return long((value - datetime.date(1970, 1, 1)).total_seconds() * 1000)

    def value_to_db_datetime(self, value):
        if value is None:
            return None
        start_point = datetime.datetime(1970, 1, 1, tzinfo=value.tzinfo)
        offset = start_point.tzinfo.utcoffset(start_point).total_seconds() \
            if start_point.tzinfo else 0
        return str(long(((value - start_point).total_seconds() - offset) * 1000))

    def value_to_db_time(self, value):
        if value is None:
            return None
        def time_to_datetime(time):
            return datetime.datetime.combine(datetime.datetime(1970, 1, 1), time)
        time_delta = time_to_datetime(value) - datetime.datetime(1970, 1, 1)
        return long(time_delta.total_seconds() * 1000000)

    def convert_values(self, value, field):

        if value is None and field and field.empty_strings_allowed:
            value = ''

        if value is None or field is None:
            return value

        internal_type = field.get_internal_type()

        if internal_type == 'FloatField':
            return float(value)

        if internal_type.endswith('IntegerField'):
            return int(value)

        if value in (1, 0) and field and internal_type in \
            ('BooleanField', 'NullBooleanField'):
            value = bool(value)

        if internal_type == 'TimeField':
            internal_microseconds = value
            delta_time = datetime.timedelta(microseconds=internal_microseconds)
            return (datetime.datetime(1970, 1, 1) + delta_time).time()

        if internal_type in ('DateField', 'DateTimeField'):
            internal_timestamp = long(value.encode('hex'), 16) / 1000
            internal_date = datetime.datetime.utcfromtimestamp(internal_timestamp)
            return internal_date

        return value

#    def bulk_insert_sql(self, fields, num_values):
#        items_sql = "(%s)" % ", ".join(["%s"] * len(fields))
#        return "VALUES " + ", ".join([items_sql] * num_values)
