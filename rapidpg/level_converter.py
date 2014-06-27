#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
"""
Command line tool for converting level file into Tiled map file or vise versa
Made to make tile map editing painless
"""
import argparse
from os.path import dirname, basename, abspath
import pygame
from . import ImageLoader
from .utilities import parse_config
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from string import ascii_letters
from math import ceil


def convert():
    parser = argparse.ArgumentParser(
        prog="Rapid Pygame level converter",
        description="""Convert Rapid Pygame level
                       file into Tiled map file or vise versa""",
        epilog="Refer to the documentation specifics about the formats")
    parser.add_argument("file", metavar="file", type=str,
                        help="the Rapid Pygame level file or Tiled map file to convert")
    parser.add_argument("-o", "--output", metavar="result", type=str,
                        help="the name of the converted file")
    parser.add_argument("--per-line", metavar="n", type=int,
                        default=10,
                        help="the number of tile images per line "
                             "when generating tile set for Tiled. Default is 10")

    args = parser.parse_args()
    try:
        # Tiled to Rapid Pygame
        tree = ET.parse(args.file)
        lvl = tree.find("layer/data").text.strip() + ","
        lvl = [x for x in lvl.split("\n")]
        result = ""
        # there can only be 61 different tiles in a given map. Should be enough
        characters = set()
        max_tile = 0
        for l in lvl:
            for c in l.strip()[:-1].split(","):
                as_int = int(c)
                final_c = c
                if as_int > 9:
                    final_c = ascii_letters[as_int - 10]
                if as_int > max_tile:
                    max_tile = as_int
                result += final_c
                characters.add(final_c)
            result += "\n"
        # take out the new line at the end
        result = result[:-1]

        header = ""
        has_collision = False
        for e in tree.findall("properties/property"):
            header += "{0} {1}\n".format(e.get("name"), e.get("value"))
            if e.get("name") == "collision":
                has_collision = True
        spawn_node = tree.find("objectgroup/object[@type='spawn']")
        if spawn_node is not None:
            header += "spawn {0} {1}\n".format(spawn_node.get("x"),
                                               spawn_node.get("y"))
        exit_node = tree.find("objectgroup/object[@type='exit']")
        if exit_node is not None:
            header += "exit {0} {1} {2} {3}\n".format(exit_node.get("x"),
                                                      exit_node.get("y"),
                                                      exit_node.get("width"),
                                                      exit_node.get("height"))
        for e in tree.findall("imagelayer"):
            header += "background {0}\n".format(e.get("name"))
        # enable collision for all tiles by default
        if not has_collision and max_tile > 0:
            cl = "1"
            if max_tile > 1:
                cl = "1..." + str(min(9, max_tile))
            # if max_tile is less than 10, nothing will happen
            for i in range(10, max_tile + 1):
                cl += "," + ascii_letters[i - 10]
        result = header + "\n" + result
        file_name = basename(args.file).split(".")[0]
        if args.output:
            file_name = args.output
        with open(file_name, "w") as f:
            f.write(result)
        print('Conversion finished, wrote to "{0}"'.format(file_name))
        raise SystemExit
    except ParseError:
        # Rapid Pygame to Tiled
        # these configs are reflected in the map, not as properties
        excluded_configs = ["background", "exit", "spawn"]
        loader = ImageLoader(dirname(abspath(args.file)))
        pygame.display.init()
        try:
            tiles = loader.load_all(["tiles"], raw=True)
        except FileNotFoundError:
            print("CONVERSION FAILED:", 'Tile images not found in "tiles" folder where the map file is located')
            raise SystemExit
        if len(tiles.values()) == 0:
            print("CONVERSION FAILED:", 'Tile images not found in "tiles" folder where the map file is located')
            raise SystemExit
        # generate tile set
        order = sorted(tiles.keys())
        tile_width = tiles[order[0]].get_width()
        width = tile_width * min(args.per_line, len(order))
        height = ceil(len(order) / args.per_line) * tile_width
        tile_set_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for c in range(len(order)):
            x = c % args.per_line * tile_width
            y = c // args.per_line * tile_width
            tile_set_surf.blit(tiles[order[c]], (x, y))
        file_name = basename(args.file)
        if args.output:
            file_name = args.output
        pygame.image.save(tile_set_surf, file_name + ".png")

        # parse level
        with open(args.file, "r") as level_file:
            as_list = level_file.read().split("\n")
        separator = as_list.index("")
        raw_config = as_list[:separator]
        data = as_list[separator + 1:]
        level = []
        for l in data:
            level.append([x if x.isdecimal() else str(ascii_letters.find(x) + 10)
                         for x in l.strip()])
        # build Tiled XML
        level_width = str(len(level[0]))
        level_height = str(len(level))
        root = ET.Element("map")
        root.set("version", "1.0")
        root.set("orientation", "orthogonal")
        root.set("width", str(level_width))
        root.set("height", str(level_height))
        root.set("tilewidth", str(tile_width))
        root.set("tileheight", str(tile_width))
        # save the original config of the level into the Tiled map
        properties = ET.SubElement(root, "properties")
        background_config = []
        for l in raw_config:
            name, value = l.split(" ", 1)
            if name not in excluded_configs:
                ET.SubElement(properties, "property", name=name, value=value)
                continue
            if name == "background":
                background_config.append(l)
        for l in background_config:
            _, value = l.split(" ", 1)
            ET.SubElement(root, "imagelayer", {
                "name": value,
                "width": level_width,
                "height": level_height
            })
        tile_set = ET.SubElement(root, "tileset", {
            "firstgid": "1",
            "name": file_name,
            "tilewidth": str(tile_width),
            "tileheight": str(tile_width)
        })
        ET.SubElement(tile_set, "image", {
            "source": file_name + ".png",
            "width": str(width),
            "height": str(height)
        })
        layer = ET.SubElement(root, "layer", {
            "name": file_name,
            "width": str(level_width),
            "height": str(level_height)
        })

        csv = ""
        for l in level:
            csv += ",".join(l) + ",\n"
        csv = csv[:-2]

        ET.SubElement(layer, "data", encoding="csv").text = csv
        config = parse_config(raw_config)
        if "exit" in config or "spawn" in config:
            control_layer = ET.SubElement(root, "objectgroup", name="Controls",
                                          width=level_width, height=level_height)
            if "exit" in config:
                x, y, w, h = config["exit"]
                ET.SubElement(control_layer, "object", {
                    "type": "exit",
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                })
            if "spawn" in config:
                x, y = config["spawn"]
                ET.SubElement(control_layer, "object", {
                    "type": "spawn",
                    "x": x,
                    "y": y
                })
        ET.ElementTree(root).write(file_name + ".tmx", encoding="UTF-8",
                                   xml_declaration=True)
        print('Conversion finished, wrote to "{0}" and "{1}"'.format(file_name + ".png", file_name + ".tmx"))

if __name__ == "__main__":
    convert()