class Animation:
    """
    Store surfaces needed for animation and keep track of
    the current frame in the animation
    """
    def __init__(self, surfs, interval):
        """
        :param sequence surfs: The sequence of Surfaces in the animation
        :param int interval: The number of :func:`update` calls between
            switching to the next frame
        """
        self._current_frame = 0
        self._since_last = 0
        self._highest_index = len(surfs) - 1
        self._surfs = tuple(surfs)
        self._interval = interval

    def _advance(self):
        propose = self._current_frame + 1
        if propose > self._highest_index:
            self._current_frame = 0
            return
        self._current_frame = propose

    def _due(self):
        return self._since_last == self._interval

    def _get_current_surface(self):
        return self._surfs[self._current_frame]

    def tick(self):
        """
        Call this to advance the animation. When *interval* is 5
        for the first 5 calls, surf will not change, on the 6th call
        surf is switched to the next frame
        """
        if self._due():
            self._since_last = 0
            self._advance()
        self._since_last += 1

    def reset(self):
        """
        Reset the animation to the first frame and reset the
        number of :func:`tick` calls needed to switch to the next frame
        """
        self._since_last = 0
        self._current_frame = 0

    surf = property(_get_current_surface)


class Animated:
    """
    An animated object consisted of many animations.
    Manage when to switch between animations and which
    animation to update.
    """
    def __init__(self, grouping, key_function, initial_key, reset_when_switch=True):
        """
        :param dict grouping: A dict that maps key to :class:`Animation`
        :param function key_function: A function that decides which animation is to be displayed
        :param str initial_key: The key to use before any calls to the *key_function*
        :param reset_when_switch: Whether the animation should reset to the first frame
            when a switch happens
        """
        self._grouping = grouping
        self._get_key = key_function
        self._current_key = initial_key
        self._reset = reset_when_switch

    def _get_current_surface(self):
            return self._grouping[self._current_key].surf

    def update(self):
        """
        Call to advance the animation, or switch to another
        group of animation when the return value of :func:`key_function`
        is changed.
        """
        key = self._get_key()
        if self._reset:
            if key != self._current_key and self._current_key is not None:
                self._grouping[self._current_key].reset()
        self._current_key = key
        self._grouping[self._current_key].tick()

    def reset(self):
        """
        Call the :func:`Animation.reset` function of the current animation
        """
        self._grouping[self._current_key].reset()


    surf = property(_get_current_surface)