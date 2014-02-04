import os

from ..settings import (
    DATA_RUN_BENCHMARKS,
    DATA_RESULTS_BENCHMARK_DIR,
    DATA_RUN_BENCHMARKS_TYPES)

# Conditional import benchmarks
if DATA_RUN_BENCHMARKS:
    from .benchmarks import BenchmarkTest
    print('Benchmark results dir: %s' % (DATA_RESULTS_BENCHMARK_DIR,))


from .query import QueryTest


