import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import current_process

from tempit import tempit


class TempitTestClass:
    @tempit
    def tempit_basic(self):
        time.sleep(0.01)

    @tempit(run_times=5)
    def tempit_5times(self):
        time.sleep(0.01)

    @tempit(run_times=5, verbose=True)
    def tempit_5times_verbose(self):
        time.sleep(0.01)

    @tempit(run_times=5, concurrent_execution=False, verbose=True)
    def tempit_5times_sequential_verbose(self):
        time.sleep(0.01)

    @tempit(run_times=5, verbose=True)
    def tempit_5times_multithreading_crash(self, a: int = 1, b: int = 2):
        current_thread_name = threading.current_thread().name
        current_process_name = current_process().name
        if current_thread_name != "MainThread" or current_process_name != "MainProcess":
            raise RuntimeError("Crashing intentionally for testing multithreading or multiprocessing inside a class")
        return a + b

    def sum(self, a: int = 1, b: int = 2):
        return a + b

    @tempit(run_times=5)
    def args_method(self, a: int = 1, b: int = 2):
        return self.sum(a, b)

    @tempit(run_times=2)
    @staticmethod
    def static_method(a: int = 1, b: int = 2):
        return a + b

    @tempit(run_times=2, verbose=True)
    @classmethod
    def class_method(cls, a: int = 1, b: int = 2):
        return cls.__name__, a + b


@tempit()
def tempit_basic():
    time.sleep(0.01)


@tempit(run_times=5)
def tempit_5times():
    time.sleep(0.01)


@tempit(run_times=5, concurrent_execution=True, verbose=True)
def tempit_5times_verbose():
    time.sleep(0.01)


@tempit(run_times=5, concurrent_execution=False, verbose=True)
def tempit_5times_sequential_verbose():
    time.sleep(0.01)


@tempit(run_times=5, concurrent_execution=True, verbose=False)
def tempit_5times_multithreading_crash():
    current_thread_name = threading.current_thread().name
    current_process_name = current_process().name
    if current_thread_name != "MainThread" or current_process_name != "MainProcess":
        raise RuntimeError("Crashing intentionally for testing multithreading outside class")
    time.sleep(0.01)


@tempit(run_times=5, concurrent_execution=True, verbose=True)
def args_func(a: int = 1, b: int = 2):
    return a + b


@tempit(run_times=5)
def tempit_other_thread(a: int = 1, b: int = 2):
    return a + b


@tempit(run_times=5)
def tempit_other_process(a: int = 1, b: int = 2):
    return a + b


@tempit(run_times=4, concurrent_execution=True, verbose=True)
def call_long_process_concurrent(n):
    for _ in range(2_000_000):
        pass  #
    return fib(n)


@tempit(run_times=4, concurrent_execution=False, verbose=True)
def call_long_process_sequential(n):
    for _ in range(2_000_000):
        pass  #
    return fib(n)


def fib(n):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)


@tempit(run_times=3, concurrent_execution=True, verbose=False, check_for_recursion=True)
def recursive_func(n):
    if n < 2:
        return n
    return recursive_func(n - 2) + recursive_func(n - 1)


@tempit
def non_recursive_func(n):
    return n


@tempit
def main():

    test_class = TempitTestClass()

    print("---CLASS EXAMPLES---")

    print("Once in class basic")
    test_class.tempit_basic()
    print("Concurrency 5 times in class")
    test_class.tempit_5times()
    print("Concurrency 5 times in class verbose")
    test_class.tempit_5times_verbose()
    print("Non concurrent 5 times in class verbose")
    test_class.tempit_5times_sequential_verbose()

    print("Multithreading crash in class")
    # If crash while running in a separate thread or process, the execution will be done in the main thread not concurrently
    _ = test_class.tempit_5times_multithreading_crash(1, b=2)

    print("Method with args")
    _ = test_class.args_method(1, b=2)
    print("Static method")
    _ = test_class.static_method(1, b=2)
    print("Class method")
    _, _ = test_class.class_method(1, b=2)

    # Test with calling the function from another thread and process
    with ThreadPoolExecutor(max_workers=1) as executor:
        print("Other thread methods")
        future_basic_method = executor.submit(test_class.tempit_basic)
        future_basic_method.result()
        future_class_method = executor.submit(test_class.class_method, 1, b=2)
        _, _ = future_class_method.result()
        future_static_method = executor.submit(test_class.static_method, 1, b=2)
        _ = future_static_method.result()

    with ProcessPoolExecutor(max_workers=1) as executor:
        print("Other process methods")
        future_basic_method = executor.submit(test_class.tempit_basic)
        future_basic_method.result()
        _, _ = future_class_method.result()
        future_static_method = executor.submit(test_class.static_method, 1, b=2)
        _ = future_static_method.result()

    print("---END CLASS EXAMPLES---")

    print("---FUNCTION EXAMPLES---")
    print("Once basic")
    tempit_basic()
    print("Concurrency 5 times")
    tempit_5times()
    print("Concurrency 5 times verbose")
    tempit_5times_verbose()
    print("Non concurrent 5 times verbose")
    tempit_5times_sequential_verbose()
    print("Multithreading crash non class")
    # If crash while running in a separate thread, the execution will be done in the main thread not concurrently
    tempit_5times_multithreading_crash()
    print("Args func")
    _ = args_func(1, b=2)

    # Test with calling the function from another thread and process
    with ThreadPoolExecutor(max_workers=1) as executor:
        print("Other thread methods")
        future_basic_func = executor.submit(tempit_basic)
        future_basic_func.result()
        future_args_func = executor.submit(args_func, 1, b=2)
        _ = future_args_func.result()

    with ProcessPoolExecutor(max_workers=1) as executor:
        print("Other process methods")
        future_basic_func = executor.submit(tempit_basic)
        future_basic_func.result()
        future_args_func = executor.submit(args_func, 1, b=2)
        _ = future_args_func.result()

    print("---END FUNCTION EXAMPLES---")
    print("---OTHER EXAMPLES---")
    _ = call_long_process_concurrent(16)
    _ = call_long_process_sequential(16)
    _ = recursive_func(10)
    print("---END OTHER EXAMPLES---")


if __name__ == "__main__":
    main()
