import os
import random
from datetime import datetime
import numpy as np
import simpy
import logging
import cfg
from CallCenter import DigitalCallCenter
from DB import DataBase
from Customer import Customer
import Logger
import SimUtils
import maintenance

logger = logging.getLogger(__name__)
customer_handled = 0


def support_flow(env, customer_id, call_center, database):
    global customer_handled
    customer = Customer(env, customer_id, database)

    registered = yield  env.process(customer.is_registered())
    if not registered:
        return

    logger.info(f"id={customer_id} enters waiting queue")
    #makes sure that the there is a bot available
    with call_center.bots.request() as request:
        yield request
        logger.info(f"id={customer_id} enters call")
        yield env.process(call_center.support(customer_id))
        # call_center.support(customer_id)
        logger.info(f"id={customer_id} left call")
        customer_handled += 1
    with call_center.updaters.request() as request:
        yield request
        yield env.process(call_center.update_incident(customer_id))


def setup(env, database, num_of_customers, customer_interval):
    call_center = DigitalCallCenter(env)
    i = 0

    while True:
        yield env.timeout(random.randint(customer_interval-1, customer_interval+1))
        i += 1
        env.process(support_flow(env, i, call_center, database))

        if num_of_customers and num_of_customers <= i:
            break


if __name__ == '__main__':
    """
    Entry point to the application.
    """
    global queue_tracker
    configurations_dir = "tc_configurations"

    tc_groups = [group for group in os.listdir(configurations_dir) if group.endswith(".json")]
    start_time = f'{datetime.now():%Y-%m-%d %H:%M:%S%z}'.replace(":", "-").replace(" ", "_")

    # Run on all scenario configurations
    test_case_index = 1
    for tc_group in tc_groups:
        _scenarios = cfg.load_scenarios_from_file(os.path.join(configurations_dir, tc_group))

        # Loop through all scenarios, run each individually
        for idx, _scenario in enumerate(_scenarios):
            SimUtils.queue_tracker = SimUtils.QueueSizeTracker()
            if idx == 0:
                case_index = 1
            else:
                test_case_index += 1
                case_index = test_case_index
            test_case_name = _scenario['name']
            test_case_desc = _scenario['Description']
            _seed = _scenario["random_seed"]
            cfg.probability_of_high_level_failure = _scenario.get("high_level_op_failure_probability", 0)
            cfg.probability_of_low_level_failure = _scenario.get("low_level_op_failure_probability", 0)
            cfg.under_performance_factor = _scenario.get("under_performance_factor", 1)
            cfg.enable_path_changes = _scenario.get("enable_path_changes", 0)
            if isinstance(cfg.enable_path_changes, int):
                cfg.enable_path_changes = [cfg.enable_path_changes]
            cfg.path_changes_factor = _scenario.get("delay_change_path_factor", 1)
            cfg.task_over_performance_factor = _scenario.get("task_over_performance_factor", 1)

            _log_path = f"../Test Cases/{start_time}/{tc_group.replace(".json", "")}/TC{case_index}_{test_case_name}"

            print(f"{tc_group}: \"{test_case_name}\",  \"{test_case_desc}\"")
            print(f"Random Seed: {_seed}")

            random.seed(_seed)
            np.random.seed(_seed)
            _env = simpy.Environment()
            Logger.logger_config(_log_path, _seed)
            logger.addFilter(Logger.SimTimeFilter(_env))

            database = DataBase(_env)


            _env.process(setup(_env, database, cfg.NUM_OF_CUSTOMERS, cfg.CUSTOMER_INTERVAL))
            _env.process(maintenance.maintenance_process(_env, database))

            _env.run(until=cfg.SIM_TIME)

            SimUtils.queue_tracker.save_to_folder(_log_path)
            SimUtils.queue_tracker.simulation_ended()

    print("*** Simulation ended ***")
    pass