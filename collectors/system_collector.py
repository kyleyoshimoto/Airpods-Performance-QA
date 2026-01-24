import psutil
import time

class SystemCollector:
    def __init__(self, interval=1):
        self.interval = interval
        self.running = False
        self.samples = []

    def collect_sample(self):
        return {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent
        }

    def start(self, duration_sec):
        self.running = True
        start_time = time.time()

        while time.time() - start_time < duration_sec:
            self.samples.append(self.collect_sample())
            time.sleep(self.interval)

        self.running = False

    def get_samples(self):
        return self.samples