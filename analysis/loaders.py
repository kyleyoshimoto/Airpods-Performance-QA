import json
from pathlib import Path

def load_connection_latency(run_dir: Path):
    file_path = run_dir / "connection_latency.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Connection latency file not found: {file_path}")
    
    with open(file_path, "r") as f:
        return json.load(f)