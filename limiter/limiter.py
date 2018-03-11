from limiter.counter import AbstractionCounter


class RateLimiter:
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
        current = self.counter.add_key(iid, self.interval)
        return current > self.threshold
