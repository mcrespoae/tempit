import random
import sys
import threading
import time

sys.path.append("../")
from simple_timeit_decorator import timeit


class TimeItTestClass:
    @timeit()
    def timeit_basic_tenth_second(self):
        time.sleep(0.1)

    @timeit(run_times=10)
    def timeit_10times_less_than_1s(self):
        time.sleep(random.random())

    @timeit(run_times=10, concurrency_mode="multithreading", verbose=True)
    def timeit_10times_multithreading_verbose(self):
        time.sleep(0.1)

    @timeit(run_times=10, concurrency_mode="none", verbose=True)
    def timeit_10times_lineal_verbose(self):
        time.sleep(0.1)

    @timeit(run_times=10, concurrency_mode="multithreading", verbose=True)
    def timeit_10times_multithreading_crash(self):
        current_thread = threading.current_thread()
        if current_thread.name != "MainThread":
            raise RuntimeError("Crashing intentionally for testing multithreading inside a class")
        time.sleep(0.1)

    def sum(self, a: int = 1, b: int = 2):
        return a + b

    @timeit(run_times=10)
    def complex_method(self, a: int = 1, b: int = 2):
        return self.sum(a, b)

    @timeit()
    @staticmethod
    def static_method():
        return 1 + 2


@timeit()
def timeit_basic_tenth_second():
    time.sleep(0.1)


@timeit(run_times=10, concurrency_mode="multithreading")
def timeit_10times_less_than_1s():
    time.sleep(random.random())


@timeit(run_times=10, concurrency_mode="multithreading", verbose=True)
def timeit_10times_multithreading_verbose():
    time.sleep(0.1)


@timeit(run_times=10, concurrency_mode="none", verbose=True)
def timeit_10times_lineal_verbose():
    time.sleep(0.1)


@timeit(run_times=10, concurrency_mode="multithreading", verbose=False)
def timeit_10times_multithreading_crash():
    current_thread = threading.current_thread()
    if current_thread.name != "MainThread":
        raise RuntimeError("Crashing intentionally for testing multithreading outside class")
    time.sleep(0.1)


def main():
    test_class = TimeItTestClass()
    print("Once in class basic 0.1s")
    test_class.timeit_basic_tenth_second()

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
    result = test_class.complex_method(1, 2)
    if result != 3:
        raise RuntimeError("Result is not 3")
    else:
        print("Result is 3")

    print("Static method")
    result = test_class.static_method()
    if result != 3:
        raise RuntimeError("Result is not 3")
    else:
        print("Result is 3")


if __name__ == "__main__":
    main()
