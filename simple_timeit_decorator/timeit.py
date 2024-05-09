import time
from functools import wraps
from queue import Queue
from statistics import mean, median, stdev
from typing import Any, Callable, Dict, List, Tuple

CONCURRENCY_MODES_AVAILABLE = ["multithreading", "none"]


def timeit(*, run_times: int = 1, concurrency_mode: str = "multithreading", verbose: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def timeit_wrapper(*args: Tuple, **kwargs: Dict) -> Any:

            nonlocal run_times
            nonlocal concurrency_mode

            if run_times < 1:
                run_times = 1
            if concurrency_mode.lower() not in CONCURRENCY_MODES_AVAILABLE:
                concurrency_mode = "multithreading"
            start_time = time.perf_counter()
            if run_times > 1 and concurrency_mode != "none":
                try:
                    result, total_times = timeit_with_concurrency(func, run_times, *args, **kwargs)
                except RuntimeError:
                    # If concurrency mode fails, run the function normally in the main process
                    result, total_times = timeit_main_process(func, run_times, *args, **kwargs)
            else:
                result, total_times = timeit_main_process(func, run_times, *args, **kwargs)
            end_time = time.perf_counter()
            real_time = end_time - start_time
            print_timeit_values(run_times, verbose, func, total_times, real_time, args, kwargs)

            return result

        return timeit_wrapper

    return decorator


def timeit_main_process(func, run_times, *args, **kwargs):
    total_times: List[float] = []
    for _ in range(run_times):
        start_time: float = time.perf_counter()
        try:
            result: Any = func(*args, **kwargs)
        except Exception as e:
            print(e)
        end_time: float = time.perf_counter()
        total_times.append(end_time - start_time)
    return result, total_times


def timeit_with_threads(func, args, kwargs, is_instance_method, exception_queue, run_times):
    from concurrent.futures import ThreadPoolExecutor
    from os import cpu_count

    workers = max(2, cpu_count() - 2) if cpu_count() is not None else 2  # type: ignore

    def run_func(func, args, kwargs, is_instance_method, exception_queue):
        start_time = time.perf_counter()
        try:
            if is_instance_method:
                result = func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
        except Exception as e:
            print(e)
            exception_queue.put(e)
            result = None
        finally:
            end_time = time.perf_counter()
            return result, end_time - start_time

    total_times = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_tasks = [
            executor.submit(run_func, func, args, kwargs, is_instance_method, exception_queue) for _ in range(run_times)
        ]

    for future in future_tasks:
        result, total_time = future.result()
        total_times.append(total_time)

    return result, total_times


def timeit_with_concurrency(
    func,
    run_times,
    *args,
    **kwargs,
):

    is_instance_method = hasattr(args[0], func.__name__) if args else False
    exception_queue = Queue()  # Queue for passing exceptions to the main thread

    result, total_times = timeit_with_threads(func, args, kwargs, is_instance_method, exception_queue, run_times)

    # If an exception was raised in one of the threads, execute the func in the main thread
    if not exception_queue.empty():
        raise RuntimeError(
            "An exception was raised in one of the concurrent jobs. Trying to execute in the main process non-concurrently."
        )
    # Return the first result and the list of total times
    return result if result else None, total_times


def print_timeit_values(
    run_times: int, verbose: bool, func: Callable, total_times: List[float], real_time: float, args: Tuple, kwargs: Dict
) -> None:
    if verbose:
        print("*" * 5, f"Timeit data for function {func.__name__}:", "*" * 5)
    if run_times == 1:
        print_single_value(verbose, func, total_times[0], args, kwargs)
    else:
        print_several_values(verbose, func, total_times, real_time, args, kwargs)
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


def print_several_values(
    verbose: bool, func: Callable, total_times: List[float], real_time: float, args: Tuple, kwargs: Dict
) -> None:
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
        print(f"\tSum time: {format_time(total_time)}")
        print(f"\tReal time: {format_time(real_time)}")
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
