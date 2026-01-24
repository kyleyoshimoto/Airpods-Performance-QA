import yaml
import logging
import os
from datetime import datetime

from collectors.system_collector import SystemCollector

def setup_logger(run_id):
    os.makedirs(f"logs/raw/{run_id}", exist_ok=True)

    logger = logging.getLogger(run_id)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(f"logs/raw/{run_id}/run.log")
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger


def main():
    with open("configs/test_config.yaml") as f:
        config = yaml.safe_load(f)

    run_id = f"{config['run']['name']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    logger = setup_logger(run_id)

    logger.info("Starting AirPods Performance QA run")
    logger.info(f"Run ID: {run_id}")

    collector = SystemCollector(
        interval=config["system"]["sample_interval_sec"]
    )

    logger.info("Collecting system metrics")
    collector.start(duration_sec=config["run"]["duration_seconds"])

    samples = collector.get_samples()
    logger.info(f"Collected {len(samples)} system samples")

    logger.info("Run completed successfully")


if __name__ == "__main__":
    main()