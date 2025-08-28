"""
Memory usage tests for monitoring application performance.
"""

import gc
import json
import time
from pathlib import Path

import psutil

from app.models.domain.role import RoleEnum
from app.models.schemas.user import UserCreate


class TestMemoryUsage:
    """
    Memory usage tests.
    """

    def test_basic_memory_monitoring(self) -> None:
        """
        Basic memory monitoring test.
        """
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024

        test_data = []
        for i in range(1000):
            test_data.append(
                {
                    "id": i,
                    "username": f"user_{i}",
                    "email": f"user_{i}@example.com",
                    "data": "x" * 100,
                },
            )

        memory_after = process.memory_info().rss / 1024 / 1024
        memory_diff = memory_after - memory_before

        assert memory_diff < 50, f"Memory usage too high: {memory_diff}MB"
        assert len(test_data) == 1000

        del test_data
        gc.collect()

        memory_final = process.memory_info().rss / 1024 / 1024
        memory_leak = memory_final - memory_before

        assert memory_leak < 10, f"Memory leak detected: {memory_leak}MB not released"

    def test_memory_growth_pattern(self) -> None:
        """
        Memory growth pattern test.
        """
        process = psutil.Process()
        memory_readings = []

        initial_memory = process.memory_info().rss / 1024 / 1024

        for iteration in range(5):
            temp_data = []
            for i in range(200):
                temp_data.append(
                    {
                        "iteration": iteration,
                        "index": i,
                        "content": f"data_{iteration}_{i}" * 10,
                    },
                )

            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_readings.append(memory_mb)

            del temp_data
            gc.collect()

            time.sleep(0.1)

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_readings.append(final_memory)

        assert len(memory_readings) == 6

        max_memory = max(memory_readings)
        min_memory = min(memory_readings)
        memory_range = max_memory - min_memory

        assert memory_range < 100, f"Memory range too large: {memory_range}MB"

        memory_leak = final_memory - initial_memory
        assert memory_leak < 15, f"Memory leak detected: {memory_leak}MB not released"

    def test_user_data_memory_usage(self) -> None:
        """
        User data memory usage test.
        """
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024

        users = []
        for i in range(100):
            user_data = UserCreate(
                username=f"memuser_{i}",
                email=f"memuser_{i}@example.com",
                password="Password123",
                full_name=f"Memory User {i}",
                role=RoleEnum.USER,
            )
            users.append(user_data)

        memory_after = process.memory_info().rss / 1024 / 1024
        memory_diff = memory_after - memory_before

        assert memory_diff < 20, f"User data memory usage too high: {memory_diff}MB"
        assert len(users) == 100

        del users
        gc.collect()

        memory_final = process.memory_info().rss / 1024 / 1024
        memory_leak = memory_final - memory_before

        assert memory_leak < 5, f"Memory leak detected: {memory_leak}MB not released"

    def test_system_resource_monitoring(self) -> None:
        """
        System resource monitoring test.
        """
        process = psutil.Process()

        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        assert cpu_percent >= 0, "CPU percent should be non-negative"
        assert memory_mb > 0, "Memory usage should be positive"
        assert memory_mb < 1000, "Memory usage seems too high for tests"

        system_memory = psutil.virtual_memory()
        available_memory_mb = system_memory.available / 1024 / 1024

        assert available_memory_mb > 100, "System should have at least 100MB available"

    def test_memory_leak_detection_simple(self) -> None:
        """
        Simple memory leak detection test.
        """
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024
        memory_readings = [initial_memory]

        for cycle in range(3):
            data_list = []
            for i in range(500):
                data_list.append(
                    {"cycle": cycle, "index": i, "content": f"test_data_{cycle}_{i}"},
                )

            del data_list
            gc.collect()

            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_readings.append(memory_mb)

            time.sleep(0.1)

        gc.collect()
        time.sleep(0.2)
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_readings.append(final_memory)

        if len(memory_readings) >= 2:
            memory_growth = memory_readings[-1] - memory_readings[0]
            assert memory_growth < 20, f"Memory leak detected: {memory_growth}MB growth"

            final_leak = final_memory - initial_memory
            assert final_leak < 15, f"Final memory leak: {final_leak}MB not released"

    def test_concurrent_memory_simulation(self) -> None:
        """
        Concurrent memory usage simulation.
        """
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024

        request_data = []

        for request_id in range(50):
            request_info = {
                "request_id": request_id,
                "timestamp": time.time(),
                "data": [f"item_{i}" for i in range(20)],
                "metadata": {
                    "user_agent": "test_agent",
                    "ip": f"192.168.1.{request_id % 255}",
                    "session": f"session_{request_id}",
                },
            }
            request_data.append(request_info)

        memory_after = process.memory_info().rss / 1024 / 1024
        memory_diff = memory_after - memory_before

        assert len(request_data) == 50
        assert memory_diff < 30, f"Concurrent memory usage too high: {memory_diff}MB"

        del request_data
        gc.collect()

        memory_final = process.memory_info().rss / 1024 / 1024
        memory_leak = memory_final - memory_before

        assert memory_leak < 8, f"Memory leak detected: {memory_leak}MB not released"

    def test_large_data_processing_memory(self) -> None:
        """
        Large data processing memory test.
        """
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024

        total_processed = 0

        for batch in range(5):
            batch_data = []
            for i in range(200):
                batch_data.append(
                    {
                        "batch": batch,
                        "item": i,
                        "payload": "x" * 50,
                    },
                )

            processed_data = []
            for item in batch_data:
                processed_item = {
                    "id": f"{item['batch']}_{item['item']}",
                    "processed": True,
                    "size": len(item["payload"]),  # type: ignore[arg-type]
                }
                processed_data.append(processed_item)

            total_processed += len(processed_data)

            del batch_data
            del processed_data
            gc.collect()

        memory_after = process.memory_info().rss / 1024 / 1024
        memory_diff = memory_after - memory_before

        gc.collect()
        time.sleep(0.1)
        memory_final = process.memory_info().rss / 1024 / 1024
        memory_leak = memory_final - memory_before

        assert total_processed == 1000
        assert memory_diff < 40, (
            f"Batch processing memory usage too high: {memory_diff}MB"
        )
        assert memory_leak < 15, f"Memory leak detected: {memory_leak}MB not released"

    def test_memory_usage_with_json_output(self) -> None:
        """
        Memory usage test with JSON output saving.
        """
        process = psutil.Process()
        memory_data = []

        for i in range(10):
            test_data = []
            for j in range(100):
                test_data.append({"id": j, "data": f"test_data_{i}_{j}" * 5})

            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_data.append(
                {
                    "timestamp": time.time(),
                    "memory_mb": round(memory_mb, 2),
                    "test_name": f"memory_test_{i}",
                    "iteration": i,
                },
            )

            del test_data
            gc.collect()
            time.sleep(0.1)

        final_memory_mb = process.memory_info().rss / 1024 / 1024
        memory_data.append(
            {
                "timestamp": time.time(),
                "memory_mb": round(final_memory_mb, 2),
                "test_name": "final_measurement",
                "iteration": "final",
            }
        )

        monitoring_dir = Path("monitoring")
        memory_dir = monitoring_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)

        memory_file = memory_dir / "memory.json"
        with open(memory_file, "w") as f:
            json.dump(memory_data, f, indent=2)

        assert memory_file.exists(), "Memory JSON file was not created"
        assert len(memory_data) == 11, "Should have 10 test measurements + 1 final"

        initial_memory = memory_data[0]["memory_mb"]
        final_memory = memory_data[-1]["memory_mb"]
        memory_growth = final_memory - initial_memory

        assert memory_growth < 20, (
            f"Excessive memory growth detected: {memory_growth}MB"
        )

        print(f"Memory data saved to {memory_file}")
