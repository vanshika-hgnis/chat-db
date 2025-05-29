import logging
from datetime import datetime


class IntentLogger:
    def __init__(self, log_file="intent_log.txt"):
        self.log_file = log_file
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def log_prompt(self, prompt):
        """Log the user prompt"""
        self.logger.info(f"User Prompt: {prompt}")

    def log_intent(self, intent):
        """Log the classified intent"""
        self.logger.info(f"Classified Intent: {intent}")
