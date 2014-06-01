"""
 Rapid Pygame
 https://github.com/XrXr/RapidPygame
 License: MIT
 example for loading images
"""
import sys
import os
current_path = os.path.dirname(os.path.realpath(__file__))
# import from one level up
sys.path.append(os.path.split(current_path)[0])
import pygame
from rapidpg.loader.image import ImageLoader


pygame.init()
a = pygame.display.set_mode((150, 80))
loader = ImageLoader(os.path.join(current_path, "collision_level", "tiles"))
a.blit(loader.load_image(["meow", "1.png"]), (0, 0))  # loading an image within a folder
a.blit(loader.load_image(["1.png"]), (20, 0))  # loading an image from the origin
surfs = loader.load_frames([], 7)  # loading from the origin
surfs2 = loader.load_all([], True)  # same as above, except use convert_alpha and results in a dict
x = 0
for s in surfs:
    a.blit(s, (x, 30))
    x += 15

x = 0
for n in surfs2:
    a.blit(surfs2[n], (x, 50))
    x += 15
pygame.display.update()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit