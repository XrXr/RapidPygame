#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
"""
Command line tool for converting level file into Tiled map file or vise versa
Made to make tile map editing painless
"""
import argparse
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from string import ascii_letters
from os.path import basename

parser = argparse.ArgumentParser(
    description="""Convert Rapid Pygame level
                   file into Tiled map file or vise versa""",
    epilog="Only single layered Tiled map file is supported")
parser.add_argument("file", metavar="file", type=str,
                    help="the Rapid Pygame level file or Tiled map file to convert")
parser.add_argument("-o", "--output", metavar="result", type=str,
                    help="the name of the converted file")
parser.add_argument("-w", "--width", metavar="width", type=int,
                    help="the tile width. This argument is required for \
                          converting from Rapid Pygame level to Tiled map file")

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
except ParseError:
    # Rapid Pygame to Tiled
    if not args.width:
        raise RuntimeError("Tile Width not specified")
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

    width = str(len(level[0]))
    height = str(len(level))
    root = ET.Element("map")
    root.set("version", "1.0")
    root.set("orientation", "orthogonal")
    root.set("width", width)
    root.set("height", height)
    root.set("tilewidth", str(args.width))
    root.set("tileheight", str(args.width))
    tile_set = ET.SubElement(root, "tileset", {
        "firstgid": "1",
        "name": "Untitled",
        "tilewidth": str(args.width),
        "tileheight": str(args.width)
    })
    ET.SubElement(tile_set, "image", {
        "source": basename(args.file) + ".png",
        "width": "cat",  # TODO: fill this
        "height": "cat"
    })
    layer = ET.SubElement(root, "layer", {
        "name": basename(args.file),
        "width": width,
        "height": height
    })
    ET.SubElement(layer, "data", encoding="csv").text = result
    ET.ElementTree(root).write(args.file + ".tmx", encoding="UTF-8",
                               xml_declaration=True)