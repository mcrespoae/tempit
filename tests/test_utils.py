import unittest
from os import cpu_count

from tempit.utils import adjust_run_times_for_parallelism, format_time


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

    def test_format_time_minutes_no_second_overflow(self):
        # 119.6s is 1m 59.6s, not "01m:60s.600ms".
        self.assertEqual(format_time(119.6), "01m:59s.600ms")

    def test_format_time_hours_no_second_overflow(self):
        self.assertEqual(format_time(3599.7), "59m:59s.700ms")

    def test_format_time_rounds_milliseconds_up_with_carry(self):
        # 119.9996s rounds to 120.000s, which must carry into the minutes.
        self.assertEqual(format_time(119.9996), "02m:00s.0ms")


class TestAdjustRunTimesForParallelism(unittest.TestCase):
    def setUp(self) -> None:
        self.cpu_count = cpu_count()

    def test_adjust_run_times_for_parallelism_no_change(self):
        # Test with available cores
        run_times = 2
        result = adjust_run_times_for_parallelism(run_times)
        self.assertEqual(result, 2)

    def test_adjust_run_times_for_parallelism_too_many_runs(self):
        # Test with no available cores
        run_times = 1000
        result = adjust_run_times_for_parallelism(run_times)
        self.assertLess(result, run_times)

    def test_adjust_run_times_for_parallelism_one_runs(self):
        # Test with no available cores
        run_times = 1
        result = adjust_run_times_for_parallelism(run_times)
        self.assertEqual(result, 1)

    def test_adjust_run_times_for_parallelism_negative(self):
        # Test with no available cores
        run_times = -1
        result = adjust_run_times_for_parallelism(run_times)
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
