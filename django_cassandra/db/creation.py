# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import time

from django.db.backends.creation import BaseDatabaseCreation
from django.db.backends.util import truncate_name


class DatabaseCreation(BaseDatabaseCreation):
    # This dictionary maps Field objects to their associated PostgreSQL column
    # types, as strings. Column-type strings can contain format strings; they'll
    # be interpolated against the values of Field.__dict__ before being output.
    # If a column type is set to None, it won't be included in the output.
    data_types = {
        'AutoField': 'timeuuid',
        'BooleanField': 'boolean',
        'CharField': 'varchar',
        'DateField': 'timestamp',
        'DateTimeField': 'timestamp',
        'DecimalField': 'double',
        'FileField': 'varchar',
        'FilePathField': 'varchar)',
        'FloatField': 'double',
        'IntegerField': 'int',
        'IPAddressField': 'inet',
        'GenericIPAddressField': 'inet',
        'NullBooleanField': 'boolean',
        'PositiveIntegerField': 'bigint',
        'PositiveSmallIntegerField': 'int',
        'SlugField': 'varchar',
        'SmallIntegerField': 'int',
        'TextField': 'text',
        'TimeField': 'bigint',
    }

    data_type_check_constraints = {
        'PositiveIntegerField': '"%(column)s" >= 0',
        'PositiveSmallIntegerField': '"%(column)s" >= 0',
    }

    def sql_for_pending_references(self, model, style, pending_references):
        """
        Returns any ALTER TABLE statements to add constraints after the fact.
        """
        return ''

    def sql_for_inline_foreign_key_references(self, model, field, known_models, style):
        """
        Return the SQL snippet defining the foreign key reference for a field.
        """
        qn = self.connection.ops.quote_name
        rel_to = field.rel.to
        if rel_to in known_models or rel_to == model:
            pending = False
        else:
            pending = True
        output = []
        return output, pending

    def sql_create_model(self, model, style, known_models=set()):
        """
        Returns the SQL required to create a single model, as a tuple of:
            (list_of_sql, pending_references_dict)
        """
        opts = model._meta
        if not opts.managed or opts.proxy or opts.swapped:
            return [], {}
        final_output = []
        table_output = []
        pending_references = {}
        qn = self.connection.ops.quote_name
        for f in opts.local_fields:
            col_type = f.db_type(connection=self.connection)
            tablespace = f.db_tablespace or opts.db_tablespace
            if col_type is None:
                # Skip ManyToManyFields, because they're not represented as
                # database columns in this table.
                continue
            # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
            field_output = [style.SQL_FIELD(qn(f.column)),
                style.SQL_COLTYPE(col_type)]
            # Oracle treats the empty string ('') as null, so coerce the null
            # option whenever '' is a possible value.
            null = f.null
            if (f.empty_strings_allowed and not f.primary_key and
                    self.connection.features.interprets_empty_strings_as_nulls):
                null = True
#            if not null:
#                field_output.append(style.SQL_KEYWORD('NOT NULL'))
            if f.primary_key:
                field_output.append(style.SQL_KEYWORD('PRIMARY KEY'))
#            elif f.unique:
#                field_output.append(style.SQL_KEYWORD('UNIQUE'))
            if tablespace and f.unique:
                # We must specify the index tablespace inline, because we
                # won't be generating a CREATE INDEX statement for this field.
                tablespace_sql = self.connection.ops.tablespace_sql(
                    tablespace, inline=True)
                if tablespace_sql:
                    field_output.append(tablespace_sql)
            if f.rel and f.db_constraint:
                ref_output, pending = self.sql_for_inline_foreign_key_references(
                    model, f, known_models, style)
                if pending:
                    pending_references.setdefault(f.rel.to, []).append(
                        (model, f))
                else:
                    field_output.extend(ref_output)
            table_output.append(' '.join(field_output))

