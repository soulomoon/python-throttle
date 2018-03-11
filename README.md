![Build Status](https://travis-ci.org/soulomoon/python-throttle.svg?branch=develop)
[![codecov](https://codecov.io/gh/soulomoon/python-throttle/branch/develop/graph/badge.svg)](https://codecov.io/gh/soulomoon/python-throttle)

# python redis backed limiter
## exmaple usage:

```python3
>>> import time
>>> import limiter
>>> TEST_REDIS_CONFIG = {'host': 'localhost','port': 6379,'db': 10}
>>> throttle = limiter.make_fixed_window_limiter(threshold=2, interval=12, redis_config=TEST_REDIS_CONFIG)
>>> throttle.exceeded(ip)
False
>>> throttle.exceeded(ip)
False
>>> throttle.exceeded(ip)
True
>>> time.sleep(12)
>>> throttle.exceeded(ip)
False
```
