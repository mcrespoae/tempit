import random
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

sys.path.append("../")
from simple_timeit_decorator import timeit


class TimeItTestClass:

    @timeit
    def timeit_basic_tenth_second(self, a=1, b=2):

        time.sleep(0.01)
        return a + b

    @timeit(run_times=5)
    def timeit_10times_less_than_1s(self):
        time.sleep(random.random())

    @timeit(run_times=5, concurrency_mode="multithreading", verbose=True)
    def timeit_10times_multithreading_verbose(self):
        time.sleep(0.01)

    @timeit(run_times=5, concurrency_mode="none", verbose=True)
    def timeit_10times_lineal_verbose(self):
        time.sleep(0.01)

    @timeit(run_times=5, concurrency_mode="multithreading", verbose=True)
    def timeit_10times_multithreading_crash(self):
        current_thread = threading.current_thread()
        if current_thread.name != "MainThread":
            raise RuntimeError("Crashing intentionally for testing multithreading inside a class")
        time.sleep(0.01)

    def sum(self, a: int = 1, b: int = 2):
        return a + b

    @timeit(run_times=5)
    def complex_method(self, a: int = 1, b: int = 2):
        return self.sum(a, b)

    @timeit(run_times=2)
    @staticmethod
    def static_method(a: int = 1, b: int = 2):
        return a + b

    @timeit(run_times=2, verbose=True)
    @classmethod
    def class_method(cls, a: int = 1, b: int = 2):
        return cls.__name__, a + b

    @timeit(run_times=2, verbose=True)
    @classmethod
    def class_method_no_args(cls):
        return cls.__name__, 1 + 2


@timeit()
def timeit_basic_tenth_second():
    time.sleep(0.01)


@timeit(run_times=5, concurrency_mode="multithreading")
def timeit_10times_less_than_1s():
    time.sleep(random.random())


@timeit(run_times=5, concurrency_mode="multithreading", verbose=True)
def timeit_10times_multithreading_verbose():
    time.sleep(0.01)


@timeit(run_times=5, concurrency_mode="none", verbose=True)
def timeit_10times_lineal_verbose():
    time.sleep(0.01)


@timeit(run_times=5, concurrency_mode="multithreading", verbose=False)
def timeit_10times_multithreading_crash():
    current_thread = threading.current_thread()
    if current_thread.name != "MainThread":
        raise RuntimeError("Crashing intentionally for testing multithreading outside class")
    time.sleep(0.01)


@timeit(run_times=5, concurrency_mode="multithreading", verbose=True)
def args_func(a: int = 1, b: int = 2):
    return a + b


@timeit(run_times=5)
def timeit_other_thread(a: int = 1, b: int = 2):
    return a + b


@timeit(run_times=5)
def timeit_other_process(a: int = 1, b: int = 2):
    return a + b


def main():
    test_class = TimeItTestClass()

    print("Once in class basic 0.1s")
    result = test_class.timeit_basic_tenth_second(2, b=3)
    print(result)

    print("Once non class basic 0.1s")
    timeit_basic_tenth_second()

    print("Concurrency 10 times in class 0.1s")
    test_class.timeit_10times_less_than_1s()

    print("Concurrency 10 times non class 0.1s")
    timeit_10times_less_than_1s()

    print("Concurrency 10 times in class verbose")
    test_class.timeit_10times_multithreading_verbose()

    print("Concurrency 10 times non class verbose")
    timeit_10times_multithreading_verbose()

    print("Non concurrent 10 times in class verbose")
    test_class.timeit_10times_lineal_verbose()

    print("Non concurrency 10 times non class verbose")
    timeit_10times_lineal_verbose()

    current_thread = threading.current_thread()
    print(f"{current_thread.name=}")
    print("Multithreading crash in class")
    test_class.timeit_10times_multithreading_crash()

    print("Multithreading crash non class")
    timeit_10times_multithreading_crash()

    print("Complex method with args")
    result = test_class.complex_method(1, b=2)
    if result != 3:
        raise RuntimeError("Result is not 3")

    print("Args func")
    result = args_func(1, b=2)
    if result != 3:
        raise RuntimeError("Result is not 3")

    print("Static method")
    result = test_class.static_method(1, b=2)
    if result != 3:
        raise RuntimeError("Result is not 3")

    print("Class method")
    cls_name, result = test_class.class_method(1, b=2)
    if result != 3 or cls_name != "TimeItTestClass":
        raise RuntimeError(f"Result is not 3 {result=} or class name is not TimeItTestClass {cls_name=}")

    print("Class method no args")
    cls_name, result = test_class.class_method_no_args()
    if result != 3 or cls_name != "TimeItTestClass":
        raise RuntimeError(f"Result is not 3 {result=} or class name is not TimeItTestClass {cls_name=}")

    # Create a thread pool executor with one worker thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        print("Other thread")
        # Submit the function to the executor
        future = executor.submit(timeit_other_thread, 1, b=2)
        # Retrieve the return value
        result = future.result()
        if result != 3:
            raise RuntimeError(f"Result is not 3 {result=}.")

    with ProcessPoolExecutor(max_workers=1) as executor:
        print("Other process")
        # Submit the function to the executor
        future = executor.submit(timeit_other_process, 1, b=2)
        # Retrieve the return value
        result = future.result()
        if result != 3:
            raise RuntimeError(f"Result is not 3 {result=}.")

    # Create a thread pool executor with one worker thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        print("Other thread class method")
        # Submit the function to the executor
        future = executor.submit(test_class.class_method, 1, b=2)
        # Retrieve the return value
        cls_name, result = future.result()

        if result != 3 or cls_name != "TimeItTestClass":
            raise RuntimeError(f"Result is not 3 {result=} or class name is not TimeItTestClass {cls_name=}")

    with ProcessPoolExecutor(max_workers=1) as executor:
        print("Other process class method")
        # Submit the function to the executor
        future = executor.submit(test_class.class_method, 1, b=2)
        cls_name, result = future.result()

        if result != 3 or cls_name != "TimeItTestClass":
            raise RuntimeError(f"Result is not 3 {result=} or class name is not TimeItTestClass {cls_name=}")

    # Create a thread pool executor with one worker thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        print("Other thread static method")
        # Submit the function to the executor
        future = executor.submit(test_class.static_method, 1, b=2)
        # Retrieve the return value
        result = future.result()

        if result != 3:
            raise RuntimeError(f"Result is not 3 {result=}")

    with ProcessPoolExecutor(max_workers=1) as executor:
        print("Other process static method")
        # Submit the function to the executor
        future = executor.submit(test_class.static_method, 1, b=2)
        result = future.result()

        if result != 3:
            raise RuntimeError(f"Result is not 3 {result=}")


if __name__ == "__main__":
    main()
