
def if_keep_grow(n, array):
    init = False
    last_i = 0
    for i in array[-n:]:
        if not init:
            last_i = i
            init = True
        if i < last_i:
            return False
        last_i = i
    return True

def if_keep_reduce(n, array):
    init = False
    last_i = 0
    for i in array[-n:]:
        if not init:
            last_i = i
            init = True
        if i > last_i:
            return False
        last_i = i
    return True