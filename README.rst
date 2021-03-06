================================================
Cassandra database backend for Django framework.
================================================

Installation and Configuration
==============================

Recommended installation::

   git clone http://
   pip install xxx
   
In the settings django:

.. code:: python

   INSTALLED_APPS += ['django_cassandra',]
   
   DATABASES = {
       'default': {
           
           # Backend module 
           # Required!
           'ENGINE': 'django_cassandra.db',
           
           # Name keyspace 
           # Required!
           'NAME': 'django_keyspace',
           
           # User, optional 
           # Default: None       
           #'USER': '',  
           
           # Password, optional 
           # Default: None
           #'PASSWORD': '',
           
           # Native connection
           # Default: False
           #'NATIVE': True
           
           # Host, optional, dafault: 'localhost'
           #'HOST': 'localhost',
           
           # Port number to connect, optional, 
           # Default: 9160 for thrift, 8000 for native
           #'PORT': 9160,
           
           # Compression Whether to use compression. For Thrift connections,
           # this can be None or the name of some supported compression
           # type (like "GZIP"). For native connections, this is treated
           # as a boolean, and if true, the connection will try to find
           # a type of compression supported by both sides.
           # Default: None
           #'COMPRESSION': '',
           
           # Consistency level to use for CQL3 queries (optional);
           # "ONE" is the default CL, other supported values are:
           # "ANY", "TWO", "THREE", "QUORUM", "LOCAL_QUORUM",
           # "EACH_QUORUM" and "ALL"; overridable on per-query basis.
           # Default: 'ONE'
           #'CONSISTENCY_LEVEL: '',
           
           # Transport. If set, use this Thrift transport instead of creating one;
           # doesn't apply to native connections.
           # Default: None
           #'TRANSPORT': '',
       }
   }


What works
==========

Django manage.py subcommands:

- syncdb

- dbshell

- sqlall

Model fields:

- CharField

- TextField

- IntegerField

- DateField

- DateTimeField

- TimeField

Additional model fields:

- TimeUUIDField(auto=False)

Options for the fields:

- db_index
   
- primary_key

What does not work
==================

Fields:

   - AutoField

Model objects:

- change the primary key in object(update object)

Tests
=====

Clone repository::

   git clone http://
   git submodule init
   git submodule update

Requirements:

- graphviz (Ubuntu/Debian: apt-get install graphviz)



Install::

   pip install -e .[tests]

Run normal tests::

   ./manage tests project.data

Run benchmarks::

   BENCHMARK=1 ./manage.py test project.data.tests.BenchmarkTest.test_benchmark_stress_cassandra

To stop benchmark, you need to terminate the program.

**Return**: <DATA_RESULTS_BENCHMARK_DIR>/benchmark_stress_cassandra.txt

::

   BENCHMARK=1 ./manage.py test project.data.tests.BenchmarkTest.test_benchmark_comparison

**Return**: <DATA_RESULTS_BENCHMARK_DIR>/*
