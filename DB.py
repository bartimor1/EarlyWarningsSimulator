import simpy
import logging
import random
import cfg
from Logger import SimTimeFilter
from SimUtils import random_std_deviation

logger = logging.getLogger(__name__)
class DataBase:
    def __init__(self, env):
        self.env = env
        self.connections = simpy.Resource(env, cfg.NUM_OF_DB_CONNECTIONS)

        logger.addFilter(SimTimeFilter(env))

    def indentify_customer(self, customer):
        """
        Search for customer in the database.
        """

        logger.info(f"id={customer} identifying customer")
        yield self.env.timeout(random_std_deviation(cfg.AVG_DB_QUERY_TIME))

        if random.random() > cfg.FAILED_IDENTIFICATION_RATE:
            logger.info(f"id={customer} Customer eligible for service")
            return True
        else:
            logger.info(f"id={customer} Customer is not eligible for service")
            return False

    def register_to_service(self, customer):
        """
        Register a new customer to the service (add customer to DB)
        """
        yield self.env.timeout(random_std_deviation(cfg.AVG_DB_INSERT_TIME))
        logger.info(f"id={customer} Customer registered to service")