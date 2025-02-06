import time
import psutil
import logging
from contextlib import contextmanager


@contextmanager
def profile_time(msg: str):
    # Record the start time (wall time)
    start_time_wall = time.time()

    # Record the start CPU time
    process = psutil.Process()
    start_time_cpu = process.cpu_times().user  # CPU user time

    # Record the start time in total CPU (including system time)
    start_time_cpu_total = process.cpu_times().system  # CPU system time

    # Yield control to the code within the 'with' block
    yield

    # Record the end time (wall time)
    end_time_wall = time.time()

    # Record the end CPU time
    end_time_cpu = process.cpu_times().user  # CPU user time

    # Calculate elapsed times
    elapsed_wall_time = end_time_wall - start_time_wall
    elapsed_cpu_time = end_time_cpu - start_time_cpu

    # Log the function name, CPU time, and wall time
    logging.info(
        f"'{msg}' - Wall time: {elapsed_wall_time:.4f}s, CPU time: {elapsed_cpu_time:.4f}s"
    )
