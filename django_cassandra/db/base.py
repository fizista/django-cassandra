"""
Cassandra database backend for Django.

"""
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from thrift.transport.TTransport import TTransportException

from django.db.utils import (
    DatabaseError,
    InterfaceError,
    NotSupportedError)
from django.db.backends import (
    BaseDatabaseFeatures,
    BaseDatabaseWrapper,
    BaseDatabaseValidation)

from . import CQL_VERSION
from .client import DatabaseClient
from .operations import DatabaseOperations
from .creation import DatabaseCreation
from .introspection import DatabaseIntrospection
from .patch import Database, connect


logger = logging.getLogger('django_cassandra.db')


class DatabaseFeatures(BaseDatabaseFeatures):
    needs_datetime_string_cast = False
    can_return_id_from_insert = False
    requires_rollback_on_dirty_transaction = False
    has_real_datatype = True
    can_defer_constraint_checks = True
    has_select_for_update = False
    has_select_for_update_nowait = False
    has_bulk_insert = False
    uses_savepoints = False
    supports_tablespaces = True
    supports_transactions = False
    can_distinct_on_fields = False
    can_rollback_ddl = False
    supports_combined_alters = False
    nulls_order_largest = True
    closed_cursor_error_class = InterfaceError
    has_case_insensitive_like = False


class DatabaseWrapper(BaseDatabaseWrapper):

    vendor = 'cassandra'

    operators = {
        'exact': '= %s',
        'iexact': '= UPPER(%s)',
        'contains': 'LIKE %s',
        'icontains': 'LIKE UPPER(%s)',
        'regex': '~ %s',
        'iregex': '~* %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'LIKE UPPER(%s)',
        'iendswith': 'LIKE UPPER(%s)',
    }

    Database = Database

    def __init__(self, *args, **kwds):
        super(DatabaseWrapper, self).__init__(*args, **kwds)

        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)

    def get_connection_params(self):

        args_params = []
        kwargs_params = {}

        args_params.append(self.settings('HOST', 'localhost'))

        kwargs_params['port'] = self.settings('PORT', None)
        kwargs_params['keyspace'] = self.settings('NAME')
        kwargs_params['user'] = self.settings('USER', None)
        kwargs_params['password'] = self.settings('PASSWORD', None)
        kwargs_params['cql_version'] = CQL_VERSION
        kwargs_params['native'] = self.settings('NATIVE', False)
        kwargs_params['compression'] = self.settings('COMPRESSION', None)
        kwargs_params['consistency_level'] = self.settings('CONSISTENCY_LEVEL', 'ONE')
        kwargs_params['transport'] = self.settings('TRANSPORT', None)

        return args_params, kwargs_params

    def get_new_connection(self, conn_params):
        connection = connect(*conn_params[0], **conn_params[1])
        return connection

    def init_connection_state(self):
        pass

    def create_cursor(self):
        cursor = self.connection.cursor()
        # TODO: add timezone
        return cursor

    def is_usable(self):
        try:
            keyspace = self.get_connection_params([1]['keyspace'])
            self.connection.cursor().execute('USE "%s"' % (keyspace,))
        except TTransportException:
            return False
        # If keyspace don't exists
        except cql.ProgrammingError:
            return False
        else:
            return True

    def _set_autocommit(self, autocommit):
        pass

    def _rollback(self):
        try:
            BaseDatabaseWrapper._rollback(self)
        except Database.NotSupportedError:
            pass
        except NotSupportedError:
            pass

    # ########################################################################
    # Helpers
    # ########################################################################

    def settings(self, name, default=(-1,)):
        """
        Small helper. 
        
        Return:
            settings[name] value or default value
        """
        conf = self.settings_dict.get(name, '')
        if conf:
            return conf

        if default != (-1,):
            return default

        raise Exception(
            'The parameter "{name}" is required. '
            'Add it to settings django!'.format(
                name=name
            ))
