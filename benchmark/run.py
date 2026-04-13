"""WSQLite Benchmark - Compare with other SQLite libraries

Measures:
- Operations per second
- Latency (mean, p50, p95, p99)
- Memory usage
- Scalability with concurrency

Usage:
    python -m benchmark.run --all
    python -m benchmark.run --lib sqlite3 --lib wsqlite --scenario insert
    python -m benchmark.run --scenario bulk --iterations 10000
"""

import argparse
import json
import os
import random
import shutil
import statistics
import string
import sys
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

tracemalloc.start()


DB_PATH = "benchmark.db"


@dataclass
class BenchmarkResult:
    library: str
    scenario: str
    operations: int
    duration_sec: float
    ops_per_second: float
    latency_mean_ms: float
    latency_p50_ms: float
    latency_p75_ms: float
    latency_p90_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    memory_peak_mb: float
    errors: int

    def to_dict(self) -> dict:
        return {
            "library": self.library,
            "scenario": self.scenario,
            "operations": self.operations,
            "duration_sec": self.duration_sec,
            "ops_per_second": self.ops_per_second,
            "latency_mean_ms": self.latency_mean_ms,
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p95_ms": self.latency_p95_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "memory_peak_mb": self.memory_peak_mb,
            "errors": self.errors,
        }


class Benchmark:
    """Base benchmark class."""

    name: str = "base"
    db_path: str = DB_PATH

    def setup(self):
        raise NotImplementedError

    def teardown(self):
        raise NotImplementedError

    def insert(self, data: dict) -> float:
        raise NotImplementedError

    def bulk_insert(self, data_list: list[dict]) -> float:
        raise NotImplementedError

    def select_all(self) -> float:
        raise NotImplementedError


class SQLite3Benchmark(Benchmark):
    """Baseline implementation using sqlite3."""

    name = "sqlite3 (stdlib)"

    def __init__(self):
        self.conn = None
        self.db_path = "benchmark_sqlite3.db"

    def setup(self):
        import sqlite3

        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.execute("""
            CREATE TABLE account (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                age INTEGER,
                balance REAL
            )
        """)
        self.conn.commit()

    def teardown(self):
        if self.conn:
            self.conn.close()
        for ext in ["", "-wal", "-shm"]:
            path = f"{self.db_path}{ext}"
            if os.path.exists(path):
                os.remove(path)

    def insert(self, data: dict) -> float:
        start = time.perf_counter()
        self.conn.execute(
            "INSERT INTO account VALUES (?, ?, ?, ?, ?)",
            (data["id"], data["name"], data["email"], data["age"], data["balance"]),
        )
        self.conn.commit()
        return (time.perf_counter() - start) * 1000

    def select_all(self) -> float:
        start = time.perf_counter()
        cursor = self.conn.execute("SELECT * FROM account")
        cursor.fetchall()
        return (time.perf_counter() - start) * 1000

    def bulk_insert(self, data_list: list[dict]) -> float:
        start = time.perf_counter()
        self.conn.executemany(
            "INSERT INTO account VALUES (?, ?, ?, ?, ?)",
            [(d["id"], d["name"], d["email"], d["age"], d["balance"]) for d in data_list],
        )
        self.conn.commit()
        return (time.perf_counter() - start) * 1000


class WSQLiteBenchmark(Benchmark):
    """WSQLite implementation."""

    name = "wSQLite (Pool)"

    def __init__(self):
        self.db = None
        self.db_path = "benchmark_wsqlite.db"
        from pydantic import BaseModel

        class Account(BaseModel):
            id: int
            name: str
            email: str
            age: int
            balance: float

        self.model = Account

    def setup(self):
        from wsqlite import WSQLite, TableSync

        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        sync = TableSync(self.model, self.db_path)
        sync.create_if_not_exists()

        self.db = WSQLite(self.model, self.db_path, pool_size=10, min_pool_size=2)

    def teardown(self):
        from wsqlite import close_pool

        close_pool()
        for ext in ["", "-wal", "-shm"]:
            path = f"{self.db_path}{ext}"
            if os.path.exists(path):
                os.remove(path)

    def _generate(self, id: int) -> Any:
        return self.model(
            id=id,
            name="".join(random.choices(string.ascii_letters, k=10)),
            email=f"user{id}@test.com",
            age=random.randint(18, 80),
            balance=random.uniform(0, 10000),
        )

    def insert(self, data: dict) -> float:
        start = time.perf_counter()
        self.db.insert(self._generate(data["id"]))
        return (time.perf_counter() - start) * 1000

    def select_all(self) -> float:
        start = time.perf_counter()
        self.db.get_all()
        return (time.perf_counter() - start) * 1000

    def bulk_insert(self, data_list: list[dict]) -> float:
        start = time.perf_counter()
        self.db.insert_many([self._generate(d["id"]) for d in data_list])
        return (time.perf_counter() - start) * 1000


