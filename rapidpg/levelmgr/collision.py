#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
from pygame import SRCALPHA
from pygame.rect import Rect
from pygame import Surface
from os.path import join
from rapidpg.loader.image import ImageLoader
from .camera import Camera
from ..types.player import Player
import math
from ..utilities import parse_config
from ..types.animation import Animation


class Level:
    """
    Responsible for handling player movement
    and level related collision detection. The structure of a level can be found in
    :doc:`level_format`
    """
    def __init__(self, config, data, tiles, backgrounds=None, player=None,
                 animations=tuple()):
        """
        Contains the interpreted level and methods that should be called every frame
        to update the level. Also handle player movement. Since the interpreted level
        is exposed, the built in movement method doesn't have to be used. The movement
        methods can be overridden by a child class to achieve a different movement
        effect. Note that if the child class has a different constructor,
        the :class:`LevelManager` will have to be sub classed as well.

        :param player: The player object to manipulate
        :param config: The config dict of the level
        :param data: The uninterpreted, but parsed level
        :param tiles: A dict of tile sets, mapping a name to a surface
        :param [Animation] animations: A list of animations that is shown in the background
        :param backgrounds: A dict of backgrounds, mapping a name to a surface
        :param [[Surface]] animation:
        """
        dummy_player = Player([], 0)
        dummy_player.speed = 0
        self.player = player if player else dummy_player
        self.config = config
        self.data = data
        self.tiles = tiles
        self.animations = animations
        for k in tiles:
            self.tile_width = tiles[k].get_rect().width
            break

        self.level_height = len(self.data) * self.tile_width
        self.level_width = len(self.data[0]) * self.tile_width
        self.camera = None
        self.camera = Camera(self.config['resolution'],
                             Rect((0, 0), (self.level_width,
                                           self.level_height)),
                             self.player.speed)

        self.backgrounds = []
        if backgrounds:
            for name, speed in config['background']:
                surf = backgrounds[name]
                if speed:
                    surf = self._construct_background(surf)
                self.backgrounds.append([surf, surf.get_rect(), speed])
        #: A list of rects that should collide with the player, see :func:`interpret`
        print("interpreting")
        self.interpreted = self.interpret()
        print("interpreting finished")
        #: Spawn point of the player ``(x, y)``
        self.spawn = 0, 0
        #: Exit of the level. ``(x, y)`` None if unspecified in the level
        self.exit = None
        if 'spawn' in config:
            self.spawn = config['spawn']
        if 'exit' in config:
            self.exit = Rect(*config['exit'])

        self.player.rect.x, self.player.rect.y = self.spawn
        self.camera.snap_to(self.player.rect)

    def get_animation_draw_list(self):
        dl = []
        for animation, point in self.animations:
            dl.append((animation.surf, (point[0] - self.camera.rect.x, point[1] - self.camera.rect.y)))
        return dl

    def get_background_draw_list(self):
        dl = []
        for surf, rect, _ in self.backgrounds:
            dl.append((surf, (rect.x, self.camera.rect.height - rect.height)))
        return dl

    def get_player_draw_tuple(self):
        return (self.player.surf,
                self.player.rect.move(-self.camera.rect.x, -self.camera.rect.y))


    def _get_draw_list(self):
        dl = []
        # backgrounds
        for surf, rect, _ in self.backgrounds:
            dl.append((surf, (rect.x, self.camera.rect.height - rect.height)))
        # animations
        for animation, point in self.animations:
            dl.append((animation.surf, (point[0] - self.camera.rect.x, point[1] - self.camera.rect.y)))

        cam_x = self.camera.rect.x
        cam_top_right = cam_x + self.camera.rect.width
        cam_y = self.camera.rect.y
        cam_bottom = cam_y + self.camera.rect.height
        # landscape
        for y in range(math.floor(cam_y / self.tile_width),
                       math.floor(cam_bottom / self.tile_width)):
            for x in range(math.floor(cam_x / self.tile_width),
                           math.floor(cam_top_right / self.tile_width)):
                try:
                    self.data[y][x]
                except IndexError:
                    print("x is ", x, "y is", y, "y length", len(self.data), "x length", len(self.data[0]))
                    print(cam_x, cam_y)
                if self.data[y][x] is '0':
                    continue
                dl.append((self.tiles[self.data[y][x]],
                          (x * self.tile_width - self.camera.rect.x,
                           y * self.tile_width - self.camera.rect.y)))


        # y = 0
        # for l in self.data:
        #     x = 0
        #     # if y < cam_y or y > cam_bottom:
        #     #     y += 1
        #     #     continue
        #     for c in l:
        #         if c is '0':
        #             x += 1
        #             continue
        #         # if x < cam_x or x > cam_top_right:
        #         #     x += 1
        #         #     continue
        #         dl.append((self.tiles[c],
        #                    (x * self.tile_width - self.camera.rect.x,
        #                     y * self.tile_width - self.camera.rect.y)))
        #         x += 1
        #     y += 1
        # player
        dl.append((self.player.surf,
                   self.player.rect.move(-self.camera.rect.x, -self.camera.rect.y)))
        return dl

    #: A list of tuples, that are ``(surface, rect)``. Drawing the whole list
    #: with ``display_surf.blit(*level.draw_list)`` will draw
    #: the background, level, and player
    draw_list = property(_get_draw_list)

    def _construct_background(self, surf):
        width = 0
        surf_width = surf.get_width()
        while width < self.camera.rect.width:
            width += surf_width
        width *= 2
        constructed = Surface((width, surf.get_height()), SRCALPHA)
        x = 0
        while x < width:
            constructed.blit(surf, (x, 0))
            x += surf_width
        return constructed

    def _bg_left(self):
        for _, rect, speed in self.backgrounds:
            if rect.move(-speed, 0).x < -rect.width / 2:
                rect.x = 0
            rect.move_ip(-speed, 0)

    def _bg_right(self):
        for _, rect, speed in self.backgrounds:
            if rect.move(speed, 0).x > 0:
                rect.x = -rect.width / 2
            rect.move_ip(speed, 0)

    def _gravity(self):
        """
        This method is called every update cycle to simulate gravity.
        Override this method to produce different behavior
        """
        self.player.down_speed += self.config['gravity']
        inflated = self.player.rect.copy()
        inflated.height += self.player.down_speed
        # this method of collision testing will work for high speed,
        # unlike moving the rect
        collision_test = inflated.collidelistall(self.interpreted)
        final = self.player.down_speed
        if collision_test:  # there are stuffs in there!
            closest_rect = Level.find_min([self.interpreted[x]
                                           for x in collision_test])
            delta = closest_rect.y - (self.player.rect.y +
                                      self.player.rect.height)
            self.player.move(0, delta)
            self.player.jumping = False
            self.player.down_speed = 0
            final = delta
        else:
            self.player.move(0, self.player.down_speed)
        return final

    def _jump_condition(self, movement):
        """
        This method is called to decide when a jump is possible

        :param: movement: The movement dict forwarded from :func:`update()`
        :rtype: bool
        """
        return movement['up'] and self.player.down_speed is 0

    def _jump_action(self):
        """
        Called by :func:`update()` when :func:`_is_jumping()` returns true
        """
        inflated = self.player.rect.move(0, -self.player.up_speed)
        inflated.height += self.player.up_speed
        collision_test = inflated.collidelistall(self.interpreted)
        if collision_test:  # when there are stuff in the list
            closest_rect = Level.find_max([self.interpreted[x]
                                           for x in collision_test])
            delta = math.fabs(self.player.rect.y -
                              (closest_rect.y + closest_rect.height))
            self.player.move(0, -delta)
            self.player.jumping = False
        else:
            self.player.move(0, -self.player.up_speed)

    def _left_action(self):
        """
        Called by :func:`update()` when left is held
        """
        collision_test = self.player.rect.move(-self.player.speed, 0). \
            collidelist(self.interpreted)
        final = -self.player.speed
        if collision_test != -1:
            delta = math.fabs(self.player.rect.x -
                              (self.interpreted[collision_test].x +
                               self.interpreted[collision_test].width))
            self.player.move(-delta, 0)
            final = delta
        else:
            self._bg_right()
            self.player.move(-self.player.speed, 0)
        self.player.dir = 'left'
        return final

    def _right_action(self):
        """
        Called by :func:`update()` when right is held
        """
        collision_test = self.player.rect.move(self.player.speed, 0). \
            collidelist(self.interpreted)
        final = self.player.speed
        if collision_test != -1:
            delta = math.fabs(self.interpreted[collision_test].x -
                              (self.player.rect.x + self.player.rect.width))
            self.player.move(delta, 0)
            final = delta
        else:
            self._bg_left()
            self.player.move(self.player.speed, 0)
        self.player.dir = 'right'
        return final

    def update(self, movement):
        """
        This method should be called every frame to update the location of
        the player and the environment. :class:`Player`'s :func:`start_jump` and
        :attr:`jumping` is used to start the jump and check if a jump is in progress,
        respectively.

        :param movement: Dict with keys *up, down, left, right* mapping to booleans
        """
        gravity = self._gravity()
        left = 0
        right = 0

        if self._jump_condition(movement):
            self.player.start_jump()

        if self.player.jumping:
            self._jump_action()

        if movement['left']:
            left = self._left_action()

        if movement['right']:
            right = self._right_action()

        left = abs(left)
        right = abs(right)
        gravity = abs(gravity)
        v_sum = (left + right, gravity)

        for a in self.animations:
            a[0].update()
        self.player.update()
        self.camera.update(self.player.rect, custom_speed=v_sum)

    def get_dimensions(self):
        """
        Get the width and height of the level

        :return: (width, height)
        """
        return len(self.data[0]) * self.tile_width, \
            len(self.data) * self.tile_width

    def interpret(self):
        """
        Interpret the level, breaking it down into a list of rect
        that should collide with the player. Whether a tile collides
        with the player or not is specified in the level file. See
        :doc:`level_format` for more details

        :return: A list of rects
        :rtype: [Rect]
        """
        rect_list = []
        raw = self.data
        tile_width = self.tile_width
        collide_set = self.config['collision']
        level_height = len(raw) * tile_width
        level_width = len(raw[0]) * tile_width
        # these are rects that surround the level
        rect_list += [Rect(-100, 0, 100, level_height),
                      Rect(0, -100, level_width, 100),
                      Rect(0, level_height, level_width, 100),
                      Rect(level_width, 0, 100, level_height)]
        for line in range(len(raw)):
            for char in range(len(raw[line])):
                #  +1 to line since the rect directly under a process
                #  rect would collide
                if Level._is_processed(char * self.tile_width,
                                      (line + 1) * self.tile_width, rect_list):
                    continue
                if raw[line][char] in collide_set:
                    tmp_char = char
                    width = 0
                    try:
                        lowest = float("inf")
                        while True:
                            try:
                                if raw[line][tmp_char] not in collide_set:
                                    break
                                width += 1
                                possible_height = 1
                                tmp_line = line
                                while True:  # go down
                                    try:
                                        tmp_line += 1
                                        if raw[tmp_line][tmp_char] not in \
                                                collide_set:
                                            break
                                        possible_height += 1
                                    except IndexError:
                                        break
                                if possible_height < lowest:
                                    lowest = possible_height
                                tmp_char += 1
                            except IndexError:
                                break
                    except IndexError:
                        pass
                    height = lowest if lowest != float("inf") else 1
                    rect_list.append(
                        Rect(char * tile_width, line * tile_width,
                             width * tile_width,
                             height * tile_width))
        return rect_list

    @staticmethod
    def _is_processed(x, y, rect_list):
        for rect in rect_list:
            if rect.x <= x <= rect.x + rect.width and \
               rect.y <= y <= rect.y + rect.height:
                return True
        return False

    @staticmethod
    def find_max(rect_list):
        """
        Find the rect with the largest y in the rect_list
        """
        max_y = rect_list[0].y
        max_rect = rect_list[0]
        for e in rect_list:
            if e.y > max_y:
                max_y = e.y
                max_rect = e
        return max_rect

    @staticmethod
    def find_min(rect_list):
        """
        Find the rect with the lowest y in the rect_list
        """
        min_y = rect_list[0].y
        min_rect = rect_list[0]
        for e in rect_list:
            if e.y < min_y:
                min_y = e.y
                min_rect = e
        return min_rect


