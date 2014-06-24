#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
import os
from os.path import join, isfile, splitext
from pygame.image import load


class ImageLoader:
    """
    Convenient class for loading images using relative path painless
    """
    def __init__(self, origin):
        """
        Create a loader pointing at the *origin*. Any loading is relative to the *origin*
        Paths passed to the methods of this object are lists where each element is either
        a directory name or a file name. ([dir1,dir2,file.txt])

        :param origin: path string
        """
        self.origin = origin

    def load_image(self, path, convert_alpha=False):
        """
        Load an image file

        :param path: Path to the image in list format
        :param convert_alpha: *boolean* convert surfaces with convert_alpha()
        :return: surface
        """
        if convert_alpha:
            return load(self.get_path(path)).convert_alpha()
        return load(self.get_path(path)).convert()

    def load_all(self, path, convert_alpha=False, no_convert=False):
        """
        Load all files in a directory. Assume they are all images.

        :param path: Path to a directory
        :param convert_alpha: *boolean* convert surfaces with convert_alpha()
        :return: Dict mapping the striped filename to its surface
        """
        result = dict()
        dir_path = self.get_path(path)
        for name in os.listdir(dir_path):
            file_path = join(dir_path, name)
            if isfile(file_path):
                striped = splitext(name)[0]
                if convert_alpha:
                    result[striped] = load(file_path).convert_alpha()
                    continue
                if no_convert:
                    result[striped] = load(file_path)
                    continue
                result[striped] = load(file_path).convert()
        return result

    def load_frames(self, path, frames, convert_alpha=False):
        """
        Load a sequence of image named 1.b...*frames*.b from *path*

        :param path: Path in list format pointing to a directory
        :param frames: Number of frames to load
        :param convert_alpha: *boolean* convert surfaces with convert_alpha()
        :return: a list of surfaces
        """
        dir_path = self.get_path(path)
        extension = ""
        for name in os.listdir(dir_path):
            file = join(dir_path, name)
            if isfile(file):
                striped, file_ext = splitext(name)
                if striped == "1":
                    extension = file_ext
                    break
        surfs = []
        for c in range(1, frames + 1):
            file = join(dir_path, str(c) + extension)
            if convert_alpha:
                surfs.append(load(file).convert_alpha())
                continue
            surfs.append(load(file).convert())
        return surfs

    def get_path(self, path):
        """
        Returns a path string relative to the origin

        :param path: a path in list format
        :return: path string
        """
        return join(self.origin, *path)