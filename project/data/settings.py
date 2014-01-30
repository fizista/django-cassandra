# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import tempfile

from django.conf import settings
from os import makedirs
from os.path import join, realpath, isdir

# Directory to hold temporary files
# Default: <system temporary dir>/django-cassandra<xyz>/
DATA_TMP_DIR = getattr(
    settings,
    'DATA_TMP_DIR',
    tempfile.mkdtemp(prefix='django-cassandra'))

# Directory where are kept the results of the benchmark
# Default: <DATA_TMP_DIR>/benchmarks/
DATA_RESULTS_BENCHMARK_DIR = getattr(
    settings,
    'DATA_RESULTS_BENCHMARK_DIR',
    join(realpath(DATA_TMP_DIR), 'benchmarks'))

# Running the benchmark
# Default: False
DATA_RUN_BENCHMARKS = getattr(
    settings,
    'DATA_RUN_BENCHMARKS',
    False)

if not isdir(DATA_RESULTS_BENCHMARK_DIR):
    makedirs(DATA_RESULTS_BENCHMARK_DIR)