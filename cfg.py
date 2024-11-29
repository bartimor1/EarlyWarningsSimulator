import json

### Scenario specific parameters ###
probability_of_high_level_failure = 0
probability_of_low_level_failure = 0
under_performance_factor = 1
enable_path_changes = 0                 # 0: Disabled, 1: A->B->C will be A->C->B, 2: A->B->C will be A->D->B->C
task_over_performance_factor = 1

#### Call Center parameters ####
NUM_OF_BOTS = 100
NUM_OF_REMOTE_LEGACY_ARCHIVES_CONNECTIONS = int(NUM_OF_BOTS / 20)
NUM_OF_UPDATERS = 30
# AVG_SUPPORT_TIME = 2
AVG_INCIDENT_UPDATE_TIME = 1
AVG_DIAGNOSTIC_TIME = 15
AVG_HW_DIAGNOSTIC_TIME = 13
AVG_CHECK_PROBLEM_SOLVED_TIME = 6
AVG_CHECK_UPDATE_NEEDED_TIME = 25
AVG_CHECK_CONFIG_TIME = 16
AVG_UPDATE_TIME = 60
AVG_CONF_TIME = 30
AVG_RESET_CASH_TIME = 5
AVG_REBOOT_TIME = 40
NEEDS_REBOOT_PROBABILITY = 0.5
REQUIRED_DEVICE_RECONFIGURATION = 0.1
REQUIRED_DEVICE_UPDATE = 0.5
REMOTE_LEGACY_ARCHIVES_RESPONSE_TIME = 30

PROBLEM_SOLVED_PROBABILITY = 0.5

#### DB & Shared resources parameters ####
NUM_OF_DB_CONNECTIONS = 60
AVG_DB_QUERY_TIME = 5
AVG_DB_INSERT_TIME = 1
FAILED_IDENTIFICATION_RATE = 0.2


#### Maintenance parallel process parameters ####
MAINTENANCE_STEP_1_DURATION = 10
MAINTENANCE_STEP_2_DB_DURATION = 10
MAINTENANCE_STEP_3_DURATION = 10


#### Customer parameters ####
REGISTER_NEW_CUSTOMER = 30
REGISTRATION_FAILURE_RATE = 0.3

#### Simulation parameters ####
SIM_TIME = 3600
NUM_OF_CUSTOMERS = 1000
CUSTOMER_INTERVAL = 5
SEED = None


def load_scenarios_from_file(configuration_file:str, verbose:bool = True):
    """
    Load scenario list and configurations from JSON
    """

    try:
        with open(configuration_file) as fj:
            scenarios = json.load(fj)["sim_scenarios"]
    except Exception as e:
        print(f"Failed to load scenarios JSON ({e})")
        exit(-1)

    if verbose:
        for scenario in scenarios:
            print(f"{scenario['name']}: {scenario['Description']}")

    return scenarios


