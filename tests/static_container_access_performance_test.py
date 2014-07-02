"""
This test aims to measure the performance difference between some
container data structures. The focus is on the difference in access
speed when the list of keys never change
"""
from collections import namedtuple
from time import time

TEST_CYCLES = 10 * 1000000


def measure(s):
    def out(func):
        def wrapper(*args):
            start = time()
            func(*args)
            passed = time() - start
            print("Finished {0} cycles for {1} in {2:0.5f} seconds, {3} accesses were made".
                  format(TEST_CYCLES, s, passed, TEST_CYCLES * 4))
        return wrapper
    return out


class Bunch:
    """
    Class courtesy of Alex Martelli.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Plain:
    __slots__ = ["a", "b", "c", "d"]

    def __init__(self, seq):
        self.a, self.b, self.c, self.d = seq


@measure('dict')
def dict_test(d):
    for _ in range(TEST_CYCLES):
        d['a']
        d['b']
        d['c']
        d['d']


@measure('Bunch')
def bunch_test(b):
    for _ in range(TEST_CYCLES):
        b.a
        b.b
        b.c
        b.d


@measure('named tuple')
def named_tuple_test(ti):
    for _ in range(TEST_CYCLES):
        ti.a
        ti.b
        ti.c
        ti.d


@measure('Plain')
def plain_slots_test(t):
    for _ in range(TEST_CYCLES):
        t.a
        t.b
        t.c
        t.d


@measure('tuple')
def tuple_indexing(t):
    for _ in range(TEST_CYCLES):
        t[0]
        t[1]
        t[2]
        t[3]


@measure('list')
def list_indexing(t):
    for _ in range(TEST_CYCLES):
        t[0]
        t[1]
        t[2]
        t[3]


@measure('checks')
def multiple_checks(get):
    for _ in range(TEST_CYCLES):
        get('a')
        get('b')
        get('c')
        get('d')


def main():
    b = Bunch(a=100, b=200, c=300, d=400)
    bunch_test(b)
    print()

    d = dict([("a", 100), ("b", 200), ("c", 300), ("d", 400)])
    dict_test(d)
    print()

    p = Plain([100, 200, 300, 400])
    plain_slots_test(p)
    print()

    t = (100, 200, 300, 400)
    tuple_indexing(t)
    print()

    l = [100, 200, 300, 400]
    list_indexing(l)
    print()

    t = namedtuple("TestTuple", ["a", "b", "c", "d"])
    ti = t._make([100, 200, 300, 400])
    named_tuple_test(ti)
    print()

    def get(s):
        if s == 'a':
            return 100
        if s == 'b':
            return 200
        if s == 'c':
            return 300
        if s == 'd':
            return 400
    multiple_checks(get)

if __name__ == '__main__':
    main()


"""
It appears that dict is the fastest in CPython:
The following was produced by CPython 3.4.1
Finished 10000000 cycles for Bunch in 2.48514 seconds, 40000000 accesses were made

Finished 10000000 cycles for dict in 1.95211 seconds, 40000000 accesses were made

Finished 10000000 cycles for Plain in 2.38814 seconds, 40000000 accesses were made

Finished 10000000 cycles for tuple in 2.23813 seconds, 40000000 accesses were made

Finished 10000000 cycles for list in 2.27613 seconds, 40000000 accesses were made

Finished 10000000 cycles for named tuple in 5.12929 seconds, 40000000 accesses were made

Finished 10000000 cycles for checks in 10.35859 seconds, 40000000 accesses were made


However Performance for each type differ drastically when using PyPy

Finished 10000000 cycles for Bunch in 0.01300 seconds, 40000000 accesses were made

Finished 10000000 cycles for dict in 0.44800 seconds, 40000000 accesses were made

Finished 10000000 cycles for Plain in 0.01200 seconds, 40000000 accesses were made

Finished 10000000 cycles for tuple in 0.02000 seconds, 40000000 accesses were made

Finished 10000000 cycles for list in 0.02600 seconds, 40000000 accesses were made

Finished 10000000 cycles for namedtuple in 0.02100 seconds, 40000000 accesses were made

Finished 10000000 cycles for checks in 0.02200 seconds, 40000000 accesses were made

A day will come when Pygame is compatible with PyPy, in the meantime, dict will be used
in CPython instead.
"""