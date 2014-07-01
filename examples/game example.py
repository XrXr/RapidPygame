#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
import sys
import os

current_path = os.path.dirname(os.path.realpath(__file__))
# import from one level up
sys.path.append(os.path.split(current_path)[0])
import pygame
from rapidpg import ImageLoader
from rapidpg.levelmgr.collision import LevelManager
from rapidpg import Player

pygame.init()
a = pygame.display.set_mode((800, 600))
loader = ImageLoader(current_path)
surfs = loader.load_frames(["geometry"], 4, True)  # load player images
geometry = Player(surfs, 50)  # make player
manager = LevelManager(current_path, geometry)
manager.load_level(["collision_level"])  # load level
manager.next_level()
clock = pygame.time.Clock()

movement_dict = {"up": False, "down": False, "left": False, "right": False}
up_released = True
while True:
    movement_dict['up'] = False
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP and up_released:
                movement_dict['up'] = True
                up_released = False
            if e.key == pygame.K_DOWN:
                movement_dict['down'] = True
            if e.key == pygame.K_LEFT:
                movement_dict['left'] = True
            if e.key == pygame.K_RIGHT:
                movement_dict['right'] = True
        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_UP:
                up_released = True
            if e.key == pygame.K_DOWN:
                movement_dict['down'] = False
            if e.key == pygame.K_LEFT:
                movement_dict['left'] = False
            if e.key == pygame.K_RIGHT:
                movement_dict['right'] = False
    a.fill(pygame.Color('black'))
    v = manager.current_level.update(movement_dict)
    for e in manager().draw_list:  # same thing as manager.current_level.draw_list
        a.blit(*e)
    # for e in v:
    # a.fill(pygame.Color("red"), e)
    clock.tick(60)
    pygame.display.update()