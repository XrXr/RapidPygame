##Basics
A level is a folder structure that contains the background, tile set and the landscape of the level.
For collision based levels, the structure will look like:

```
tiles/
    1.png
    2.png
    3.png
    ...
map
background
```

The simplest level must have the map file and one image file under the tiles folder.

Tiles images must be square and have consistent file extension.

##Format of _map_
A _map_ file represents the landscape of the level and some of its property. It is consist of two
parts, a config portion and a data portion. The two is separated by an empty line

The config portion follows the following format:
    `config_name config_value`
Here is the list of config names and their description:

 - _collision_: The name of tiles that should collide with the player separated by ",".
  Each entry must be a single character or a range take looks like _"start...end"_ where start start and end are both
  between 1 and 10 (inclusive)
    
the simplest _map_ file must contain a _collision_ config

The data portion of _map_ are characters that each represent a tile in the level landscape. Their
value match the names of files under the _tiles_ folder. _e_ is used to indicate the exit of a level