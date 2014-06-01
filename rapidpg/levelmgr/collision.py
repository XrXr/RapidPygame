"""
 Rapid Pygame
 https://github.com/XrXr/RapidPygame
 License: MIT
"""
from pygame.rect import Rect
from os.path import join
from rapidpg.loader.image import ImageLoader
from copy import deepcopy


class Level:
    """
    Responsible for handling player movement
    and level related collision detection. The structure of a level can be found in
    *level format.md*
    """
    def __init__(self, player, config, data, tiles, background=None):
        """
        Contains the interpreted level and methods that should be called every frame
        to update the level. Also handle player movement.
        :param player: The player object to manipulate
        :param config: The config dict of the level
        :param data: The uninterpreted, but parsed level
        :param tiles: A dict of tile sets, mapping their name to a surface
        :param background: A list of backgrounds, can be None
        """
        self.player = player
        self.config = config
        self.data = data
        # making a copy since interpreting a level is destructive
        # and the original is needed for drawing
        self.map = deepcopy(data)
        self.tiles = tiles
        self.background = background
        for k in tiles:
            self.tile_width = tiles[k].get_rect().width
            break
        self.interpreted, self.spawn, self.exits = self.interpret()

    def fill_bottom(self):
        """
        return a list of rects that fills all the space below the interpreted level
        Destructive
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
                                rect_list.append(Rect(c * self.tile_width, tmp_l * self.tile_width,
                                                      self.tile_width, height * self.tile_width))
                                self.data[tmp_l][c] = 'FILLED'
                        except IndexError:
                            break
        return rect_list

    def get_dimensions(self):
        return len(self.data[0]) * self.tile_width, len(self.data) * self.tile_width

    def interpret(self):
        """
        Interpret a level. Destructive.
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
                #  +1 to line since the rect directly under a process rect would collide
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
                                            if raw[tmp_line][tmp_char] in collide_set:
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
                    rect_list.append(Rect(char * tile_width, line * tile_width,
                                          width * tile_width, height * tile_width))
                elif raw[line][char] == exit_char:
                    spawn = (char * tile_width, line * tile_width)
                elif raw[line][char] == spawn_char:
                    exits.append(Rect(char * tile_width, 0, tile_width, level_height))
        return rect_list, spawn, exits

    @staticmethod
    def _processed(x, y, rect_list):
        for rect in rect_list:
            if rect.x <= x <= rect.x + rect.width and \
               rect.y <= y <= rect.y + rect.height:
                return True
        return False


class LevelManager:
    """
    Load and manage levels.
    """
    def __init__(self, origin, player):
        """
        Takes a path to the level file and the player object to manipulate
        :param origin: *string* origin of loading
        :param player: An instance of a class that implement the Player interface
        :return:
        """
        self.player = player
        self.levels = []
        self._current_level = -1
        self.tile_width = 0
        self.loader = ImageLoader(origin)

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
        config = LevelManager._parse_config(as_list[0:separator])
        data = LevelManager._parse_level(as_list[separator + 1:])
        tiles = self.loader.load_all(path + ["tiles"])
        self.levels.append(Level(self.player, config, data, tiles))

    def next_level(self):
        if len(self.levels) >= self._current_level + 1:
            self._current_level += 1
            return True
        return False

    def previous_level(self):
        if self._current_level - 1 >= 0:
            self._current_level -= 1
            return True
        return False

    def _get_current_level(self):
        return self.levels[self._current_level]

    current_level = property(_get_current_level)

    @staticmethod
    def _parse_config(raw_config):
        def collision_reader(s):
            """
            Config into a set of int.
            The config must be in the format of e,e,e....
            where e is either a single character, or a range that is looks like *start...end*
            the range is inclusive
            """
            as_list = s.split(",")
            as_list = [x.strip() for x in as_list]
            result = set()
            for e in as_list:
                if "..." in e:
                    start, _, end = e.partition("...")
                    for c in range(int(start), int(end) + 1):
                        result.add(str(c))
                else:
                    result.add(e)
            return result

        processors = {"collision": collision_reader}
        config = dict()
        # populate dict
        for l in raw_config:
            name, _, value = l.partition(" ")
            config[name] = value
        # process everything
        for n, v in config.items():
            if n in processors:
                config[n] = processors[n](v)
        return config

    @staticmethod
    def _parse_level(raw_level):
        level = []
        for l in raw_level:
            level.append([x for x in l.strip()])
        return level

if __name__ == "__main__":
    print(LevelManager._parse_config(["collision 1...7, 10, 12, 20...30"]))
    print(LevelManager._parse_config(["collision 1...7,10,12,20...30"]))