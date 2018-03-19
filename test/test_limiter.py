import random
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from unittest import TestCase

from limiter.rate_limiter import FixedWindowLimiter, SlidingWindowLimiter
from test.config import TEST_REDIS_CONFIG


class TestRateLimiter(TestCase):
    def setUp(self):
        self.test_limiter_factory = [
            FixedWindowLimiter,
            SlidingWindowLimiter
        ]
        # threshold interval
        self.test_data = [(random.randint(1, 100), random.randint(1, 2)) for _ in range(5)]

    def test_rate_limiter(self):
        for maker in self.test_limiter_factory:
            for threshold, interval in self.test_data:
                self.limiter_test(maker, threshold, interval)

    def limiter_test(self, make_limiter, threshold, interval):
        """test if rate limiter is working
        """
        key = "test_sliding_rate_limiter"
        rate_limiter = make_limiter(threshold=threshold, interval=interval, redis_config=TEST_REDIS_CONFIG)
        rate_limiter.reset(key)
        # with in range, not blocking
        for _ in range(threshold):
            self.assertEqual(False, rate_limiter.exceeded(key))

        self.assertEqual(threshold, rate_limiter.current(key))
        # gas down, blocked!!
        self.assertEqual(True, rate_limiter.exceeded(key))
        self.assertEqual(True, rate_limiter.exceeded(key))
        time.sleep(interval + 0.1)

        # gas up, now you can go
        self.assertEqual(0, rate_limiter.current(key))
        self.assertEqual(False, rate_limiter.exceeded(key))
        rate_limiter.reset(key)

    def test_race_condition(self):
        for maker in self.test_limiter_factory:
            self.race_condition_test(maker)

    def race_condition_test(self, make_limiter):
        """reject time should be the same no mater running in one thread , multi thread or multi process
        for the same threshold
        """
        threshold_list = [30 for _ in range(10)]
        attempt_list = [i for i in range(10, 60, 5)]
        threshold_attempt_tuples = list(zip(threshold_list, attempt_list))

        key = "race_condition_test"
        throttle = make_limiter(threshold=10, interval=1000, redis_config=TEST_REDIS_CONFIG)
        print("{} :{}".format(key, type(throttle._counter)))

        single_thread = 0
        for threshold, attempt in threshold_attempt_tuples:
            single_thread += _repeat_attempt(make_limiter, key, (threshold, attempt))
        throttle.reset(key)

        with ProcessPoolExecutor(max_workers=4) as executor:
            multi_process = sum(executor.map(partial(_repeat_attempt, make_limiter, key), threshold_attempt_tuples))
        throttle.reset(key)

        with ThreadPoolExecutor(max_workers=14) as executor:
            multi_thread = sum(executor.map(partial(_repeat_attempt, make_limiter, key), threshold_attempt_tuples))
        throttle.reset(key)

        result_msg = "single_thread: {}, multi_process: {}, multi_thread:{}"
        print(result_msg.format(single_thread, multi_process, multi_thread))
        self.assertEqual(multi_process, single_thread)
        self.assertEqual(multi_thread, single_thread)


def _repeat_attempt(maker, key, threshold_attempt) -> int:
    """ test attempt failure
    :return: blocked times
    """
    threshold = threshold_attempt[0]
    attempt = threshold_attempt[1]
    throttle = maker(threshold=threshold, interval=1000, redis_config=TEST_REDIS_CONFIG)  # type: RateLimiter
    return [throttle.exceeded(key) for _ in range(attempt)].count(True)
