import random
import time
from unittest import TestCase

from limiter import make_sliding_limiter, make_fixed_window_limiter
from test.config import TEST_REDIS_CONFIG


class TestRateLimiter(TestCase):
    def setUp(self):
        self.test_limiter_factory = [
            make_sliding_limiter,
            make_fixed_window_limiter
        ]
        # threshold interval
        self.test_data = [(random.randint(0, 100), random.randint(1, 2)) for i in range(5)]

    def test_sliding_rate_limiter(self):
        for maker in self.test_limiter_factory:
            for threshold, interval in self.test_data:
                self.limiter_test(maker, threshold, interval)

    def limiter_test(self, make_limiter, threshold, interval):
        """test if rate limiter is working"""
        key = "test_sliding_rate_limiter"
        rate_limiter = make_limiter(threshold=threshold, interval=interval,
                                    redis_config=TEST_REDIS_CONFIG)
        rate_limiter.reset(key)
        # with in range, not blocking
        for _ in range(threshold):
            # print(rate_limiter.current(key))
            self.assertEqual(False, rate_limiter.exceeded(key))

        self.assertEqual(threshold, rate_limiter.current(key))
        # gas down, blocked!!
        self.assertEqual(True, rate_limiter.exceeded(key))
        self.assertEqual(True, rate_limiter.exceeded(key))
        time.sleep(interval)

        # gas up, now you can go
        self.assertEqual(0, rate_limiter.current(key))
        self.assertEqual(False, rate_limiter.exceeded(key))
