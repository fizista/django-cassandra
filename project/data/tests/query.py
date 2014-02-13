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
from django.test import TestCase
from django.db import connection
from django.db.utils import ProgrammingError

from .. import models
from .utils import clear_tables, count_rows

# !!!!!!!!!!!!!!!!!
#TODO: batch_create using MISSING


class QueryTest(TestCase):

    TABLES_IN_USE = [
        'data_dataprimary',
        'data_dataprimaryauto',
        'data_dataindex',
        'data_datafields',
        'data_dataprimary']

    def setUp(self):
        clear_tables(*self.TABLES_IN_USE)

    def tearDown(self):
        pass

    def test_insert_autoid(self):

        data_object1 = models.DataPrimaryAuto()
        data_object1.data = 10
        data_object1.save()

        self.assertTrue(len(data_object1.pk) >= 1)

        data_object2 = models.DataPrimaryAuto()
        data_object2.data = 20
        data_object2.save()

        self.assertNotEqual(data_object1.pk, data_object2.pk)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_dataprimaryauto")
        self.assertEqual(
            cursor.fetchall(),
            [[data_object1.pk, 10],
             [data_object2.pk, 20]]
        )

    def test_insert(self):

        # Save first object
        data_object = models.DataPrimary()
        data_object.id = 1
        data_object.data = 10
        data_object.save(force_insert=True)

        # Save second object
        data_object = models.DataPrimary()
        data_object.id = 3
        data_object.data = 30
        data_object.save(force_insert=True)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_dataprimary")
        self.assertEqual(
            cursor.fetchall(),
            [[1, 10],
             [3, 30]]
        )

    def test_update(self):

        # Save first object
        data_object = models.DataPrimary()
        data_object.id = 1
        data_object.data = 10
        data_object.save(force_insert=True)

        data_object.data = 999
        data_object.save(force_update=True)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_dataprimary")
        self.assertEqual(
            cursor.fetchall(),
            [[1, 999], ]
        )

    def test_insert_bulk(self):

        # Create first object
        data_object1 = models.DataPrimary()
        data_object1.id = 1
        data_object1.data = 10

        # Create second object
        data_object2 = models.DataPrimary()
        data_object2.id = 3
        data_object2.data = 30

        # Save objects
        models.DataPrimary.objects.bulk_create([data_object1, data_object2])

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_dataprimary")
        self.assertEqual(
            cursor.fetchall(),
            [[1, 10],
             [3, 30]]
        )

    def off_test_insert_bulk_multi_heavy(self):
        """
        Check here if there is no accident: rpc_timeout
        
        """

        MAX_INSERTS = 200000

        template_string = \
            '1' * 10 + '2' * 10 + '3' * 10 + '4' * 10 + \
            '5' * 10 + '6' * 10 + '7' * 10 + '8' * 10
        insert = 0

        for number_package_inserts in range(1, 3):
            buffer = []
            while 1:
                insert += 1

                # create new object
                data_object = models.DataBenchmark()
                data_object.id = insert
                template_string_local = str(insert) + '_' + template_string
                data_object.data1 = 'd1_' + template_string_local
                data_object.data2 = 'd2_' + template_string_local
                data_object.data3 = 'd3_' + template_string_local
                buffer.append(data_object)

                if not insert % MAX_INSERTS:
                    break

            models.DataBenchmark.objects.bulk_create(buffer)

    def test_get(self):

        d1 = models.DataPrimary(id=1, data=1)
        d1.save()
        d2 = models.DataPrimary(2, 2)
        d2.save()
        d3 = models.DataPrimary(3, 3)
        d3.save()

        self.assertEqual(
            d3,
            models.DataPrimary.objects.get(pk=3))

        self.assertEqual(
            d1,
            models.DataPrimary.objects.get(pk=1))

    def test_all(self):

        d1 = models.DataPrimary(id=1, data=1)
        d1.save()
        d2 = models.DataPrimary(2, 2)
        d2.save()
        d3 = models.DataPrimary(3, 3)
        d3.save()

        self.assertEqual(
            d1,
            models.DataPrimary.objects.all()[0])

        self.assertEqual(
            [{b'data': 1, b'id': 1}, {b'data': 2, b'id': 2}, {b'data': 3, b'id': 3}],
            list(models.DataPrimary.objects.all().values()))

    def test_filter(self):

        d1 = models.DataPrimary(id=1, data=1)
        d1.save()
        d2 = models.DataPrimary(2, 2)
        d2.save()
        d3 = models.DataPrimary(3, 3)
        d3.save()

        # test EQ
        self.assertEqual(
            [{b'data': 2, b'id': 2}],
            list(models.DataPrimary.objects.filter(pk=2).values()))

        # test IN
        self.assertEqual(
            [{b'data': 1, b'id': 1}, {b'data': 3, b'id': 3}],
            list(models.DataPrimary.objects.filter(pk__in=(1, 3)).values()))


    def test_fields(self):

        primary_key = 1

        date_start = datetime.datetime.now()
        datafields_object = models.DataFields()
        datafields_object.id = primary_key
        datafields_object.integer_field = 123456789
        datafields_object.datetime_field = datetime.datetime(1999, 12, 30, 23, 59, 59)
        datafields_object.time_field = datetime.time(23, 59, 59, 99)
        datafields_object.date_field = datetime.datetime(1999, 12, 30)
        datafields_object.char_field = 'abcdABCD'
        datafields_object.text_field = 'abcdABCD'
        datafields_object.timeuuid_field = datetime.datetime(1999, 12, 30, 23, 59, 59)
        datafields_object.save()
        date_end = datetime.datetime.now()

        del datafields_object

        datafields_object_db = models.DataFields.objects.get(pk=primary_key)

        self.assertEqual(
            datafields_object_db.integer_field,
            123456789)

        self.assertEqual(
            datafields_object_db.datetime_field,
            datetime.datetime(1999, 12, 30, 23, 59, 59))

        self.assertEqual(
            datafields_object_db.time_field,
            datetime.time(23, 59, 59, 99))

        self.assertEqual(
            datafields_object_db.date_field,
            datetime.datetime(1999, 12, 30))

        self.assertEqual(
            datafields_object_db.char_field,
            'abcdABCD')

        self.assertEqual(
            datafields_object_db.text_field,
            'abcdABCD')

        self.assertEqual(
            datafields_object_db.timeuuid_field.get_datetime(),
            datetime.datetime(1999, 12, 30, 23, 59, 59))

        db_date = datafields_object_db.timeuuid_auto_field.get_datetime()
        self.assertTrue(db_date > date_start)
        self.assertTrue(db_date < date_end)