#        for field_constraints in opts.unique_together:
#            table_output.append(style.SQL_KEYWORD('UNIQUE') + ' (%s)' %
#                ", ".join(
#                    [style.SQL_FIELD(qn(opts.get_field(f).column))
#                     for f in field_constraints]))

        full_statement = [style.SQL_KEYWORD('CREATE TABLE') + ' ' +
                          style.SQL_TABLE(qn(opts.db_table)) + ' (']
        for i, line in enumerate(table_output):  # Combine and add commas.
            full_statement.append(
                '    %s%s' % (line, ',' if i < len(table_output) - 1 else ''))
        full_statement.append(')')
        if opts.db_tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(
                opts.db_tablespace)
            if tablespace_sql:
                full_statement.append(tablespace_sql)
        full_statement.append(';')
        final_output.append('\n'.join(full_statement))

        if opts.has_auto_field:
            # Add any extra SQL needed to support auto-incrementing primary
            # keys.
            auto_column = opts.auto_field.db_column or opts.auto_field.name
            autoinc_sql = self.connection.ops.autoinc_sql(opts.db_table,
                                                          auto_column)
            if autoinc_sql:
                for stmt in autoinc_sql:
                    final_output.append(stmt)

        return final_output, pending_references

    def _create_test_db(self, verbosity, autoclobber):
        """
        Internal implementation - creates the test db tables.
        """
        suffix = self.sql_table_creation_suffix()

        test_database_name = self._get_test_db_name()

        qn = self.connection.ops.quote_name

        # Create the test database and connect to it.
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "CREATE KEYSPACE %s%s "
                "WITH REPLICATION = { "
                "    'class' : 'SimpleStrategy', "
                "    'replication_factor' : 3 "
                "};" % (qn(test_database_name), suffix))
        except Exception as e:
            sys.stderr.write(
                "Got an error creating the test database: %s\n" % e)
            if not autoclobber:
                confirm = raw_input(
                    "Type 'yes' if you would like to try deleting the test "
                    "database '%s', or 'no' to cancel: " % test_database_name)
            if autoclobber or confirm == 'yes':
                try:
                    if verbosity >= 1:
                        print("Destroying old test database '%s'..."
                              % self.connection.alias)
                    cursor.execute(
                        "DROP KEYSPACE %s" % qn(test_database_name))
                    cursor.execute(
                        "CREATE KEYSPACE %s%s "
                        "WITH REPLICATION = { "
                        "    'class' : 'SimpleStrategy', "
                        "    'replication_factor' : 3 "
                        "};" % (qn(test_database_name), suffix))
                except Exception as e:
                    sys.stderr.write(
                        "Got an error recreating the test database: %s\n" % e)
                    sys.exit(2)
            else:
                print("Tests cancelled.")
                sys.exit(1)

        return test_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        """
        Internal implementation - remove the test db tables.
        """
        # Remove the test database to clean up after
        # ourselves. Connect to the previous database (not the test database)
        # to do so, because it's not allowed to delete a database while being
        # connected to it.
        cursor = self.connection.cursor()
        # Wait to avoid "database is being accessed by other users" errors.
        time.sleep(1)
        cursor.execute("DROP KEYSPACE %s"
                       % self.connection.ops.quote_name(test_database_name))
        self.connection.close()

    def sql_indexes_for_fields(self, model, fields, style):
        if len(fields) == 1 and fields[0].db_tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(fields[0].db_tablespace)
        elif model._meta.db_tablespace:
            tablespace_sql = self.connection.ops.tablespace_sql(model._meta.db_tablespace)
        else:
            tablespace_sql = ""
        if tablespace_sql:
            tablespace_sql = " " + tablespace_sql

        field_names = []
        qn = self.connection.ops.quote_name
        for f in fields:
            field_names.append(style.SQL_FIELD(qn(f.column)))

        index_name = "%s_%s" % (model._meta.db_table, self._digest([f.name for f in fields]))

        return [
            style.SQL_KEYWORD("CREATE INDEX") + " " +
            style.SQL_TABLE(truncate_name(index_name, self.connection.ops.max_name_length())) + " " +
            style.SQL_KEYWORD("ON") + " " +
            style.SQL_TABLE(qn(model._meta.db_table)) + " " +
            "(%s)" % style.SQL_FIELD(", ".join(field_names)) +
            "%s;" % tablespace_sql,
        ]