from rapidpg.utilities import parse_config


def test_collision():
    expect = set()
    for c in range(1, 7 + 1):
        expect.add(str(c))
    expect.add('10')
    expect.add('12')
    for c in range(20, 30 + 1):
        expect.add(str(c))
    expect.add('a')
    expect.add('b')
    expect.add('c')
    result = parse_config(["collision 1...7, 10, 12, 20...30, a, b,c"])['collision']
    assert isinstance(result, set)
    assert result == expect


def test_gravity():
    result = parse_config(["gravity 15.1"])['gravity']
    assert isinstance(result, float)
    assert result == 15.1


def test_resolution():
    result = parse_config(["resolution 800 600"])['resolution']
    assert isinstance(result, tuple)
    assert result == (800, 600)


def test_background():
    result = parse_config(["background static 0"])['background']  # single element
    assert isinstance(result, list)
    assert isinstance(result[0], tuple)
    assert result == [("static", 0)]
    result = parse_config(["background static 0",
                           "background mountains 15", "background trees 10"])['background']
    assert result == [("static", 0), ("mountains", 15), ("trees", 10)]


def test_spawn():
    result = parse_config(["spawn 10 20"])['spawn']
    assert isinstance(result, tuple)
    assert result == (10, 20)


def test_exit():
    result = parse_config(["exit 10 10 10 10"])['exit']
    assert isinstance(result, tuple)
    assert result == (10, 10, 10, 10)


def test_animations():
    result = parse_config(["animations asdkj 123 1 2"])['animations']
    assert isinstance(result, list)
    assert isinstance(result[0], tuple)
    assert result == [('asdkj', 123, 1, 2)]