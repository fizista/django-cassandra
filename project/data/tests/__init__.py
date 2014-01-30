import os

from ..settings import DATA_RUN_BENCHMARKS, DATA_RESULTS_BENCHMARK_DIR

# Conditional import benchmarks
if (DATA_RUN_BENCHMARKS or
        'BENCHMARK' in os.environ and int(os.environ['BENCHMARK'])):
    from .benchmarks import BenchmarkTest
    print('Benchmark results dir: %s' % (DATA_RESULTS_BENCHMARK_DIR,))

from .query import QueryTest


