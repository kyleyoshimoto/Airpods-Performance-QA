import yaml
import logging
import os
from datetime import datetime

from collectors.system_collector import SystemCollector

from scenarios.test_connection_latency import ConnectionLatencyScenario

SCENARIO_REGISTRY = {
    "connection_latency": ConnectionLatencyScenario,
}

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

    enabled_scenarios = [
        s for s in config.get("scenarios", []) if s.get("enabled", False)
    ]

    collector = SystemCollector(
        interval=config["system"]["sample_interval_sec"]
    )

    logger.info("Collecting system metrics")

    # TEMP: blocking collection (we'll fix this later)
    collector.start(duration_sec=config["run"]["duration_seconds"])

    for scenario_cfg in enabled_scenarios:
        scenario_name = scenario_cfg["name"]

        if scenario_name not in SCENARIO_REGISTRY:
            logger.warning(f"Scenario {scenario_name} not recognized, skipping.")
            continue

        logger.info(f"Executing scenario: {scenario_name}")

        scenario_class = SCENARIO_REGISTRY[scenario_name]
        scenario = scenario_class(config=config, logger=logger)

        scenario.execute()

        logger.info(f"Completed scenario: {scenario_name}")

    samples = collector.get_samples()
    logger.info(f"Collected {len(samples)} system samples")

    logger.info("Run completed successfully")


if __name__ == "__main__":
    main()