class SQLAlchemyBenchmark(Benchmark):
    """SQLAlchemy ORM implementation."""

    name = "SQLAlchemy"

    def __init__(self):
        self.db_path = "benchmark_sqlalchemy.db"
        self.engine = None
        self.Session = None

    def setup(self):
        try:
            from sqlalchemy import create_engine, Column, Integer, String, Float
            from sqlalchemy.orm import sessionmaker, declarative_base

            if os.path.exists(self.db_path):
                os.remove(self.db_path)

            self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
            self.Base = declarative_base()

            class Account(self.Base):
                __tablename__ = "account"
                id = Column(Integer, primary_key=True)
                name = Column(String)
                email = Column(String)
                age = Column(Integer)
                balance = Column(Float)

            self.Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)

        except ImportError:
            raise ImportError("SQLAlchemy not installed. Run: pip install sqlalchemy")

    def teardown(self):
        if self.engine:
            self.engine.dispose()
        for ext in ["", "-wal", "-shm"]:
            path = f"{self.db_path}{ext}"
            if os.path.exists(path):
                os.remove(path)

    def _generate(self, id: int):
        from sqlalchemy import Column, Integer, String, Float
        from sqlalchemy.orm import declarative_base

        return type(
            "Account",
            (),
            {
                "id": id,
                "name": "".join(random.choices(string.ascii_letters, k=10)),
                "email": f"user{id}@test.com",
                "age": random.randint(18, 80),
                "balance": random.uniform(0, 10000),
            },
        )()

    def insert(self, data: dict) -> float:
        from sqlalchemy import Column, Integer, String, Float
        from sqlalchemy.orm import declarative_base

        start = time.perf_counter()
        session = self.Session()
        try:
            Account = type(
                "Account",
                (),
                {
                    "__tablename__": "account",
                    "id": Column(Integer, primary_key=True),
                    "name": Column(String),
                    "email": Column(String),
                    "age": Column(Integer),
                    "balance": Column(Float),
                },
            )
            obj = Account(
                id=data["id"],
                name=data["name"],
                email=data["email"],
                age=data["age"],
                balance=data["balance"],
            )
            session.add(obj)
            session.commit()
        finally:
            session.close()
        return (time.perf_counter() - start) * 1000

    def select_all(self) -> float:
        from sqlalchemy import Column, Integer, String, Float
        from sqlalchemy.orm import declarative_base

        start = time.perf_counter()
        session = self.Session()
        try:
            Account = type(
                "Account",
                (),
                {
                    "__tablename__": "account",
                    "id": Column(Integer, primary_key=True),
                    "name": Column(String),
                    "email": Column(String),
                    "age": Column(Integer),
                    "balance": Column(Float),
                },
            )
            session.query(Account).all()
        finally:
            session.close()
        return (time.perf_counter() - start) * 1000

    def bulk_insert(self, data_list: list[dict]) -> float:
        from sqlalchemy import Column, Integer, String, Float
        from sqlalchemy.orm import declarative_base

        start = time.perf_counter()
        session = self.Session()
        try:
            Account = type(
                "Account",
                (),
                {
                    "__tablename__": "account",
                    "id": Column(Integer, primary_key=True),
                    "name": Column(String),
                    "email": Column(String),
                    "age": Column(Integer),
                    "balance": Column(Float),
                },
            )
            session.add_all(
                [
                    Account(
                        id=d["id"],
                        name=d["name"],
                        email=d["email"],
                        age=d["age"],
                        balance=d["balance"],
                    )
                    for d in data_list
                ]
            )
            session.commit()
        finally:
            session.close()
        return (time.perf_counter() - start) * 1000


def generate_data(count: int) -> list[dict]:
    return [
        {
            "id": i,
            "name": "".join(random.choices(string.ascii_letters, k=10)),
            "email": f"user{i}@test.com",
            "age": random.randint(18, 80),
            "balance": random.uniform(0, 10000),
        }
        for i in range(count)
    ]


