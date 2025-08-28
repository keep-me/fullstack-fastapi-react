## Commands to run unit tests

### Run tests with pytest-xdist
```bash
pytest -n auto tests/unit --cov=.
```

### Run analyze PostgreSQL queries
```bash
python scripts/analyze_queries.py --sort total_time
```

## Commands to run performance tests

### Benchmark tests with report saving

```bash
pytest tests/performance/benchmark/test_api_performance.py -v --benchmark-only --benchmark-json=monitoring/benchmark/benchmark.json

pytest tests/performance/benchmark/test_database_performance.py -v --benchmark-only --benchmark-json=monitoring/benchmark/benchmark.json

python tests/performance/analyze_performance.py --benchmark-json monitoring/benchmark/benchmark.json --test-type benchmark
```

### Memory tests with report saving

```bash
pytest tests/performance/memory/test_memory_usage.py -v

python tests/performance/analyze_performance.py --memory-json monitoring/memory/memory.json --test-type memory
```

### Load tests with report saving

```bash
python tests/performance/load/run_load_tests.py --preset standard

python tests/performance/analyze_performance.py --load-csv monitoring/load --test-type load
```

Or directly with `locust`:

```bash
locust -f tests/performance/load/locustfile.py --host http://localhost:8000 --users 5 --spawn-rate 1 --run-time 30s --headless --only-summary
```