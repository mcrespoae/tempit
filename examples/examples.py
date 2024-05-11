import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

sys.path.append("../")
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

    @tempit(run_times=5, concurrency_mode="none", verbose=True)
    def tempit_5times_lineal_verbose(self):
        time.sleep(0.01)

    @tempit(run_times=5, verbose=True)
    def tempit_5times_multithreading_crash(self):
        current_thread = threading.current_thread()
        if current_thread.name != "MainThread":
            raise RuntimeError("Crashing intentionally for testing multithreading inside a class")
        time.sleep(0.01)

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


@tempit(run_times=5, concurrency_mode="multithreading", verbose=True)
def tempit_5times_verbose():
    time.sleep(0.01)


@tempit(run_times=5, concurrency_mode="none", verbose=True)
def tempit_5times_lineal_verbose():
    time.sleep(0.01)


@tempit(run_times=5, concurrency_mode="multithreading", verbose=False)
def tempit_5times_multithreading_crash():
    current_thread = threading.current_thread()
    if current_thread.name != "MainThread":
        raise RuntimeError("Crashing intentionally for testing multithreading outside class")
    time.sleep(0.01)


@tempit(run_times=5, concurrency_mode="multithreading", verbose=True)
def args_func(a: int = 1, b: int = 2):
    return a + b


@tempit(run_times=5)
def tempit_other_thread(a: int = 1, b: int = 2):
    return a + b


@tempit(run_times=5)
def tempit_other_process(a: int = 1, b: int = 2):
    return a + b


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
    test_class.tempit_5times_lineal_verbose()
    print("Multithreading crash in class")
    # If crash while running in a separate thread, the execution will be done in the main thread not concurrently
    test_class.tempit_5times_multithreading_crash()
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
        future_class_method = executor.submit(test_class.class_method, 1, b=2)
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
    tempit_5times_lineal_verbose()
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


if __name__ == "__main__":
    main()