def run_scenario(
    benchmark: Benchmark,
    scenario: str,
    iterations: int,
    warmup: int = 100,
) -> Optional[BenchmarkResult]:
    """Run a benchmark scenario."""
    print(f"  {benchmark.name}: ", end="", flush=True)

    latencies = []
    errors = 0

    try:
        benchmark.setup()
    except ImportError as e:
        print(f"SKIPPED ({e})")
        return None
    except Exception as e:
        print(f"ERROR ({e})")
        return None

    try:
        if warmup > 0:
            warmup_data = generate_data(min(warmup, 100))
            for d in warmup_data[: min(warmup, 100)]:
                try:
                    benchmark.insert(d)
                except:
                    pass

        tracemalloc.start()
        process = psutil.Process() if HAS_PSUTIL else None
        start_time = time.perf_counter()

        if scenario == "insert":
            for i in range(iterations):
                data = generate_data(1)[0]
                data["id"] = 10000 + i
                try:
                    duration = benchmark.insert(data)
                    latencies.append(duration)
                except Exception as e:
                    errors += 1

        elif scenario == "select":
            for d in generate_data(1000):
                try:
                    benchmark.insert(d)
                except:
                    pass

            for _ in range(iterations):
                try:
                    duration = benchmark.select_all()
                    latencies.append(duration)
                except Exception as e:
                    errors += 1

        elif scenario == "bulk":
            data = generate_data(iterations)
            try:
                duration = benchmark.bulk_insert(data)
                latencies.append(duration)
            except Exception as e:
                errors += 1

        duration = time.perf_counter() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        result = BenchmarkResult(
            library=benchmark.name,
            scenario=scenario,
            operations=iterations - errors,
            duration_sec=duration,
            ops_per_second=(iterations - errors) / duration if duration > 0 else 0,
            latency_mean_ms=statistics.mean(latencies) if latencies else 0,
            latency_p50_ms=sorted_latencies[int(n * 0.50)] if latencies and n > 0 else 0,
            latency_p75_ms=sorted_latencies[int(n * 0.75)] if latencies and n > 0 else 0,
            latency_p90_ms=sorted_latencies[int(n * 0.90)] if latencies and n > 0 else 0,
            latency_p95_ms=sorted_latencies[int(n * 0.95)] if latencies and n > 0 else 0,
            latency_p99_ms=sorted_latencies[int(n * 0.99)] if latencies and n > 0 else 0,
            memory_peak_mb=peak / 1024 / 1024,
            errors=errors,
        )

        print(
            f"{result.ops_per_second:>10,.0f} ops/s | "
            f"{result.latency_mean_ms:>8.3f}ms avg | "
            f"P95: {result.latency_p95_ms:>8.3f}ms | "
            f"Mem: {result.memory_peak_mb:>6.2f}MB"
        )

    finally:
        try:
            benchmark.teardown()
        except:
            pass

    return result


def print_comparison(results: list[BenchmarkResult]):
    if not results:
        return

    print("\n" + "=" * 100)
    print("BENCHMARK COMPARISON")
    print("=" * 100)
    print(
        f"{'Library':<20} {'Ops/sec':>12} {'Mean ms':>10} {'P50 ms':>10} {'P95 ms':>10} {'P99 ms':>10} {'Mem MB':>10}"
    )
    print("-" * 100)

    sorted_results = sorted(results, key=lambda r: -r.ops_per_second)
    winner = sorted_results[0] if sorted_results else None

    for r in sorted_results:
        marker = "🏆" if r.library == winner.library else "  "
        print(
            f"{marker}{r.library:<18} "
            f"{r.ops_per_second:>12,.0f} "
            f"{r.latency_mean_ms:>10.3f} "
            f"{r.latency_p50_ms:>10.3f} "
            f"{r.latency_p95_ms:>10.3f} "
            f"{r.latency_p99_ms:>10.3f} "
            f"{r.memory_peak_mb:>10.2f}"
        )

    print("-" * 100)

    if winner and len(sorted_results) > 1:
        second = sorted_results[1]
        if second.ops_per_second > 0:
            improvement = ((winner.ops_per_second / second.ops_per_second) - 1) * 100
            print(f"\n🏆 WINNER: {winner.library}")
            if improvement > 0:
                print(f"   {improvement:.1f}% faster than {second.library}")
            else:
                print(f"   {abs(improvement):.1f}% slower than {second.library}")


