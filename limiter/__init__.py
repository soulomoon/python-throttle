from redis import StrictRedis

from .counter import SlidingRedisCounter, FixedWindowRedisCounter
from .rate_limiter import RateLimiter


def make_fixed_window_limiter(threshold, interval, redis_config) -> RateLimiter:
    """return RateLimiter with FixedWindowRedisCounter, which 10 times faster than sliding
    but it the limit is not smooth, may overflow two threshold near the gap between two interval
    """
    return RateLimiter(threshold, interval, FixedWindowRedisCounter(StrictRedis(**redis_config)))


def make_sliding_limiter(threshold, interval, redis_config) -> RateLimiter:
    """return RateLimiter with SlidingRedisCounter, slow
    but offer smooth limit, and offer more info
    """
    return RateLimiter(threshold, interval, SlidingRedisCounter(StrictRedis(**redis_config)))
