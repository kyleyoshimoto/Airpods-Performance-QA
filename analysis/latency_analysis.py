import statistics
import matplotlib.pyplot as plt

def compute_latency_metrics(records):
    latencies = [r["latency_seconds"] for r in records]

    return {
        "count": len(latencies),
        "mean_sec": round(statistics.mean(latencies), 3),
        "median_sec": round(statistics.median(latencies), 3),
        "p95_sec": round(sorted(latencies)[int(0.95 * len(latencies)) - 1], 3),
        "min_sec": round(min(latencies), 3),
        "max_sec": round(max(latencies), 3),
        "stdev_sec": round(statistics.stdev(latencies), 3) if len(latencies) > 1 else 0.0,
    }

def generate_latency_chart(latencies, output_path):
    plt.figure(figsize=(7.5, 4.5))
    plt.plot(latencies, marker='o', linestyle='-', color='b')
    plt.title('Connection Latency Over Time')
    plt.xlabel('Iteration')
    plt.ylabel('Latency (seconds)')
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()