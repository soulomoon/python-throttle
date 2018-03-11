from limiter.counter import AbstractionCounter


class SlidingLimiter:
    """rate limiter"""

    def __init__(self, threshold, interval, counter: AbstractionCounter):
        """
        :param threshold: threshold
        :param interval: window size resolution second
        """
        self.threshold = threshold
        self.interval = interval
        self.prefix = "rate-limiter:{}"
        self.counter = counter

    def exceeded(self, iid):
        self.counter.incr(iid, self.interval)
