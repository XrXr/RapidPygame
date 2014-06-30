import rapidpg.types.animation as animation
from rapidpg.types.containers import Bunch


def call(function, num):
    for _ in range(num):
        function()


class TestAnimation:
    def test_tick(self):
        a = animation.Animation([1, 2, 3, 5, 6, 7], 5)
        assert a.surf == 1
        call(a.tick, 5)
        assert a.surf == 1
        a.tick()
        assert a.surf == 2
        call(a.tick, 4)
        a.tick()
        assert a.surf == 3

    def test_cycle(self):
        a = animation.Animation([1, 2, 3, 5, 6, 7], 5)
        call(a.tick, 30)
        assert a.surf == 7
        a.tick()
        assert a.surf == 1

    def test_reset(self):
        a = animation.Animation([1, 2, 3, 5, 6, 7], 5)
        call(a.tick, 20)
        assert a.surf == 5
        a.reset()
        assert a.surf == 1


class TestAnimated:
    def test_key_function(self):
        c = 0

        def change_in_eleven():
            nonlocal c
            if c >= 11:
                return "another"
            c += 1
            return "original"

        animation_a = animation.Animation([1, 2, 3], 5)
        animation_b = animation.Animation([4, 5, 6], 5)
        a = animation.Animated(Bunch(original=animation_a, another=animation_b),
                               change_in_eleven, "original")
        assert a.surf == 1
        call(a.update, 5)
        assert a.surf == 1
        call(a.update, 5)
        assert a.surf == 2
        a.update()
        assert a.surf == 3
        a.update()  # 12th call
        assert a._current_key == "another"
        assert a.surf == 4

    def test_reset(self):
        animation_a = animation.Animation([1, 2, 3], 5)
        animation_b = animation.Animation([4, 5, 6], 5)
        key = "original"

        def get_key():
            return key
        a = animation.Animated(Bunch(original=animation_a, another=animation_b),
                               get_key, key)
        assert a.surf == 1
        call(a.update, 6)
        assert a.surf == 2
        key = "another"
        a.update()
        assert a.surf == 4
        key = "original"
        a.update()
        assert a.surf == 1
