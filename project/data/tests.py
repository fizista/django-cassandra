# -*- encoding: utf-8

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
from django.test import TestCase
from django.db import connection
from django.db.utils import ProgrammingError

from . import models


def benchmark(test_method, out_file, name, loops):
    """
    Args:
        test_method - 
        out_file - filename without extension
        name - test name
    """
    graphviz = GraphvizOutput()
    graphviz.output_file = '%s.png' % (out_file,)
    config = Config(max_depth=20)
    start = datetime.datetime.now()
    with PyCallGraph(output=graphviz, config=config):
        test_method()
    end = datetime.datetime.now()
    time_delta = end - start
    time_seconds = time_delta.seconds
    loops_per_sec = loops / time_seconds
    print("%40s %18s %s" % (name, str(time_delta), str(loops_per_sec)))

def clear_tables():
    cursor = connection.cursor()
    for table_name in ('data_dataprimary',
                       'data_dataprimaryauto',
                       'data_dataindex',
                       'data_datafields'):
        cursor.execute("TRUNCATE %s" % (table_name,))

def count_rows(table_name):
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM %s;' % (table_name,))
    return cursor.fetchall()[0][0]

class ModelTest(TestCase):

    # Turn on benchmarks
    BENCHMARKS = False

    def setUp(self):
        clear_tables()

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
            [{b'data': 1, b'id': 1}, {b'data': 2, b'id': 2}, {b'data': 3, b'id': 3}][0],
            models.DataPrimary.objects.all().values()[0])

        self.assertEqual(
            [{b'data': 1, b'id': 1}, {b'data': 2, b'id': 2}, {b'data': 3, b'id': 3}][2],
            models.DataPrimary.objects.all().values()[2])

    def test_fields(self):

        primary_key = 1

        datafields_object = models.DataFields()
        datafields_object.id = primary_key
        datafields_object.integer_field = 123456789
        datafields_object.datetime_field = datetime.datetime(1999, 12, 30, 23, 59, 59)
        datafields_object.time_field = datetime.time(23, 59, 59, 99)
        datafields_object.date_field = datetime.datetime(1999, 12, 30)
        datafields_object.char_field = 'abcdABCD'
        datafields_object.text_field = 'abcdABCD'
        datafields_object.save()

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

    def test_benchmark(self):

        LOOPS = 10000

        clear_tables()
        def test_orm_insert():
            for i in range(LOOPS):
                # Save first object
                data_object = models.DataPrimary()
                data_object.id = i
                data_object.data = i + 5
                data_object.save(force_insert=True)
            self.assertEqual(LOOPS, count_rows('data_dataprimary'))
        benchmark(test_orm_insert, 'orm_insert', 'ORM insert', LOOPS)

        clear_tables()
        def test_orm_insert_bulk():
            buffer = []
            for i in range(LOOPS):
                # Save first object
                data_object = models.DataPrimary()
                data_object.id = i
                data_object.data = i + 5
                buffer.append(data_object)
            models.DataPrimary.objects.bulk_create(buffer)
            self.assertEqual(LOOPS, count_rows('data_dataprimary'))
        benchmark(test_orm_insert_bulk, 'orm_insert_bulk', 'ORM insert bulk', LOOPS)

        clear_tables()
        def test_cql_insert():
            cursor = connection.cursor()
            for i in range(LOOPS):
                cursor.execute("INSERT INTO data_dataprimary (id, data) VALUES (%d,%d)" % (i, i + 5))
            self.assertEqual(LOOPS, count_rows('data_dataprimary'))
        benchmark(test_cql_insert, 'cql_insert', 'CQL insert', LOOPS)

        clear_tables()
        def test_cql_insert_batch():
            cursor = connection.cursor()
            buffer = ['BEGIN BATCH']
            for i in range(LOOPS):
                buffer.append("INSERT INTO data_dataprimary (id, data) VALUES (%d,%d)" % (i, i + 5))
            buffer.append('APPLY BATCH')
            cursor.execute('  '.join(buffer))
            self.assertEqual(LOOPS, count_rows('data_dataprimary'))
        benchmark(test_cql_insert, 'cql_insert_batch', 'CQL insert batch', LOOPS)

    if not (BENCHMARKS or
            'BENCHMARK' in os.environ and int(os.environ['BENCHMARK'])):
        test_benchmark = None
