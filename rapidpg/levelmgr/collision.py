#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
import pygame
from pygame.rect import Rect
from pygame import Surface
from os.path import join
from rapidpg.loader.image import ImageLoader
from .camera import Camera
import math
from ..utilities import parse_config


class Level:
    """
    Responsible for handling player movement
    and level related collision detection. The structure of a level can be found in
    *level format.md*
    """
    def __init__(self, config, data, tiles, backgrounds=None, player=None):
        """
        Contains the interpreted level and methods that should be called every frame
        to update the level. Also handle player movement. Since the interpreted level
        is exposed, the built in movement method doesn't have to be used.

        :param player: The player object to manipulate
        :param config: The config dict of the level
        :param data: The uninterpreted, but parsed level
        :param tiles: A dict of tile sets, mapping a name to a surface
        :param backgrounds: A dict of backgrounds, mapping a name to a surface

        .. py:attribute:: interpreted

            A list of rect representing the landscape of the level

        .. py:attribute:: draw_list

            A list of tuple of surfaces and rect. Drawing them with *Suface.blit*
            will show the level and the player
        """

        self.player = player
        self.config = config
        self.data = data
        self.tiles = tiles
        for k in tiles:
            self.tile_width = tiles[k].get_rect().width
            break

        self.level_height = len(self.data) * self.tile_width
        self.level_width = len(self.data[0]) * self.tile_width
        self.camera = Camera(self.config['resolution'],
                             Rect((0, 0), (self.level_width, self.level_height)),
                             player.speed)

        self.backgrounds = []
        if backgrounds:
            for name, speed in config['background']:
                surf = backgrounds[name]
                if speed:
                    surf = self._construct_background(surf)
                self.backgrounds.append([surf, surf.get_rect(), speed])

        self.interpreted, self.spawn, self.exits = self.interpret()
        self.player.rect.x, self.player.rect.y = self.spawn
        self.camera.snap_to(self.player.rect)

    def _get_draw_list(self):
        dl = []
        # backgrounds
        for surf, rect, _ in self.backgrounds:
            dl.append((surf, (rect.x, self.camera.rect.height - rect.height)))
        # landscape
        y = 0
        for l in self.data:
            x = 0
            for c in l:
                if c in ('0', 'e', 's'):
                    x += 1
                    continue
                dl.append((self.tiles[c],
                           (x * self.tile_width - self.camera.rect.x,
                            y * self.tile_width - self.camera.rect.y)))
                x += 1
            y += 1
        # player
        dl.append((self.player.surf,
                   self.player.rect.move(-self.camera.rect.x, -self.camera.rect.y)))
        return dl

    draw_list = property(_get_draw_list)

    def _construct_background(self, surf):
        width = 0
        surf_width = surf.get_width()
        while width < self.camera.rect.width:
            width += surf_width
        width *= 2
        constructed = Surface((width, surf.get_height()), pygame.SRCALPHA)
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


    def update(self, movement):
        """
        This method should be called every frame to update the location of
        the player and the environment

        :param movement: Dict with keys *up, down, left, right* mapping to booleans
        """
        m = []
        self.player.down_speed += self.config['gravity']
        inflated = self.player.rect.copy()
        inflated.height += self.player.down_speed
        # this method of collision testing will work for high speed,
        # unlike moving the rect
        collision_test = inflated.collidelistall(self.interpreted)
        block = False
        if collision_test:  # there are stuffs in there!
            closest_rect = Level.find_min([self.interpreted[x]
                                           for x in collision_test])
            delta = closest_rect.y - (self.player.rect.y +
                                      self.player.rect.height)
            self.player.move(0, delta)
            if self.player.jumping:
                block = True
            self.player.jumping = False
            self.player.down_speed = 0
            m.append(closest_rect)
        else:
            self.player.move(0, self.player.down_speed)

        if movement['up'] and not block:
            self.player.start_jump()
        if self.player.jumping:
            inflated = self.player.rect.move(0, -self.player.up_speed)
            inflated.height += self.player.up_speed
            collision_test = inflated.collidelistall(self.interpreted)
            if collision_test:  # when there are stuff in the list
                closest_rect = Level.find_max([self.interpreted[x]
                                               for x in collision_test])
                m.append(closest_rect)
                delta = math.fabs(self.player.rect.y -
                                  (closest_rect.y + closest_rect.height))
                self.player.move(0, -delta)
                self.player.jumping = False
            else:
                self.player.move(0, -self.player.up_speed)

        if movement['left']:
            collision_test = self.player.rect.move(-self.player.speed, 0). \
                collidelist(self.interpreted)
            if collision_test != -1:
                delta = math.fabs(self.player.rect.x -
                                 (self.interpreted[collision_test].x +
                                  self.interpreted[collision_test].width))
                self.player.move(-delta, 0)
                m.append(self.interpreted[collision_test])
            else:
                self._bg_right()
                self.player.move(-self.player.speed, 0)
            self.player.dir = 'left'

        if movement['right']:
            collision_test = self.player.rect.move(self.player.speed, 0). \
                collidelist(self.interpreted)
            if collision_test != -1:
                delta = math.fabs(self.interpreted[collision_test].x -
                                 (self.player.rect.x + self.player.rect.width))
                self.player.move(delta, 0)
                m.append(self.interpreted[collision_test])
            else:
                self._bg_left()
                self.player.move(self.player.speed, 0)
            self.player.dir = 'right'

        self.camera.update(self.player.rect)
        return m

    def fill_bottom(self):
        """
        .. warning::
            *Broken*

        Return a list of rects that fills all the space
        below the interpreted level
        """
        rect_list = []
        for l in range(len(self.data)):
            for c in range(len(self.data[l])):
                if self.data[l][c] is None:
                    height = 0
                    tmp_l = l
                    while True:
                        tmp_l += 1
                        try:
                            if self.data[tmp_l][c] == 'FILLED':
                                continue
                            else:
                                rect_list.append(
                                    Rect(c * self.tile_width, tmp_l
                                         * self.tile_width,
                                         self.tile_width,
                                         height * self.tile_width))
                                self.data[tmp_l][c] = 'FILLED'
                        except IndexError:
                            break
        return rect_list

    def get_dimensions(self):
        """
        Get the width and height of the level

        :return: (width, height)
        """
        return len(self.data[0]) * self.tile_width, \
            len(self.data) * self.tile_width

    def interpret(self):
        """
        Interpret a level.

        :return: Three tuple that looks like (rect_list, spawn, exits)
        """
        exit_char = 'e'
        spawn_char = 's'
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
        spawn = None
        exits = []
        for line in range(len(raw)):
            for char in range(len(raw[line])):
                #  +1 to line since the rect directly under a process
                #  rect would collide
                if Level._processed(char * self.tile_width,
                                    (line + 1) * self.tile_width, rect_list):
                    continue
                if raw[line][char] in collide_set:
                    tmp_char = char
                    width = 0
                    try:
                        lowest = float("inf")
                        while True:
                            try:
                                if raw[line][tmp_char] in collide_set:
                                    width += 1
                                    possible_height = 1
                                    tmp_line = line
                                    while True:  # go down
                                        try:
                                            tmp_line += 1
                                            if raw[tmp_line][tmp_char] in \
                                                    collide_set:
                                                possible_height += 1
                                            else:
                                                break
                                        except IndexError:
                                            break
                                    if possible_height < lowest:
                                        lowest = possible_height
                                else:
                                    break
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
                elif raw[line][char] == spawn_char:
                    spawn = (char * tile_width, line * tile_width)
                elif raw[line][char] == exit_char:
                    exits.append(Rect(char * tile_width, 0
                                      ,tile_width, level_height))
        return rect_list, spawn, exits

    @staticmethod
    def _processed(x, y, rect_list):
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
        """
        return self._get_current_level()

    def load_level(self, path):
        """
        Load a level relative to the origin

        :param path: Path to the level in list format
        :return: None
        """
        map_path = join(self.loader.get_path(path), "map")
        with open(map_path, 'r') as level_file:
            as_list = level_file.read().split("\n")
        separator = as_list.index("")
        config = parse_config(as_list[0:separator])
        data = LevelManager._parse_level(as_list[separator + 1:])
        tiles = self.loader.load_all(path + ["tiles"])
        backgrounds = self.loader.load_all(path + ["backgrounds"], True)
        self.levels.append(Level(config, data, tiles, player=self.player, backgrounds=backgrounds))

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

    current_level = property(_get_current_level)
    """Current level object"""

    @staticmethod
    def _parse_level(raw_level):
        level = []
        for l in raw_level:
            level.append([x for x in l.strip()])
        return level