import time
from limiter import FixedWindowLimiter


TEST_REDIS_CONFIG = {'host': 'localhost', 'port': 6379, 'db': 10}
ip = "who are you?"
throttle = FixedWindowLimiter(threshold=2, interval=3, redis_config=TEST_REDIS_CONFIG, name_space="default")
print("first time, blocked?: {}".format(throttle.exceeded(ip)))
print("second time, blocked?: {}".format(throttle.exceeded(ip)))
print("now I block you, blocked?: {}".format(throttle.exceeded(ip)))
time.sleep(3)
print("refill energy, blocked?: {}".format(throttle.exceeded(ip)))
