import random

import pygame
from pygame.math import Vector2

from config import Config


class Food:
    """食物类，支持多种类型，参数从balancer动态获取"""

    def __init__(self, x, y, food_type='plankton'):
        self.position = Vector2(x, y)
        self.food_type = food_type
        self.consumed = False
        self.spawn_time = pygame.time.get_ticks()
        if food_type == 'plankton':
            self.size = Config.FOOD_SIZE * 0.5
            self.energy = 10
            self.velocity = Vector2(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
        elif food_type == 'small_fish':
            self.size = Config.FOOD_SIZE * 0.8
            self.energy = 50
            self.velocity = Vector2(0, 0.2)
        elif food_type == 'large_corpse':
            self.size = Config.FOOD_SIZE
            self.energy = 100
            self.velocity = Vector2(0, 0.1)

    def update(self, water_current=None):
        if self.food_type == 'plankton' and water_current:
            self.position += water_current * 0.05
        elif self.food_type in ['small_fish', 'large_corpse']:
            self.position += self.velocity
        if (self.position.y > Config.WINDOW_HEIGHT + 50 or
                self.position.x < 0 or
                self.position.x > Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH):
            self.consumed = True

    def is_consumed(self, fish):
        distance = self.position.distance_to(fish.position)
        return distance < self.size + fish.size

