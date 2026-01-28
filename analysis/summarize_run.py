from pathlib import Path
from .loaders import load_connection_latency
from .latency_analysis import compute_latency_metrics

def summarize(run_dir: Path):
    latency_records = load_connection_latency(run_dir)
    latency_metrics = compute_latency_metrics(latency_records)

    summary = {
        "connection_latency": latency_metrics,
    }

    return summary