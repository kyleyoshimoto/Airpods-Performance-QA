from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


@dataclass(frozen=True)
class LatencyMetrics:
    count: int
    mean_sec: float
    median_sec: float
    p95_sec: float
    min_sec: float
    max_sec: float
    stddev_sec: float


def generate_html_report(
    *,
    run_id: str,
    processed_dir: Path,
    metrics: LatencyMetrics,
    output_dir: Path,
    status: str = "PASS",
) -> Path:
    """Render an HTML report into output_dir/report.html"""
    templates_dir = Path("reports/templates")
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("report_template.html")

    html = template.render(
        run_id=run_id,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        processed_dir=str(processed_dir),
        metrics=metrics,
        status=status,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path