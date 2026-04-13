"""WSQLite Stress Test Suite

Comprehensive stress testing for wsqlite library.
Tests concurrent access, bulk operations, memory usage, and more.

Usage:
    python -m stress_test.run --scenario bulk --records 100000
    python -m stress_test.run --scenario concurrent --threads 100
    python -m stress_test.run --all --report html

Examples:
    # Basic stress test
    python -m stress_test.run --records 50000

    # Concurrent writes
    python -m stress_test.run --scenario concurrent --threads 50 --records 10000

    # Full benchmark suite
    python -m stress_test.run --all --report html --output ./reports
"""

import argparse
import asyncio
import gc
import json
import os
import random
import shutil
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean, median, stdev
from threading import Lock
from typing import Any, Optional

import tracemalloc

tracemalloc.start()

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from pydantic import BaseModel


DB_PATH = "stress_test.db"


@dataclass
class StressConfig:
    db_path: str = DB_PATH
    scenario: str = "bulk"
    records: int = 10000
    threads: int = 50
    batch_size: int = 1000
    warmup: int = 100
    report_format: str = "text"
    output_dir: str = "./reports"
    verbose: bool = False


class Account(BaseModel):
    id: int
    name: str
    email: str
    age: int
    balance: float
    status: str
    created_at: str
    tags: str


class Transaction(BaseModel):
    id: int
    account_id: int
    amount: float
    type: str
    description: str
    created_at: str


class OperationMetrics:
    def __init__(self, operation: str, duration_ms: float, success: bool = True, error: str = None):
        self.operation = operation
        self.duration_ms = duration_ms
        self.success = success
        self.error = error


class MetricsCollector:
    def __init__(self):
        self.lock = Lock()
        self.operations: list[OperationMetrics] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.memory_samples: list[float] = []
        self._process = psutil.Process() if HAS_PSUTIL else None
        self._start_memory = 0

    def start(self):
        self.start_time = time.perf_counter()
        gc.collect()
        tracemalloc.start()
        if self._process:
            self._start_memory = self._process.memory_info().rss / 1024 / 1024

    def stop(self):
        self.end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        if self._process:
            self._start_memory = self._process.memory_info().rss / 1024 / 1024 - self._start_memory

    def record(self, operation: str, duration_ms: float, success: bool = True, error: str = None):
        with self.lock:
            self.operations.append(OperationMetrics(operation, duration_ms, success, error))

    def sample_memory(self):
        if self._process:
            memory_mb = self._process.memory_info().rss / 1024 / 1024
            with self.lock:
                self.memory_samples.append(memory_mb)

    def get_stats(self) -> dict:
        durations = [op.duration_ms for op in self.operations if op.success]
        failures = [op for op in self.operations if not op.success]
        successes = len(self.operations) - len(failures)

        if not durations:
            return {}

        sorted_durations = sorted(durations)
        n = len(sorted_durations)
        elapsed = self.end_time - self.start_time if self.end_time else 1

        stats = {
            "total_operations": len(self.operations),
            "successful": successes,
            "failed": len(failures),
            "success_rate": successes / len(self.operations) * 100,
            "total_time_ms": sum(durations),
            "ops_per_second": len(self.operations) / elapsed,
            "latency_mean_ms": mean(durations),
            "latency_median_ms": median(durations),
            "latency_min_ms": min(durations),
            "latency_max_ms": max(durations),
            "latency_std_ms": stdev(durations) if len(durations) > 1 else 0,
            "latency_p50_ms": sorted_durations[int(n * 0.50)] if n > 0 else 0,
            "latency_p75_ms": sorted_durations[int(n * 0.75)] if n > 0 else 0,
            "latency_p90_ms": sorted_durations[int(n * 0.90)] if n > 0 else 0,
            "latency_p95_ms": sorted_durations[int(n * 0.95)] if n > 0 else 0,
            "latency_p99_ms": sorted_durations[int(n * 0.99)] if n > 0 else 0,
            "latency_p999_ms": sorted_durations[int(n * 0.999)]
            if n > 1000
            else sorted_durations[-1]
            if sorted_durations
            else 0,
            "peak_memory_mb": max(self.memory_samples) if self.memory_samples else 0,
            "memory_delta_mb": self._start_memory,
            "by_operation": self._stats_by_operation(),
        }

        if failures:
            stats["errors"] = self._error_summary(failures)

        return stats

    def _stats_by_operation(self) -> dict:
        ops_by_type: dict[str, list[float]] = {}
        for op in self.operations:
            if op.success:
                if op.operation not in ops_by_type:
                    ops_by_type[op.operation] = []
                ops_by_type[op.operation].append(op.duration_ms)

        return {
            op_type: {
                "count": len(durations),
                "mean_ms": mean(durations),
                "median_ms": median(durations),
                "p95_ms": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                "min_ms": min(durations) if durations else 0,
                "max_ms": max(durations) if durations else 0,
            }
            for op_type, durations in ops_by_type.items()
        }

    def _error_summary(self, failures: list) -> dict:
        errors: dict[str, int] = {}
        for op in failures:
            key = f"{op.operation}:{op.error}"
            errors[key] = errors.get(key, 0) + 1
        return dict(sorted(errors.items(), key=lambda x: -x[1])[:10])


