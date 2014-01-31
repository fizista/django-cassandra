from django.db.models.sql import compiler
from django.utils.six.moves import zip_longest


class SQLCompiler(compiler.SQLCompiler):
    pass


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):

    def __init__(self, *args, **kwargs):
        self.return_id = False
        super(SQLInsertCompiler, self).__init__(*args, **kwargs)

    def placeholder(self, num, field, val):
        if field is None:
            # A field value of None means the value is raw.
            return val
        else:
            # Return the common case for the placeholder
            if isinstance(val, (unicode, str)):
                return "'%s'" % val
            else:
                return "%s" % str(val)

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
            (self.placeholder(num, data[0], data[1])
             for num, data in enumerate(zip(fields, val)))
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


from django.db.models.sql.expressions import SQLEvaluator
class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    def as_sql(self):
        """
        Creates the SQL for this query. Returns the SQL string and list of
        parameters.
        """
        self.pre_sql_setup()
        if not self.query.values:
            return '', ()
        table = self.query.tables[0]
        qn = self.quote_name_unless_alias
        result = ['UPDATE %s' % qn(table)]
        result.append('SET')
        values, update_params = [], []
        for field, model, val in self.query.values:
            if hasattr(val, 'prepare_database_save'):
                val = val.prepare_database_save(field)
            else:
                val = field.get_db_prep_save(val, connection=self.connection)

            # Getting the placeholder for the field.
            if hasattr(field, 'get_placeholder'):
                placeholder = field.get_placeholder(val, self.connection)
            else:
                placeholder = '%s'

            if hasattr(val, 'evaluate'):
                val = SQLEvaluator(val, self.query, allow_joins=False)
            name = field.column
            if hasattr(val, 'as_sql'):
                sql, params = val.as_sql(qn, self.connection)
                values.append('%s = %s' % (qn(name), sql))
                update_params.extend(params)
            elif val is not None:
                values.append('%s = %s' % (qn(name), placeholder))
                update_params.append(val)
            else:
                values.append('%s = NULL' % qn(name))
        if not values:
            return '', ()
        result.append(', '.join(values))
        where, params = self.query.where.as_sql(qn=qn, connection=self.connection)
        if where:
            result.append('WHERE %s' % where)
        return ' '.join(result), tuple(update_params + params)

    def execute_sql(self, result_type):
        """
        Execute the specified update. Returns the number of rows affected by
        the primary update query. The "primary update query" is the first
        non-empty query that is executed. Row counts for any subsequent,
        related queries are not available.
        """
        cursor = super(SQLUpdateCompiler, self).execute_sql(result_type)
        rows = cursor.rowcount if cursor else 0
        is_empty = cursor is None
        del cursor
        for query in self.query.get_related_updates():
            aux_rows = query.get_compiler(self.using).execute_sql(result_type)
            if is_empty:
                rows = aux_rows
                is_empty = False
        return rows

    def pre_sql_setup(self):
        """
        If the update depends on results from other tables, we need to do some
        munging of the "where" conditions to match the format required for
        (portable) SQL updates. That is done here.

        Further, if we are going to be running multiple updates, we pull out
        the id values to update at this point so that they don't change as a
        result of the progressive updates.
        """
        self.query.select_related = False
        self.query.clear_ordering(True)
        super(SQLUpdateCompiler, self).pre_sql_setup()
        count = self.query.count_active_tables()
        if not self.query.related_updates and count == 1:
            return

        # We need to use a sub-select in the where clause to filter on things
        # from other tables.
        query = self.query.clone(klass=Query)
        query.bump_prefix()
        query.extra = {}
        query.select = []
        query.add_fields([query.get_meta().pk.name])
        # Recheck the count - it is possible that fiddling with the select
        # fields above removes tables from the query. Refs #18304.
        count = query.count_active_tables()
        if not self.query.related_updates and count == 1:
            return

        must_pre_select = count > 1 and not self.connection.features.update_can_self_select

        # Now we adjust the current query: reset the where clause and get rid
        # of all the tables we don't need (since they're in the sub-select).
        self.query.where = self.query.where_class()
        if self.query.related_updates or must_pre_select:
            # Either we're using the idents in multiple update queries (so
            # don't want them to change), or the db backend doesn't support
            # selecting from the updating table (e.g. MySQL).
            idents = []
            for rows in query.get_compiler(self.using).execute_sql(MULTI):
                idents.extend([r[0] for r in rows])
            self.query.add_filter(('pk__in', idents))
            self.query.related_ids = idents
        else:
            # The fast path. Filters and updates in one query.
            self.query.add_filter(('pk__in', query))
        for alias in self.query.tables[1:]:
            self.query.alias_refcount[alias] = 0

class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass


class SQLDateCompiler(compiler.SQLDateCompiler, SQLCompiler):
    pass


class SQLDateTimeCompiler(compiler.SQLDateTimeCompiler, SQLCompiler):
    pass

