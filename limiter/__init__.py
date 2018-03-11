from redis import StrictRedis

from .counter import SlidingRedisCounter, FixedWindowRedisCounter
from .rate_limiter import RateLimiter


def make_fixed_window_limiter(threshold, interval, redis_config) -> RateLimiter:
    return RateLimiter(threshold, interval, FixedWindowRedisCounter(StrictRedis(**redis_config)))


def make_sliding_limiter(threshold, interval, redis_config) -> RateLimiter:
    return RateLimiter(threshold, interval, SlidingRedisCounter(StrictRedis(**redis_config)))