class LevelManager:
    """
    Load and manage levels.
    """
    def __init__(self, origin, player=None):
        """
        Takes a path to the level file and the player object to manipulate

        :param origin: *string* origin of loading
        :param player: An instance of a class that has a rect property
        """
        self.player = player
        self.levels = []
        self._current_level = -1
        self.loader = ImageLoader(origin)

    def __call__(self):
        """
        A shortcut for level_manager.current_level
        :rtype: Level
        """
        return self._get_current_level()

    def load_level(self, path):
        """
        Load a level relative to the origin

        :param path: Path to the level in list format
        """
        map_path = join(self.loader.get_path(path), "map")
        with open(map_path, 'r') as level_file:
            as_list = level_file.read().split("\n")
        separator = as_list.index("")
        config = parse_config(as_list[0:separator])
        data = LevelManager._parse_level(as_list[separator + 1:])
        tiles = self.loader.load_all(path + ["tiles"], True)
        backgrounds = self.loader.load_all(path + ["backgrounds"], True)
        animations = []
        if 'animations' in config:
            for folder, interval, x, y in config['animations']:
                surfs = self.loader.load_all_frames(path + ["animations", folder], True)
                animations.append((Animation(surfs, interval), (x, y)))
        self.levels.append(Level(config, data, tiles, player=self.player,
                                 backgrounds=backgrounds, animations=animations))

    def next_level(self):
        """
        Advance current_level
        """
        if len(self.levels) >= self._current_level + 1:
            self._current_level += 1
            return True
        return False

    def previous_level(self):
        """
        Set current_level to the previous level
        """
        if self._current_level - 1 >= 0:
            self._current_level -= 1
            return True
        return False

    def _get_current_level(self):
        """
        :rtype: Level
        """
        return self.levels[self._current_level]

    #: Current level object, set by using :func:`next_level` and :func:`previous_level`
    current_level = property(_get_current_level)

    @staticmethod
    def _parse_level(raw_level):
        level = []
        for l in raw_level:
            level.append([x for x in l.strip()])
        return level