import contextlib
import io
import os
import re
import threading
import time
import unittest
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import current_process
from os import cpu_count
from unittest.mock import patch

from tempit.core import TempitConfig, run_func_concurrency, run_func_sequential, tempit

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def setUpModule():
    # test_tempit_deactivated sets TempitConfig.ACTIVE = False at import time;
    # make sure this module always runs with the decorator active.
    TempitConfig.ACTIVE = True


@tempit(run_times=5, concurrent_execution=True, verbose=False)
def _warmup_concurrency_pool():
    pass


def warm_concurrency_pool() -> None:
    # Warm the joblib/loky process pool once so concurrency tests do not pay the
    # worker-spawn cost (and timing-sensitive paths stay stable) during a run.
    if max(1, (cpu_count() or 1) - 1) >= 2:
        _warmup_concurrency_pool()


@contextlib.contextmanager
def capture_stdout():
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        yield buffer


class TempitTestClass:
    @tempit()
    def tempit_basic(self):
        time.sleep(0.01)

    @tempit
    def tempit_basic_no_parenthesis(self, a: int, b: int = 2):
        return a + b

    @tempit(run_times=2, concurrent_execution=True)
    def test_tempit_with_concurrency(self):
        time.sleep(0.01)

    @tempit(run_times=2, concurrent_execution=False, verbose=False)
    def test_tempit_no_concurrency(self):
        time.sleep(0.01)

    @tempit(run_times=2, concurrent_execution=True, verbose=True)
    def test_tempit_concurrency_verbose(self):
        time.sleep(0.01)

    @tempit(run_times=2, concurrent_execution=True, verbose=True)
    def test_tempit_thread_crash(self, a: int = 1, b: int = 2, thread_name: str = "ThreadPoolExecutor-"):
        current_thread_name = threading.current_thread().name
        if not current_thread_name.startswith(thread_name):
            raise RuntimeError("Crashing intentionally for testing other process inside a class")
        return a + b

    def sum(self, a: int = 1, b: int = 2):
        return a + b

    @tempit(run_times=2)
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
    @classmethod
    def setUpClass(cls):
        # Warm up the joblib/loky process pool once, so the first concurrency
        # test does not pay the worker-spawn cost during the run.
        warm_concurrency_pool()

    def setUp(self):
        self.test_class = TempitTestClass()

    def test_tempit_basic(self):
        with capture_stdout() as captured:
            self.test_class.tempit_basic()
        self.assertRegex(captured.getvalue(), r"Function tempit_basic took ")

    def test_tempit_basic_no_parenthesis(self):
        with capture_stdout() as captured:
            result = self.test_class.tempit_basic_no_parenthesis(1, b=2)
        self.assertEqual(result, 3)
        self.assertRegex(captured.getvalue(), r"Function tempit_basic_no_parenthesis took ")

    def test_tempit_with_concurrency(self):
        with patch("tempit.core.run_func_concurrency", wraps=run_func_concurrency) as mocked:
            self.test_class.test_tempit_with_concurrency()
        mocked.assert_called_once()

    def test_tempit_no_concurrency(self):
        with patch("tempit.core.run_func_sequential", wraps=run_func_sequential) as mocked:
            self.test_class.test_tempit_no_concurrency()
        mocked.assert_called_once()

    def test_tempit_concurrency_verbose(self):
        # Just check it doesn't crash and takes the concurrent path
        with patch("tempit.core.run_func_concurrency", wraps=run_func_concurrency) as mocked:
            self.test_class.test_tempit_concurrency_verbose()
        mocked.assert_called_once()

    def test_tempit_other_thread_crash(self):
        # Just check if it the parallel execution doesn't work, it should be executed in the main thread
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.test_tempit_thread_crash, 1, b=2)
            result = future.result()
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

        with capture_stdout() as captured:
            my_function()
        self.assertRegex(captured.getvalue(), r"Function my_function took ")

    def test_tempit_basic_no_parenthesis(self):
        @tempit
        def my_function():
            time.sleep(0.01)

        with capture_stdout() as captured:
            my_function()
        self.assertRegex(captured.getvalue(), r"Function my_function took ")

    def test_tempit_with_concurrency(self):
        @tempit(run_times=2, concurrent_execution=True)
        def my_function():
            time.sleep(0.01)

        with patch("tempit.core.run_func_concurrency", wraps=run_func_concurrency) as mocked:
            my_function()
        mocked.assert_called_once()

    def test_tempit_no_concurrency(self):
        @tempit(run_times=3, concurrent_execution=False)
        def my_function():
            time.sleep(0.01)

        with patch("tempit.core.run_func_sequential", wraps=run_func_sequential) as mocked:
            my_function()
        mocked.assert_called_once()

    def test_tempit_concurrency_verbose(self):
        # Just check it doesn't crash and takes the concurrent path
        @tempit(run_times=2, concurrent_execution=True, verbose=True)
        def my_function():
            time.sleep(0.01)

        with capture_stdout() as captured, patch(
            "tempit.core.run_func_concurrency", wraps=run_func_concurrency
        ) as mocked:
            my_function()
        mocked.assert_called_once()
        self.assertIn("tempit data for function my_function", captured.getvalue())

    def test_tempit_concurrency_crash(self):
        # Just check if it the parallel execution doesn't work, it should be executed in the main thread
        @tempit(run_times=2, concurrent_execution=True)
        def my_function():
            current_thread_name = threading.current_thread().name
            process_name = current_process().name
            if current_thread_name != "MainThread" or process_name != "MainProcess":
                raise RuntimeError("Crashing intentionally for testing multithreading outside class")
            time.sleep(0.01)

        start_time = time.perf_counter()
        with capture_stdout() as captured:
            my_function()
        execution_time = time.perf_counter() - start_time

        # It tries parallel processing, then parallel threading and finally the
        # sequential execution; only sanity-check that it terminates.
        self.assertLess(execution_time, 10)
        self.assertRegex(captured.getvalue(), r"Function my_function took")

    def test_tempit_args(self):
        @tempit(run_times=0, concurrent_execution=True, verbose=True)
        def my_function(a: int = 1, b: int = 2):
            return a + b

        result = my_function(1, b=2)
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

    def test_recursive(self):
        @tempit(run_times=2, concurrent_execution=True, verbose=True)
        def my_function(n: int = 10):
            if n < 2:
                return n
            return my_function(n - 2) + my_function(n - 1)

        result = my_function(7)
        self.assertEqual(result, 13)

    def test_exception_does_not_poison_recursion_stack(self):
        # A raising call must not leave the function on the recursion stack,
        # otherwise every later call would be wrongly treated as recursive.
        @tempit(run_times=1)
        def my_function(x: int = 0):
            if x == 1:
                raise ValueError("boom")
            return x

        with self.assertRaises(ValueError):
            my_function(1)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with capture_stdout() as captured:
                result = my_function(2)

        self.assertEqual(result, 2)
        self.assertFalse(any("Recursive function detected" in str(w.message) for w in caught))
        self.assertRegex(captured.getvalue(), r"Function my_function took ")

    def test_time_wasted_resets_between_top_level_calls(self):
        # The accumulated recursion overhead must be reset after the outermost
        # call, otherwise subsequent calls report a bogus (zeroed) measurement.
        @tempit(run_times=1, verbose=True)
        def recursive_func(n: int = 0):
            if n < 2:
                return n
            return recursive_func(n - 2) + recursive_func(n - 1)

        for _ in range(2):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with capture_stdout() as captured:
                    result = recursive_func(6)

            self.assertEqual(result, 8)
            match = re.search(r"Time: ([\d.]+)µs", captured.getvalue())
            assert match is not None
            self.assertGreater(float(match.group(1)), 0.0)

    def test_concurrent_calls_do_not_falsely_detect_recursion(self):
        # Calls of the same decorated function from different threads must not
        # share the recursion stack, which would raise spurious warnings.
        @tempit(run_times=1)
        def slow_function(x: int = 0):
            time.sleep(0.05)
            return x

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with capture_stdout(), ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(slow_function, range(4)))

        self.assertEqual(results, [0, 1, 2, 3])
        self.assertFalse(any("Recursive function detected" in str(w.message) for w in caught))

    def test_run_func_concurrency_reports_per_run_times(self):
        # Each concurrent run must report its own measured time, not a single
        # wall-clock average replicated across every run (which would erase the
        # min/max/median/stdev information shown in verbose mode).
        if max(1, (cpu_count() or 1) - 1) < 2:
            self.skipTest("Not enough CPU cores for concurrent execution")

        def sleeper():
            time.sleep(0.02)
            return 42

        result, total_times = run_func_concurrency(sleeper, 2)

        self.assertEqual(result, 42)
        self.assertEqual(len(total_times), 2)
        for run_time in total_times:
            # A replicated average of two parallel 20ms runs would be ~10ms.
            self.assertGreaterEqual(run_time, 0.015)

    def test_non_method_arg_with_matching_attribute_is_not_stripped(self):
        # An argument that merely has an attribute with the function's name must
        # not be stripped as if it were the `self` of a method.
        @tempit(run_times=1, verbose=True)
        def process(self):
            return "ok"

        class Fake:
            process = 1

        with capture_stdout() as captured:
            result = process(Fake())

        self.assertEqual(result, "ok")
        self.assertIn("Args: (<", captured.getvalue())

    @unittest.skipUnless(not IN_GITHUB_ACTIONS, "Skip if running in GitHub Actions: too expensive.")
    def test_tempit_long_running_function(self):
        # Ensure the loky pool is already spawned before timing the concurrent call.
        warm_concurrency_pool()

        @tempit(run_times=5, concurrent_execution=True)
        def my_concurrent_function(a=2_000_000, n=18):
            for _ in range(a):
                pass
            return fib(n=n)

        @tempit(run_times=5, concurrent_execution=False)
        def my_sequential_function(a=2_000_000, n=18):
            for _ in range(a):
                pass
            return fib(n=n)

        start_time = time.perf_counter()
        result_concurrent = my_concurrent_function(2_000_000, n=18)
        execution_time_concurrent = time.perf_counter() - start_time

        start_time = time.perf_counter()
        result_sequential = my_sequential_function(2_000_000, n=18)
        execution_time_sequential = time.perf_counter() - start_time

        self.assertEqual(result_concurrent, 2584)
        self.assertEqual(result_sequential, 2584)

        # Concurrency should not be drastically slower than sequential execution.
        # The margin is intentionally generous to stay robust on loaded machines.
        self.assertLessEqual(execution_time_concurrent, execution_time_sequential * 3 + 1.0)


# Added here since calling a function from another process inside a test method doesn't work
@tempit(run_times=2, concurrent_execution=True, verbose=True)
def my_process_function(a: int = 1, b: int = 2):
    return a + b


def fib(n):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)


if __name__ == "__main__":
    unittest.main()
