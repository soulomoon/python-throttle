import math

from redis import StrictRedis

from .counter import AbstractionCounter, SlidingRedisCounter, FixedWindowRedisCounter

__all__ = ['FixedWindowLimiter', 'SlidingWindowLimiter']


class RateLimiter:
    """rate limiter, please give it a counter implementing all methods of AbstractionCounter"""

    def __init__(self, threshold, interval, counter: AbstractionCounter, name_space="default"):
        """
        :param threshold: int, or we try to ceil, no smaller than 0
        :param interval: int, or we try to ceil, no smaller than 1
        :param counter: subclass of or one with all methods of AbstractionCounter
        """
        assert threshold >= 0
        assert interval >= 1
        self._threshold = math.ceil(threshold)
        self._interval = math.ceil(interval)
        self._prefix = "rate-limiter:" + name_space + "{}"
        self._counter = counter

    def exceeded(self, iid):
        current = self._counter.add_key(self._prefix.format(iid), self._interval)
        return current >= self._threshold

    def current(self, iid):
        return self._counter.current(self._prefix.format(iid))

    def reset(self, iid):
        self._counter.reset(self._prefix.format(iid))


class FixedWindowLimiter(RateLimiter):
    """return RateLimiter with FixedWindowRedisCounter, which 10 times faster than sliding
    but it the limit is not smooth, may overflow two threshold near the gap between two interval
    """

    def __init__(self, threshold, interval, redis_config, name_space="default"):
        super().__init__(threshold, interval, FixedWindowRedisCounter(StrictRedis(**redis_config)), name_space)


class SlidingWindowLimiter(RateLimiter):
    """return RateLimiter with SlidingRedisCounter, slow
    but offer smooth limit, and offer more info
    """

    def __init__(self, threshold, interval, redis_config, name_space="default"):
        super().__init__(threshold, interval, SlidingRedisCounter(StrictRedis(**redis_config)), name_space)