def generate_account(uid: int) -> Account:
    return Account(
        id=uid,
        name="".join(random.choices(string.ascii_letters, k=12)),
        email=f"user{uid}@test.com",
        age=random.randint(18, 80),
        balance=round(random.uniform(0, 50000), 2),
        status=random.choice(["active", "inactive", "pending", "suspended"]),
        created_at=datetime.now().isoformat(),
        tags=json.dumps(random.sample(["vip", "new", "premium", "trial"], k=2)),
    )


def cleanup_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    for ext in ["-wal", "-shm"]:
        if os.path.exists(f"{db_path}{ext}"):
            os.remove(f"{db_path}{ext}")


class BulkInsertScenario:
    name = "bulk_insert"

    def __init__(self, config: StressConfig):
        self.config = config
        self.metrics = MetricsCollector()

    def setup(self):
        cleanup_db(self.config.db_path)

    def run(self) -> dict:
        from wsqlite import WSQLite, TableSync

        sync = TableSync(Account, self.config.db_path)
        sync.create_if_not_exists()

        db = WSQLite(Account, self.config.db_path, pool_size=min(20, self.config.threads))

        accounts = [generate_account(i) for i in range(self.config.records)]
        self.metrics.start()

        for i in range(0, len(accounts), self.config.batch_size):
            batch = accounts[i : i + self.config.batch_size]
            start = time.perf_counter()
            db.insert_many(batch)
            duration = (time.perf_counter() - start) * 1000
            self.metrics.record("insert_many", duration)
            self.metrics.sample_memory()

        self.metrics.stop()
        return self.metrics.get_stats()


class ConcurrentWritesScenario:
    name = "concurrent_writes"

    def __init__(self, config: StressConfig):
        self.config = config
        self.metrics = MetricsCollector()

    def setup(self):
        cleanup_db(self.config.db_path)

    def run(self) -> dict:
        from wsqlite import WSQLite, TableSync

        sync = TableSync(Account, self.config.db_path)
        sync.create_if_not_exists()

        records_per_thread = self.config.records // self.config.threads

        def write_batch(thread_id: int) -> list:
            db = WSQLite(Account, self.config.db_path, pool_size=5)
            start_id = thread_id * records_per_thread
            results = []

            for batch_start in range(0, records_per_thread, self.config.batch_size):
                batch_end = min(batch_start + self.config.batch_size, records_per_thread)
                accounts = [
                    generate_account(start_id + batch_start + i)
                    for i in range(batch_end - batch_start)
                ]

                start = time.perf_counter()
                db.insert_many(accounts)
                duration = (time.perf_counter() - start) * 1000
                results.append(duration)

            return results

        self.metrics.start()

        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(write_batch, i) for i in range(self.config.threads)]

            for future in as_completed(futures):
                for duration in future.result():
                    self.metrics.record("concurrent_insert", duration)
                    self.metrics.sample_memory()

        self.metrics.stop()
        return self.metrics.get_stats()


