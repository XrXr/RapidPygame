"""
This test aims to measure the performance difference between some
container data structures. The focus is on the difference in access
speed when the list of keys never change
"""
from collections import namedtuple
from time import time

TEST_CYCLES = 10 * 1000000


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


def dict_test():
    d = dict([("a", 100), ("b", 100), ("c", 100), ("d", 100)])
    start = time()
    for _ in range(TEST_CYCLES):
        d['a']
        d['b']
        d['c']
        d['d']
    passed = time() - start
    print("Finished {0} cycles for dict in {1:0.5f} seconds, {2} accesses were made".
          format(TEST_CYCLES, passed, TEST_CYCLES * 4))


def bunch_test():
    b = Bunch(a=100, b=100, c=100, d=100)
    start = time()
    for _ in range(TEST_CYCLES):
        b.a
        b.b
        b.c
        b.d
    passed = time() - start
    print("Finished {0} cycles for Bunch in {1:0.5f} seconds, {2} accesses were made".
          format(TEST_CYCLES, passed, TEST_CYCLES * 4))


def named_tuple_test():
    t = namedtuple("TestTuple", ["a", "b", "c", "d"])
    ti = t._make([100, 100, 100, 100])
    start = time()
    for _ in range(TEST_CYCLES):
        ti.a
        ti.b
        ti.c
        ti.d
    passed = time() - start
    print("Finished {0} cycles for namedtuple in {1:0.5f} seconds, {2} accesses were made".
          format(TEST_CYCLES, passed, TEST_CYCLES * 4))

def plain_slots_test():
    t = Plain([100, 100, 100, 100])
    start = time()
    for _ in range(TEST_CYCLES):
        t.a
        t.b
        t.c
        t.d
    passed = time() - start
    print("Finished {0} cycles for Plain in {1:0.5f} seconds, {2} accesses were made".
          format(TEST_CYCLES, passed, TEST_CYCLES * 4))

def tuple_indexing():
    t = (100, 100, 100, 100)
    start = time()
    for _ in range(TEST_CYCLES):
        t[0]
        t[1]
        t[2]
        t[3]
    passed = time() - start
    print("Finished {0} cycles for tuple in {1:0.5f} seconds, {2} accesses were made".
          format(TEST_CYCLES, passed, TEST_CYCLES * 4))

def list_indexing():
    t = [100, 100, 100, 100]
    start = time()
    for _ in range(TEST_CYCLES):
        t[0]
        t[1]
        t[2]
        t[3]
    passed = time() - start
    print("Finished {0} cycles for list in {1:0.5f} seconds, {2} accesses were made".
          format(TEST_CYCLES, passed, TEST_CYCLES * 4))

def main():
    bunch_test()
    print()
    dict_test()
    print()
    plain_slots_test()
    print()
    tuple_indexing()
    print()
    list_indexing()
    print()
    named_tuple_test()

if __name__ == '__main__':
    main()


"""
It appears that dict is the fastest in CPython:
The following was produced by CPython 3.4.1
Finished 10000000 cycles for Bunch in 2.50514 seconds, 40000000 accesses were made

Finished 10000000 cycles for dict in 1.92811 seconds, 40000000 accesses were made

Finished 10000000 cycles for Plain in 2.41814 seconds, 40000000 accesses were made

Finished 10000000 cycles for tuple in 2.22713 seconds, 40000000 accesses were made

Finished 10000000 cycles for list in 2.20913 seconds, 40000000 accesses were made

Finished 10000000 cycles for namedtuple in 5.23730 seconds, 40000000 accesses were made


However Performance for each type differ drastically when using PyPy

Finished 10000000 cycles for Bunch in 0.01200 seconds, 40000000 accesses were made

Finished 10000000 cycles for dict in 0.45300 seconds, 40000000 accesses were made

Finished 10000000 cycles for Plain in 0.01300 seconds, 40000000 accesses were made

Finished 10000000 cycles for tuple in 0.01200 seconds, 40000000 accesses were made

Finished 10000000 cycles for list in 0.02600 seconds, 40000000 accesses were made

Finished 10000000 cycles for namedtuple in 0.02100 seconds, 40000000 accesses were made

A day will come when Pygame is compatible with PyPy, in the meantime, dict will be used
in CPython instead.
"""