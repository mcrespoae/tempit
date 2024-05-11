from statistics import mean, median, stdev
from typing import Callable, Dict, List, Tuple


def print_tempit_values(
    run_times: int,
    verbose: bool,
    func: Callable,
    total_times: List[float],
    real_time: float,
    *args: Tuple,
    **kwargs: Dict,
) -> None:
    """
    Print the tempit values for a given function.
    Args:
        run_times (int): The number of times the function was executed.
        verbose (bool): Whether to print verbose information.
        func (Callable): The function to print the values for.
        total_times (List[float]): The total execution times for each run of the function.
        real_time (float): The real time taken to execute the function.
        *args (Tuple): Additional positional arguments to pass to the function.
        **kwargs (Dict): Additional keyword arguments to pass to the function.
    Returns:
        None
    """
    if verbose:
        print("*" * 5, f"tempit data for function {func.__name__}:", "*" * 5)
    if run_times == 1:
        print_single_value(verbose, func, total_times[0], *args, **kwargs)
    else:
        print_several_values(verbose, func, total_times, real_time, *args, **kwargs)
    if verbose:
        print("*" * 5, "End of tempit data.", "*" * 5)


def print_verbose_common_parts(func: Callable, *args: Tuple, **kwargs: Dict) -> None:
    """
    Print the tempti verbose common parts of a function.
    Args:
        func (Callable): The function to print the common parts for.
        *args (Tuple): Additional positional arguments.
        **kwargs (Dict): Additional keyword arguments.
    Returns:
        None
    """
    print(f"Function name: {func.__name__}")
    print(f"\tFuncion object: {func}")
    print(f"\tArgs: {args}")
    print(f"\tKwargs: {kwargs}")


def print_single_value(verbose: bool, func: Callable, total_time: float, *args: Tuple, **kwargs: Dict) -> None:
    """
    Print a single value based on the given parameters.
    Args:
        verbose (bool): Whether to print verbose information.
        func (Callable): The function to print the value for.
        total_time (float): The total execution time of the function.
        *args (Tuple): Additional positional arguments.
        **kwargs (Dict): Additional keyword arguments.
    Returns:
        None
    """
    if verbose:
        print_verbose_common_parts(func, *args, **kwargs)
        print(f"\tTime: {format_time(total_time)}.")
    else:
        print(f"Function {func.__name__} took {format_time(total_time)}.")


def print_several_values(
    verbose: bool, func: Callable, total_times: List[float], real_time: float, *args: Tuple, **kwargs: Dict
) -> None:
    """
    Print several values based on the given parameters.
    Args:
        verbose (bool): Whether to print verbose information.
        func (Callable): The function to print the values for.
        total_times (List[float]): The total execution times for each run of the function.
        real_time (float): The real time taken to execute the function.
        *args (Tuple): Additional positional arguments.
        **kwargs (Dict): Additional keyword arguments.
    Returns:
        None
    """
    avg_time = mean(total_times)

    if verbose:
        med_time = median(total_times)
        min_time = min(total_times)
        max_time = max(total_times)
        std_dev = stdev(total_times)
        total_time = sum(total_times)
        print_verbose_common_parts(func, *args, **kwargs)
        print(f"\tRun times: {len(total_times)}")
        print(f"\tMean: {format_time(avg_time)}")
        print(f"\tMedian: {format_time(med_time)}")
        print(f"\tMin: {format_time(min_time)}")
        print(f"\tMax: {format_time(max_time)}")
        print(f"\tStandard deviation: {format_time(std_dev)}")
        print(f"\tSum time: {format_time(total_time)}")
        print(f"\tReal time: {format_time(real_time)}")
    else:
        print(f"Function {func.__name__} took and avg of {format_time(avg_time)}.")


def format_time(total_time: float) -> str:
    """
    Formats the given total time into a human-readable string representation.
    Args:
        total_time (float): The total time to be formatted.
    Returns:
        str: The formatted time string.
    """
    if total_time < 0.001:
        microseconds = total_time * 1_000_000
        return f"{microseconds:.4f}µs"
    elif total_time < 0.1:
        return f"{(total_time * 1000):.4f}ms"
    elif total_time < 1:
        return f"{total_time:.3f}s"
    elif total_time < 60:
        return f"{total_time:.2f}s"
    elif total_time < 3600:
        minutes = int(total_time // 60)
        seconds = total_time % 60
        ms = seconds % 1 * 1000
        return f"{minutes:02}m:{seconds:02.0f}s.{ms:.0f}ms"
    if total_time < 86400:
        hours = int(total_time // 3600)
        total_time %= 3600
        minutes = int(total_time // 60)
        seconds = total_time % 60
        ms = seconds % 1 * 1000
        return f"{hours:02}h:{minutes:02}m:{seconds:02.0f}s.{ms:.0f}ms"
    else:
        days = int(total_time // 86400)
        total_time %= 86400
        hours = int(total_time // 3600)
        total_time %= 3600
        minutes = int(total_time // 60)
        seconds = total_time % 60
        ms = seconds % 1 * 1000
        return f"{days}d:{hours:02}h:{minutes:02}m:{seconds:02.0f}s.{ms:.0f}ms"
