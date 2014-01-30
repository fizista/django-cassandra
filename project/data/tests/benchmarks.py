# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import cql
import datetime
import math
import os
import time

from django.test import TestCase
from django.db import connection
from django.db.utils import ProgrammingError
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from pycallgraph import Config
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.system_manager import SystemManager
from pycassa.system_manager import INT_TYPE

from .. import models
from .utils import clear_tables, count_rows
from ..settings import DATA_RESULTS_BENCHMARK_DIR

# !!!!!!!!!!!!!!!!!
#TODO: batch_create using MISSING


def round_sig(x, sig=3):
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


def benchmark_profile(test_method, calls=1, test_method_args=None):
    """
    pycallgraph
    
    Args:
        test_method - 
        calls - number of internal calls the block action
    Return:
        out_data =  test_method()
    """
    id_test = 'bench_profile_' + test_method.__name__
    if not test_method_args:
        test_method_args = []
    graphviz = GraphvizOutput()
    graphviz.output_file = os.path.join(
        DATA_RESULTS_BENCHMARK_DIR,
        '%s.png' % (id_test,))
    config = Config(max_depth=20)
    start = datetime.datetime.now()
    with PyCallGraph(output=graphviz, config=config):
        out = test_method(*test_method_args)
    end = datetime.datetime.now()
    time_delta = end - start
    time_seconds = round_sig(time_delta.total_seconds())
    loops_per_sec = round_sig(calls / time_seconds)
    out_info = "%9.3f %6.0f" % (time_seconds, loops_per_sec)
    out_txt_file = os.path.join(
        DATA_RESULTS_BENCHMARK_DIR,
        '%s.txt' % (id_test,))
    with open(out_txt_file, 'w') as fh:
        fh.write(out_txt_file + '\n')
    print("%40s %s" % (test_method.__name__, out_info,))
    return out


def benchmark_simple_time(test_method, calls=1, test_method_args=None):
    """
    delta time
    
    Args:
        test_method - 
        calls - number of internal calls the block action
        
    Return:
        out_data =  test_method()
    """
    id_test = 'bench_simple_' + test_method.__name__
    if not test_method_args:
        test_method_args = []
    start = datetime.datetime.now()
    out = test_method(*test_method_args)
    end = datetime.datetime.now()
    time_delta = end - start
    time_seconds = round_sig(time_delta.total_seconds())
    loops_per_sec = round_sig(calls / time_seconds)
    out_info = "%9.3f %6.0f" % (time_seconds, loops_per_sec)
    out_txt_file = os.path.join(
        DATA_RESULTS_BENCHMARK_DIR,
        '%s.txt' % (id_test,))
    with open(out_txt_file, 'w') as fh:
        fh.write(out_txt_file + '\n')
    print("%40s %s" % (test_method.__name__, out_info,))
    return out

