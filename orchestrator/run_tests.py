import yaml
import logging
import os
from datetime import datetime, timezone
import threading

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

    # Add console logging to help identify why scenario logs may not appear
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def main():
    with open("configs/test_config.yaml") as f:
        config = yaml.safe_load(f)

    run_id = f"{config['run']['name']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
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

    # Run the collector in a background thread so that scenario execution can proceed concurrently.
    # This fixes the previous issue where scenario logs did not appear because the collector was blocking.
    collector_thread = threading.Thread(target=collector.start, kwargs={"duration_sec": config["run"]["duration_seconds"]})
    collector_thread.start()

    for scenario_cfg in enabled_scenarios:
        scenario_name = scenario_cfg["name"]

        if scenario_name not in SCENARIO_REGISTRY:
            logger.warning(f"Scenario {scenario_name} not recognized, skipping.")
            continue

        logger.info(f"Executing scenario: {scenario_name}")

        scenario_class = SCENARIO_REGISTRY[scenario_name]
        scenario = scenario_class(config=config, logger=logger)

        logger.info(f"About to call execute() on {scenario_name}")
        scenario.execute()
        logger.info(f"Returned from execute() on {scenario_name}")

        logger.info(f"Completed scenario: {scenario_name}")

    # Wait for the collector thread to finish after all scenarios complete
    collector_thread.join()

    samples = collector.get_samples()
    logger.info(f"Collected {len(samples)} system samples")

    logger.info("Run completed successfully")


if __name__ == "__main__":
    main()