"""
Utilities for the library, not all of the functions are suppose to be used
externally
"""
import pygame


def parse_config(raw_config):
    def collision_reader(s):
        """
        Config into a set of int.
        The config must be in the format of e,e,e....
        where e is either a single character, or a range that
        looks like *start...end*
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

    def extract_float(s):
        return float(s.strip())

    def parse_two_int(s):
        w, _, h = s.strip().partition(" ")
        return int(w), int(h)

    def parse_background(s):
        n, _, speed = s.strip().partition(" ")
        return [(n, int(speed))]

    def parse_exit(s):
        l = s.strip().split(" ")
        return l[0], l[1], l[2], l[3]

    processors = {"collision": collision_reader, "gravity": extract_float,
                  "resolution": parse_two_int,
                  "background": parse_background,
                  "exit": parse_exit,
                  "spawn": parse_two_int}
    # read the raw lines
    config = []
    for l in raw_config:
        name, _, value = l.partition(" ")
        config.append((name, value))
    # process everything
    processed_config = dict()
    for n, v in config:
        if n in processors:
            if n in processed_config:
                processed_config[n] = processed_config[n] + processors[n](v)
            else:
                processed_config[n] = processors[n](v)
    return processed_config


def set_alpha(surface, alpha):
    """
    Takes a surface with per-pixel transparency, then return a new one with
    a new alpha level. Setting a alpha higher than the original will not work.
    :param surface: original surface
    :param alpha: new alpha level
    :return: surface
    """
    new = surface.copy()
    new.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MIN)
    return new

if __name__ == "__main__":
    print(parse_config(["collision 1...7, 10, 12, 20...30"]))
    print(parse_config(["collision 1...7,10,12,20...30"]))
    print(parse_config(["background static 0", "background trees 15", "background mountains 5"]))