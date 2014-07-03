"""
This example shows a simple way to implement constant game
speed. constant game speed separate the update of game logic
from rendering, allowing the game to happen at a constant
pace regardless of the fps, above or below the number of updates
per second.

Observe the speed of the square, then press c. Press c again then
press space, then c again.

Controls:
space - Toggle FPS limit of 200
c - Toggle constant game speed
"""
import pygame
from time import sleep

pygame.init()
d = pygame.display.set_mode((800, 600), pygame.HWSURFACE)
clock = pygame.time.Clock()
block = pygame.surface.Surface((100, 100))
block.fill(pygame.Color('#90EE90'))
UPDAE_CAPTION = pygame.USEREVENT + 1
UPDAE_GAME = pygame.USEREVENT + 2
pygame.time.set_timer(UPDAE_GAME, 10)
pygame.time.set_timer(UPDAE_CAPTION, 500)

coords = [200, 200]
fps = 0
constant_speed = True

def update_game():
    p = coords[0] + 1
    if p + 100 > 800:
        p -= 800 - 100
    coords[0] = p

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif e.type == UPDAE_CAPTION:
            pygame.display.set_caption("FPS: {0:0.2f}, constant game speed: {1}".
                format(clock.get_fps(), constant_speed))
        elif e.type == UPDAE_GAME and constant_speed:
            update_game()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            fps = 200 if fps == 0 else 0
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_c:
            constant_speed = not constant_speed
    if not constant_speed:
        update_game()
    d.fill(pygame.Color('black'))
    d.blit(block, coords)
    pygame.display.update()
    clock.tick(fps)