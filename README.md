![Build Status](https://travis-ci.org/soulomoon/python-throttle.svg?branch=develop)
[![codecov](https://codecov.io/gh/soulomoon/python-throttle/branch/develop/graph/badge.svg)](https://codecov.io/gh/soulomoon/python-throttle)

# python redis backed limiter

## sliding log or fixed window limiter
* make_sliding_limiter
* make_fixed_window_limiter
## dummy exmaple usage:
```python
import time
import limiter
TEST_REDIS_CONFIG = {'host': 'localhost','port': 6379,'db': 10}
ip = "who are you?"
throttle = limiter.make_fixed_window_limiter(threshold=2, interval=3, redis_config=TEST_REDIS_CONFIG)
print("first time, blocked?: {}".format(throttle.exceeded(ip)))
print("second time, blocked?: {}".format(throttle.exceeded(ip)))
print("now I block you, blocked?: {}".format(throttle.exceeded(ip)))
time.sleep(3)
print("refill energy, blocked?: {}".format(throttle.exceeded(ip)))
```

ouput:
```
first time blocked?: False
second time blocked?: False
now I block you blocked?: True
refill energy blocked?: False
```
