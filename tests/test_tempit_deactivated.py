import os
import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from tempit.core import TempitConfig, tempit

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
TempitConfig.ACTIVE = False


class TempitTestClassDeactivated:

    @tempit()
    def tempit_basic(self, a: int = 0, b: int = 1):
        return a + b

    @tempit
    def tempit_basic_no_parenthesis(self, a: int = 0, b: int = 1):
        return a + b

    def sum(self, a: int = 1, b: int = 2):
        return a + b

    @tempit(run_times=2)
    def test_tempit_args(self, a: int = 0, b: int = 1):
        return self.sum(a, b)

    @tempit(run_times=2)
    @staticmethod
    def static_method(a: int = 0, b: int = 1):
        return a + b

    @tempit
    @classmethod
    def class_method(cls, a: int = 0, b: int = 1):
        return cls.__name__, a + b


class TestTempitDecoratorClassDeactivated(unittest.TestCase):
    def setUp(self):
        self.test_class = TempitTestClassDeactivated()

    def test_tempit_basic(self):
        result_1 = self.test_class.tempit_basic(1, b=2)
        result_2 = self.test_class.tempit_basic()
        self.assertEqual(result_1, 3)
        self.assertEqual(result_2, 1)

    def test_tempit_basic_no_parenthesis(self):
        result_1 = self.test_class.tempit_basic_no_parenthesis(1, b=2)
        result_2 = self.test_class.tempit_basic_no_parenthesis()
        self.assertEqual(result_1, 3)
        self.assertEqual(result_2, 1)

    def test_tempit_args(self):
        result_1 = self.test_class.test_tempit_args(1, b=2)
        result_2 = self.test_class.test_tempit_args()
        self.assertEqual(result_1, 3)
        self.assertEqual(result_2, 1)

    def test_tempit_static_method(self):
        result_1 = self.test_class.static_method(1, b=2)
        result_2 = self.test_class.static_method()
        self.assertEqual(result_1, 3)
        self.assertEqual(result_2, 1)

    def test_tempit_class_method(self):
        class_name_1, result_1 = self.test_class.class_method(1, b=2)
        class_name_2, result_2 = self.test_class.class_method()
        self.assertEqual(class_name_1, "TempitTestClassDeactivated")
        self.assertEqual(result_1, 3)
        self.assertEqual(class_name_2, "TempitTestClassDeactivated")
        self.assertEqual(result_2, 1)

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

        self.assertEqual(class_name, "TempitTestClassDeactivated")
        self.assertEqual(result, 3)

    def test_tempit_class_method_run_from_other_process(self):
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.test_class.class_method, 2, b=6)
            class_name, result = future.result()

        self.assertEqual(class_name, "TempitTestClassDeactivated")
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


class TestTempitDeactivated(unittest.TestCase):

    def test_tempit_basic_deactivated(self):
        @tempit
        def my_function(a: int = 0, b: int = 1):
            return a + b

        self.assertEqual(my_function(1, b=2), 3)
        self.assertEqual(my_function(), 1)

    def test_tempit_with_args_deactivated(self):
        @tempit(run_times=0, concurrent_execution=True, verbose=True)
        def my_function(a: int = 0, b: int = 1):
            return a + b

        self.assertEqual(my_function(1, b=2), 3)
        self.assertEqual(my_function(), 1)

    def test_run_from_other_process(self):

        with ProcessPoolExecutor(max_workers=1) as executor:
            future_1 = executor.submit(my_process_function_deactivated, 1, b=2)
            result_1 = future_1.result()
            future_2 = executor.submit(my_process_function_deactivated)
            result_2 = future_2.result()
            future_3 = executor.submit(my_process_function_no_args_deactivated, 1, b=2)
            result_3 = future_3.result()
            future_4 = executor.submit(my_process_function_no_args_deactivated)
            result_4 = future_4.result()

        self.assertEqual(result_1, 3)
        self.assertEqual(result_2, 1)
        self.assertEqual(result_3, 3)
        self.assertEqual(result_4, 1)

    def test_run_from_other_thread(self):
        @tempit()
        def my_thread_function(a=0, b=1):
            return a + b

        @tempit
        def my_thread_no_args_function(a=0, b=1):
            return a + b

        with ThreadPoolExecutor(max_workers=1) as executor:
            future_1 = executor.submit(my_thread_function, 1, b=2)
            result_1 = future_1.result()
            future_2 = executor.submit(my_thread_function)
            result_2 = future_2.result()
            future_3 = executor.submit(my_thread_no_args_function, 1, b=2)
            result_3 = future_3.result()
            future_4 = executor.submit(my_thread_no_args_function)
            result_4 = future_4.result()

        self.assertEqual(result_1, 3)
        self.assertEqual(result_2, 1)
        self.assertEqual(result_3, 3)
        self.assertEqual(result_4, 1)


# Added here since calling a function from another process inside a test method doesn't work
@tempit(run_times=2, concurrent_execution=True, verbose=True)
def my_process_function_deactivated(a: int = 0, b: int = 1):
    return a + b


@tempit
def my_process_function_no_args_deactivated(a: int = 0, b: int = 1):
    return a + b


if __name__ == "__main__":
    unittest.main()
