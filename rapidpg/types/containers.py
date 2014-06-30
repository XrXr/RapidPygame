#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT


class Bunch:
    """
    Class courtesy of Alex Martelli. A lot of the time a static dict is used to
    represent a *Bunch*, which is an object with a fixed number of attributes.
    using *dict* for the representation introduces overhead and minimize the
    optimization done by CPython. Note that obj.*__dict__* is represented differently
    internally than a regular *dict* object. Using *Bunch* also allow for cleaner
    syntax.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)