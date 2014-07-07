#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
from .animation import Animated, Animation
from pygame.rect import Rect

class Player(Animated):
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
        super(Player, self).__init__({"right": Animation(surfs, interval)},
                                     lambda: "right", "right")
        self.jump_frames_left = 0
        self.jumping = False
        self.in_air = False
        self.up_speed = 20
        self.down_speed = 0
        self.dir = 'right'
        self.surfs = surfs
        self.rect = Rect(0, 0, 0, 0)
        if surfs:
            self.rect = surfs[0].get_rect()
        self.animation_interval = interval
        self.speed = 7

    def move(self, x, y):
        """
        Alias for ``plr.rect.move_ip``
        """
        self.rect.move_ip(x, y)

    def start_jump(self):
        if not self.jumping:
            self.jumping = True
            self.in_air = True

    def jump_progress(self, landed=False):
        if landed:
            self.jumping = False