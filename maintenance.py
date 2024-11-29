import logging
import cfg
from Logger import SimTimeFilter
from SimUtils import random_std_deviation

logger = logging.getLogger(__name__)


def maintenance_process(env, database) -> None:
    """
    Maintenance process is a parallel process to the call center in which the system performs maintenance operations
    in parallel to taking calls.
    At a specific point in the maintenance, the process requires DB resources for a short duration.
    """

    global logger
    maintenance_id = 1000000000

    logger.addFilter(SimTimeFilter(env))

    while True:
        # Perform maintenance step A
        yield env.timeout(random_std_deviation(cfg.MAINTENANCE_STEP_1_DURATION / cfg.task_over_performance_factor))
        logger.info(f"id={maintenance_id} Maintenance process step 1/3")

        # Perform maintenance on DB
        with database.connections.request() as request:
            yield request
            yield env.timeout(random_std_deviation(cfg.MAINTENANCE_STEP_2_DB_DURATION))
            logger.info(f"id={maintenance_id} Maintenance process step 2/3")

        # Perform maintenance step B
        yield env.timeout(random_std_deviation(cfg.MAINTENANCE_STEP_3_DURATION) / cfg.task_over_performance_factor)
        logger.info(f"id={maintenance_id} Maintenance process step 3/3")

        maintenance_id += 1