from scenarios.base_scenario import BaseScenario
from collectors.bluetooth_controller import BluetoothController

import time
from datetime import datetime

import json
import os
import yaml

class ConnectionLatencyScenario(BaseScenario):

    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.disconnect_start = True
        self.connect_initiated = False
        self.bt_connected = False
        self.audio_started = False

    def save_results(self, run_id, scenario_name, results):
        output_dir = f"logs/processed/{run_id}"
        os.makedirs(output_dir, exist_ok=True)

        path = f"{output_dir}/{scenario_name}.json"
        with open(path, "w") as f:
            json.dump(results, f, indent=2)    

    def run(self):
        self.logger.info("⛓️ Running Test Connection Latency Scenario")

        with open("configs/devices.yaml") as f:
            device_config = yaml.safe_load(f)

        device_key = device_config.get("default_device", "airpods")
        device = device_config["devices"][device_key]
        device_name = device.get("name")
        device_address = device.get("address")

        bt_controller = BluetoothController(device_name=device_name, device_address=device_address) # Adjust as needed
        results = []

        iterations = self.config.get("iterations", 5)

        for i in range(iterations):
            self.logger.info(f"Iteration {i+1} of {iterations}")

            bt_controller.disconnect() # user manually disconnects Airpods
            start_time = time.time()

            bt_controller.connect()

            end_time = time.time()
            latency = end_time - start_time

            self.logger.info(f"Iteration {i+1}: connection latency = {latency:.2f} seconds")

            results.append({
                "iteration": i + 1,
                "latency_seconds": latency,
                "timestamp": start_time
            })

        self.results = results

        run_id = f"{self.config['run']['name']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.save_results(run_id, "connection_latency", results)