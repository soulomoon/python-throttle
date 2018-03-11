import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from unittest import TestCase

import redis

from limiter.counter import SlidingRedisCounter, AbstractionCounter

TEST_REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'decode_responses': True,
    'db': 0
}


def repeat_incr(counter_factory, key, n):
    counter = counter_factory()  # type: AbstractionCounter
    for _ in range(n):
        counter.add_key(key, 10000)


def _get_redis_counter(counter):
    return counter(redis.StrictRedis(**TEST_REDIS_CONFIG))


class TestSlidingCounter(TestCase):
    def setUp(self):
        self.counter_factories = [
            partial(partial(_get_redis_counter, SlidingRedisCounter))
        ]
        self.pressure_test_on = True

    def test_add_key(self):
        expired = 1000
        key = "test_add_key"
        for counter_factory in self.counter_factories:
            counter = counter_factory()
            print("{}: {}".format(key, counter.__class__.__name__))
            counter.reset(key)
            self.assertEqual(0, counter.add_key(key, expired))
            counter.add_key(key, expired)
            self.assertEqual(2, counter.add_key(key, expired))
            self.assertEqual(3, counter.current(key))

    def test_expired(self):
        delay = 1
        key = "test_expired"
        for counter_factory in self.counter_factories:
            tf = counter_factory()
            print("{}: {}".format(key, tf.__class__.__name__))
            tf.reset(key)
            tf.add_key(key, delay)
            self.assertIsNotNone(tf.current(key))
            time.sleep(delay * 1.1)
            self.assertEqual(0, tf.current(key))
            tf.reset(key)

    def test_naive_pressure_test(self):
        if self.pressure_test_on:
            for counter_factory in self.counter_factories:
                repeat = [1, 10, 1000, 1000, 10, 1]
                key = "rate_counter_pressure_test"
                tf = counter_factory()
                begin = time.perf_counter()
                print("{}: {}".format(key, tf.__class__.__name__))
                tf.reset(key)

                for n in repeat:
                    repeat_incr(counter_factory, key, n)
                self.assertEqual(sum(repeat), tf.current(key))
                tf.reset(key)

                with ProcessPoolExecutor(max_workers=4) as executor:
                    list(executor.map(partial(repeat_incr, counter_factory, key), repeat))
                self.assertEqual(sum(repeat), tf.current(key))
                tf.reset(key)

                with ThreadPoolExecutor(max_workers=14) as executor:
                    list(executor.map(partial(repeat_incr, counter_factory, key), repeat))
                self.assertEqual(sum(repeat), tf.current(key))
                tf.reset(key)
                print("{}: {} time count: {}".format(key, tf.__class__.__name__, time.perf_counter() - begin))
