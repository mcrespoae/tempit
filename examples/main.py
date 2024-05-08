import random
import sys
import time

sys.path.append("../")
from simple_timeit_decorator import timeit


class TimeItTestClass:
    @timeit()
    def timeit_basic(self, a: int = 1, b: int = 1):
        time.sleep(random.randint(a, b))

    @timeit(verbose=True)
    def timeit_verbose(self, a: int = 1, b: int = 1):
        time.sleep(random.randint(a, b))

    @timeit()
    def timeit_less_than_1s(self):
        time.sleep(random.random())

    @timeit(run_times=10)
    def timeit_10times_less_than_1s(self):
        time.sleep(random.random())

    @timeit(run_times=10, verbose=True)
    def timeit_10times_tenth_second_verbose(self):
        time.sleep(0.1)

    def timeit_basic_1s(self):
        self.timeit_basic(1, 1)

    def timeit_basic_60s(self):
        self.timeit_basic(60, 60)

    def timeit_verbose_1s(self):
        self.timeit_verbose(1, 1)


def main():
    test_class = TimeItTestClass()
    test_class.timeit_basic_1s()
    test_class.timeit_less_than_1s()
    # test_class.timeit_basic_60s()
    test_class.timeit_verbose_1s()
    test_class.timeit_10times_tenth_second_verbose()
    test_class.timeit_10times_less_than_1s()


if __name__ == "__main__":
    main()
