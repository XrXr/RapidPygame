Working with level file
=======================

The map file used for the :doc:`collision level manager <levelmgr>` in Rapid Pygame is a very simple tile map. While the format
is easy to understand, it is not easy for editing in a text editor. To make designing level easy and fast, Rapid Pygame provides
an utility that converts to and from native *.tmx* `Tiled`_ map file. Since `Tiled`_ is well established and easy to use, using it
for level editing should be painless and effective.

Using the converter
-------------------

The converter can be executed using ``python -m rapidpg *file*`` *file* is required and points to either a Tiled map file(.tmx)
or a Rapid Pygame :ref:`map` file. The data encoding of the Tiled file must be *CSV*. When converting from Rapid Pygame to
Tiled, the Rapid Pygame map must also have its tile images in the *tiles* folder in the same directory

There are extra options outlined in ``python -m rapidpg -h``

Formatting of Tiled map file
----------------------------

While all Tiled map file with *CSV* data encoding will convert successfully into a :ref:`map <map>` file, the level might not be
handled correctly by the :doc:`collision level manager <levelmgr>`. The layers in the Tiled file must be structured as follows.
Order is important.

For clarity, each item is formatted as ``<layer name> <layer type> <description>``

* Control *Object*

    This layer is optional and can have a up to 2 unique objects, the objects must be rectangles and with type *exit* or *spawn*.
    Their location and/or size will be converted into the *exit* and *spawn* config field of the Rapid Pygame :ref:`map <map>`
    
* map *Tile*

    The landscape of the level. If more than 9 tile images are used, the converter assumes the name of the tile images are
    alphabet letters. The 10th tile is converted into ``a`` and continues following alphabetical order. When lower case letters
    run out, upper case is used. The maximum number of unique tile images is 61
    
* ``<background name> <speed>`` *Image*

    A background layer, multiple of these can exist for making parallax effect. The name is in the exact format of the
    :ref:`background <background>` config field. The order they will be rendered is bottom to top.
    
Extra config fields can be specified by editing *map properties*. (:menuselection:`Map --> Map properties...`)
Layers that reflect a config field such as the ``Control`` layer are prioritized over these fields when there is a conflict.
When the ``Collision`` field is unspecified, all tiles are marked as collidable 

Accuracy of conversion
----------------------

If a well-formed map is converted to the other format and back, the level should remain the same; the files before and after might
not be identical, as the order of the config fields might be changed.


.. _Tiled: http://www.mapeditor.org/