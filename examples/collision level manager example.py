"""
 Rapid Pygame
 https://github.com/XrXr/RapidPygame
 License: MIT
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
level_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "collision_level")
mgr = LevelManager(level_path, None)
mgr.load_level([])
mgr.next_level()
for rect in mgr.current_level.interpreted:
    color = (randrange(0, 256), randrange(0, 256), randrange(0, 256))
    a.fill(pygame.Color(color[0], color[1], color[2]), rect)
pygame.display.update()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit