def compute_reliability(results):
    total = len(results)
    failures = sum(1 for r in results if r.get("timeout", False))

    return {
        "total_runs": total,
        "failures": failures,
        "failure_rate": round(failures / total, 3) if total else 0.0
    }