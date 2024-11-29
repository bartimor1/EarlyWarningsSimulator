import os
import logging

logger = logging.getLogger(__name__)


class SimTimeFilter(logging.Filter):
    """A custom logging filter to add `env.now` as a log attribute."""
    def __init__(self, env):
        super().__init__()
        self.env = env

    def filter(self, record):
        # Inject the simulated time (`env.now`) into the log record
        record.sim_time = self.env.now
        return True


def logger_config(log_path, seed):
    global logger

    os.makedirs(log_path, exist_ok=True)

    logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler(f'{log_path}/eventLog_{seed}.log')],
                        level=logging.DEBUG, format='%(sim_time)s %(levelname)s  module=%(name)s funcName=%(funcName)s lineno=%(lineno)d %(message)s', force=True)


