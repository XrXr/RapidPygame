#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
"""
Command line tool for converting level file into Tiled map file or vise versa
Made to make tile map editing painless
"""
import sys
import os
current_path = os.path.dirname(os.path.realpath(__file__))
# import from one level up
sys.path.append(os.path.split(current_path)[0])
import argparse
from rapidpg import ImageLoader
import pygame
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from string import ascii_letters
from os.path import basename
from math import ceil

parser = argparse.ArgumentParser(
    description="""Convert Rapid Pygame level
                   file into Tiled map file or vise versa""",
    epilog="Only single layered Tiled map file is supported")
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
    # there can only be 62 different tiles in a given map. Should be enough
    characters = set()
    result = ""
    for l in lvl:
        for c in l[:-1].split(","):
            final_c = c
            if int(c) > 9:
                final_c = ascii_letters[int(c) - 10]
            result += final_c
            characters.add(final_c)
        result += "\n"
    # mark all tiles as collidable
    result = "collision " + ",".join(characters) + "\n\n" + result
    # take out the new line at the end
    result = result[:-1]
    file_name = basename(args.file).split(".")[0]
    if args.output:
        file_name = args.output
    with open(file_name, "a") as f:
        f.write(result)
    print('Conversion finished, wrote to "{0}"'.format(file_name))
    raise SystemExit
except ParseError:
    # Rapid Pygame to Tiled
    loader = ImageLoader(os.path.dirname(os.path.abspath(args.file)))
    pygame.display.init()
    try:
        tiles = loader.load_all(["tiles"], no_convert=True)
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
    data = as_list[separator + 1:]
    level = []
    for l in data:
        level.append([x if x.isdecimal() else str(ascii_letters.find(x) + 10)
                     for x in l.strip()])
    result = ""
    for l in level:
        result += ",".join(l) + ","
    result = result[:-1]
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
    ET.SubElement(layer, "data", encoding="csv").text = result
    ET.ElementTree(root).write(file_name + ".tmx", encoding="UTF-8",
                               xml_declaration=True)
    print('Conversion finished, wrote to "{0}" and "{1}"'.format(file_name + ".png", file_name + ".tmx"))