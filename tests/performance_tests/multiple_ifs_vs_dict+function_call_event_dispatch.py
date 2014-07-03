"""
This test aims to determine which is the ideal bethod of
event dispatch for handling events in pygame.
It is common that a pygame program iterate through pygame.event.get()
and decide what to do.
if-elif might be faster because it doesn't call any function
dict is faster at dispatching to the proper handler, but is it fast enough
to make up for the function call overhead?
"""
from random import randint
from timer import measure

TEST_CYCLES = 5 * 1000000

def if_tree(e):
    if e == 1:
        return 1
    elif e == 2:
        return 2

    elif e == 3:
        return 3

    elif e == 4:
        return 4
    elif e == 5:
        return 5

def r1():
    return 1
def r2():
    return 2
def r3():
    return 3
def r4():
    return 4
def r5():
    return 5

dispatch = {1: r1, 2: r2, 3: r3, 4: r4, 5: r5}

def dict_(e):
    try:
        return dispatch[e]()
    except KeyError:
        pass

@measure("ifs", TEST_CYCLES)
def test_ifs(sample):
    for e in sample:
        if_tree(e)

@measure("dict", TEST_CYCLES)
def test_dict(sample):
    for e in sample:
        dict_(e)

def main():
    print("Generating samples...")
    sample = [randint(0, 10) for x in range(TEST_CYCLES)]
    print("\nStarting tests\n")
    test_ifs(sample)
    print()
    test_dict(sample)

if __name__ == '__main__':
    main()

"""
Turns out if-elif is faster than dict.
dict's fast dispatch isn't enough to make up for the overhead of function call.
if there is more events to handle(there is only 5 in this test, which is a common amount)
dict might come up on top
"""