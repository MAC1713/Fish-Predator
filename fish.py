# -*- coding: utf-8 -*-
"""
智能鱼类 - Nova优化版，参数全从Config获取，动态调整丝滑 ♥
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
"""

import math
import random
import pygame
from pygame import Vector2
from config import Config


def limit_vector(vector, max_magnitude):
    if vector.length() > max_magnitude:
        return vector.normalize() * max_magnitude
    return vector


class Fish:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * Config.FISH_SPEED
        self.acceleration = Vector2(0, 0)
        self.size = Config.FISH_SIZE
        self.max_speed = Config.FISH_SPEED
        self.max_force = Config.FISH_FORCE
        self.is_alive = True
        self.max_age = random.randint(3600, 7200)
        self.age = 0
        self.is_mature = False
        self.can_reproduce = False
        self.last_reproduction = 0
        self.last_feed_time = 0
        self.experience = 0
        self.fear_level = 0
        self.panic_resistance = random.uniform(0.5, 1.0)
        self.trail = []
        self.color_offset = random.uniform(0, 360)

    def update(self, neighbors, foods=None, predators=None, current_time=0, day_night_factor=1.0, water_current=None,
               separation_weight=Config.SEPARATION_WEIGHT, alignment_weight=Config.ALIGNMENT_WEIGHT,
               cohesion_weight=Config.COHESION_WEIGHT, food_weight=Config.FOOD_WEIGHT,
               escape_weight=Config.ESCAPE_WEIGHT):
        if not self.is_alive:
            return
        if self.age > self.max_age:
            self.is_alive = False
            return
        self.age += 1
        # 动态更新参数
        self.max_speed = Config.FISH_SPEED
        self.max_force = Config.FISH_FORCE
        self.size = Config.FISH_SIZE
        if self.age > Config.FISH_REPRODUCTION_AGE:
            self.is_mature = True
            self.can_reproduce = (current_time - self.last_reproduction) > Config.FISH_BREED_COOLDOWN
        if predators and any(self.position.distance_to(p.position) < 100 for p in predators if p.is_alive):
            self.experience += 0.1
        else:
            self.experience += 0.01
        self.acceleration *= 0
        margin = 50
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        map_height = Config.WINDOW_HEIGHT
        near_border = (self.position.x < margin or self.position.x > map_width - margin or
                       self.position.y < margin or self.position.y > map_height - margin)
        cohesion_multiplier = 1.0 + (1.0 - day_night_factor) * Config.NIGHT_COHESION_BONUS * 2
        sep_weight = separation_weight * (2.0 if near_border else 1.0)
        coh_weight = cohesion_weight * (0.5 if near_border else 1.0) * cohesion_multiplier
        speed_multiplier = day_night_factor * 0.8 + 0.2
        sep = self.separate(neighbors) * sep_weight
        ali = self.align(neighbors) * alignment_weight
        coh = self.cohesion(neighbors) * coh_weight
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
            self.apply_force(food_force * food_weight)
        if predators:
            escape_force = self.flee_from_predators(predators)
            experience_multiplier = 1.0 + min(self.experience * 0.1, 0.5)
            self.apply_force(escape_force * escape_weight * experience_multiplier)
        self.handle_boundaries()
        self.velocity += self.acceleration
        max_speed = self.max_speed * speed_multiplier
        self.velocity = limit_vector(self.velocity, max_speed)
        self.position += self.velocity
        self.update_trail()
        fear_recovery = 0.02 + self.panic_resistance * 0.01
        self.fear_level = max(0, self.fear_level - fear_recovery)

    def separate(self, neighbors):
        steer = Vector2(0, 0)
        count = 0
        for fish in neighbors:
            distance = self.position.distance_to(fish.position)
            if 0 < distance < Config.FISH_SEPARATION_RADIUS:
                diff = self.position - fish.position
                if diff.length() > 0:
                    diff = diff.normalize() / distance
                    steer += diff
                    count += 1
        if count > 0:
            steer /= count
        if steer.length() > 0:
            steer = steer.normalize() * self.max_speed - self.velocity
            steer = limit_vector(steer, self.max_force)
        return steer

    def align(self, neighbors):
        steer = Vector2(0, 0)
        count = 0
        for fish in neighbors:
            distance = self.position.distance_to(fish.position)
            if distance < Config.FISH_ALIGNMENT_RADIUS:
                steer += fish.velocity
                count += 1
        if count > 0:
            steer /= count
            if steer.length() > 0:
                steer = steer.normalize() * self.max_speed - self.velocity
                steer = limit_vector(steer, self.max_force)
        return steer

    def cohesion(self, neighbors):
        steer = Vector2(0, 0)
        count = 0
        center = Vector2(0, 0)
        for fish in neighbors:
            distance = self.position.distance_to(fish.position)
            if distance < Config.FISH_COHESION_RADIUS:
                center += fish.position
                count += 1
        if count > 0:
            center /= count
            steer = center - self.position
            if steer.length() > 0:
                steer = steer.normalize() * self.max_speed - self.velocity
                steer = limit_vector(steer, self.max_force)
        return steer

    def wander(self):
        if random.random() < 0.05:
            angle = random.uniform(0, 2 * math.pi)
            return Vector2(math.cos(angle), math.sin(angle)) * self.max_force
        return Vector2(0, 0)

    def seek_food(self, foods):
        closest_food = None
        min_distance = float('inf')
        for food in foods:
            if food.food_type == 'plankton' and not food.consumed:
                distance = self.position.distance_to(food.position)
                if distance < Config.FOOD_DETECTION_RADIUS and distance < min_distance:
                    min_distance = distance
                    closest_food = food
        if closest_food:
            desired = closest_food.position - self.position
            if desired.length() > 0:
                desired = desired.normalize() * self.max_speed
                steer = desired - self.velocity
                return limit_vector(steer, self.max_force)
        return Vector2(0, 0)

    def flee_from_predators(self, predators):
        flee_force = Vector2(0, 0)
        count = 0
        for predator in predators:
            if not predator.is_alive:
                continue
            distance = self.position.distance_to(predator.position)
            detection_range = Config.ESCAPE_RADIUS + self.experience * 5
            if distance < detection_range:
                escape_dir = self.position - predator.position
                if escape_dir.length() > 0:
                    escape_dir = escape_dir.normalize()
                    force_magnitude = (detection_range - distance) / detection_range
                    if predator.is_dashing:
                        force_magnitude *= 1.5
                        self.fear_level = min(1.0, self.fear_level + 0.1)
                    escape_dir += Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
                    if escape_dir.length() > 0:
                        escape_dir = escape_dir.normalize()
                    flee_force += escape_dir * force_magnitude * 1.5
                    count += 1
        if count > 0:
            flee_force /= count
        return limit_vector(flee_force, self.max_force * 2)

    def handle_boundaries(self):
        force = Vector2(0, 0)
        margin = 50
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        map_height = Config.WINDOW_HEIGHT
        if self.position.x < 0:
            self.position.x += map_width
            self.velocity += Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
        elif self.position.x > map_width:
            self.position.x -= map_width
            self.velocity += Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
        if self.position.y < margin:
            distance_to_border = margin - self.position.y
            force.y = Config.BOUNDARY_FORCE * (distance_to_border / margin)
            self.position.y = max(margin, self.position.y)
        elif self.position.y > map_height - margin:
            distance_to_border = self.position.y - (map_height - margin)
            force.y = -Config.BOUNDARY_FORCE * (distance_to_border / margin)
            self.position.y = min(map_height - margin, self.position.y)
        self.apply_force(force)

    def apply_force(self, force):
        self.acceleration += force

    def feed(self, current_time):
        self.last_feed_time = current_time
        self.can_reproduce = False

    def attempt_reproduction(self, current_time, adjusted_breed_chance):
        if not self.can_reproduce or not self.is_mature or not self.is_alive:
            return None
        if (random.random() < adjusted_breed_chance or
                (current_time - self.last_feed_time < 300 and random.random() < Config.FISH_FOOD_BREED_CHANCE)):
            self.last_reproduction = current_time
            self.can_reproduce = False
            return self.create_offspring(current_time)
        return None

    def create_offspring(self, current_time):
        offspring = Fish(self.position.x, self.position.y)
        offspring.velocity = self.velocity.rotate(random.uniform(-30, 30))
        return offspring

    def update_trail(self):
        self.trail.append(self.position.copy())
        if len(self.trail) > Config.TRAIL_LENGTH:
            self.trail.pop(0)

    def get_shape_points(self):
        direction = self.velocity.normalize()
        perpendicular = Vector2(-direction.y, direction.x)
        body_length = self.size * 2
        body_width = self.size
        tail_length = self.size * 1.5
        front = self.position + direction * body_length
        left = self.position - perpendicular * body_width
        right = self.position + perpendicular * body_width
        tail_base_left = self.position - perpendicular * (body_width * 0.5)
        tail_base_right = self.position + perpendicular * (body_width * 0.5)
        tail_tip = self.position - direction * tail_length
        return [front, left, right], [tail_base_left, tail_tip, tail_base_right]

    def get_color(self, day_night_factor=1.0):
        base_color = Config.COLORS['fish_body']
        if self.fear_level > 0:
            fear_intensity = self.fear_level * 255
            return (
                min(255, base_color[0] + fear_intensity),
                max(0, base_color[1] - fear_intensity // 2),
                max(0, base_color[2] - fear_intensity // 2)
            )
        time_offset = pygame.time.get_ticks() * 0.002 + self.color_offset
        color_variation = math.sin(time_offset) * 30 * day_night_factor
        return (
            max(0, min(255, base_color[0] + color_variation)),
            max(0, min(255, base_color[1] + color_variation // 2)),
            max(0, min(255, base_color[2] + color_variation // 3))
        )
