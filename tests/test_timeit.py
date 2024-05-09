import time
import unittest

from simple_timeit_decorator.timeit import timeit


class TestTimeitDecorator(unittest.TestCase):

    def test_timeit_decorator_basic(self):
        @timeit()
        def my_function():
            time.sleep(0.1)

        start_time = time.time()
        my_function()
        end_time = time.time()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.1, delta=0.01)  # Check if execution time is close to 0.1 seconds

    def test_timeit_decorator_with_concurrency(self):
        @timeit(run_times=10)
        def my_function():
            time.sleep(0.1)

        start_time = time.time()
        my_function()
        end_time = time.time()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 0.10, delta=0.1)  # Check if execution time is close to 0.1 seconds

    def test_timeit_decorator_no_concurrency(self):
        @timeit(run_times=10, concurrency_mode="none")
        def my_function():
            time.sleep(0.1)

        start_time = time.time()
        my_function()
        end_time = time.time()

        execution_time = end_time - start_time
        self.assertAlmostEqual(execution_time, 1.0, delta=0.1)  #


if __name__ == "__main__":
    unittest.main()
