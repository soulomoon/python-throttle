import time
import uuid
from abc import ABC, abstractmethod

from redis import StrictRedis

__all__ = ['AbstractionCounter', 'BaseRedisCounter', 'SlidingRedisCounter', 'FixedWindowRedisCounter']


class AbstractionCounter(ABC):
    @abstractmethod
    def add_key(self, key, expired) -> int:
        """increase the counter and return current number"""

    @abstractmethod
    def current(self, key) -> int:
        """pass return current numbers"""

    @abstractmethod
    def reset(self, key):
        """reset key"""


class BaseRedisCounter(AbstractionCounter):
    def __init__(self, redis: StrictRedis):
        self.redis = redis


class SlidingRedisCounter(BaseRedisCounter):
    """counter using redis' ordered set
    """

    def add_key(self, key, expired):
        """use ordered set for counting keys get_set manner
        """
        now = time.time()
        with self.redis.pipeline() as session:
            session.zremrangebyscore(key, 0, now - expired)
            session.zrange(key, 0, -1)
            session.zadd(key, now, uuid.uuid4().hex)
            session.expire(key, expired)
            result = session.execute()
        return len(result[1])

    def current(self, key):
        """return keys' current numbers if there is key else 0
        """
        return len(self.redis.zrange(key, 0, -1))

    def reset(self, key):
        self.redis.delete(key)


class FixedWindowRedisCounter(BaseRedisCounter):
    """counter using redis' incr
    """

    # lua script from (https://redis.io/commands/incr) to avoid race condition
    # slightly modify to return current
    lua_incr = """
                local current
                current = redis.call("incr",KEYS[1])
                if tonumber(current) == 1 then
                    redis.call("expire",KEYS[1],KEYS[2])
                end
                return current-1
                """

    def add_key(self, key, expired):
        """use lua script to avoid race condition"""
        multiply = self.redis.register_script(self.lua_incr)
        return multiply([key, expired])

    def current(self, key):
        """return keys' current numbers if there is key else 0
        """
        r = self.redis.get(key)
        if r:
            return int(r)
        else:
            return 0

    def reset(self, key):
        self.redis.delete(key)
