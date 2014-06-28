Level format
============

A level is a folder structure that contains the background, tile set and the landscape of the level.
For collision based levels, the structure will look like: ::

    tiles/
        1.png
        2.png
        3.png
        ...
        a.png
        b.png
        ...
    backgrounds/
        background1.jpg
        background2.jpg
        background3.jpg
        background4.jpg
    map


The simplest level must have the map file and one image file under the tiles folder.

Tiles images must be square and have consistent file extension. Background images must also have consistent file extension.

.. _map:

Format of *map*
---------------

A *map* file represents the landscape of the level and some of its property. It is consist of two
parts, a config portion and a data portion. The two is separated by an empty line

The config portion follows the following format:

    ``config_name config_value``
    
Here is the list of config names and their description:

.. _background:

* *collision*: The name of tiles that should collide with the player separated by ``","``.
  Each entry must be a single character or a range take looks like *"start...end"* where start start and end are both
  between 1 and 9 (inclusive)
* *gravity*: Downward acceleration of the player, in :math:`pixels/frame^2`
* *background*: Format of ``filename speed`` filename will match a file in the backgrounds folder, and the speed controls
  how fast the background moves. Multiple lines of this config can be specified, the backgrounds laid out in the order of
  the lines.
* *exit*: ``x y width height`` The specification of a rectangle that represent the exit area. All values are integers
* *spawn*: ``x y`` The spawn coordinate of the player, default is ``(0,0)``

*map* file must at least contain the *collision* config

The data portion of *map* are characters that each represent a tile in the level landscape. Their
value match the names of files under the *tiles* folder. Only numbers and alphabet characters are allowed. This limits
the maximum possible number of unique tile image to 61. (``0`` is used to represent empty) 

Working with the data portion of *map* as plain text can be very ineffective and time consuming.
To address this, Rapid Pygame provides a :doc:`level converter <level_converter>` that will convert to and
from `Tiled <http://www.mapeditor.org/>`_ map file.