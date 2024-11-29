from datetime import datetime
import random
import os
import copy
from threading import Thread, Lock
import statistics
import cfg
import numpy as np
from math import ceil



def random_std_deviation(rand_center:int ) ->float:
    """
    Returns a random number centered around a requested number
    with normal deviation of 0.1
    """
    return max(1, np.random.normal(rand_center, ceil(rand_center * 0.1)))


class RetryWrapper:
    """
    Contains the retry construct for operations
    """

    def __init__(self, failure_probability):
        """
        Constructor
        """
        self.execution_count = 0
        self.failure_probability = failure_probability
        self.mutex = Lock()


    def retry_needed(self) -> bool:
        """
        Returns True if retry is required, else return False
        Will always return True if this is the first execution of the task.
        """

        with self.mutex:
            self.execution_count += 1
            return (random.random() < self.failure_probability) or (self.execution_count == 1)


    def get_try_count(self) -> int:
        """
        returns the try count
        """
        with self.mutex:
            return self.execution_count



class QueueSizeTracker:
    """
    Tracks queue occupancy at any given time. Produces an histogram.
    """

    def __init__(self):
        """
        Class constructor
        """
        self.mutex = Lock()

        self.queue_changes_log = []
        self.activities_in_queue = {}
        self.activity_queue_history = []

        self.activities_runtime_history = {}        # Contains the list of execution time for each activity
        self._simulation_ended = False

    def simulation_ended(self):
        """
        During simulation cleanup, all suspended processes finalize and exit.
        Therefore unexpected "activity_exit" will be called and should be ignored.
        """
        with self.mutex:
            self._simulation_ended = True

    def _activity_change(self, activity_name:str, activity_time:float, entry_exit:bool, customer_id:int =-1):
        """
        Logs an entry or exit for an activity
        Params:
            entry_exit: True if entry to activity, False if exit from activity
        """
        with self.mutex:

            # Do not updated status if simulation has ended (Do no track activity ends during python cleanups)
            if self._simulation_ended is True:
                return

            if entry_exit:
                ee_str = "entry"
            else:
                ee_str = "exit"

            #Log entry/exit in the log
            self.queue_changes_log.append(f"{activity_time}, {activity_name}, {ee_str}")

            # Handle entry into a queue
            if entry_exit is True:
                if activity_name not in self.activities_in_queue:
                    self.activities_in_queue[activity_name] = 0

                self.activities_in_queue[activity_name] += 1
            # Handle exit from the queue
            else:
                assert(activity_name in self.activities_in_queue)
                self.activities_in_queue[activity_name] -= 1

                assert(self.activities_in_queue[activity_name] >= 0)

            # Store a snapshot of the current status for the histogram
            activity_copy = copy.copy(self.activities_in_queue)
            activity_copy["timestamp"] = round(activity_time, 2)
            self.activity_queue_history.append(activity_copy)

    def activity_enter(self, activity_name:str, activity_time:float, customer_id:int =-1):
        """
        More readable/verifiable way to make sure we enter activity then activity_change()
        """
        self._activity_change(activity_name, activity_time, True, customer_id)

    def activity_exit(self, activity_name:str, activity_time:float, customer_id:int =-1):
        """
        More readable/verifiable way to make sure we exit activity then activity_change()
        """
        self._activity_change(activity_name, activity_time, False, customer_id)

    def log_activity_run_duration(self, activity_name: str, execution_duration: int):
        """
        Logs the run duration of a specific activity
        """
        with self.mutex:
            if self.activities_runtime_history.get(activity_name, None) is None:
                self.activities_runtime_history[activity_name] = []

            self.activities_runtime_history[activity_name].append(execution_duration)


    def save_to_folder(self, path:str, verbose=True):

        with self.mutex:
            # Store queue changes log
            with open(f"{os.path.join(path, 'queue_size_tracking.log')}", 'wt') as f:
                for line in self.queue_changes_log:
                    f.write(f"{line}\n")

            max_per_activity = copy.copy(self.activity_queue_history[len(self.activity_queue_history) - 1])
            max_of_maxes = -1

            # Get the most up-to-date list of all the activities

            # Store histogram
            with open(f"{os.path.join(path, 'queue_size_tracking.csv')}", 'wt') as f:
                keys = list(self.activity_queue_history[len(self.activity_queue_history) - 1].keys())

                # Write column names in CSV
                for key in keys:
                    f.write(f"{key}, ")
                f.write("\n")

                # Write histogram
                for entry in self.activity_queue_history:
                    for key in keys:
                        f.write(f"{entry.get(key, '')}, ")

                        if key != "timestamp":
                            max_per_activity[key] = max(max_per_activity[key], entry.get(key, 0))
                            max_of_maxes = max(max_of_maxes, max_per_activity[key])
                    f.write("\n")

                if verbose:
                    print("queue size statistics:\n")
                    for key in keys:
                        print(f"{key}: MAX={max_per_activity[key]}")
                    print(f"Max of maxes : {max_of_maxes}")

            # Store runtime history
            if verbose:
                print("\n\nActivity runtime duration statistics:")

            with open(f"{os.path.join(path, 'activity_time_log.csv')}", 'wt') as f:
                keys = list(self.activities_runtime_history.keys())

                # Write column names in CSV
                s = f"{'Activity': <22}, {'max': <22}, {'min': <22}, {'average': <22}"
                f.write(f"{s}\n")
                if verbose:
                    print(s)

                for key in keys:
                    l =   self.activities_runtime_history[key]
                    s = f"{key: <22}, {max(l): <22}, {min(l): <22}, {statistics.mean(l): <22}"
                    f.write(f"{s}\n")
                    if verbose:
                        print(s)

                # Store in details
                f.write(f"\n\nExhaustive list of execution time:")
                for key in keys:
                    f.write(f"\n{key}, ")
                    for item in self.activities_runtime_history[key]:
                        f.write(f"{item}, ")

            print(f"Saved statistics to {path}")


queue_tracker = None

class ActivityRunTimeLogger:
    """
    Logs the runtime duration of a specific activity and adds it to the queue tracker
    for logging/recording. Utilizes the "with" python statement.
    """

    def __init__(self, activity_name:str, env):
        self.activity_name = activity_name
        self.env = env

    def __enter__(self):
        global queue_tracker

        assert(queue_tracker is not None)
        self.activity_start_time = self.env.now

    def __exit__(self, *args):
        global queue_tracker
        queue_tracker.log_activity_run_duration(self.activity_name, self.env.now - self.activity_start_time)



