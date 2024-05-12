import os
import threading
import time
import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import current_process

from tempit.core import tempit
from tempit.utils import format_time

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


class TempitTestClass:
    @tempit()
    def tempit_basic(self):
        time.sleep(0.01)

    @tempit
    def tempit_basic_no_parenthesis(self):
        time.sleep(0.01)

    @tempit(run_times=5)
    def test_tempit_with_concurrency(self):
        time.sleep(0.01)

    @tempit(run_times=5, concurrent_execution=False, verbose=False)
    def test_tempit_no_concurrency(self):
        time.sleep(0.01)

    @tempit(run_times=5, concurrent_execution=True, verbose=True)
    def test_tempit_concurrency_verbose(self):
        time.sleep(0.01)

    @tempit(run_times=10, concurrent_execution=True, verbose=True)
    def test_tempit_thread_crash(self, a: int = 1, b: int = 2, thread_name: str = "ThreadPoolExecutor-"):
        current_thread_name = threading.current_thread().name
        if not current_thread_name.startswith(thread_name):
            raise RuntimeError("Crashing intentionally for testing other process inside a class")
        return a + b

    def sum(self, a: int = 1, b: int = 2):
        return a + b

    @tempit(run_times=10)
    def test_tempit_args(self, a: int = 1, b: int = 2):
        return self.sum(a, b)

    @tempit(run_times=2)
    @staticmethod
    def static_method(a: int = 1, b: int = 2):
        return a + b

    @tempit(run_times=2, verbose=True)
    @classmethod
    def class_method(cls, a: int = 1, b: int = 2):
        return cls.__name__, a + b


class TestTempitDecoratorClass(unittest.TestCase):
    def setUp(self):
        self.test_class = TempitTestClass()

    def test_tempit_basic(self):

        start_time = time.perf_counter()
        self.test_class.tempit_basic()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.01)

    def test_tempit_basic_no_parenthesis(self):

        start_time = time.perf_counter()
        self.test_class.tempit_basic_no_parenthesis()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.01)

    def test_tempit_with_concurrency(self):

        start_time = time.perf_counter()
        self.test_class.test_tempit_with_concurrency()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.1)

    def test_tempit_no_concurrency(self):
        start_time = time.perf_counter()
        self.test_class.test_tempit_no_concurrency()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.05, delta=0.1)

    def test_tempit_concurrency_verbose(self):
        # Just check it doesn't crash
        start_time = time.perf_counter()
        self.test_class.test_tempit_concurrency_verbose()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.1)

    def test_tempit_other_thread_crash(self):
        # Just check if it the parallel execution doesn't work, it should be executed in the main thread
        start_time = time.perf_counter()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.test_tempit_thread_crash, 1, b=2)
            result = future.result()
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.05, delta=0.1)
        self.assertEqual(result, 3)

    def test_tempit_args(self):
        result = self.test_class.test_tempit_args(1, b=2)
        self.assertEqual(result, 3)

    def test_tempit_static_method(self):
        result = self.test_class.static_method(1, b=2)
        self.assertEqual(result, 3)

    def test_tempit_class_method(self):
        class_name, result = self.test_class.class_method(1, b=2)
        self.assertEqual(class_name, "TempitTestClass")
        self.assertEqual(result, 3)

    def test_tempit_run_from_other_thread(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.test_tempit_args, 1, b=2)
            result = future.result()

        self.assertEqual(result, 3)

    def test_tempit_run_from_other_process(self):
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.test_tempit_args, 1, b=2)
            result = future.result()

        self.assertEqual(result, 3)

    def test_tempit_class_method_from_other_thread(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.class_method, 1, b=2)
            class_name, result = future.result()

        self.assertEqual(class_name, "TempitTestClass")
        self.assertEqual(result, 3)

    def test_tempit_class_method_run_from_other_process(self):
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.class_method, 2, b=6)
            class_name, result = future.result()

        self.assertEqual(class_name, "TempitTestClass")
        self.assertEqual(result, 8)

    def test_tempit_static_method_from_other_thread(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.static_method, 4, b=5)
            result = future.result()

        self.assertEqual(result, 9)

    def test_tempit_static_method_run_from_other_process(self):
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.static_method, 1, b=2)
            result = future.result()

        self.assertEqual(result, 3)


