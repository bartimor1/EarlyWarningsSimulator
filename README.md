# EarlyWarningsSimulator
Response time simulator for the evaluation of EarlyWarningInCI thesis(https://github.com/bartimor1/EarlyWarningsInCI.git).
The simulator uses SimPy , a process-based, discrete-event simulation framework, to develop a software application that simulates a call center operated by autonomous bots. Incoming customer calls are processed through a sequence of tasks aimed at repairing the customer’s device. At the end of each task, the system evaluates whether the device has been successfully repaired. 
Each task is associated with a probability of success; if successful, the call is completed. Otherwise, the process continues with the next task. The completion of each task, whether successful or unsuccessful, is an event recorded in the event log. 
Task’s latency follows a normal distribution centered around a predefined constant that is specific to each task type, introducing variability into the model. Shared resources such as bots, database connections and a remote archive are included in the simulation. Tasks that require these resources must wait until they are available before they can proceed, e.g., a customer waiting for an available bot before proceeding with the call. To enable reproducibility, we use seeds to initialize the random generator. 
The simulated application consists of five different modules, referred as resources, and comprises a total of 25 activities distributed across these modules.

## Prerequisite:
Ensure the following Python modules are installed before running the simulation:

* simpy
* numpy
* inspect

## Configuration:
All response times for operations, resource counts, and simulation parameters are defined in the `cfg.py` file. Modify this file to adjust the simulation settings as needed.

## Define new simulation:
The simulator supports five configurable states:
* probability_of_high_level_failure - Implements resilience patterns by simulating failures and repetitions of multiple operations.
* probability_of_low_level_failure - Implements resilience patterns by simulating failures and repetitions of a single atomic operation.
* under_performance_factor - Simulates operational slowdowns, causing decreased performance.
* task_over_performance_factor - Simulates an increase in operational performance.
* enable_path_changes -  Modifies the sequence of operations: (0: Disabled, 1: Reorders operations, 2: Introduces a new operation in the sequence).

Create a new JSON configuration file and place it in the `tc_configurations` directory. Each JSON file should include a base scenario along with at least one additional scenario for comparison. The structure should follow this format:  

```json
{
  "sim_scenarios": [
    {
      "name": "baseline_scenario",
      "Description": "TC 1 - Normal scenario, baseline for all performance degradations.",
      "random_seed": 10,
      "high_level_op_failure_probability": 0.1,
      "low_level_op_failure_probability": 0.2,
      "under_performance_factor": 1,
      "enable_path_changes": 0,
      "task_over_performance_factor": 1
    },
    {
      "name": "over_performance_and_add_api_call_and_change_api_order",
      "Description": "TC 2 - Mixed scenario, overperformance, add API call, and change API call order.",
      "random_seed": 10,
      "enable_path_changes": [1, 2],
      "task_over_performance_factor": 7,
      "high_level_op_failure_probability": 0.1,
      "low_level_op_failure_probability": 0.2
    }
  ]
}
```

To execute the simulation, run the `main.py` file. The simulation logs will be generated and stored in the `Test Cases` folder.
