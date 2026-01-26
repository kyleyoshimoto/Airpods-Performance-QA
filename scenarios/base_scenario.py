from abc import ABC, abstractmethod
from datetime import datetime

class BaseScenario(ABC):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.start_time = None
        self.end_time = None
        self.results = []

    def setup(self):
        self.logger.info("Setting up scenario")

    @abstractmethod
    def run(self):
        pass

    def teardown(self):
        self.logger.info("Tearing down scenario")

    def execute(self):
        self.start_time = datetime.utcnow()
        self.logger.info(f"Scenario started at {self.start_time}")
        self.setup()
        self.run()
        self.teardown()
        self.end_time = datetime.utcnow()
        self.logger.info(f"Scenario ended at {self.end_time}")