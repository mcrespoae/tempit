import multiprocessing
import threading
import unittest
from concurrent.futures import ProcessPoolExecutor

from tempit.core import TempitConfig, tempit

# Ensure the decorator is active for this module at import time, before the
# module-level targets below are decorated, regardless of the import order of
# the other test modules (test_tempit_deactivated sets the flag to False).
TempitConfig.ACTIVE = True


def setUpModule():
    TempitConfig.ACTIVE = True


@tempit(run_times=2, concurrent_execution=False)
def decorated_function(a: int = 1, b: int = 2) -> int:
    return a + b


@tempit(run_times=2, concurrent_execution=True)
def decorated_concurrent_function(a: int = 1, b: int = 2) -> int:
    return a + b


class DecoratedClass:
    def __init__(self, factor: int = 1):
        self.factor = factor

    @tempit(run_times=2, concurrent_execution=False)
    def decorated_method(self, a: int = 1, b: int = 2) -> int:
        return self.factor * (a + b)


def _available_start_methods():
    """Return the start methods to exercise.

    'fork' is skipped once threads exist because forking a multithreaded process
    is deprecated and unsafe (and no longer a default on any platform as of 3.14).
    """
    methods = multiprocessing.get_all_start_methods()
    if "fork" in methods and threading.active_count() > 1:
        methods = [method for method in methods if method != "fork"]
    return methods


class TestStartMethods(unittest.TestCase):
    """Verify tempit-decorated callables work when executed in processes started
    with each multiprocessing start method (fork / forkserver / spawn)."""

    def _assert_in_each_start_method(self, target, expected):
        methods = _available_start_methods()
        if not methods:
            self.skipTest("No multiprocessing start methods available")
        for method in methods:
            with self.subTest(start_method=method):
                context = multiprocessing.get_context(method)
                with ProcessPoolExecutor(max_workers=1, mp_context=context) as executor:
                    result = executor.submit(target).result()
                self.assertEqual(result, expected)

    def test_decorated_function_across_start_methods(self):
        self._assert_in_each_start_method(decorated_function, 3)

    def test_decorated_concurrent_function_across_start_methods(self):
        self._assert_in_each_start_method(decorated_concurrent_function, 3)

    def test_decorated_method_across_start_methods(self):
        self._assert_in_each_start_method(DecoratedClass(2).decorated_method, 6)


if __name__ == "__main__":
    unittest.main()
