import random
import simpy
import logging
import cfg
import SimUtils
import inspect
from Logger import SimTimeFilter
from SimUtils import random_std_deviation


logger = logging.getLogger(__name__)
class DigitalCallCenter:
    def __init__(self, env):
        self.env = env
        self.bots = simpy.Resource(env,cfg.NUM_OF_BOTS)
        self.legacy_archives_connections_available = simpy.Resource(env, cfg.NUM_OF_REMOTE_LEGACY_ARCHIVES_CONNECTIONS)
        self.updaters = simpy.Resource(env,cfg.NUM_OF_UPDATERS)
        logger.addFilter(SimTimeFilter(env))

    def is_problem_solved(self, customer):
        result = None
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_CHECK_PROBLEM_SOLVED_TIME))
            if random.random() < cfg.PROBLEM_SOLVED_PROBABILITY:
                logger.info(f"id={customer} Problem solved ending communication with customer")
                result = True
            else:
                result = False
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
        return result


    def initiate_diagnostic(self, customer :int):
        """
        Initiate diagnostic with the customer
        NOTE: this operation can fail and will be retried if needed. Failure is based on
              scenario's "probabiliy of failure for low level operations"
        """
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            rerun_manager = SimUtils.RetryWrapper(cfg.probability_of_low_level_failure)

            while rerun_manager.retry_needed() is True:
                yield self.env.timeout(random_std_deviation(cfg.AVG_DIAGNOSTIC_TIME))
                logger.info(f"id={customer} Initiated diagnostic on customer device")

            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)


    def is_upgrade_needed(self, customer :int) -> bool:
        """
        Checks if customer's system requires an upgrade.
        Note: This operation may be subject to bandwidth degradation
        """
        result = None

        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_CHECK_UPDATE_NEEDED_TIME))

            if random.random() < cfg.REQUIRED_DEVICE_UPDATE:
                logger.info(f"id={customer} Device need software update")
                result = True
            else:
                logger.info(f"id={customer} Device is up to date")
                result = False

            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
        return result

    def is_config_correct(self, customer :int):
        result = None

        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_CHECK_CONFIG_TIME))
            if random.random() < cfg.REQUIRED_DEVICE_RECONFIGURATION:
                logger.info(f"id={customer} Device is not configured correctly")
                result = False
            else:
                logger.info(f"id={customer} Device is configured correctly")
                result = True

            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
        return result

    def reset_cashed_memory(self, customer :int):
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_RESET_CASH_TIME))
            logger.info(f"id={customer} Reset cash memory on customer device")
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)


    def configure_device(self, customer :int):
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_CONF_TIME))
            logger.info(f"id={customer} Apply configuration to customer device")
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)


    def update_software(self, customer :int):
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_UPDATE_TIME))
            logger.info(f"id={customer} Software updated on customer device")
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)


    def reboot_device(self, customer :int):
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_REBOOT_TIME))
            logger.info(f"id={customer} Rebooting customer device")
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)


    def is_hw_issue(self, customer :int, hw_issue=0.1):
        result = None

        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_HW_DIAGNOSTIC_TIME))
            if random.random() < hw_issue:
                logger.info(f"id={customer} Device has HW issue please take it to the lab")
                result = True
            else:
                result = False

            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
            return result


    def query_remote_archives(self, customer:int):
        """
        Query remote archives if the solution is found there
        """
        with self.legacy_archives_connections_available.request() as request:
           yield request
           with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
                SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
                yield self.env.timeout(random_std_deviation(cfg.REMOTE_LEGACY_ARCHIVES_RESPONSE_TIME) * cfg.under_performance_factor)
                logger.info(f"id={customer} Remote legacy archives queried.")
                SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)


    def support(self, customer: int):
        """
        Support customer process flow
        """

        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)

            # we use max to avoid negative values or zeros
            # --------
            is_config_correct = yield self.env.process(self.is_config_correct(customer))
            if not is_config_correct:

                config_flow = [self.reset_cashed_memory, self.is_problem_solved, self.configure_device]
                if 1 in cfg.enable_path_changes:
                    # Change order of the three functions resulting from A->B->C to C->A->B
                    config_flow = [self.configure_device, self.reset_cashed_memory, self.is_problem_solved]

                for func in config_flow:
                    res = yield self.env.process(func(customer))
                    if func == self.is_problem_solved and res==True:
                        SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
                        return

            # Run flow changes A->B->C to A->D->B->C (introduce a new task)
            if (2 in cfg.enable_path_changes) and (random.random() <= cfg.NEEDS_REBOOT_PROBABILITY):
                    yield self.env.process(self.reboot_device(customer))
                    is_problem_solved = yield self.env.process(self.is_problem_solved(customer))
                    if is_problem_solved:
                        SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
                        return
            # --------
            yield self.env.process(self.initiate_diagnostic(customer))
            is_update_needed = yield self.env.process(self.is_upgrade_needed(customer))
            if is_update_needed:
                yield self.env.process(self.update_software(customer))
                is_problem_solved = yield self.env.process(self.is_problem_solved(customer))
                if is_problem_solved:
                    SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
                    return
            # --------
            is_hw_issue = yield self.env.process(self.is_hw_issue(customer))
            if is_hw_issue:
                SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
                return
            # --------
            yield self.env.process(self.query_remote_archives(customer))
            is_problem_solved = yield self.env.process(self.is_problem_solved(customer))
            if is_problem_solved:
                SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)
                return

            else:
                logger.error(f"id={customer} Could not solve device issue. please visit one of our reception desks")

            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)

    def update_incident(self, customer):
        with SimUtils.ActivityRunTimeLogger(inspect.currentframe().f_code.co_name, self.env):
            SimUtils.queue_tracker.activity_enter(inspect.currentframe().f_code.co_name, self.env.now)
            yield self.env.timeout(random_std_deviation(cfg.AVG_INCIDENT_UPDATE_TIME))
            logger.info(f"id={customer} Connection is cleaned")
            SimUtils.queue_tracker.activity_exit(inspect.currentframe().f_code.co_name, self.env.now)



