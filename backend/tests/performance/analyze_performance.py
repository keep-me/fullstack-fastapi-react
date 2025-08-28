#!/usr/bin/env python3
"""
Performance test results analyzer.
"""

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import settings

MONITORING_DIR = Path(settings.BASE_DIR) / "backend" / "monitoring"


class PerformanceAnalyzer:
    """
    Performance analyzer.
    """

    def __init__(
        self,
        results_dir: str | None = None,
        test_type: str = "benchmark",
    ) -> None:
        self.test_type = test_type
        results_dir_path: Path
        if results_dir is None:
            results_dir_path = MONITORING_DIR / test_type
        else:
            results_dir_path = Path(results_dir)
        self.results_dir = results_dir_path
        self.results_dir.mkdir(exist_ok=True, parents=True)

    def analyze_benchmark_results(self, benchmark_json_path: str) -> dict[str, Any]:
        """
        Analyzes benchmark test results.
        """
        try:
            with open(benchmark_json_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            return {"error": f"File {benchmark_json_path} not found"}
        except json.JSONDecodeError:
            return {"error": f"JSON parsing error in file {benchmark_json_path}"}

        benchmarks = data.get("benchmarks", [])
        if not benchmarks:
            return {"error": "No benchmark test data"}

        analysis: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(benchmarks),
            "tests_analysis": [],
            "performance_score": 0,
        }

        scores: list[float] = []

        for benchmark in benchmarks:
            test_name = benchmark.get("name", "Unknown")
            stats = benchmark.get("stats", {})

            mean_time = stats.get("mean", 0)
            min_time = stats.get("min", 0)
            max_time = stats.get("max", 0)
            stddev = stats.get("stddev", 0)
            rounds = stats.get("rounds", 0)

            score: float
            if mean_time > 0:
                if mean_time < 0.01:
                    score = 100.0
                elif mean_time < 0.05:
                    score = 90.0
                elif mean_time < 0.1:
                    score = 80.0
                elif mean_time < 0.5:
                    score = 70.0
                elif mean_time < 1.0:
                    score = 60.0
                elif mean_time < 2.0:
                    score = 50.0
                elif mean_time < 5.0:
                    score = 30.0
                else:
                    score = 10.0

                if stddev > 0 and mean_time > 0:
                    cv = stddev / mean_time
                    if cv > 0.5:
                        score *= 0.8
                    elif cv > 0.3:
                        score *= 0.9
            else:
                score = 0.0

            scores.append(score)

            test_analysis = {
                "name": test_name,
                "mean_time_ms": mean_time * 1000,
                "min_time_ms": min_time * 1000,
                "max_time_ms": max_time * 1000,
                "stddev_ms": stddev * 1000,
                "rounds": rounds,
                "score": round(score, 1),
                "status": self._get_performance_status(score),
            }

            analysis["tests_analysis"].append(test_analysis)

        if scores:
            analysis["performance_score"] = round(statistics.mean(scores), 1)

        return analysis

    def analyze_memory_results(self, memory_json_path: str) -> dict[str, Any]:
        """
        Analyzes memory test results.
        """
        try:
            with open(memory_json_path) as f:
                memory_data = json.load(f)
        except Exception:
            return {"error": f"File {memory_json_path} not found or corrupted"}
        return self._analyze_memory_data(memory_data)

    def _analyze_memory_data(self, memory_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyzes memory test results.
        """
        if not memory_data:
            return {"error": "No memory data"}

        memory_usage = [item.get("memory_mb", 0) for item in memory_data]

        leak_analysis = self._analyze_memory_leaks(memory_data)

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "memory_stats": {
                "average_mb": round(statistics.mean(memory_usage), 2),
                "peak_mb": max(memory_usage),
                "min_mb": min(memory_usage),
                "stddev_mb": round(
                    statistics.stdev(memory_usage) if len(memory_usage) > 1 else 0,
                    2,
                ),
            },
            "leak_analysis": leak_analysis,
            "memory_score": self._calculate_memory_score(memory_usage, leak_analysis),
        }

        return analysis

    def analyze_load_test_results(self, csv_path: str) -> dict[str, Any]:
        """
        Analyzes Locust load test results.
        """
        try:
            csv_path_obj = Path(csv_path)

            if csv_path_obj.is_dir():
                reports_dir = csv_path_obj / "reports"
                if reports_dir.exists():
                    csv_files = list(reports_dir.glob("*_stats.csv"))
                    if not csv_files:
                        csv_files = list(reports_dir.glob("load_test_*_stats.csv"))
                else:
                    csv_files = list(csv_path_obj.glob("*_stats.csv"))

                if not csv_files:
                    return {
                        "error": f"CSV result files (*_stats.csv) not found in {csv_path}",
                    }

                csv_file = max(csv_files, key=lambda f: f.stat().st_mtime)
            else:
                csv_file = csv_path_obj

            print(f"Analyzing file: {csv_file}")
            df = pd.read_csv(csv_file)
            print(f"CSV columns: {list(df.columns)}")
            print(f"First rows:\n{df.head()}")

        except Exception as e:
            return {"error": f"CSV file reading error: {e!s}"}

        analysis: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "csv_file": str(csv_file),
            "total_requests": 0,
            "endpoints_analysis": {},
            "performance_metrics": {},
            "load_test_score": 0,
        }

        if "Name" in df.columns and "Average Response Time" in df.columns:
            endpoint_df = df[df["Name"] != "Aggregated"].copy()

            if len(endpoint_df) == 0:
                return {"error": "No endpoint data in CSV file"}

            analysis["total_requests"] = df["Request Count"].sum()

            for _, row in endpoint_df.iterrows():
                endpoint_name = row["Name"]
                method = row.get("Type", "UNKNOWN")
                endpoint_key = f"{method} {endpoint_name}"

                analysis["endpoints_analysis"][endpoint_key] = {
                    "avg_response_time_ms": float(row.get("Average Response Time", 0)),
                    "median_response_time_ms": float(
                        row.get("Median Response Time", 0),
                    ),
                    "min_response_time_ms": float(row.get("Min Response Time", 0)),
                    "max_response_time_ms": float(row.get("Max Response Time", 0)),
                    "total_requests": int(row.get("Request Count", 0)),
                    "total_failures": int(row.get("Failure Count", 0)),
                    "failure_rate_percent": round(
                        (
                            int(row.get("Failure Count", 0))
                            / max(int(row.get("Request Count", 1)), 1)
                        )
                        * 100,
                        2,
                    ),
                }

            total_requests = endpoint_df["Request Count"].sum()
            total_failures = endpoint_df["Failure Count"].sum()

            weighted_avg_response = (
                endpoint_df["Average Response Time"] * endpoint_df["Request Count"]
            ).sum() / max(total_requests, 1)

            analysis["performance_metrics"] = {
                "avg_response_time_ms": round(weighted_avg_response, 2),
                "total_requests": int(total_requests),
                "total_failures": int(total_failures),
                "failure_rate_percent": round(
                    (total_failures / max(total_requests, 1)) * 100,
                    2,
                ),
                "endpoints_tested": len(endpoint_df),
            }

            analysis["load_test_score"] = self._calculate_load_test_score(
                analysis["performance_metrics"],
            )
        else:
            return {
                "error": f"Unexpected CSV file structure. Columns: {list(df.columns)}",
            }

        return analysis

    def save_report(
        self,
        report: dict[str, Any],
        filename: str | None = None,
    ) -> str:
        """
        Saves report in Markdown format.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"RESULT_{self.test_type}_{timestamp}.md"
        out_dir = self.results_dir
        out_dir.mkdir(exist_ok=True, parents=True)
        filepath = out_dir / filename
        markdown = self._report_to_markdown(report)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)
        return str(filepath)

    def _report_to_markdown(self, report: dict[str, Any]) -> str:
        """
        Formats Markdown report with tables and legend.
        """
        lines = []

        if "error" in report:
            lines.append("# Analysis Error\n")
            lines.append(
                f"An error occurred during analysis: `{report.get('error', 'Unknown error')}`",
            )
            return "\n".join(lines)

        if "load_test_score" in report:
            score = report.get("load_test_score", 0)
            lines.append(f"# Load Test - Final Score: {score}/100\n")

            metrics = report.get("performance_metrics", {})
            lines.append("## Overall Metrics")
            lines.append(f"- **Total Requests:** {metrics.get('total_requests', 0)}")
            lines.append(
                f"- **Average Response Time:** {metrics.get('avg_response_time_ms', 0):.2f} ms",
            )
            lines.append(
                f"- **Error Rate:** {metrics.get('failure_rate_percent', 0):.2f}%",
            )
            lines.append(
                f"- **Endpoints Tested:** {metrics.get('endpoints_tested', 0)}\n",
            )

            endpoints = report.get("endpoints_analysis", {})
            if endpoints:
                lines.append("## Endpoint Results\n")
                lines.append(
                    f"| {'Method':<8} | {'Endpoint':<30} | {'Requests':<10} | {'Avg Time (ms)':<15} | {'Errors (%)':<12} | {'Status':<15} |"
                )
                lines.append(
                    f"| :{'-' * 7} | :{'-' * 29} | :{'-' * 9} | :{'-' * 14} | :{'-' * 11} | :{'-' * 14} |"
                )

                for endpoint_key, data in endpoints.items():
                    parts = endpoint_key.split(" ", 1)
                    if len(parts) == 2:
                        method, endpoint = parts
                    else:
                        method = "UNKNOWN"
                        endpoint = endpoint_key

                    avg_time = data.get("avg_response_time_ms", 0)
                    failure_rate = data.get("failure_rate_percent", 0)
                    requests = data.get("total_requests", 0)

                    if failure_rate > 5:
                        status = "critical"
                    elif failure_rate > 1:
                        status = "warning"
                    elif method == "DELETE" and avg_time > 2000:
                        status = "slow delete"
                    elif method in ["POST", "PUT", "PATCH"] and avg_time > 1500:
                        status = "slow write"
                    elif method == "GET" and avg_time > 500:
                        status = "slow read"
                    else:
                        status = "goat"

                    lines.append(
                        f"| {method:<8} | {endpoint:<30} | {requests:<10} | {avg_time:<15.2f} | {failure_rate:<12.2f} | {status:<15} |"
                    )

                lines.append("")

        elif "memory_score" in report:
            score = report.get("memory_score", 0)
            lines.append(f"# Memory Test - Final Score: {score}/100\n")

            memory_stats = report.get("memory_stats", {})
            lines.append("## Memory Statistics")
            lines.append(
                f"- **Average Consumption:** {memory_stats.get('average_mb', 0):.2f} MB",
            )
            lines.append(
                f"- **Peak Consumption:** {memory_stats.get('peak_mb', 0):.2f} MB",
            )
            lines.append(
                f"- **Minimum Consumption:** {memory_stats.get('min_mb', 0):.2f} MB",
            )
            lines.append(
                f"- **Standard Deviation:** {memory_stats.get('stddev_mb', 0):.2f} MB\n",
            )

            leak_analysis = report.get("leak_analysis", {})
            if leak_analysis.get("has_leak_test", False):
                lines.append("## Memory Leak Analysis")
                leak_mb = leak_analysis.get("memory_leak_mb", 0)
                leak_detected = leak_analysis.get("leak_detected", False)
                leak_severity = leak_analysis.get("leak_severity", "none")

                if leak_detected:
                    lines.append(f"- **Leak Status:** {leak_severity.upper()}")
                    lines.append(f"- **Memory Leak:** {leak_mb:.2f} MB")
                else:
                    lines.append("- **Leak Status:** No leaks detected")
                    lines.append(f"- **Memory Difference:** {leak_mb:.2f} MB")

                lines.append("")

        else:
            score = report.get("performance_score", 0)
            lines.append(f"# Benchmark - Final Score: {score}/100\n")

            lines.append("## Test Results\n")
            lines.append(
                f"| {'Test':<50} | {'Average Time (ms)':<22} | {'Score':<18} |"
            )
            lines.append(f"| :{'-' * 49} | :{'-' * 21} | :{'-' * 17} |")

            for t in report.get("tests_analysis", []):
                status = t["status"]
                emoji = (
                    "goat"
                    if status in ["good", "goat"]
                    else ("not good" if status == "not good" else "poor")
                )
                lines.append(
                    f"| {t['name']:<50} | {t['mean_time_ms']:<22.2f} | {emoji:<18} |"
                )

            lines.append("\n**Legend:**")
            lines.append("- goat: < 100ms (API) / < 10ms (DB)")
            lines.append("- not good: 100-500ms (API) / 10-100ms (DB)")
            lines.append("- poor: > 500ms (API) / > 100ms (DB)\n")

        return "\n".join(lines)

    def _get_performance_status(self, score: float) -> str:
        """
        Determines performance status by score.
        """
        if score >= 90:
            return "goat"
        if score >= 80:
            return "good"
        if score >= 70:
            return "not good"
        if score >= 50:
            return "poor"
        return "critical"

    def _analyze_memory_leaks(
        self, memory_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyzes memory leaks by comparing initial and final measurements.
        """
        leak_analysis = {
            "has_leak_test": False,
            "memory_leak_mb": 0.0,
            "leak_detected": False,
            "leak_severity": "none",
        }

        initial_memory = None
        final_memory = None

        for item in memory_data:
            test_name = item.get("test_name", "")
            iteration = item.get("iteration", "")

            if initial_memory is None and iteration != "final":
                initial_memory = item.get("memory_mb", 0)

            if iteration == "final" or test_name == "final_measurement":
                final_memory = item.get("memory_mb", 0)
                leak_analysis["has_leak_test"] = True

        if initial_memory is not None and final_memory is not None:
            memory_leak = final_memory - initial_memory
            leak_analysis["memory_leak_mb"] = round(memory_leak, 2)

            if memory_leak > 20:
                leak_analysis["leak_detected"] = True
                leak_analysis["leak_severity"] = "critical"
            elif memory_leak > 10:
                leak_analysis["leak_detected"] = True
                leak_analysis["leak_severity"] = "high"
            elif memory_leak > 5:
                leak_analysis["leak_detected"] = True
                leak_analysis["leak_severity"] = "medium"
            elif memory_leak > 2:
                leak_analysis["leak_detected"] = True
                leak_analysis["leak_severity"] = "low"

        return leak_analysis

    def _calculate_memory_score(
        self, memory_usage: list[float], leak_analysis: dict[str, Any]
    ) -> float:
        """
        Calculates memory usage score.
        """
        if not memory_usage:
            return 0

        avg_memory = statistics.mean(memory_usage)
        peak_memory = max(memory_usage)

        score: float
        if peak_memory < 100:
            score = 100.0
        elif peak_memory < 200:
            score = 90.0
        elif peak_memory < 500:
            score = 80.0
        elif peak_memory < 1000:
            score = 70.0
        elif peak_memory < 2000:
            score = 50.0
        else:
            score = 30.0

        if len(memory_usage) > 1:
            stddev = statistics.stdev(memory_usage)
            cv = stddev / avg_memory if avg_memory > 0 else 0
            if cv > 0.3:
                score *= 0.9

        if leak_analysis.get("leak_detected", False):
            leak_severity = leak_analysis.get("leak_severity", "none")
            if leak_severity == "critical":
                score *= 0.3
            elif leak_severity == "high":
                score *= 0.5
            elif leak_severity == "medium":
                score *= 0.7
            elif leak_severity == "low":
                score *= 0.9

        return round(score, 1)

    def _calculate_load_test_score(self, metrics: dict[str, Any]) -> float:
        """
        Calculates load test score.
        """
        avg_response = metrics.get("avg_response_time_ms", 0)
        failure_rate = metrics.get("failure_rate_percent", 0)

        response_score: float
        if avg_response < 100:
            response_score = 100.0
        elif avg_response < 200:
            response_score = 90.0
        elif avg_response < 500:
            response_score = 80.0
        elif avg_response < 1000:
            response_score = 70.0
        elif avg_response < 2000:
            response_score = 50.0
        else:
            response_score = 30.0

        failure_score: float
        if failure_rate == 0:
            failure_score = 100.0
        elif failure_rate < 1:
            failure_score = 90.0
        elif failure_rate < 5:
            failure_score = 70.0
        elif failure_rate < 10:
            failure_score = 50.0
        else:
            failure_score = 20.0

        total_score = response_score * 0.6 + failure_score * 0.4
        return round(total_score, 1)


def main() -> None:
    """
    Main function for CLI.
    """

    parser = argparse.ArgumentParser(description="Performance test results analysis")
    parser.add_argument(
        "--benchmark-json",
        help="Path to JSON file with benchmark results",
    )
    parser.add_argument("--load-csv", help="Path to CSV file with load test results")
    parser.add_argument(
        "--memory-json",
        help="Path to JSON file with memory test results",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for saving reports (default: monitoring/<type>)",
    )
    parser.add_argument(
        "--test-type",
        help="Test type: benchmark, load, memory",
        default="benchmark",
    )

    args = parser.parse_args()

    analyzer = PerformanceAnalyzer(args.output_dir, test_type=args.test_type)

    if args.test_type == "benchmark" and args.benchmark_json:
        print(f"Analyzing benchmark results: {args.benchmark_json}")
        report = analyzer.analyze_benchmark_results(args.benchmark_json)
        report_path = analyzer.save_report(report)
        print(f"Report saved: {report_path}")
        print(f"Final score: {report.get('performance_score', 0)}/100")
    elif args.test_type == "load" and args.load_csv:
        print(f"Analyzing load tests: {args.load_csv}")
        report = analyzer.analyze_load_test_results(args.load_csv)
        report_path = analyzer.save_report(report)
        print(f"Report saved: {report_path}")
        print(f"Final score: {report.get('load_test_score', 0)}/100")
    elif args.test_type == "memory" and args.memory_json:
        print(f"Analyzing memory tests: {args.memory_json}")
        report = analyzer.analyze_memory_results(args.memory_json)
        report_path = analyzer.save_report(report)
        print(f"Report saved: {report_path}")
        print(f"Final score: {report.get('memory_score', 0)}/100")
    else:
        print("No results file path provided or test type not specified.")
        return
    print(
        f"Final score: {report.get('performance_score', report.get('memory_score', report.get('load_test_score', 0)))}/100",
    )


if __name__ == "__main__":
    main()
