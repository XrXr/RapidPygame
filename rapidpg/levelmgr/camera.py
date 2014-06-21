#  Rapid Pygame
#  https://github.com/XrXr/RapidPygame
#  License: MIT
import pygame


class Camera:
    """
    Class for keeping track of the camera position. In early stage of development
    """
    def __init__(self, screen_res, level_rect, x_speed=15, y_speed=15,
                 left_threshold=10, right_threshold=75, up_threshold=10,
                 down_threshold=75):
        """

        :param screen_res: A tuple of int. (w, h)
        :param level_rect: A rectangle that covers all of the level
        :param x_speed: The horizontal speed of the camera
        :param y_speed: The vertical speed of the camera
        :param left_threshold:
            The percentage of screen to reach in order for the camera to scroll
            left
        :param right_threshold:
            The percentage of screen to reach in order for the camera to scroll
            right
        :param up_threshold:
            The percentage of screen to reach in order for the camera to scroll
            up
        :param down_threshold:
            The percentage of screen to reach in order for the camera to scroll
            down
        """
        self.level_rect = level_rect
        self.horizontal_speed = x_speed
        self.vertical_speed = y_speed
        self.screen_res = screen_res
        self.rect = pygame.Rect((0, 0), screen_res)

        self.x_bound = self.level_rect.width - self.rect.width
        self.y_bound = self.level_rect.height - self.rect.height

        self.right_threshold = self.rect.width * right_threshold / 100
        self.left_threshold = self.rect.width * left_threshold / 100
        self.up_threshold = self.rect.height * up_threshold / 100
        self.down_threshold = self.rect.height * down_threshold / 100

    def pan_left(self):
        if self.rect.x == 0:
            return
        if self.rect.move(-self.horizontal_speed, 0).x < 0:
            self.rect.move_ip(-self.rect.x, 0)
        else:
            self.rect.move_ip(-self.horizontal_speed, 0)

    def pan_right(self):
        if self.rect.x == self.x_bound:
            return
        if self.rect.x + self.horizontal_speed + self.rect.width > self.level_rect.width:
            self.rect.move_ip((self.level_rect.width - (self.rect.x + self.rect.width)), 0)
        else:
            self.rect.move_ip(self.horizontal_speed, 0)

    def pan_down(self):
        if self.rect.y == self.y_bound:
            return
        if self.rect.y + self.vertical_speed + self.rect.height > self.level_rect.height:
            self.rect.move_ip(0, (self.level_rect.height - self.rect.y - self.rect.height))
        else:
            self.rect.move_ip(0, self.vertical_speed)

    def pan_up(self):
        if self.rect.y == 0:
            return
        if self.rect.move(0, -self.vertical_speed).y < 0:
            self.rect.move_ip(0, -self.rect.y)
        else:
            self.rect.move_ip(0, -self.vertical_speed)

    def snap_to(self, player_rect):
        propose = self.rect.move(0, 0)
        propose.x = min(max(0, player_rect.x - self.screen_res[0] / 2), self.x_bound)
        propose.y = min(max(0, player_rect.y - self.screen_res[1] / 2), self.y_bound)
        self.rect = propose

    def update(self, player_rect):
        if player_rect.x - self.rect.x > self.right_threshold:
            self.pan_right()
        elif player_rect.x - self.rect.x < self.left_threshold:
            self.pan_left()
        if player_rect.y - self.rect.y > self.down_threshold:
            self.pan_down()
        elif player_rect.y - self.rect.y < self.up_threshold:
            self.pan_up()