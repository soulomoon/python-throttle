from redis import StrictRedis

from .counter import SlidingRedisCounter, FixedWindowRedisCounter
from .rate_limiter import RateLimiter


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
