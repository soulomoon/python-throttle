import time
import uuid
from abc import ABC, abstractmethod


class AbstractionCounter(ABC):
    @abstractmethod
    def incr(self, key, expired):
        """incr the counter and return result"""

    @abstractmethod
    def current(self, key):
        """pass return current numbers"""

    @abstractmethod
    def reset(self, key):
        """reset key"""


class SlidingRedisCounter(AbstractionCounter):
    """Abstraction layer of counter using redis"""

    def __init__(self, redis):
        self.redis = redis

    def incr(self, key, expired):
        now = time.time()
        with self.redis.pipeline() as session:
            session.zremrangebyscore(key, 0, now - expired)
            session.zrange(key, 0, -1)
            session.zadd(key, now, uuid.uuid4().hex)
            session.expire(key, expired)
            result = session.execute()
        return len(result[1])

    def current(self, key):
        return len(self.redis.zrange(key, 0, -1))

    def reset(self, key):
        return self.redis.delete(key)