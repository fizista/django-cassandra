# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import cql
from django.db.utils import DatabaseError

from djangotoolbox.db.base import (
    NonrelDatabaseFeatures,
    NonrelDatabaseOperations,
    NonrelDatabaseWrapper,
    NonrelDatabaseClient,
    NonrelDatabaseValidation,
    NonrelDatabaseIntrospection,
    NonrelDatabaseCreation
)


class DatabaseWrapper(NonrelDatabaseWrapper):

    Database = Database

    CQL_VERSION = '3.1.2'

    def __init__(self, *args, **kwds):
        super(DatabaseWrapper, self).__init__(*args, **kwds)



    def get_connection_params(self):


        args_params = []
        kwargs_params = {}

        args_params.append(self.settings('HOST', 'localhost'))

        kwargs_params['port'] = self.settings('PORT', None)
        kwargs_params['keyspace'] = self.settings('KEYSPACE')
        kwargs_params['user'] = self.settings('USER', None)
        kwargs_params['password'] = self.settings('PASSWORD', None)
        kwargs_params['cql_version'] = DatabaseWrapper.CQL_VERSION
        kwargs_params['native'] = self.settings('NATIVE', False)
        kwargs_params['compression'] = self.settings('COMPRESSION', None)
        kwargs_params['consistency_level'] = self.settings('CONSISTENCY_LEVEL', 'ONE')
        kwargs_params['transport'] = self.settings('TRANSPORT', None)

        return args_params, kwargs_params

    def get_new_connection(self, conn_params):
        connection = cql.connect(*conn_params[0], **conn_params[1])
        self.Database = connection.__class__
        return connection

    def get_db_cursor(self):
        query = \
            '''
            USE %(keyspace)s;
            ''' % {'keyspace':self.keyspace_name}
        self.cursor.execute(query)


    def get_db_connection(self):

        if self._db_connection:
            return self._db_connection

        host = self.settings('HOST', 'localhost')
        port = self.settings('PORT', 9160)
        name = self.settings('NAME')
        user = self.settings('USER', '')
        password = self.settings('PASSWORD', '')

        self._db_connection = cql.connect(
            host,
            port,
            cql_version=settings.CASSANDRA_CQL_VERSION
            )

        # TODO: get supportes CQL
        self.cursor = self.connection.cursor()
        self.keyspace_name = name

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
