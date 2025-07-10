# -*- coding: utf-8 -*-
"""
中型鱼类 - Nova优化版，参数全从Config获取，动态调整丝滑 ♥
作者: 星瑶 (Nova) ♥
"""

import math
import random
import pygame
from pygame import Vector2

from common_def import limit_vector
from config import Config



class MidFish:
    def __init__(self, x, y, parent_age=0):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1),
                                            random.uniform(-1, 1)).normalize() * Config.MID_FISH_SPEED
        self.acceleration = pygame.math.Vector2(0, 0)
        self.age = 0
        self.hunger = 150
        self.max_hunger = 150
        self.hunger_decay = 0.15
        self.last_breed_time = 0
        self.can_reproduce = False
        self.last_reproduction = 0
        self.last_feed_time = 0
        self.is_alive = True
        self.max_age = random.randint(7200, 14400)
        age_factor = min(parent_age * 0.001, 0.3)
        base_speed_variation = random.uniform(0.7, 1.3)
        age_bonus = age_factor * 0.5
        self.max_speed = Config.MID_FISH_SPEED * (base_speed_variation + age_bonus)
        self.max_force = Config.MID_FISH_FORCE + age_factor * 0.02
        self.size = Config.MID_FISH_SIZE
        self.experience = 0
        self.panic_resistance = random.uniform(0.5, 1.0)
        self.trail = []
        self.preferred_food = 'small_fish' if random.random() < Config.MID_FISH_FOOD_PREFERENCE else 'plankton'
        self.color_offset = random.random() * math.pi * 2
        self.fear_level = 0
        self.target_food = None
        self.energy = 100 + random.randint(-20, 20)
        self.is_mature = False

    def update(self, neighbors, foods=None, predators=None, current_time=0, day_night_factor=1.0, water_current=None,
               separation_weight=Config.SEPARATION_WEIGHT, alignment_weight=Config.ALIGNMENT_WEIGHT,
               cohesion_weight=Config.COHESION_WEIGHT, food_weight=Config.FOOD_WEIGHT,
               escape_weight=Config.MID_FISH_ESCAPE_WEIGHT):
        if not self.is_alive:
            return
        if self.hunger <= 0 or self.age > self.max_age:
            self.is_alive = False
            return
        self.age += 1
        self.hunger -= self.hunger_decay
        # 动态更新参数
        self.max_speed = Config.MID_FISH_SPEED
        self.max_force = Config.MID_FISH_FORCE
        self.size = Config.MID_FISH_SIZE
        if self.age > Config.FISH_REPRODUCTION_AGE * 1.5:
            self.is_mature = True
            self.can_reproduce = (current_time - self.last_breed_time) > Config.FISH_BREED_COOLDOWN * 1.5
        if current_time - self.last_reproduction > Config.FISH_BREED_COOLDOWN * 1.5:
            self.can_reproduce = True
        if predators:
            for p in predators:
                if p.is_alive and self.position.distance_to(p.position) < 120:
                    self.experience += 0.1
                    break
        else:
            self.experience += 0.01
        self.acceleration *= 0
        cohesion_multiplier = 1.0 + (1.0 - day_night_factor) * Config.NIGHT_COHESION_BONUS
        speed_multiplier = day_night_factor * Config.NIGHT_SPEED_REDUCTION + (1.0 - Config.NIGHT_SPEED_REDUCTION)
        self.get_color(day_night_factor)
        sep = self.separate(neighbors) * separation_weight
        ali = self.align(neighbors) * alignment_weight
        coh = self.cohesion(neighbors) * cohesion_weight * cohesion_multiplier
        wan = self.wander() * Config.WANDER_WEIGHT
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)
        self.apply_force(wan)
        if water_current:
            self.apply_force(water_current * Config.CURRENT_STRENGTH)
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

    def attempt_reproduction(self, current_time, adjusted_breed_chance, swarm):
        """中型鱼繁殖，Nova调参，冷却时间动态调整，生鱼崽崽稳稳的~"""
        breed_cooldown = swarm.balancer.adjusted_params.get('FISH_BREED_COOLDOWN', Config.FISH_BREED_COOLDOWN) * 1.5
        if not self.can_reproduce or not self.is_mature or not self.is_alive:
            return None
        if (current_time - self.last_reproduction) < breed_cooldown:  # Nova: 动态冷却，优雅又精准！
            return None
        if (random.random() < adjusted_breed_chance or
                (current_time - self.last_feed_time < 300 and random.random() < Config.FISH_FOOD_BREED_CHANCE)):
            self.last_reproduction = current_time
            self.can_reproduce = False
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
        self.hunger = min(self.max_hunger, self.hunger + 30)

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
        return limit_vector(flee_force, self.max_force * 3)

    def handle_boundaries(self):
        force = pygame.math.Vector2(0, 0)
        margin = 50
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        map_height = Config.WINDOW_HEIGHT
        if self.position.x < margin:
            force.x = Config.BOUNDARY_FORCE
        elif self.position.x > map_width - margin:
            force.x = -Config.BOUNDARY_FORCE
        if self.position.y < margin:
            force.y = Config.BOUNDARY_FORCE
            self.position.y = max(margin, self.position.y)
        elif self.position.y > map_height - margin:
            force.y = -Config.BOUNDARY_FORCE
            self.position.y = min(map_height - margin, self.position.y)
        self.apply_force(force)

    def separate(self, neighbors):
        desired_separation = Config.MID_FISH_SEPARATION_RADIUS
        steer = pygame.math.Vector2(0, 0)
        count = 0
        for fish in neighbors:
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
            steer = limit_vector(steer, self.max_force)
        return steer

    def align(self, neighbors):
        neighbor_dist = Config.MID_FISH_ALIGNMENT_RADIUS
        sum_velocity = pygame.math.Vector2(0, 0)
        count = 0
        for fish in neighbors:
            distance = self.position.distance_to(fish.position)
            if 0 < distance < neighbor_dist:
                sum_velocity += fish.velocity
                count += 1
        if count > 0:
            sum_velocity /= count
            sum_velocity = sum_velocity.normalize() * self.max_speed
            steer = sum_velocity - self.velocity
            steer = limit_vector(steer, self.max_force)
        return pygame.math.Vector2(0, 0)

    def cohesion(self, neighbors):
        neighbor_dist = Config.MID_FISH_COHESION_RADIUS
        sum_position = pygame.math.Vector2(0, 0)
        count = 0
        for fish in neighbors:
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
        steer = limit_vector(steer, self.max_force)
        return steer

    def wander(self):
        wander_angle = random.uniform(-0.3, 0.3)
        desired = pygame.math.Vector2(
            math.cos(wander_angle),
            math.sin(wander_angle)
        ) * self.max_speed * 0.5
        steer = desired - self.velocity
        steer = limit_vector(steer, self.max_force * 0.3)
        return steer

    def seek_food(self, foods):
        if not foods:
            return Vector2(0, 0)
        preferred_foods = [f for f in foods if f.food_type == self.preferred_food and not f.consumed]
        other_foods = [f for f in foods if f.food_type != self.preferred_food and not f.consumed]
        target_foods = preferred_foods if preferred_foods else other_foods
        if not target_foods:
            return Vector2(0, 0)
        closest_food = min(target_foods, key=lambda f: self.position.distance_to(f.position))
        desired = closest_food.position - self.position
        desired = desired.normalize() * self.max_speed
        steer = desired - self.velocity
        return limit_vector(steer, self.max_force)

    def apply_force(self, force):
        self.acceleration += force

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
        base_color = Config.COLORS['mid_fish_body']
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
