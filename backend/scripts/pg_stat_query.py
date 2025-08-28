#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/fastapi")
cur = conn.cursor()
cur.execute(
    """
    SELECT query, calls, total_exec_time, mean_exec_time, rows 
    FROM pg_stat_statements 
    WHERE query NOT ILIKE 'CREATE DATABASE%'
      AND query NOT ILIKE 'DROP DATABASE%'
      AND query NOT ILIKE 'CREATE TABLE%'
      AND query NOT ILIKE 'DROP TABLE%'
      AND query NOT ILIKE 'TRUNCATE%'
      AND query NOT ILIKE 'CREATE INDEX%'
      AND query NOT ILIKE 'CREATE UNIQUE INDEX%'
      AND query NOT ILIKE '%pg_terminate_backend%'
    ORDER BY total_exec_time DESC 
    LIMIT 10
"""
)

rows = cur.fetchall()
print("Query | Calls | Total Time (ms) | Mean Time (ms) | Rows")
print("-" * 80)
for row in rows:
    query = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
    print(f"{query} | {row[1]} | {row[2]:.2f} | {row[3]:.2f} | {row[4]}")

cur.close()
conn.close()