class BenchmarkTest(TestCase):

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

    def test_benchmark_stress_cassandra(self):
        """
        Runs stress tests for the database cassandra
        
        ********** ATTENTION ***********
        It is running in an infinite loop. 
        To stop benchmark, you need to 
        terminate the program.
        ********************************
        """

        OUT_FILE_NAME = 'benchmark_stress_cassandra.txt'
        LOOPS_PER_PERIOD = 10000

        out_file_path = os.path.join(
            DATA_RESULTS_BENCHMARK_DIR,
            OUT_FILE_NAME)
        out_file_fh = open(out_file_path, 'w')

        clear_tables('data_dataprimary')

        # initial values
        loops = 0
        number_periods = 0
        buffer = []
        start = datetime.datetime.now()
        template_string = \
            '1' * 10 + '2' * 10 + '3' * 10 + '4' * 10 + \
            '5' * 10 + '6' * 10 + '7' * 10 + '8' * 10

        while 1:
            loops += 1

            # create new object
            data_object = models.DataBenchmark()
            data_object.id = loops
            template_string_local = str(loops) + '_' + template_string
            data_object.data1 = 'd1_' + template_string_local
            data_object.data2 = 'd2_' + template_string_local
            data_object.data3 = 'd3_' + template_string_local
            buffer.append(data_object)

            if not loops % LOOPS_PER_PERIOD:
                # ##################################################
                # Operations at the end of the period

                # send data to databse
                models.DataBenchmark.objects.bulk_create(buffer)

                number_periods += 1
                buffer = []
                end = datetime.datetime.now()

                time_delta = end - start
                time_seconds = time_delta.seconds
                loops_per_sec = LOOPS_PER_PERIOD / time_seconds

                # number_periods nr, loops/sek, time delta
                out_string = '%15d, %10d, %10d' % (number_periods, loops_per_sec, time_seconds)
                print(out_string)
                out_file_fh.write(out_string + '\n')
                out_file_fh.flush()

                # ##################################################
                # Operations at the start of the period
                start = datetime.datetime.now()

        out_file_fh.close()


    def test_benchmark_comparison(self):

        clear_tables('data_dataprimary')
        def get_inserts_base(min_base_time_benchmark=0.4):
            print('MIN: %f' % min_base_time_benchmark)
            insert_number = 0
            start = datetime.datetime.now()
            while 1:
                insert_number += 1
                data_object = models.DataPrimary()
                data_object.id = insert_number
                data_object.data = insert_number
                end = datetime.datetime.now()
                time_delta = end - start
                time_seconds = time_delta.total_seconds()
                if time_seconds >= min_base_time_benchmark:
                    print('%s %s %s %d' % (time_delta, start, end, insert_number))
                    break
            return insert_number

        inserts_simple = get_inserts_base()
        inserts_profile = benchmark_profile(get_inserts_base, 999999999)

        print('Benchmark simple')
        self.run_benchmark_comparison(benchmark_simple_time, inserts_simple)

        print('Benchmark profile')
        self.run_benchmark_comparison(benchmark_profile, inserts_profile)

    def run_benchmark_comparison(self, benchmark, inserts):

        INSERTS = inserts
        print('Insert: %d' % INSERTS)

        clear_tables('data_dataprimary')
        def test_orm_create_objects_speed():
            insert_number = 0
            start = datetime.datetime.now()
            while 1:
                insert_number += 1
                data_object = models.DataPrimary()
                data_object.id = insert_number
                data_object.data = insert_number
                if not insert_number % INSERTS:
                    break
        benchmark(test_orm_create_objects_speed, INSERTS)

        clear_tables('data_dataprimary')
        def test_orm_insert():
            insert_number = 0
            while 1:
                insert_number += 1
                data_object = models.DataPrimary()
                data_object.id = insert_number
                data_object.data = insert_number
                data_object.save(force_insert=True)
                if not insert_number % INSERTS:
                    break
        benchmark(test_orm_insert, INSERTS)
        self.assertEqual(INSERTS, count_rows('data_dataprimary'))

        clear_tables('data_dataprimary')
        def test_orm_insert_bulk():
            buffer = []
            insert_number = 0
            while 1:
                insert_number += 1
                # Save first object
                data_object = models.DataPrimary()
                data_object.id = insert_number
                data_object.data = insert_number
                buffer.append(data_object)
                if not insert_number % INSERTS:
                    break
            models.DataPrimary.objects.bulk_create(buffer)
        benchmark(test_orm_insert_bulk, INSERTS)
        self.assertEqual(INSERTS, count_rows('data_dataprimary'))

        clear_tables('data_dataprimary')
        def test_orm_insert_bulk_for():
            buffer = []
            for insert_number in range(INSERTS):
                data_object = models.DataPrimary()
                data_object.id = insert_number
                data_object.data = insert_number
                buffer.append(data_object)
            models.DataPrimary.objects.bulk_create(buffer)
        benchmark(test_orm_insert_bulk_for, INSERTS)
        self.assertEqual(INSERTS, count_rows('data_dataprimary'))

        clear_tables('data_dataprimary')
        def test_cql_insert():
            cursor = connection.cursor()
            insert_number = 0
            while 1:
                insert_number += 1
                cursor.execute("INSERT INTO data_dataprimary (id, data) VALUES (%d,%d)" % (insert_number, insert_number))
                if not insert_number % INSERTS:
                    break
        benchmark(test_cql_insert, INSERTS)
        self.assertEqual(INSERTS, count_rows('data_dataprimary'))

        clear_tables('data_dataprimary')
        def test_cql_insert_batch():
            cursor = connection.cursor()
            buffer = [b'BEGIN BATCH']
            insert_number = 0
            while 1:
                insert_number += 1
                buffer.append(b"INSERT INTO data_dataprimary (id, data) VALUES (%d,%d)" % (insert_number, insert_number))
                if not insert_number % INSERTS:
                    break
            buffer.append(b'APPLY BATCH')
            cursor.execute(b'  '.join(buffer))
        benchmark(test_cql_insert_batch, INSERTS)
        self.assertEqual(INSERTS, count_rows('data_dataprimary'))

        clear_tables('pycassa_dataprimary')
        cursor = connection.cursor()
        ip = cursor.db.get_connection_params()[0][0]
        port = cursor.db.get_connection_params()[1]['port']
        keyspace = cursor.db.get_connection_params()[1]['keyspace']
        if not port:
            port = 9160
        ip_link = '%s:%d' % (ip, port)
        sys = SystemManager(ip_link)
        table_name = 'pycassa_dataprimary'
        try:
            sys.create_column_family(
                 keyspace,
                 table_name,
                 key_validation_class=INT_TYPE,
                 default_validation_class=INT_TYPE)
        except:
            pass
        def test_pycassa_insert():
            pool = ConnectionPool(keyspace, [ip_link])
            col_dataprimary = ColumnFamily(pool, table_name)
            insert_number = 0
            while 1:
                insert_number += 1
                col_dataprimary.insert(insert_number, {'data': insert_number})
                if not insert_number % INSERTS:
                    break
        benchmark(test_pycassa_insert, INSERTS)
        self.assertEqual(INSERTS, count_rows(table_name))


        clear_tables('pycassa_dataprimary')
        def test_pycassa_insert_batch():
            pool = ConnectionPool(keyspace, [ip_link])
            col_dataprimary = ColumnFamily(pool, table_name)
            with col_dataprimary.batch() as b:
                insert_number = 0
                while 1:
                    insert_number += 1
                    b.insert(insert_number, {'data': insert_number})
                    if not insert_number % INSERTS:
                        break
        benchmark(test_pycassa_insert_batch, INSERTS)
        self.assertEqual(INSERTS, count_rows(table_name))
