import logging
import time
import uuid

from redis import StrictRedis


class SlidingLimiter:
    """python limiter redis backed"""

    def __init__(self, threshold, interval, redis: StrictRedis):
        """
        :param threshold: threshold resolution second
        :param interval: window size
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.threshold = threshold
        self.interval = interval
        self.redis = redis
        self.prefix = "rate-limiter:{}"

    def incr(self, iid):
        key = self.prefix.format(iid)
        now = time.time()
        with self.redis.pipeline() as session:
            self.logger.debug("in pipeline")
            session.zremrangebyscore(key, 0, now - self.interval)
            session.zrange(key, 0, -1)
            session.zadd(key, now, uuid.uuid4().hex)
            session.expire(key, self.interval)
            result = session.execute()
        return len(result[1])

    def current(self, iid):
        key = self.prefix.format(iid)
        return len(self.redis.zrange(key, 0, -1))

    def reset(self, iid):
        key = self.prefix.format(iid)
        return self.redis.delete(key)
