#! /usr/bin/env bash

set -e
set -x

mkdir -p /app/monitoring
mkdir -p /app/monitoring/profiling
mkdir -p /app/monitoring/benchmark
mkdir -p /app/monitoring/memory
mkdir -p /app/monitoring/load

python -m app.backend_pre_start

alembic upgrade head

sleep 5

exit 0