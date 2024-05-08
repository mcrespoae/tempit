import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from statistics import mean, median, stdev
from typing import Any, Callable, Dict, List, Tuple


def timeit(*, run_times: int = 1, concurrency: str = "multithreading", verbose: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def timeit_wrapper(*args: Tuple, **kwargs: Dict) -> Any:
            nonlocal run_times
            if run_times < 1:
                run_times = 1

            if run_times > 1:
                if concurrency.lower() == "multithreading":
                    result, total_times = timeit_with_thread_pool(func, run_times, *args, **kwargs)

                elif concurrency == "multiprocessing":
                    result, total_times = timeit_with_thread_pool(func, run_times, *args, **kwargs)
                    # To do: use multiprocessing
                else:
                    result, total_times = timeit_main_process(func, run_times, *args, **kwargs)

            else:
                result, total_times = timeit_main_process(func, run_times, *args, **kwargs)

            print_timeit_values(run_times, verbose, func, total_times, args, kwargs)

            return result

        return timeit_wrapper

    return decorator


def timeit_main_process(func, run_times, *args, **kwargs):
    total_times: List[float] = []
    for _ in range(run_times):
        start_time: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        end_time: float = time.perf_counter()
        total_times.append(end_time - start_time)
    return result, total_times


def timeit_with_thread_pool(func, run_times, *args, **kwargs):
    total_times = []
    with ThreadPoolExecutor() as executor:
        start_times = list(executor.map(lambda _: time.perf_counter(), range(run_times)))
        for start_time in start_times:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_times.append(end_time - start_time)
    return result, total_times


def print_timeit_values(
    run_times: int, verbose: bool, func: Callable, total_times: List[float], args: Tuple, kwargs: Dict
) -> None:
    if verbose:
        print("*" * 5, f"Timeit data for function {func.__name__}:", "*" * 5)
    if run_times == 1:
        print_single_value(verbose, func, total_times[0], args, kwargs)
    else:
        print_several_values(verbose, func, total_times, args, kwargs)
    if verbose:
        print("*" * 5, "End of timeit data.", "*" * 5)


def print_verbose_common_parts(func: Callable, args: Tuple, kwargs: Dict) -> None:
    print(f"Function name: {func.__name__}")
    print(f"\tFuncion object: {func}")
    print(f"\tArgs: {args[1:]}")
    print(f"\tKwargs: {kwargs}")


def print_single_value(verbose: bool, func: Callable, total_time: float, args: Tuple, kwargs: Dict) -> None:
    if verbose:
        print_verbose_common_parts(func, args, kwargs)
        print(f"\tTime: {format_time(total_time)}.")
    else:
        print(f"Function {func.__name__} took {format_time(total_time)}.")


def print_several_values(verbose: bool, func: Callable, total_times: List[float], args: Tuple, kwargs: Dict) -> None:
    # Get statistics like mean, std, min, max, etc. from the total_times list
    avg_time = mean(total_times)

    if verbose:
        med_time = median(total_times)
        min_time = min(total_times)
        max_time = max(total_times)
        std_dev = stdev(total_times)
        total_time = sum(total_times)
        print_verbose_common_parts(func, args, kwargs)
        print(f"\tRun times: {len(total_times)}")
        print(f"\tMean: {format_time(avg_time)}")
        print(f"\tMedian: {format_time(med_time)}")
        print(f"\tMin: {format_time(min_time)}")
        print(f"\tMax: {format_time(max_time)}")
        print(f"\tStandard deviation: {format_time(std_dev)}")
        print(f"\tTotal time: {format_time(total_time)}")
    else:
        print(f"Function {func.__name__} took and avg of {format_time(avg_time)}.")


def format_time(total_time: float) -> str:
    if total_time < 1:
        return f"{total_time:.8f}s"
    elif total_time < 60:
        return f"{total_time:.2f}s"
    elif total_time < 3600:
        minutes = int(total_time // 60)
        seconds = total_time % 60
        ms = seconds % 1 * 100
        return f"{minutes:02}m:{seconds:02.0f}s.{ms:.0f}ms"
    else:
        hours = int(total_time // 3600)
        total_time %= 3600
        minutes = int(total_time // 60)
        seconds = total_time % 60
        ms = seconds % 1 * 100
        return f"{hours:02}h:{minutes:02}m:{seconds:02.0f}s.{ms:.0f}ms"


if __name__ == "__main__":
    total_time = 0.3465
    print(format_time(total_time))
