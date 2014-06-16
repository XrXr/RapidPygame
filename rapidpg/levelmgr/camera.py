#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
import pygame


class Camera:
    """
    Class for keeping track of the camera position. In early stage of development
    """
    def __init__(self, screen_res, level_rect, x_speed=15, y_speed=30):
        self.level_rect = level_rect
        self.left_threshold = 10  # in percentage
        self.right_threshold = 75  # in percentage
        self.horizontal_speed = x_speed
        self.vertical_speed = y_speed
        self.screen_res = screen_res
        self.rect = pygame.Rect((0, 0), screen_res)

        self.right_threshold = self.rect.width * self.right_threshold / 100
        self.left_threshold = self.rect.width * self.left_threshold / 100

    def pan_left(self):
        if self.rect.move(-self.horizontal_speed, 0).x < 0:
            self.rect.move_ip(-self.rect.x, 0)
        else:
            self.rect.move_ip(-self.horizontal_speed, 0)

    def pan_right(self):
        if self.rect.x + self.horizontal_speed + self.rect.width > self.level_rect.width:
            self.rect.move_ip((self.level_rect.width - (self.rect.x + self.rect.width)), 0)
        else:
            self.rect.move_ip(self.horizontal_speed, 0)

    def snap_to(self, player_rect):
        propose = self.rect.move(0, 0)
        propose.x = max(0, player_rect.x - self.screen_res[0] / 2)
        propose.y = max(0, player_rect.y - self.screen_res[1] / 2)
        self.rect = propose

    def update(self, player_rect):
        if player_rect.x - self.rect.x > self.right_threshold:
            self.pan_right()
        elif player_rect.x - self.rect.x < self.left_threshold:
            self.pan_left()