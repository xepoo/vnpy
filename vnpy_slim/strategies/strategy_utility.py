import numpy as np


def grow_rate(n, array):
    x = np.arange(0, n)
    y = np.array(array[-n:])
    z = np.polyfit(x, y, 1)
    return z[0]


def if_keep_grow(n, array):
    init = False
    last_i = 0
    down_count = 0
    max_i = 0
    for i in array[-n:]:
        if not init:
            last_i = i
            init = True
        if i < last_i:
            #     down_count += 1
            # if down_count > 1:
            return False
        last_i = i
        max_i = max(i, last_i)
    if array[-1] == max_i:
        return True
    else:
        return False


def if_keep_reduce(n, array):
    init = False
    last_i = 0
    up_count = 0
    min_i = 0
    for i in array[-n:]:
        if not init:
            last_i = i
            init = True
        if i > last_i:
            #     up_count += 1
            # if up_count > 1:
            return False
        last_i = i
        min_i = min(i, last_i)
    if array[-1] == min_i:
        return True
    else:
        return False


def get_trade_long_price(close, rate):
    return close + (rate * close)

def get_trade_short_price(close, rate):
    return close - (rate * close)
