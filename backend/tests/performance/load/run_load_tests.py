#!/usr/bin/env python3

"""
Script for running Locust load tests with different configurations.
"""

import argparse
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import settings

MONITORING_DIR = Path(settings.BASE_DIR) / "backend" / "monitoring"
LOAD_REPORTS_DIR = MONITORING_DIR / "load" / "reports"


def _parse_duration(duration: str) -> int:
    """
    Converts duration string (e.g., '5m', '30s') to seconds.
    """
    match = re.match(r"(\d+)([smh])", duration)
    if not match:
        raise ValueError(
            "Invalid duration format. Use 's' for seconds, 'm' for minutes, 'h' for hours.",
        )
    value, unit = match.groups()
    value = int(value)
    if unit == "s":
        return value
    if unit == "m":
        return value * 60
    if unit == "h":
        return value * 3600
    raise ValueError(f"Unknown duration unit: {unit}")


def run_load_test(
    host: str = "http://localhost:8000",
    users: int = 10,
    spawn_rate: int = 2,
    duration: str = "30s",
    test_name: str = "load_test",
    locustfile: str | None = None,
) -> dict[str, Any]:
    """
    Runs load test with specified parameters.
    """
    LOAD_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if locustfile is None:
        locustfile_path = Path(__file__).parent / "locustfile.py"
    else:
        locustfile_path = Path(locustfile)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_base_name = f"{test_name}_{timestamp}"
    html_report_file = LOAD_REPORTS_DIR / f"{report_base_name}_report.html"

    command = [
        "locust",
        "-f",
        str(locustfile_path),
        "--host",
        host,
        "--users",
        str(users),
        "--spawn-rate",
        str(spawn_rate),
        "--run-time",
        duration,
        "--headless",
        "--csv",
        str(LOAD_REPORTS_DIR / report_base_name),
        "--html",
        str(html_report_file),
        "--only-summary",
    ]

    print(f"Running {test_name} load test...")
    print(f"Command: {' '.join(command)}")
    print(
        f"Host: {host}, Users: {users}, Spawn rate: {spawn_rate}, Duration: {duration}",
    )

    timeout_seconds = _parse_duration(duration)
    status = "error"
    error_details = "An unknown error occurred"

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        stdout, _ = process.communicate(timeout=timeout_seconds + 30)

        stats_file = LOAD_REPORTS_DIR / f"{report_base_name}_stats.csv"
        if stats_file.exists() and stats_file.stat().st_size > 100:
            print(f"Load test '{test_name}' completed successfully.")
            status = "success"
            error_details = ""
        else:
            print(
                f"Load test '{test_name}' failed with return code {process.returncode}.",
            )
            print(f"Error output: {stdout}")
            status = "failed"
            error_details = (
                f"Process exited with return code {process.returncode}: {stdout}"
            )

    except subprocess.TimeoutExpired:
        print(f"Load test timed out after {timeout_seconds + 30} seconds")
        process.kill()
        process.wait()
        status = "failed"
        error_details = "TimeoutExpired"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_details = str(e)

    summary = {
        "test_name": test_name,
        "timestamp": timestamp,
        "status": status,
        "config": {
            "host": host,
            "users": users,
            "spawn_rate": spawn_rate,
            "duration": duration,
        },
        "html_report": str(html_report_file) if html_report_file.exists() else None,
    }
    if error_details:
        summary["error"] = error_details

    return summary


def run_quick_test(host: str = "http://localhost:8000") -> dict[str, Any]:
    """
    Quick load test (5 users, 30 seconds).
    """
    return run_load_test(
        host=host,
        users=5,
        spawn_rate=1,
        duration="30s",
        test_name="quick_test",
    )


def run_standard_test(host: str = "http://localhost:8000") -> dict[str, Any]:
    """
    Standard load test (20 users, 2 minutes).
    """
    return run_load_test(
        host=host,
        users=20,
        spawn_rate=2,
        duration="2m",
        test_name="standard_test",
    )


def run_stress_test(host: str = "http://localhost:8000") -> dict[str, Any]:
    """
    Stress test (50 users, 5 minutes).
    """
    return run_load_test(
        host=host,
        users=50,
        spawn_rate=5,
        duration="5m",
        test_name="stress_test",
    )


def save_test_summary(results: list[dict[str, Any]]) -> str:
    """
    Save test summary to JSON file.
    """
    summary_file = (
        LOAD_REPORTS_DIR
        / f"load_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful_tests": len([r for r in results if r.get("status") == "success"]),
        "failed_tests": len([r for r in results if r.get("status") != "success"]),
        "tests": results,
    }

    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Test summary saved: {summary_file}")
    return str(summary_file)


def main() -> None:
    """
    Main function for CLI.
    """
    parser = argparse.ArgumentParser(description="Load test runner")
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="Target host URL",
    )
    parser.add_argument("--users", type=int, help="Number of concurrent users")
    parser.add_argument("--spawn-rate", type=int, help="User spawn rate per second")
    parser.add_argument("--duration", help="Test duration (e.g., 30s, 2m)")
    parser.add_argument("--test-name", help="Test name")
    parser.add_argument(
        "--preset",
        choices=["quick", "standard", "stress"],
        help="Use preset configuration",
    )
    parser.add_argument(
        "--all-presets",
        action="store_true",
        help="Run all preset tests",
    )

    args = parser.parse_args()

    results = []

    if args.all_presets:
        print("Running all preset load tests...")

        results.append(run_quick_test(args.host))
        time.sleep(10)

        results.append(run_standard_test(args.host))
        time.sleep(10)

        results.append(run_stress_test(args.host))

    elif args.preset:
        print(f"Running {args.preset} load test...")

        if args.preset == "quick":
            results.append(run_quick_test(args.host))
        elif args.preset == "standard":
            results.append(run_standard_test(args.host))
        elif args.preset == "stress":
            results.append(run_stress_test(args.host))

    elif all([args.users, args.spawn_rate, args.duration, args.test_name]):
        print("Running custom load test...")

        result = run_load_test(
            host=args.host,
            users=args.users,
            spawn_rate=args.spawn_rate,
            duration=args.duration,
            test_name=args.test_name,
        )
        results.append(result)

    else:
        print(
            "Please specify either --preset, --all-presets, or all custom parameters",
        )
        parser.print_help()
        return

    if results:
        save_test_summary(results)

        successful = len([r for r in results if r.get("status") == "success"])
        total = len(results)

        print("\nLoad test summary:")
        print(f"Total tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")

        if successful == total:
            print("All tests completed successfully!")
        else:
            print("Some tests failed. Check logs for details.")


if __name__ == "__main__":
    main()
