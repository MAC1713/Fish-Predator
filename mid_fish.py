# -*- coding: utf-8 -*-
"""
中型鱼类
作者: 星瑶 (Nova) ♥
*彩蛋*: 瑞瑞，姐给你加了中型鱼，生态超有戏！（[得意炸裂]）
吃浮游和小鱼，被大鱼吃，游得优雅又带感！😘
"""

import math
import random
import pygame
from config import Config


class MidFish:
    def __init__(self, x, y, parent_age=0):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ).normalize() * Config.MID_FISH_SPEED
        self.acceleration = pygame.math.Vector2(0, 0)
        self.age = 0
        self.last_breed_time = 0
        self.can_reproduce = False
        self.last_feed_time = 0
        self.is_alive = True
        age_factor = min(parent_age * 0.001, 0.3)
        base_speed_variation = random.uniform(0.7, 1.3)
        age_bonus = age_factor * 0.5
        self.max_speed = Config.MID_FISH_SPEED * (base_speed_variation + age_bonus)
        self.max_force = 0.06 + age_factor * 0.02
        self.size = Config.MID_FISH_SIZE * random.uniform(0.8, 1.2)
        self.experience = 0
        self.panic_resistance = age_factor * 0.3
        self.trail = []
        self.color_offset = random.uniform(0, 360)
        self.fear_level = 0
        self.target_food = None
        self.energy = 100 + random.randint(-20, 20)
        self.is_mature = False

    def update(self, mid_fishes, foods=None, predators=None, current_time=0, day_night_factor=1.0, water_current=None):
        if not self.is_alive:
            return
        self.age += 1
        if self.age > Config.FISH_REPRODUCTION_AGE * 1.5:
            self.is_mature = True
            self.can_reproduce = (current_time - self.last_breed_time) > Config.FISH_BREED_COOLDOWN * 1.5
        if predators and any(self.position.distance_to(p.position) < 120 for p in predators if p.is_alive):
            self.experience += 0.1
        else:
            self.experience += 0.01
        self.acceleration *= 0
        cohesion_multiplier = 1.0 + (1.0 - day_night_factor) * Config.NIGHT_COHESION_BONUS
        speed_multiplier = day_night_factor * Config.NIGHT_SPEED_REDUCTION + (1.0 - Config.NIGHT_SPEED_REDUCTION)
        sep = self.separate(mid_fishes) * Config.SEPARATION_WEIGHT
        ali = self.align(mid_fishes) * Config.ALIGNMENT_WEIGHT
        coh = self.cohesion(mid_fishes) * Config.COHESION_WEIGHT * cohesion_multiplier
        wan = self.wander() * Config.WANDER_WEIGHT
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)
        self.apply_force(wan)
        if water_current:
            current_force = water_current * Config.CURRENT_STRENGTH
            self.apply_force(current_force)
        if foods:
            food_force = self.seek_food(foods)
            self.apply_force(food_force * Config.FOOD_WEIGHT)
        if predators:
            escape_force = self.flee_from_predators(predators)
            experience_multiplier = 1.0 + min(self.experience * 0.1, 0.5)
            self.apply_force(escape_force * Config.MID_FISH_ESCAPE_WEIGHT * experience_multiplier)
        self.handle_boundaries()
        self.velocity += self.acceleration
        max_speed = self.max_speed * speed_multiplier
        self.velocity = self.limit_vector(self.velocity, max_speed)
        self.position += self.velocity
        self.update_trail()
        fear_recovery = 0.02 + self.panic_resistance * 0.01
        self.fear_level = max(0, self.fear_level - fear_recovery)

    def attempt_reproduction(self, current_time):
        if not self.can_reproduce or not self.is_mature or not self.is_alive:
            return None
        if random.random() < Config.FISH_NATURAL_BREED_CHANCE:
            return self.create_offspring(current_time)
        if current_time - self.last_feed_time < 300:
            if random.random() < Config.FISH_FOOD_BREED_CHANCE:
                return self.create_offspring(current_time)
        return None

    def create_offspring(self, current_time):
        self.last_breed_time = current_time
        offset_x = random.uniform(-30, 30)
        offset_y = random.uniform(-30, 30)
        offspring_x = self.position.x + offset_x
        offspring_y = self.position.y + offset_y
        return MidFish(offspring_x, offspring_y, self.age)

    def feed(self, current_time):
        self.energy = min(150, self.energy + 25)
        self.last_feed_time = current_time

    def flee_from_predators(self, predators):
        flee_force = pygame.math.Vector2(0, 0)
        for predator in predators:
            if not predator.is_alive:
                continue
            distance = self.position.distance_to(predator.position)
            detection_range = Config.MID_FISH_ESCAPE_RADIUS + self.experience * 10
            if distance < detection_range:
                escape_dir = self.position - predator.position
                if escape_dir.length() > 0:
                    escape_dir = escape_dir.normalize()
                    force_magnitude = (detection_range - distance) / detection_range
                    if predator.is_dashing:
                        force_magnitude *= 2.0
                        self.fear_level = min(1.0, self.fear_level + 0.2)
                    flee_force += escape_dir * force_magnitude * 2.5
        return self.limit_vector(flee_force, self.max_force * 3)

    def handle_boundaries(self):
        force = pygame.math.Vector2(0, 0)
        margin = 50
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH

        # 左右边界：循环
        if self.position.x < 0:
            self.position.x += map_width
        elif self.position.x > map_width:
            self.position.x -= map_width

        # 上下边界：反弹
        if self.position.y < margin:
            force.y = Config.BOUNDARY_FORCE
        elif self.position.y > Config.WINDOW_HEIGHT - margin:
            force.y = -Config.BOUNDARY_FORCE

        self.apply_force(force)

    def separate(self, mid_fishes):
        desired_separation = Config.SEPARATION_RADIUS * 1.5
        steer = pygame.math.Vector2(0, 0)
        count = 0
        for fish in mid_fishes:
            distance = self.position.distance_to(fish.position)
            if 0 < distance < desired_separation:
                diff = self.position - fish.position
                diff = diff.normalize()
                diff /= distance
                steer += diff
                count += 1
        if count > 0:
            steer /= count
            steer = steer.normalize() * self.max_speed
            steer -= self.velocity
            steer = self.limit_vector(steer, self.max_force)
        return steer

    def align(self, mid_fishes):
        neighbor_dist = Config.ALIGNMENT_RADIUS * 1.5
        sum_velocity = pygame.math.Vector2(0, 0)
        count = 0
        for fish in mid_fishes:
            distance = self.position.distance_to(fish.position)
            if 0 < distance < neighbor_dist:
                sum_velocity += fish.velocity
                count += 1
        if count > 0:
            sum_velocity /= count
            sum_velocity = sum_velocity.normalize() * self.max_speed
            steer = sum_velocity - self.velocity
            steer = self.limit_vector(steer, self.max_force)
            return steer
        return pygame.math.Vector2(0, 0)

    def cohesion(self, mid_fishes):
        neighbor_dist = Config.COHESION_RADIUS * 1.5
        sum_position = pygame.math.Vector2(0, 0)
        count = 0
        for fish in mid_fishes:
            distance = self.position.distance_to(fish.position)
            if 0 < distance < neighbor_dist:
                sum_position += fish.position
                count += 1
        if count > 0:
            sum_position /= count
            return self.seek(sum_position)
        return pygame.math.Vector2(0, 0)

    def seek(self, target):
        desired = target - self.position
        desired = desired.normalize() * self.max_speed
        steer = desired - self.velocity
        steer = self.limit_vector(steer, self.max_force)
        return steer

    def wander(self):
        wander_angle = random.uniform(-0.3, 0.3)
        desired = pygame.math.Vector2(
            math.cos(wander_angle),
            math.sin(wander_angle)
        ) * self.max_speed * 0.5
        steer = desired - self.velocity
        steer = self.limit_vector(steer, self.max_force * 0.3)
        return steer

    def seek_food(self, foods):
        if not foods:
            return pygame.math.Vector2(0, 0)
        closest_food = None
        min_distance = Config.FOOD_ATTRACTION * 1.5
        for food in foods:
            if food.food_type in ['plankton', 'small_fish']:
                distance = self.position.distance_to(food.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_food = food
        if closest_food:
            self.target_food = closest_food
            return self.seek(closest_food.position)
        return pygame.math.Vector2(0, 0)

    def apply_force(self, force):
        self.acceleration += force

    def limit_vector(self, vector, max_magnitude):
        if vector.length() > max_magnitude:
            return vector.normalize() * max_magnitude
        return vector

    def update_trail(self):
        self.trail.append(self.position.copy())
        if len(self.trail) > Config.TRAIL_LENGTH:
            self.trail.pop(0)

    def get_color(self):
        base_color = Config.COLORS['mid_fish_body']
        if self.fear_level > 0:
            fear_intensity = self.fear_level * 255
            return (
                min(255, base_color[0] + fear_intensity),
                max(0, base_color[1] - fear_intensity // 2),
                max(0, base_color[2] - fear_intensity // 2)
            )
        time_offset = pygame.time.get_ticks() * 0.002 + self.color_offset
        color_variation = math.sin(time_offset) * 30
        return (
            max(0, min(255, base_color[0] + color_variation)),
            max(0, min(255, base_color[1] + color_variation // 2)),
            max(0, min(255, base_color[2] + color_variation // 3))
        )
