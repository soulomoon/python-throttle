import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from unittest import TestCase

import redis

from limiter.counter import SlidingRedisCounter, AbstractionCounter, FixedWindowRedisCounter, BaseRedisCounter
from test.config import TEST_REDIS_CONFIG


def _mixed_counter_init(counter_cls):
    """try to boot up counter of any type
    """
    assert issubclass(counter_cls, AbstractionCounter)
    if issubclass(counter_cls, BaseRedisCounter):
        redis_ins = redis.StrictRedis(**TEST_REDIS_CONFIG)
        return counter_cls(redis_ins)
    else:
        return counter_cls()


def _repeat_incr(counter_cls, key, n):
    assert issubclass(counter_cls, AbstractionCounter)
    counter = _mixed_counter_init(counter_cls)
    for _ in range(n):
        counter.add_key(key, 10000)


class TestCounter(TestCase):
    def setUp(self):
        self.counter_class_list = [
            SlidingRedisCounter,
            FixedWindowRedisCounter
        ]
        self.pressure_test_on = True

    def test_add_key(self):
        expired = 1000
        key = "test_add_key"
        for counter_cls in self.counter_class_list:
            counter = _mixed_counter_init(counter_cls)
            print("{}: {}".format(key, counter.__class__.__name__))
            counter.reset(key)
            self.assertEqual(0, counter.add_key(key, expired))
            self.assertEqual(1, counter.add_key(key, expired))
            self.assertEqual(2, counter.add_key(key, expired))
            self.assertEqual(3, counter.current(key))

    def test_expired(self):
        delay = 1
        key = "test_expired"
        for counter_cls in self.counter_class_list:
            tf = _mixed_counter_init(counter_cls)
            print("{}: {}".format(key, tf.__class__.__name__))
            tf.reset(key)
            tf.add_key(key, delay)
            self.assertEqual(1, tf.current(key))
            # time out
            time.sleep(delay * 1.1)
            self.assertEqual(0, tf.current(key))
            tf.reset(key)

    def test_naive_pressure_test(self):
        """simply repeating, multi thread or multi process
        run all the repeat, and test the sum of the result
        """
        if self.pressure_test_on:
            for counter_cls in self.counter_class_list:
                repeat = [1, 10, 100, 100, 10, 1]
                key = "rate_counter_pressure_test"
                tf = _mixed_counter_init(counter_cls)
                begin = time.perf_counter()
                print("{}: {}".format(key, tf.__class__.__name__))
                tf.reset(key)

                for n in repeat:
                    _repeat_incr(counter_cls, key, n)
                self.assertEqual(sum(repeat), tf.current(key))
                tf.reset(key)

                with ProcessPoolExecutor(max_workers=4) as executor:
                    list(executor.map(partial(_repeat_incr, counter_cls, key), repeat))
                self.assertEqual(sum(repeat), tf.current(key))
                tf.reset(key)

                with ThreadPoolExecutor(max_workers=14) as executor:
                    list(executor.map(partial(_repeat_incr, counter_cls, key), repeat))
                self.assertEqual(sum(repeat), tf.current(key))
                tf.reset(key)
                print("{}: {} time count: {}".format(key, tf.__class__.__name__, time.perf_counter() - begin))
