import random
import logging
import cfg
import SimUtils
import inspect
from Logger import SimTimeFilter
from SimUtils import RetryWrapper
from SimUtils import random_std_deviation

logger = logging.getLogger(__name__)

class Customer:
    def __init__(self, env, id, db):
        self.env = env
        self.id = id
        self.db = db
        logger.addFilter(SimTimeFilter(env))

    def is_registered(self):
        """
        Checks if a customer is already registered in the database.
        """
        res = None

        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            rerun_manager = RetryWrapper(cfg.probability_of_high_level_failure)
            logger.info(f"id={self.id} check if customer registered")

            while rerun_manager.retry_needed() is True:
                with self.db.connections.request() as request:
                    yield request
                    res = yield self.env.process(self.db.indentify_customer(self.id))
                if not res:
                    res = yield self.env.process(self.register_new_customer())

            assert(res is not None)
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
        return res

    def register_new_customer(self):
        """
        Registers a new customer into the database
        """
        result = None

        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            rerun_manager = RetryWrapper(cfg.probability_of_high_level_failure)
            yield self.env.timeout(random_std_deviation(cfg.REGISTER_NEW_CUSTOMER))

            if random.random() > cfg.REGISTRATION_FAILURE_RATE:
                while rerun_manager.retry_needed() is True:
                    with self.db.connections.request() as request:
                        yield request
                        yield self.env.process(self.db.register_to_service(self.id))
                result = True
            else:
                logger.info(f"id={self.id} Failed to register new customer. Terminating connection.")
                result = False

            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
        return result