def generate_html_report(results: list[BenchmarkResult], output_path: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scenarios = sorted(set(r.scenario for r in results))

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WSQLite Benchmark Results</title>
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
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{
            color: #00d9ff;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{ color: #888; margin-bottom: 40px; }}
        .card {{
            background: rgba(22, 33, 62, 0.8);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        h2 {{ color: #fff; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ color: #00d9ff; }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        .winner {{ background: rgba(0, 255, 136, 0.1); }}
        .winner td {{ color: #00ff88; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #00d9ff; }}
        .metric-label {{ font-size: 0.8em; color: #888; }}
        .chart-container {{ height: 400px; margin-top: 20px; }}
        .tabs {{ margin-bottom: 20px; }}
        .tab {{
            display: inline-block;
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            margin-right: 5px;
        }}
        .tab.active {{
            background: #00d9ff;
            color: #1a1a2e;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>WSQLite Benchmark</h1>
        <p class="subtitle">Generated: {timestamp}</p>
"""

    for scenario in scenarios:
        scenario_results = [r for r in results if r.scenario == scenario]
        if not scenario_results:
            continue

        sorted_scenario = sorted(scenario_results, key=lambda r: -r.ops_per_second)
        winner = sorted_scenario[0]

        html += f"""
        <div class="card">
            <h2>{scenario.upper()} - Winner: {winner.library}</h2>
            <table>
                <tr>
                    <th>Library</th>
                    <th>Ops/sec</th>
                    <th>Mean (ms)</th>
                    <th>P50 (ms)</th>
                    <th>P95 (ms)</th>
                    <th>P99 (ms)</th>
                    <th>Memory (MB)</th>
                </tr>
"""
        for r in sorted_scenario:
            is_winner = r.library == winner.library
            html += f"""
                <tr{' class="winner"' if is_winner else ""}>
                    <td>{"🏆 " if is_winner else ""}{r.library}</td>
                    <td>{r.ops_per_second:,.0f}</td>
                    <td>{r.latency_mean_ms:.3f}</td>
                    <td>{r.latency_p50_ms:.3f}</td>
                    <td>{r.latency_p95_ms:.3f}</td>
                    <td>{r.latency_p99_ms:.3f}</td>
                    <td>{r.memory_peak_mb:.2f}</td>
                </tr>
"""
        html += """
            </table>
        </div>
"""

    html += f"""
        <div class="card">
            <h2>Performance Comparison Chart</h2>
            <div class="chart-container">
                <canvas id="comparisonChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([r.library for r in sorted_scenario])},
                datasets: [{{
                    label: 'Operations per Second',
                    data: {json.dumps([r.ops_per_second for r in sorted_scenario])},
                    backgroundColor: {json.dumps(["rgba(0, 255, 136, 0.7)" if r.library == winner.library else "rgba(0, 217, 255, 0.7)" for r in sorted_scenario])},
                    borderColor: {json.dumps(["#00ff88" if r.library == winner.library else "#00d9ff" for r in sorted_scenario])},
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
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
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
    parser = argparse.ArgumentParser(description="WSQLite Benchmark")
    parser.add_argument(
        "--libraries",
        "-l",
        nargs="+",
        choices=["sqlite3", "sqlalchemy", "wsqlite", "all"],
        default=["sqlite3", "wsqlite"],
    )
    parser.add_argument(
        "--scenario", "-s", choices=["insert", "select", "bulk", "all"], default="insert"
    )
    parser.add_argument("--iterations", "-i", type=int, default=1000)
    parser.add_argument("--warmup", "-w", type=int, default=100)
    parser.add_argument("--output", "-o", help="Output file (JSON or HTML)")

    args = parser.parse_args()

    benchmarks: list[Callable[[], Benchmark]] = []
    if "sqlite3" in args.libraries or "all" in args.libraries:
        benchmarks.append(SQLite3Benchmark)
    if "wsqlite" in args.libraries or "all" in args.libraries:
        benchmarks.append(WSQLiteBenchmark)
    if "sqlalchemy" in args.libraries or "all" in args.libraries:
        benchmarks.append(SQLAlchemyBenchmark)

    scenarios = ["insert", "select", "bulk"] if args.scenario == "all" else [args.scenario]

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              WSQLite Benchmark Suite v1.0                  ║
╠══════════════════════════════════════════════════════════════╣
║  Libraries:   {", ".join(set(b().name for b in benchmarks)):<40} ║
║  Scenarios:   {", ".join(scenarios):<40} ║
║  Iterations:  {args.iterations:<40,} ║
║  Warmup:      {args.warmup:<40,} ║
╚══════════════════════════════════════════════════════════════╝
""")

    results = []

    for scenario in scenarios:
        print(f"\n{'=' * 60}")
        print(f"  SCENARIO: {scenario.upper()}")
        print(f"{'=' * 60}")

        for benchmark_class in benchmarks:
            result = run_scenario(benchmark_class(), scenario, args.iterations, args.warmup)
            if result:
                results.append(result)

    print_comparison(results)

    if args.output:
        if args.output.endswith(".html"):
            generate_html_report(results, args.output)
            print(f"\n📊 HTML report saved to: {args.output}")
        else:
            with open(args.output, "w") as f:
                json.dump([r.to_dict() for r in results], f, indent=2)
            print(f"\n📊 JSON report saved to: {args.output}")

    print("\n✅ Benchmark completed!")


if __name__ == "__main__":
    main()
