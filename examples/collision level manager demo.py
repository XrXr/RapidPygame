#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
"""
This demo is made to showcase how the collision level manager interprets
the level into rectangles.
"""
import sys
import os
from random import randrange

current_path = os.path.dirname(os.path.realpath(__file__))
# import from one level up
sys.path.append(os.path.split(current_path)[0])
import pygame
from rapidpg.levelmgr.collision import LevelManager

pygame.init()
a = pygame.display.set_mode((800, 600))
mgr = LevelManager(current_path, None)
mgr.load_level(["collision_level"])
mgr.next_level()
for rect in mgr.current_level.interpreted:
    color = (randrange(0, 256), randrange(0, 256), randrange(0, 256))
    a.fill(pygame.Color(color[0], color[1], color[2]), rect)

for rect in mgr.current_level.exits:
    color = (randrange(0, 256), randrange(0, 256), randrange(0, 256))
    a.fill(pygame.Color(color[0], color[1], color[2]), rect)
pygame.display.update()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit