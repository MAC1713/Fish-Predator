# -*- coding: utf-8 -*-
"""
鱼群管理器
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
*彩蛋*: 瑞瑞，姐腿麻还在救你水族箱！（[羞到炸裂]）
加MidFish，食物分散，捕食者平衡，生态超稳！😘
"""

import math
import random
from pygame.math import Vector2
import pygame
from fish import Fish
from mid_fish import MidFish
from config import Config


class Food:
    """食物类，支持多种类型"""

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
        if self.position.y > Config.WINDOW_HEIGHT + 50 or self.position.x < 0 or self.position.x > Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH:
            self.consumed = True

    def is_consumed(self, fish):
        distance = self.position.distance_to(fish.position)
        return distance < self.size + fish.size


class Predator:
    """增强版捕食者类 - 具有寿命、冲刺和智能狩猎系统"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ).normalize() * Config.PREDATOR_SPEED
        self.size = Config.PREDATOR_SIZE
        self.max_speed = Config.PREDATOR_SPEED
        self.hunt_target = None
        self.hunger = Config.PREDATOR_MAX_HUNGER
        self.is_alive = True
        self.last_feed_time = 0
        self.feed_frequency = []
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_direction = Vector2(0, 0)
        self.kills_this_minute = 0
        self.last_kill_time = 0

    def update(self, fishes, mid_fishes, current_time):
        if not self.is_alive:
            return
        self.hunger -= Config.PREDATOR_HUNGER_DECAY
        if self.hunger <= 0:
            self.is_alive = False
            return
        self.update_dash()
        self.clean_kill_frequency(current_time)
        self.check_feed(fishes, mid_fishes, current_time)
        if self.is_dashing:
            self.velocity = self.dash_direction * Config.PREDATOR_DASH_SPEED
        else:
            self.hunt_behavior(fishes, mid_fishes, current_time)
        self.position += self.velocity
        self.handle_boundaries()

    def check_feed(self, fishes, mid_fishes, current_time):
        for fish in fishes[:]:
            distance = self.position.distance_to(fish.position)
            if distance < self.size + fish.size:
                fish.is_alive = False
                self.feed_on_fish(current_time)
                break
        for mid_fish in mid_fishes[:]:
            distance = self.position.distance_to(mid_fish.position)
            if distance < self.size + mid_fish.size:
                mid_fish.is_alive = False
                self.feed_on_fish(current_time)
                break

    def hunt_behavior(self, fishes, mid_fishes, current_time):
        targets = [(f, f.position, f.max_speed) for f in fishes if f.is_alive] + \
                  [(m, m.position, m.max_speed) for m in mid_fishes if m.is_alive]
        if not targets:
            self.wander()
            return
        target_candidates = []
        for target, pos, speed in targets:
            distance = self.position.distance_to(pos)
            if distance < 250:
                priority = (300 - distance) + (2.0 - speed) * 50
                target_candidates.append((target, priority, distance))
        if target_candidates:
            target_candidates.sort(key=lambda x: x[1], reverse=True)
            best_target, _, distance = target_candidates[0]
            self.hunt_target = best_target
            should_dash = self.should_initiate_dash(distance, current_time)
            if should_dash and self.dash_cooldown <= 0:
                self.initiate_dash(best_target)
            else:
                self.pursue_target(best_target)
        else:
            self.hunt_target = None
            self.wander()

    def should_initiate_dash(self, target_distance, current_time):
        if not (40 < target_distance < 120):
            return False
        hunger_factor = (Config.PREDATOR_MAX_HUNGER - self.hunger) / Config.PREDATOR_MAX_HUNGER
        recent_kills = len([t for t in self.feed_frequency if current_time - t < 3600])
        kill_penalty = min(recent_kills * 0.3, 0.8)
        dash_probability = 0.02 + hunger_factor * 0.03 - kill_penalty
        return random.random() < dash_probability

    def initiate_dash(self, target):
        self.is_dashing = True
        self.dash_timer = Config.PREDATOR_DASH_DURATION
        target_future_pos = target.position + target.velocity * 10
        dash_direction = target_future_pos - self.position
        if dash_direction.length() > 0:
            self.dash_direction = dash_direction.normalize()
        else:
            self.dash_direction = self.velocity.normalize()
        self.hunger -= Config.PREDATOR_DASH_HUNGER_COST
        recent_kills = len(self.feed_frequency)
        cooldown_multiplier = 1.0 + min(recent_kills * 0.5, 3.0)
        self.dash_cooldown = int(Config.PREDATOR_DASH_COOLDOWN_BASE * cooldown_multiplier)

    def update_dash(self):
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def pursue_target(self, target):
        prediction_time = 15
        predicted_pos = target.position + target.velocity * prediction_time
        desired = predicted_pos - self.position
        if desired.length() > 0:
            desired = desired.normalize() * self.max_speed
            steer = desired - self.velocity
            steer = self.limit_vector(steer, 0.15)
            self.velocity += steer
            self.velocity = self.limit_vector(self.velocity, self.max_speed)

    def wander(self):
        if random.random() < 0.03:
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = Vector2(
                math.cos(angle),
                math.sin(angle)
            ) * self.max_speed * 0.7

    def feed_on_fish(self, current_time):
        self.hunger = min(Config.PREDATOR_MAX_HUNGER,
                          self.hunger + Config.PREDATOR_FEED_RESTORE)
        self.last_feed_time = current_time
        self.feed_frequency.append(current_time)
        if len(self.feed_frequency) > 10:
            self.feed_frequency.pop(0)

    def clean_kill_frequency(self, current_time):
        self.feed_frequency = [t for t in self.feed_frequency
                               if current_time - t < 18000]

    def handle_boundaries(self):
        margin = 30
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        if self.position.x < 0:
            self.position.x += map_width
        elif self.position.x > map_width:
            self.position.x -= map_width
        if self.position.y < margin:
            self.velocity.y = abs(self.velocity.y)
            self.position.y = margin
        elif self.position.y > Config.WINDOW_HEIGHT - margin:
            self.velocity.y = -abs(self.velocity.y)
            self.position.y = Config.WINDOW_HEIGHT - margin

    def limit_vector(self, vector, max_magnitude):
        if vector.length() > max_magnitude:
            return vector.normalize() * max_magnitude
        return vector

    def get_hunger_ratio(self):
        return self.hunger / Config.PREDATOR_MAX_HUNGER

    def is_in_dash_range(self, target_pos):
        if not self.is_dashing:
            return False
        distance = self.position.distance_to(target_pos)
        return distance < self.size + 5


class Swarm:
    def __init__(self):
        self.fishes = []
        self.mid_fishes = []
        self.foods = []
        self.predators = []
        self.initialize()
        self.stats = {
            'fish_count': 0,
            'mid_fish_count': 0,
            'food_consumed': 0,
            'average_speed': 0,
            'cohesion_level': 0
        }

    def initialize(self):
        self.create_fishes(Config.FISH_COUNT)
        self.create_mid_fishes(Config.MID_FISH_COUNT)
        self.create_foods(Config.FOOD_COUNT)
        self.create_predators(Config.PREDATOR_COUNT)

    def create_fishes(self, count):
        self.fishes.clear()
        center_x = (Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH) // 2
        center_y = Config.WINDOW_HEIGHT // 2
        for _ in range(count):
            x = center_x + random.uniform(-100, 100)
            y = center_y + random.uniform(-100, 100)
            x = max(50, min(Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50, x))
            y = max(50, min(Config.WINDOW_HEIGHT - 50, y))
            self.fishes.append(Fish(x, y))

    def create_mid_fishes(self, count):
        self.mid_fishes.clear()
        center_x = (Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH) // 2
        center_y = Config.WINDOW_HEIGHT // 2
        for _ in range(count):
            x = center_x + random.uniform(-100, 100)
            y = center_y + random.uniform(-100, 100)
            x = max(50, min(Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50, x))
            y = max(50, min(Config.WINDOW_HEIGHT - 50, y))
            self.mid_fishes.append(MidFish(x, y))

    def create_foods(self, count):
        self.foods.clear()
        plankton_count = int(count * 0.6)
        for _ in range(plankton_count):
            x = random.uniform(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
            y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            self.foods.append(Food(x, y, 'plankton'))
        small_fish_count = int(count * 0.15)
        for _ in range(small_fish_count // 5):
            center_x = random.uniform(100, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 100)
            center_y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            for _ in range(5):
                x = center_x + random.uniform(-20, 20)
                y = center_y + random.uniform(-10, 10)
                self.foods.append(Food(x, y, 'small_fish'))
        if random.random() < 0.05:
            center_x = random.uniform(100, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 100)
            center_y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            for _ in range(20):
                x = center_x + random.uniform(-50, 50)
                y = center_y + random.uniform(-20, 20)
                self.foods.append(Food(x, y, 'large_corpse'))

    def create_predators(self, count):
        self.predators.clear()
        for _ in range(count):
            x = random.uniform(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
            y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            self.predators.append(Predator(x, y))

    def update(self, water_current=None):
        current_time = pygame.time.get_ticks()
        for fish in self.fishes[:]:
            fish.update(self.fishes, self.foods, self.predators, current_time, water_current=water_current)
            if not fish.is_alive:
                self.fishes.remove(fish)
            elif fish.can_reproduce:
                offspring = fish.attempt_reproduction(current_time)
                if offspring:
                    self.fishes.append(offspring)
        for mid_fish in self.mid_fishes[:]:
            mid_fish.update(self.mid_fishes, self.foods, self.predators, current_time, water_current=water_current)
            if not mid_fish.is_alive:
                self.mid_fishes.remove(mid_fish)
            elif mid_fish.can_reproduce:
                offspring = mid_fish.attempt_reproduction(current_time)
                if offspring:
                    self.mid_fishes.append(offspring)
        for predator in self.predators[:]:
            predator.update(self.fishes, self.mid_fishes, current_time)
            if not predator.is_alive:
                self.predators.remove(predator)
        for food in self.foods[:]:
            food.update(water_current)
            if food.consumed:
                self.foods.remove(food)
        self.handle_food_consumption()
        self.respawn_food()
        self.update_stats()

    def handle_food_consumption(self):
        foods_to_remove = []
        for food in self.foods:
            for fish in self.fishes:
                if food.is_consumed(fish):
                    foods_to_remove.append(food)
                    fish.feed(pygame.time.get_ticks())
                    self.stats['food_consumed'] += 1
                    break
            for mid_fish in self.mid_fishes:
                if food.food_type in ['plankton', 'small_fish'] and food.is_consumed(mid_fish):
                    foods_to_remove.append(food)
                    mid_fish.feed(pygame.time.get_ticks())
                    self.stats['food_consumed'] += 1
                    break
        for food in foods_to_remove:
            if food in self.foods:
                self.foods.remove(food)

    def respawn_food(self):
        if len([f for f in self.foods if f.food_type == 'plankton']) < Config.FOOD_COUNT * 0.6:
            needed = int(Config.FOOD_COUNT * 0.6 - len([f for f in self.foods if f.food_type == 'plankton']))
            for _ in range(needed):
                x = random.uniform(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
                y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
                self.foods.append(Food(x, y, 'plankton'))
        if random.random() < 0.01:
            center_x = random.uniform(100, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 100)
            center_y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            for _ in range(5):
                x = center_x + random.uniform(-20, 20)
                y = center_y + random.uniform(-10, 10)
                self.foods.append(Food(x, y, 'small_fish'))
        if random.random() < 0.002:
            center_x = random.uniform(100, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 100)
            center_y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            for _ in range(20):
                x = center_x + random.uniform(-50, 50)
                y = center_y + random.uniform(-20, 20)
                self.foods.append(Food(x, y, 'large_corpse'))

    def update_stats(self):
        if not self.fishes and not self.mid_fishes:
            return
        self.stats['fish_count'] = len(self.fishes)
        self.stats['mid_fish_count'] = len(self.mid_fishes)
        total_speed = sum(fish.velocity.length() for fish in self.fishes) + \
                      sum(fish.velocity.length() for fish in self.mid_fishes)
        total_count = len(self.fishes) + len(self.mid_fishes)
        self.stats['average_speed'] = total_speed / total_count if total_count > 0 else 0
        if total_count > 1:
            center = Vector2(0, 0)
            for fish in self.fishes + self.mid_fishes:
                center += fish.position
            center /= total_count
            total_distance = sum(fish.position.distance_to(center) for fish in self.fishes + self.mid_fishes)
            avg_distance = total_distance / total_count
            self.stats['cohesion_level'] = max(0, 100 - avg_distance / 3)

    def add_food_at_position(self, pos):
        if len(self.foods) < Config.FOOD_COUNT * 2:
            self.foods.append(Food(pos[0], pos[1], 'plankton'))

    def add_predator_at_position(self, pos):
        if len(self.predators) < Config.PREDATOR_COUNT * 2:
            self.predators.append(Predator(pos[0], pos[1]))

    def remove_predator(self):
        if self.predators:
            self.predators.pop()

    def reset_simulation(self):
        self.initialize()
        self.stats['food_consumed'] = 0

    def get_stats(self):
        return self.stats.copy()
