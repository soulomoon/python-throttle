from unittest import TestCase
from unittest.mock import patch

import redis
from mockredis import mock_strict_redis_client

from limiter import SlidingLimiter


class TestSlidingLimiter(TestCase):

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_addkey(self):
        redis_ins = redis.StrictRedis()
        key = "it is a test"

        sl = SlidingLimiter(10, 100, redis_ins)
        sl.reset(key)
        result = sl.incr(key)
        self.assertEqual(0, result)
        sl.incr(key)
        self.assertEqual(2, sl.incr(key))
        self.assertEqual(3, sl.current(key))
