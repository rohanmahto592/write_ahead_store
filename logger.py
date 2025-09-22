import logging
import os

class Logger:
    def __init__(self, log_file="kv.log"):
        # Create directory if needed
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

        logging.basicConfig(
            filename=log_file,
            filemode="a",
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG
        )
        self.logger = logging.getLogger("AppLogger")

    def log(self, message):
        self.logger.debug(message)   # general log

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)
    def warning(self, message):
        self.logger.warning(message)