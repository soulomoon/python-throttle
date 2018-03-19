![Build Status](https://travis-ci.org/soulomoon/python-throttle.svg?branch=develop)
[![codecov](https://codecov.io/gh/soulomoon/python-throttle/branch/develop/graph/badge.svg)](https://codecov.io/gh/soulomoon/python-throttle)

# python redis backed limiter

## sliding log or fixed window limiter
This module mainly offer two limiter
* FixedWindowLimiter  
simply using redis incr, which about 10 times the speed of the sliding version but the limit is not smooth, may overflow a threshold size near the gap between two intervals
* SlidingWindowLimiter    
using redis ordered set, slow but offers more smooth limit and more extendability

## dummy exmaple usage:
```python
import time
import limiter
TEST_REDIS_CONFIG = {'host': 'localhost','port': 6379,'db': 10}
ip = "who are you?"
throttle = limiter.FixedWindowLimiter(threshold=2, interval=3, redis_config=TEST_REDIS_CONFIG)
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

## dummy beach mark
It is from my unittest and not accurate,
```
rate_counter_pressure_test: SlidingRedisCounter
rate_counter_pressure_test: SlidingRedisCounter time count: 1.0075314449495636
rate_counter_pressure_test: FixedWindowRedisCounter
rate_counter_pressure_test: FixedWindowRedisCounter time count: 0.13711917598266155
```
