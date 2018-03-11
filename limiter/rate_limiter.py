import math

from limiter.counter import AbstractionCounter


class RateLimiter:
    """rate limiter, please give it a counter with add_key method..."""

    def __init__(self, threshold, interval, counter: AbstractionCounter):
        """
        :param threshold: int, or we try to ceil
        :param interval: int, or we try to ceil
        """
        assert threshold > 0
        assert interval > 0
        self._threshold = math.ceil(threshold)
        self._interval = math.ceil(interval)
        self._prefix = "rate-limiter:{}"
        self._counter = counter

    def exceeded(self, iid):
        current = self._counter.add_key(self._prefix.format(iid), self._interval)
        return current >= self._threshold

    def current(self, iid):
        return self._counter.current(self._prefix.format(iid))

    def reset(self, iid):
        self._counter.reset(self._prefix.format(iid))