class MixedWorkloadScenario:
    name = "mixed_workload"

    def __init__(self, config: StressConfig):
        self.config = config
        self.metrics = MetricsCollector()

    def setup(self):
        cleanup_db(self.config.db_path)

    def run(self) -> dict:
        from wsqlite import WSQLite, TableSync

        sync = TableSync(Account, self.config.db_path)
        sync.create_if_not_exists()

        db = WSQLite(Account, self.config.db_path, pool_size=min(20, self.config.threads))

        accounts = [generate_account(i) for i in range(self.config.records // 2)]
        db.insert_many(accounts)

        operations = ["select", "insert", "update", "count"]

        def mixed_operation(op_id: int):
            op = random.choice(operations)
            start = time.perf_counter()
            error = None

            try:
                if op == "select":
                    db.get_all()
                elif op == "insert":
                    db.insert(generate_account(1000000 + op_id))
                elif op == "update":
                    if self.config.records > 0:
                        db.update(1, generate_account(1))
                elif op == "count":
                    db.count()
            except Exception as e:
                error = str(e)[:50]

            duration = (time.perf_counter() - start) * 1000
            self.metrics.record(op, duration, error is None, error)

        self.metrics.start()

        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(self.config.records)]
            for future in as_completed(futures):
                pass

        self.metrics.stop()
        return self.metrics.get_stats()


class PaginationScenario:
    name = "pagination"

    def __init__(self, config: StressConfig):
        self.config = config
        self.metrics = MetricsCollector()

    def setup(self):
        cleanup_db(self.config.db_path)

    def run(self) -> dict:
        from wsqlite import WSQLite, TableSync

        sync = TableSync(Account, self.config.db_path)
        sync.create_if_not_exists()

        db = WSQLite(Account, self.config.db_path)

        accounts = [generate_account(i) for i in range(self.config.records)]
        db.insert_many(accounts)

        page_size = 100
        total_pages = self.config.records // page_size

        def fetch_page(page: int):
            start = time.perf_counter()
            db.get_page(page=page, per_page=page_size)
            return (time.perf_counter() - start) * 1000

        self.metrics.start()

        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [
                executor.submit(fetch_page, i % total_pages + 1) for i in range(self.config.records)
            ]
            for future in as_completed(futures):
                self.metrics.record("get_page", future.result())
                self.metrics.sample_memory()

        self.metrics.stop()
        return self.metrics.get_stats()


SCENARIOS = {
    "bulk": BulkInsertScenario,
    "concurrent": ConcurrentWritesScenario,
    "mixed": MixedWorkloadScenario,
    "pagination": PaginationScenario,
}


def print_report(stats: dict, title: str = ""):
    if not stats:
        print("No stats available")
        return

    print(f"\n{'=' * 70}")
    print(f"STRESS TEST RESULTS: {title}")
    print(f"{'=' * 70}")

    print(f"\n{'SUMMARY':=^70}")
    print(f"  Total operations:    {stats['total_operations']:>15,}")
    print(f"  Successful:          {stats['successful']:>15,}")
    print(f"  Failed:              {stats['failed']:>15,}")
    print(f"  Success rate:        {stats['success_rate']:>14.2f}%")
    print(f"  Ops/second:          {stats['ops_per_second']:>15,.0f}")

    print(f"\n{'LATENCY (ms)':=^70}")
    print(f"  Mean:               {stats['latency_mean_ms']:>15.3f}")
    print(f"  Median:             {stats['latency_median_ms']:>15.3f}")
    print(f"  Min:                {stats['latency_min_ms']:>15.3f}")
    print(f"  Max:                {stats['latency_max_ms']:>15.3f}")
    print(f"  Std Dev:            {stats['latency_std_ms']:>15.3f}")

    print(f"\n{'PERCENTILES (ms)':=^70}")
    print(f"  P50:                {stats['latency_p50_ms']:>15.3f}")
    print(f"  P75:                {stats['latency_p75_ms']:>15.3f}")
    print(f"  P90:                {stats['latency_p90_ms']:>15.3f}")
    print(f"  P95:                {stats['latency_p95_ms']:>15.3f}")
    print(f"  P99:                {stats['latency_p99_ms']:>15.3f}")
    print(f"  P99.9:              {stats['latency_p999_ms']:>15.3f}")

    if stats.get("peak_memory_mb"):
        print(f"\n{'MEMORY':=^70}")
        print(f"  Peak:               {stats['peak_memory_mb']:>15.2f} MB")

    if "by_operation" in stats:
        print(f"\n{'BY OPERATION':=^70}")
        print(f"  {'Operation':<20} {'Count':>10} {'Mean':>12} {'P95':>12} {'Max':>12}")
        print(f"  {'-' * 66}")
        for op, data in stats["by_operation"].items():
            print(
                f"  {op:<20} {data['count']:>10,} {data['mean_ms']:>11.3f} {data['p95_ms']:>11.3f} {data['max_ms']:>11.3f}"
            )

    if "errors" in stats:
        print(f"\n{'ERRORS':=^70}")
        for error, count in stats["errors"].items():
            print(f"  [{count:>5}x] {error}")

    print(f"\n{'=' * 70}")


def generate_html_report(stats: dict, output_path: str, title: str = ""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WSQLite Stress Test Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 40px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            color: #00d9ff; 
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
        }}
        .subtitle {{ color: #888; margin-bottom: 40px; }}
        .card {{ 
            background: rgba(22, 33, 62, 0.8);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h2 {{ color: #fff; margin-bottom: 20px; font-size: 1.3em; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .metric {{ 
            background: rgba(0, 217, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: #00d9ff; }}
        .metric-label {{ font-size: 0.85em; color: #888; margin-top: 5px; }}
        .success {{ color: #00ff88; }}
        .failure {{ color: #ff4757; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ color: #00d9ff; font-weight: 600; }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        .chart-container {{ position: relative; height: 300px; margin-top: 20px; }}
        .badge {{ 
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .badge-success {{ background: rgba(0, 255, 136, 0.2); color: #00ff88; }}
        .badge-failure {{ background: rgba(255, 71, 87, 0.2); color: #ff4757; }}
        .errors {{ background: rgba(255, 71, 87, 0.1); border: 1px solid rgba(255, 71, 87, 0.3); }}
        .errors td {{ color: #ff4757; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>WSQLite Stress Test Report</h1>
        <p class="subtitle">Generated: {timestamp} | Scenario: {title}</p>

        <div class="card">
            <h2>Summary</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{stats.get("total_operations", 0):,}</div>
                    <div class="metric-label">Total Operations</div>
                </div>
                <div class="metric">
                    <div class="metric-value {"success" if stats.get("success_rate", 0) > 99 else "failure"}">{stats.get("success_rate", 0):.2f}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{stats.get("ops_per_second", 0):,.0f}</div>
                    <div class="metric-label">Ops/Second</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{stats.get("latency_mean_ms", 0):.2f}ms</div>
                    <div class="metric-label">Avg Latency</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Latency Distribution</h2>
            <div class="chart-container">
                <canvas id="latencyChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>Latency Statistics (ms)</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Mean</td><td>{stats.get("latency_mean_ms", 0):.3f}</td></tr>
                <tr><td>Median</td><td>{stats.get("latency_median_ms", 0):.3f}</td></tr>
                <tr><td>Std Dev</td><td>{stats.get("latency_std_ms", 0):.3f}</td></tr>
                <tr><td>Min</td><td>{stats.get("latency_min_ms", 0):.3f}</td></tr>
                <tr><td>Max</td><td>{stats.get("latency_max_ms", 0):.3f}</td></tr>
            </table>
        </div>

        <div class="card">
            <h2>Percentiles (ms)</h2>
            <table>
                <tr><th>Percentile</th><th>Latency</th></tr>
                <tr><td>P50</td><td>{stats.get("latency_p50_ms", 0):.3f}</td></tr>
                <tr><td>P75</td><td>{stats.get("latency_p75_ms", 0):.3f}</td></tr>
                <tr><td>P90</td><td>{stats.get("latency_p90_ms", 0):.3f}</td></tr>
                <tr><td>P95</td><td>{stats.get("latency_p95_ms", 0):.3f}</td></tr>
                <tr><td>P99</td><td>{stats.get("latency_p99_ms", 0):.3f}</td></tr>
                <tr><td>P99.9</td><td>{stats.get("latency_p999_ms", 0):.3f}</td></tr>
            </table>
        </div>
"""

    if "by_operation" in stats:
        html += """
        <div class="card">
            <h2>Performance by Operation</h2>
            <table>
                <tr><th>Operation</th><th>Count</th><th>Mean (ms)</th><th>P95 (ms)</th><th>Max (ms)</th></tr>
"""
        for op, data in stats["by_operation"].items():
            html += f"""                <tr><td>{op}</td><td>{data["count"]:,}</td><td>{data["mean_ms"]:.3f}</td><td>{data["p95_ms"]:.3f}</td><td>{data["max_ms"]:.3f}</td></tr>
"""
        html += """            </table>
        </div>
"""

    if "errors" in stats and stats["errors"]:
        html += """
        <div class="card errors">
            <h2>Errors</h2>
            <table>
                <tr><th>Count</th><th>Error</th></tr>
"""
        for error, count in stats["errors"].items():
            html += f"""                <tr><td>{count}</td><td>{error}</td></tr>
"""
        html += """            </table>
        </div>
"""

    html += f"""
        <div class="card">
            <h2>Memory Usage</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{stats.get("peak_memory_mb", 0):.2f} MB</div>
                    <div class="metric-label">Peak Memory</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{stats.get("memory_delta_mb", 0):.2f} MB</div>
                    <div class="metric-label">Memory Delta</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('latencyChart'), {{
            type: 'bar',
            data: {{
                labels: ['P50', 'P75', 'P90', 'P95', 'P99', 'P99.9'],
                datasets: [{{
                    label: 'Latency (ms)',
                    data: [
                        {stats.get("latency_p50_ms", 0)},
                        {stats.get("latency_p75_ms", 0)},
                        {stats.get("latency_p90_ms", 0)},
                        {stats.get("latency_p95_ms", 0)},
                        {stats.get("latency_p99_ms", 0)},
                        {stats.get("latency_p999_ms", 0)}
                    ],
                    backgroundColor: 'rgba(0, 217, 255, 0.7)',
                    borderColor: '#00d9ff',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        ticks: {{ color: '#888' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#888' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="WSQLite Stress Test Suite")
    parser.add_argument(
        "--scenario",
        "-s",
        default="bulk",
        choices=["bulk", "concurrent", "mixed", "pagination", "all"],
    )
    parser.add_argument("--records", "-r", type=int, default=10000)
    parser.add_argument("--threads", "-t", type=int, default=50)
    parser.add_argument("--batch", "-b", type=int, default=1000)
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--report", choices=["text", "json", "html"], default="text")
    parser.add_argument("--output", "-o", default="./reports")
    parser.add_argument("--warmup", "-w", type=int, default=100)

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    config = StressConfig(
        db_path=args.db,
        scenario=args.scenario,
        records=args.records,
        threads=args.threads,
        batch_size=args.batch,
        report_format=args.report,
        output_dir=args.output,
        warmup=args.warmup,
    )

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           WSQLite Stress Test Suite v1.1.0                 ║
╠══════════════════════════════════════════════════════════════╣
║  Scenario:    {args.scenario:<40} ║
║  Records:     {args.records:>40,} ║
║  Threads:     {args.threads:>40} ║
║  Batch Size:  {args.batch:>40} ║
╚══════════════════════════════════════════════════════════════╝
""")

    scenarios_to_run = list(SCENARIOS.keys()) if args.scenario == "all" else [args.scenario]
    all_results = {}

    for scenario_name in scenarios_to_run:
        print(f"\n▶ Running scenario: {scenario_name}")

        scenario_class = SCENARIOS[scenario_name]
        scenario = scenario_class(config)
        scenario.setup()

        try:
            stats = scenario.run()
            all_results[scenario_name] = stats

            if args.report == "text":
                print_report(stats, scenario_name.upper())
            elif args.report == "html":
                output_path = os.path.join(args.output, f"stress_test_{scenario_name}.html")
                generate_html_report(stats, output_path, scenario_name.upper())
                print(f"  ✓ HTML report: {output_path}")
            elif args.report == "json":
                output_path = os.path.join(args.output, f"stress_test_{scenario_name}.json")
                with open(output_path, "w") as f:
                    json.dump(stats, f, indent=2)
                print(f"  ✓ JSON report: {output_path}")

        finally:
            cleanup_db(config.db_path)

    if args.scenario == "all" and len(all_results) > 1:
        print("\n" + "=" * 70)
        print("COMPARISON SUMMARY")
        print("=" * 70)
        print(f"\n{'Scenario':<25} {'Ops/sec':>15} {'Avg Latency':>15} {'Success':>10}")
        print("-" * 65)
        for name, stats in all_results.items():
            print(
                f"{name:<25} {stats['ops_per_second']:>15,.0f} {stats['latency_mean_ms']:>14.3f}ms {stats['success_rate']:>9.2f}%"
            )

    print("\n✅ Stress test completed!")


if __name__ == "__main__":
    main()
