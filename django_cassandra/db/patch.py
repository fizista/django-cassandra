# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import re
import cql as Database

from cql.thrifteries import (
    ThriftCursor as ThriftCursorPrimitive,
    ThriftConnection as ThriftConnectionPrimitive)
from cql.native import (
    NativeCursor as NativeCursorPrimitive,
    NativeConnection as NativeConnectionPrimitive)


class Counter(object):
    """
    Class counting calls.
    
    Example:
    
    > c1 = Counter()
    > c1()
    1
    > c1()
    2
    
    > c2 = Counter(lambda c: "-%d-" % (c,))
    > c2()
    '-1-'
    > c2()
    '-2-'
    
    """

    def __init__(self, out_function=None):
        """
        
        Args:
            out_function - method(counter)
        """
        self.counter = 0
        self.out_function = out_function

    def __call__(self, *args, **kwargs):
        """
        Return:
            method(counter, *args, **kwargs)
            OR
            counter - int
        """
        self.counter += 1
        if self.out_function:
            return self.out_function(self.counter, *args, **kwargs)
        else:
            return self.counter


re_param = re.compile('%s')
re_param_table_name = re.compile('("[^"]+")\.("[^"]+")')
re_none = re.compile('([^"\']\s*)(None)(\s*[^"\'])')
re_offset = re.compile('OFFSET\s+(\d+)')
re_limit = re.compile('LIMIT\s+(\d+)')

def execute_decorator(f):
    def execute(self, cql_query, params=None, *args, **kwargs):
        # #############################
        # The patches for SQL queries
        # #############################
#        if params:
#            # correct parameters "%s" => :d<x>, where x = 1,2,3,...
#            param_counter = Counter(lambda c, m: ":d%s " % (c,))
#            cql_query = re_param.sub(param_counter, cql_query)
#            params = dict([('d%s' % (k), v) for k, v in enumerate(params, 1)])

#        # remove the name of the table from parameters
#        cql_query = re_param_table_name.sub(lambda m: m.groups()[1], cql_query)
#
#        # remove "OFFSET <offset_number>", add LIMIT <limit_number>+<offset_number>
#        if 'OFFSET' in cql_query:
#            offset = int(re_offset.findall(cql_query)[0])
#            limit = int(re_limit.findall(cql_query)[0])
#            # remove offset
#            cql_query = re_offset.sub('', cql_query)
#            # change limit
#            cql_query = re_limit.sub('LIMIT %d' % (offset + limit,), cql_query)

        # The patch converts unicode to ascii.
        # Django unfortunately working on unicode
        # while Cassandra requires bytes.
        if isinstance(cql_query, unicode):
            try:
                cql_query = cql_query.encode('ascii')
            except UnicodeEncodeError:
                raise ValueError("CQL query must be ASCII")

        return f(self, cql_query, params, *args, **kwargs)

    return execute


def prepare_inline_decorator(f):
    def prepare_inline(self, query, params):
        prepared_query = f(self, query, params)
        # Correct null values
        # 'None' => 'null'
        prepared_query = re_none.sub(lambda m: m.groups()[0] + 'null' + m.groups()[2], prepared_query)
        return prepared_query
    return prepare_inline


class ThriftCursor(ThriftCursorPrimitive):
    execute = execute_decorator(ThriftCursorPrimitive.execute)
    #prepare_inline = prepare_inline_decorator(ThriftCursorPrimitive.prepare_inline)


class ThriftConnection(ThriftConnectionPrimitive):
    cursorclass = ThriftCursor


class NativeCursor(NativeCursorPrimitive):
    execute = execute_decorator(NativeCursorPrimitive.execute)
    #prepare_inline = prepare_inline_decorator(ThriftCursorPrimitive.prepare_inline)


class NativeConnection(NativeConnectionPrimitive):
    cursorclass = NativeCursor


def connect(host, port=None, keyspace=None, user=None, password=None,
            cql_version=None, native=False, compression=None,
            consistency_level="ONE", transport=None):
    if native:
        connclass = NativeConnection
        if port is None:
            port = 8000
    else:
        connclass = ThriftConnection
        if port is None:
            port = 9160
    return connclass(host, port, keyspace, user, password,
                     cql_version=cql_version, compression=compression,
                     consistency_level=consistency_level, transport=transport)

