#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
from itertools import cycle


class Player():
    """
    An instance is compatible with the level manager. Note that if
    :func:`rapidpg.levelmgr.collision.Level.update` is not used, a player
    instance doesn't have to be passed to the level manager
    """
    def __init__(self, surfs, interval):
        """
        :param surfs: A list of surfaces for animation
        :param interval: The interval between animation updates
        """
        self.jump_frames_left = 0
        self.jumping = False
        self.in_air = False
        self.up_speed = 20
        self.down_speed = 0
        self.dir = 'right'
        self.surfs = surfs
        self.rect = surfs[0].get_rect()
        self.animation_interval = interval
        self.speed = 10
        self._frames_since_last = 0
        self._frame_cycle = cycle(range(len(surfs)))
        self._current_frame = self._frame_cycle.__next__()

    def _get_surf(self):
        self._frames_since_last += 1
        if self._frames_since_last == self.animation_interval:
            self._frames_since_last = 0
            self._current_frame = self._frame_cycle.__next__()
        return self.surfs[self._current_frame]

    def move(self, x, y):
        """
        Alias for *plr.rect.move_ip*
        :return:
        """
        self.rect.move_ip(x, y)

    def start_jump(self):
        if not self.jumping:
            self.jumping = True
            self.in_air = True

    def jump_progress(self, landed=False):
        if landed:
            self.jumping = False

    #: The player's current surface. Note that every time this
    #: attribute is accessed, next frame in the animation is brought closer
    surf = property(_get_surf)