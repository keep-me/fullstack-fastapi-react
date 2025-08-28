#!/usr/bin/env python3
"""
PostgreSQL query analyzer script.
"""

import argparse

import psycopg2
from tabulate import tabulate


def reset_stats():
    """
    Reset pg_stat_statements statistics.
    """
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/fastapi")
    cur = conn.cursor()
    cur.execute("SELECT pg_stat_statements_reset()")
    conn.commit()
    cur.close()
    conn.close()
    print("Statistics reset successfully")


def analyze_queries(limit=20, sort_by="total_time"):
    """
    Analyze queries from pg_stat_statements.
    """
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/fastapi")
    cur = conn.cursor()

    sort_options = {
        "total_time": "total_exec_time DESC",
        "mean_time": "mean_exec_time DESC",
        "calls": "calls DESC",
        "rows": "rows DESC",
    }

    sort_clause = sort_options.get(sort_by, "total_exec_time DESC")

    query_sql = f"""
        SELECT 
            query,
            calls,
            total_exec_time,
            mean_exec_time,
            rows
        FROM 
            pg_stat_statements 
        WHERE 
            query NOT ILIKE %s
            AND query NOT ILIKE %s
            AND query NOT ILIKE %s
            AND query NOT ILIKE %s
            AND query NOT ILIKE %s
            AND query NOT ILIKE %s
            AND query NOT ILIKE %s
            AND query NOT ILIKE %s
        ORDER BY 
            {sort_clause}
        LIMIT 
            %s"""

    cur.execute(
        query_sql,
        (
            "CREATE DATABASE%",
            "DROP DATABASE%",
            "CREATE TABLE%",
            "DROP TABLE%",
            "TRUNCATE%",
            "CREATE INDEX%",
            "CREATE UNIQUE INDEX%",
            "%pg_terminate_backend%",
            limit,
        ),
    )

    rows = cur.fetchall()

    headers = ["Query", "Calls", "Total Time (ms)", "Mean Time (ms)", "Rows"]
    table_data = []

    for row in rows:
        query = row[0][:80] + "..." if len(row[0]) > 80 else row[0]
        table_data.append([query, row[1], f"{row[2]:.2f}", f"{row[3]:.2f}", row[4]])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    cur.close()
    conn.close()


def explain_query(query):
    """
    Run EXPLAIN ANALYZE on a query.
    """
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/fastapi")
    cur = conn.cursor()

    try:
        cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {query}")
        results = cur.fetchall()
        print("Query Execution Plan:")
        print("-" * 80)
        for row in results:
            print(row[0])
    except Exception as e:
        print(f"Error running EXPLAIN ANALYZE: {e}")

    cur.close()
    conn.close()


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="PostgreSQL Query Analyzer")
    parser.add_argument("--reset", action="store_true", help="Reset query statistics")
    parser.add_argument(
        "--limit", type=int, default=10, help="Number of queries to show"
    )
    parser.add_argument(
        "--sort",
        choices=["total_time", "mean_time", "calls", "rows"],
        default="total_time",
        help="Sort queries by",
    )
    parser.add_argument(
        "--explain", type=str, help="Run EXPLAIN ANALYZE on a specific query"
    )

    args = parser.parse_args()

    try:
        if args.reset:
            reset_stats()
        elif args.explain:
            explain_query(args.explain)
        else:
            analyze_queries(args.limit, args.sort)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
