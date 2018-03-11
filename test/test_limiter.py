from unittest import TestCase
from unittest.mock import patch

import redis
from mockredis import mock_strict_redis_client

from limiter.counter import SlidingRedisCounter


class TestSlidingCounter(TestCase):

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_addkey(self):
        redis_ins = redis.StrictRedis()
        expired = 1000
        key = "it is a test"

        sl = SlidingRedisCounter(redis_ins)
        sl.reset(key)
        result = sl.incr(key, expired)
        self.assertEqual(0, result)
        sl.incr(key, expired)
        self.assertEqual(2, sl.incr(key, expired))
        self.assertEqual(3, sl.current(key))
