import time
from functools import partial, wraps
from queue import Queue
from typing import Any, Callable, Dict, List, Tuple

from .utils import print_timeit_values

CONCURRENCY_MODES_AVAILABLE = ["multithreading", "none"]


def timeit(*args, run_times: int = 1, concurrency_mode: str = "multithreading", verbose: bool = False) -> Callable:
    """
    Decorator function that measures the execution time of a given function. It can be called like @timeit or using arguments @timeit(...)

    Args:
        args: contains the function to be decorated if no arguments are provided when calling the decorator
        run_times (int, optional): The number of times the function should be executed. Defaults to 1.
        concurrency_mode (str, optional): The concurrency mode to use for executing the function.
            Possible values are "multithreading" and "none". Defaults to "multithreading".
        verbose (bool, optional): Whether to print detailed information after execution. Defaults to False.

    Returns:
        Callable: The decorated function if arguments are provided, otherwise a partial function.

    Raises:
        RuntimeError: If the concurrency mode fails, the function is executed in the main process.

    Notes:
        - If `run_times` is less than 1, it will be set to 1.
        - If `concurrency_mode` is not one of the available concurrency modes, it will be set to "multithreading".
        - If the function is a method, the first argument will be removed from `args_to_print`.
        - If the function is a class method, the first argument will be replaced with the class itself.
        - If the function is a static method, the first argument will be removed.

    Example:
        @timeit(run_times=5, concurrency_mode="multithreading", verbose=True)
        def my_function(arg1, arg2):
            # function body

        # The decorated function can be used as usual
        result = my_function(arg1_value, arg2_value)
    """

    def decorator(
        func: Callable, run_times: int = 1, concurrency_mode: str = "multithreading", verbose: bool = False
    ) -> Callable:
        @wraps(func)
        def timeit_wrapper(*args: Tuple, **kwargs: Dict) -> Any:
            validated_concurrency_mode = validate_concurrency_mode(concurrency_mode)
            callable_func, args, args_to_print = extract_callable_and_args_if_method(func, *args)
            result, total_times, real_time = function_execution(
                callable_func,
                run_times,
                validated_concurrency_mode,
                *args,
                **kwargs,
            )

            print_timeit_values(run_times, verbose, callable_func, total_times, real_time, *args_to_print, **kwargs)

            return result

        return timeit_wrapper

    if args:  # If arguments are not provided, return a decorator
        return decorator(*args, run_times=run_times, concurrency_mode=concurrency_mode, verbose=verbose)

    else:  # Otherwise, return a partial function
        return partial(decorator, run_times=run_times, concurrency_mode=concurrency_mode, verbose=verbose)


def validate_concurrency_mode(concurrency_mode: str) -> str:
    """Validate and normalize the concurrency mode."""
    return concurrency_mode.lower() if concurrency_mode.lower() in CONCURRENCY_MODES_AVAILABLE else "multithreading"


def function_execution(
    callable_func: Callable, run_times: int, concurrency_mode: str, *args: Tuple, **kwargs: Dict
) -> Tuple[Any, List[float], float]:
    """Measure the execution time of a function."""
    if run_times < 1:
        run_times = 1
    start_time = time.perf_counter()
    if run_times > 1 and concurrency_mode != "none":
        try:
            result, total_times = timeit_with_concurrency(callable_func, run_times, *args, **kwargs)
        except RuntimeError:
            result, total_times = timeit_main_process(callable_func, run_times, *args, **kwargs)
    else:
        result, total_times = timeit_main_process(callable_func, run_times, *args, **kwargs)
    end_time = time.perf_counter()
    real_time = end_time - start_time

    return result, total_times, real_time


def extract_callable_and_args_if_method(func, *args) -> Tuple[Callable, Tuple, Tuple]:
    """Extract the callable function and arguments."""
    callable_func = func
    args_to_print = args

    is_method = hasattr(args[0], func.__name__) if args else False
    if is_method:
        args_to_print = args[1:]
        if isinstance(func, classmethod):
            args = (args[0].__class__,) + args[1:]  # type: ignore
            callable_func = func.__func__
        elif isinstance(func, staticmethod):
            args = args[1:]

    return callable_func, args, args_to_print


def timeit_main_process(func: Callable, run_times: int, *args: Tuple, **kwargs: Dict) -> Tuple[Any, List[float]]:

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


def timeit_with_concurrency(func: Callable, run_times: int, *args: Tuple, **kwargs: Dict) -> Tuple[Any, List[float]]:
    from concurrent.futures import ThreadPoolExecutor
    from os import cpu_count

    workers: int = max(2, cpu_count() - 1) if cpu_count() is not None else 2  # type: ignore

    def run_func(
        func: Callable,
        exception_queue: Queue,
        *args: Tuple,
        **kwargs: Dict,
    ):
        start_time = time.perf_counter()
        try:
            result: Any = func(*args, **kwargs)
        except Exception as e:
            print(e)
            exception_queue.put(e)
            result = None
        finally:
            end_time = time.perf_counter()
            return result, end_time - start_time

    exception_queue: Queue = Queue()  # Queue for passing exceptions to the main thread
    total_times: List[float] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_tasks = [executor.submit(run_func, func, exception_queue, *args, **kwargs) for _ in range(run_times)]

    for future in future_tasks:
        result, total_time = future.result()
        total_times.append(total_time)
    # If an exception was raised in one of the threads, execute the func in the main thread
    if not exception_queue.empty():
        raise RuntimeError(
            "An exception was raised in one of the concurrent jobs. Trying to execute in the main process non-concurrently."
        )
    return result if result else None, total_times