class TestTempitDecoratorFunction(unittest.TestCase):

    def test_tempit_basic(self):
        @tempit()
        def my_function():
            time.sleep(0.01)

        start_time = time.perf_counter()
        my_function()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.1)

    def test_tempit_basic_no_parenthesis(self):
        @tempit
        def my_function():
            time.sleep(0.01)

        start_time = time.perf_counter()
        my_function()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.01)

    def test_tempit_with_concurrency(self):
        @tempit(run_times=5, concurrent_execution=True)
        def my_function():
            time.sleep(0.01)

        start_time = time.perf_counter()
        my_function()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.1)  # Check if execution time is close to 0.1 seconds

    def test_tempit_no_concurrency(self):
        @tempit(run_times=5, concurrent_execution=False)
        def my_function():
            time.sleep(0.01)

        start_time = time.perf_counter()
        my_function()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.05, delta=0.1)

    def test_tempit_multithreading_verbose(self):
        # Just check it doesn't crash
        @tempit(run_times=5, concurrent_execution=True, verbose=True)
        def my_function():
            time.sleep(0.01)

        start_time = time.perf_counter()
        my_function()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.01, delta=0.1)

    def test_tempit_multithreading_crash(self):
        # Just check if it the multihreading doesn't work, it should be executed in the main thread
        @tempit(run_times=5, concurrent_execution=True)
        def my_function():
            current_thread_name = threading.current_thread().name
            process_name = current_process().name
            if current_thread_name != "MainThread" or process_name != "MainProcess":
                raise RuntimeError("Crashing intentionally for testing multithreading outside class")
            time.sleep(0.01)

        start_time = time.perf_counter()
        my_function()
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertLess(execution_time, 0.5)

    def test_tempit_args(self):
        @tempit(run_times=2, concurrent_execution=True, verbose=True)
        def my_function(a: int = 1, b: int = 2):
            return a + b

        start_time = time.perf_counter()
        result = my_function(1, b=2)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        self.assertLess(execution_time, 0.05)
        self.assertEqual(result, 3)

    def test_run_from_other_thread(self):
        @tempit(run_times=2, concurrent_execution=True, verbose=True)
        def my_function(a: int = 1, b: int = 2):
            return a + b

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(my_function, 2, b=4)
            result = future.result()

        self.assertEqual(result, 6)

    def test_run_from_other_process(self):
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(my_process_function, 1, b=2)
            result = future.result()

        self.assertEqual(result, 3)

    @unittest.skipUnless(not IN_GITHUB_ACTIONS, "Skip if running in GitHub Actions: too expensive.")
    def test_tempit_long_running_function(self):
        @tempit(run_times=4, concurrent_execution=True)
        def my_concurrent_function(a=2_000_000, n=16):
            for _ in range(a):
                pass  #
            return fib(n=n)

        @tempit(run_times=4, concurrent_execution=False)
        def my_sequential_function(a=2_000_000, n=16):
            for _ in range(a):
                pass  #
            return fib(n=n)

        start_time = time.perf_counter()
        result_concurrent = my_concurrent_function(200_000_000, n=32)
        end_time = time.perf_counter()
        execution_time_concurrent = end_time - start_time

        start_time = time.perf_counter()
        result_sequential = my_sequential_function(200_000_000, n=32)
        end_time = time.perf_counter()
        execution_time_sequential = end_time - start_time

        # self.assertGreaterEqual(execution_time_sequential, lower_bound)
        self.assertLessEqual(
            execution_time_concurrent, (execution_time_sequential / 4) + (execution_time_sequential * 0.1)
        )

        self.assertEqual(result_concurrent, 2178309)
        self.assertEqual(result_sequential, 2178309)


def fib(n):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)


# Added here since calling a function from another process inside a test method doesn't work
@tempit(run_times=2, concurrent_execution=True, verbose=True)
def my_process_function(a: int = 1, b: int = 2):
    return a + b


class TestFormatTime(unittest.TestCase):
    def test_format_time_microseconds(self):
        self.assertEqual(format_time(0.0005), "500.0000µs")

    def test_format_time_milliseconds(self):
        self.assertEqual(format_time(0.08256741), "82.5674ms")

    def test_format_time_deconds1(self):
        self.assertEqual(format_time(0.25), "0.250s")

    def test_format_time_seconds2(self):
        self.assertEqual(format_time(3.14159), "3.14s")

    def test_format_time_minutes(self):
        self.assertEqual(format_time(65.4321), "01m:05s.432ms")

    def test_format_time_hours(self):
        self.assertEqual(format_time(3665.4321), "01h:01m:05s.432ms")

    def test_format_time_days(self):
        self.assertEqual(format_time(86465.4321), "1d:00h:01m:05s.432ms")


if __name__ == "__main__":
    unittest.main()
