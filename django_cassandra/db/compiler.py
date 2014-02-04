import re

from django.db.models.sql import compiler
from django.utils.six.moves import zip_longest


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



class SQLCompiler(compiler.SQLCompiler):

    def resolve_columns(self, row, fields=()):
        values = [self.query.convert_values(v, f, connection=self.connection)
                  for v, f in zip(row, fields)]
        return tuple(values)

    def as_sql(self):
        query, params = super(SQLCompiler, self).as_sql()

        if params:
            # correct parameters "%s" => :d<x>, where x = 1,2,3,...
            param_counter = Counter(lambda c, m: ":d%s " % (c,))
            query = re_param.sub(param_counter, query)
            params = dict([('d%s' % (k), v) for k, v in enumerate(params, 1)])

        # remove the name of the table from parameters
        query = re_param_table_name.sub(lambda m: m.groups()[1], query)

        return query, params

    def placeholder(self, field, val):
        if field is None:
            # A field value of None means the value is raw.
            return val
        else:
            # Return the common case for the placeholder
            if isinstance(val, (unicode, str)):
                return "'%s'" % val
            else:
                return "%s" % str(val)


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):

    def __init__(self, *args, **kwargs):
        self.return_id = False
        super(SQLInsertCompiler, self).__init__(*args, **kwargs)

    placeholder = SQLCompiler.placeholder

    def as_sql(self):

        opts = self.query.get_meta()
        has_fields = bool(self.query.fields)
        fields = self.query.fields if has_fields else [opts.pk]

        insert_template = 'INSERT INTO %s ' % opts.db_table
        insert_template += '(%s)' % ', '.join((f.column for f in fields))

        if has_fields:
            values = (
                (
                    f.get_db_prep_save(
                        getattr(obj, f.attname)
                            if self.query.raw else f.pre_save(obj, True),
                        connection=self.connection)
                    for f in fields
                )
                for obj in self.query.objs
            )
        else:
            values = (tuple(self.connection.ops.pk_default_value()) for obj in self.query.objs)
            fields = (None,)

        can_bulk = (not any(hasattr(field, "get_placeholder") for field in fields) and
            not self.return_id and self.connection.features.has_bulk_insert)

        # ###
        # [ [:d<number> or <value>, :d<number> or <value>, ...], ...]
        # ###
        placeholders = (
            (self.placeholder(field, value)
             for field, value in zip(fields, val))
            for val in values
        )

        return_inserts = (
            " ".join(
                (insert_template,) +
                ("VALUES (%s)" % ", ".join(vals),) +
                (';',))
            for vals in placeholders
        )

        if can_bulk:
            return_list = ('BEGIN BATCH',)
            return_list += tuple(return_inserts)
            return_list += ('APPLY BATCH',)
            return '  '.join(return_list)
        else:
            return '  '.join(return_inserts)

    def execute_sql(self, return_id=False):
        assert not (return_id and len(self.query.objs) != 1)
        self.return_id = return_id
        cursor = self.connection.cursor()
        sql = self.as_sql()
        cursor.execute(sql)
        if not (return_id and cursor):
            return
        if self.connection.features.can_return_id_from_insert:
            return self.connection.ops.fetch_returned_insert_id(cursor)
        return self.connection.ops.last_insert_id(cursor,
                self.query.get_meta().db_table, self.query.get_meta().pk.column)


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):

    as_sql = SQLCompiler.as_sql


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass


class SQLDateCompiler(compiler.SQLDateCompiler, SQLCompiler):
    as_sql = SQLCompiler.as_sql


class SQLDateTimeCompiler(compiler.SQLDateTimeCompiler, SQLCompiler):
    as_sql = SQLCompiler.as_sql

