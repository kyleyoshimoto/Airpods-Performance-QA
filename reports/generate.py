from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import matplotlib.pyplot as plt

from reports.report_generator import generate_html_report, LatencyMetrics


def load_connection_latency(processed_dir: Path) -> list[dict]:
    path = processed_dir / "connection_latency.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def compute_latency_metrics(records: list[dict]) -> tuple[LatencyMetrics, list[float]]:
    latencies = [float(r["latency_seconds"]) for r in records]
    latencies_sorted = sorted(latencies)

    # p95 index: nearest-rank style, safe for small N
    if len(latencies_sorted) == 0:
        raise ValueError("No latency records found.")
    p95_idx = max(0, int(round(0.95 * len(latencies_sorted))) - 1)

    metrics = LatencyMetrics(
        count=len(latencies_sorted),
        mean_sec=round(statistics.mean(latencies_sorted), 3),
        median_sec=round(statistics.median(latencies_sorted), 3),
        p95_sec=round(latencies_sorted[p95_idx], 3),
        min_sec=round(min(latencies_sorted), 3),
        max_sec=round(max(latencies_sorted), 3),
        stddev_sec=round(statistics.stdev(latencies_sorted), 3) if len(latencies_sorted) > 1 else 0.0,
    )
    return metrics, latencies


def generate_latency_chart(latencies: list[float], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7.5, 4.5))
    plt.plot(range(1, len(latencies) + 1), latencies, marker="o")
    plt.title("Connection Latency per Iteration")
    plt.xlabel("Iteration")
    plt.ylabel("Latency (seconds)")
    plt.grid(True)
    plt.savefig(out_path)
    plt.close()


def find_latest_run_dir(processed_root: Path) -> Path:
    if not processed_root.exists():
        raise FileNotFoundError(f"Processed logs directory not found: {processed_root}")

    run_dirs = [p for p in processed_root.iterdir() if p.is_dir()]
    if not run_dirs:
        raise FileNotFoundError(f"No run folders found in: {processed_root}")

    # Use folder mtime as "latest" heuristic
    run_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return run_dirs[0]                                                                                                                                                                                                                                                  


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML reports for AirPods Performance QA runs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", help="Run ID folder name under logs/processed/ (e.g., harness_validation_20260128_004135)")
    group.add_argument("--latest", action="store_true", help="Generate report for the most recent run in logs/processed/")

    args = parser.parse_args()

    processed_root = Path("logs/processed")
    processed_dir = Path(processed_root / args.run) if args.run else find_latest_run_dir(processed_root)
    run_id = processed_dir.name

    records = load_connection_latency(processed_dir)
    metrics, latencies = compute_latency_metrics(records)

    # Simple status rule (tune later)
    status = "PASS"
    if metrics.p95_sec > 5.0:
        status = "WARN"
    if metrics.p95_sec > 10.0:
        status = "FAIL"

    report_dir = Path("reports") / run_id
    assets_dir = report_dir / "assets"
    chart_path = assets_dir / "connection_latency.png"
    generate_latency_chart(latencies, chart_path)

    html_path = generate_html_report(
        run_id=run_id,
        processed_dir=processed_dir,
        metrics=metrics,
        output_dir=report_dir,
        status=status,
    )

    print(f"✅ Report generated: {html_path}")


if __name__ == "__main__":
    main()