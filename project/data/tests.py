# -*- encoding: utf-8

# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import cql
import time
import datetime

from django.test import TestCase
from django.db import connection
from django.db.utils import ProgrammingError

from . import models


class ModelTest(TestCase):

    def setUp(self):
        cursor = connection.cursor()
        cursor.execute("TRUNCATE data_dataprimary")

    def tearDown(self):
        pass

    def test_insert(self):

        # Save first object
        data_object = models.DataPrimary()
        data_object.id = 1
        data_object.data = 10
        data_object.save()

        # Save second clone object
        # TODO: if it is possible to add the ability to change the primary key
#        data_object = models.DataPrimary()
#        data_object.id = 2
#        data_object.save()

        # Save third object
        data_object = models.DataPrimary()
        data_object.id = 3
        data_object.data = 30
        data_object.save()

        # Test auto ID
        with self.assertRaises(ProgrammingError):
            data_object.id = None
            data_object.save()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_dataprimary")
        self.assertEqual(
            cursor.fetchall(),
            [[1, 10],
             #[2, 10],
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

    def test_bench_orm(self):
        start = datetime.datetime.now()

        def test_orm():
            for i in range(10000):
                # Save first object
                data_object = models.DataPrimary()
                data_object.id = i
                data_object.data = i + 5
                data_object.save()

        from pycallgraph import PyCallGraph
        from pycallgraph.output import GraphvizOutput
        from pycallgraph import Config
        graphviz = GraphvizOutput()
        graphviz.output_file = 'p_orm.png'
        config = Config(max_depth=20)
        with PyCallGraph(output=graphviz, config=config):
            test_orm()

        end = datetime.datetime.now()
        print("ORM %s" % str(end - start))

    def test_bench_cql(self):
        cursor = connection.cursor()
        start = datetime.datetime.now()

        def test_orm():
            for i in range(10000):
                cursor.execute("INSERT INTO data_dataprimary (id, data) VALUES (%d,%d)" % (i, i + 5))

        from pycallgraph import PyCallGraph
        from pycallgraph.output import GraphvizOutput
        from pycallgraph import Config
        graphviz = GraphvizOutput()
        graphviz.output_file = 'p_cql.png'
        config = Config(max_depth=20)
        with PyCallGraph(output=graphviz, config=config):
            test_orm()

        end = datetime.datetime.now()
        print("CQL %s" % str(end - start))
