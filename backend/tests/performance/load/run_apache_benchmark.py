#!/usr/bin/env python3

"""
Runs Apache Benchmark (ab) command with specified parameters.
"""

import argparse
import subprocess


def run_apache_benchmark(
    requests: int,
    concurrency: int,
    keepalive: bool,
    url: str,
) -> None:
    """
    Runs Apache Benchmark (ab) command with specified parameters.
    """
    command = ["ab"]

    if keepalive:
        command.append("-k")

    command.extend(["-n", str(requests), "-c", str(concurrency), url])

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if process.stdout:
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A Python wrapper for Apache Benchmark (ab).",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:8000/health",
        help="URL to benchmark.\n(default: http://127.0.0.1:8000/health)",
    )
    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=10000,
        help="Number of requests to perform (ab -n).\n(default: 10000)",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=1000,
        help="Number of multiple requests to make at a time (ab -c).\n(default: 1000)",
    )
    parser.add_argument(
        "-k",
        "--keepalive",
        action="store_true",
        default=True,
        help="Enable KeepAlive feature (ab -k).\n(default: True)",
    )

    args = parser.parse_args()

    run_apache_benchmark(
        requests=args.requests,
        concurrency=args.concurrency,
        keepalive=args.keepalive,
        url=args.url,
    )
