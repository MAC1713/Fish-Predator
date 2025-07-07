# -*- coding: utf-8 -*-
"""
鱼群管理器 - Nova的优化版，动态参数全靠balancer接管 ♥
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
备注: 参数调用全从balancer.adjusted_params获取，实时动态调整，丝滑到飞起~
"""

import math
import random
from pygame.math import Vector2
import pygame
from fish import Fish
from mid_fish import MidFish
from config import Config
from intelligent_ecosystem_balancer import SmartEcosystemBalancer


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


def limit_vector(vector, max_magnitude):
    if vector.length() > max_magnitude:
        return vector.normalize() * max_magnitude
    return vector


class Predator:
    """增强版捕食者类 - 动态参数从balancer获取"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * Config.PREDATOR_SPEED
        self.size = Config.PREDATOR_SIZE
        self.max_speed = Config.PREDATOR_SPEED
        self.max_force = Config.PREDATOR_MAX_FORCE
        self.hunt_target = None
        self.hunger = Config.PREDATOR_MAX_HUNGER
        self.is_alive = True
        self.last_feed_time = 0
        self.feed_frequency = []
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_direction = Vector2(0, 0)
        self.age = 0
        self.max_age = 18000
        self.growth_stage = 'juvenile'
        self.trail = []
        self.color_offset = random.random() * math.pi * 2

    def update(self, fishes, mid_fishes, current_time, swarm):
        if not self.is_alive:
            return
        self.age += 1
        # 动态更新参数
        self.max_speed = swarm.balancer.adjusted_params.get('PREDATOR_SPEED', Config.PREDATOR_SPEED)
        self.max_force = swarm.balancer.adjusted_params.get('PREDATOR_MAX_FORCE', Config.PREDATOR_MAX_FORCE)
        self.size = swarm.balancer.adjusted_params.get('PREDATOR_SIZE', Config.PREDATOR_SIZE)
        hunger_decay = swarm.balancer.adjusted_params.get('PREDATOR_HUNGER_DECAY', Config.PREDATOR_HUNGER_DECAY)
        self.hunger -= hunger_decay
        if self.hunger <= 0 or self.age > self.max_age:
            self.is_alive = False
            swarm.foods.append(Food(self.position.x, self.position.y, 'large_corpse'))
            return
        self.update_growth()
        self.update_dash(current_time)
        self.check_feed(fishes, mid_fishes, current_time, swarm)
        self.acceleration = Vector2(0, 0)
        if self.is_dashing:
            self.velocity = self.dash_direction
        else:
            steer = self.hunt(fishes, mid_fishes)
            self.apply_force(steer)
            self.handle_boundaries()
            self.velocity += self.acceleration
            self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.update_trail()

    def apply_force(self, force):
        """应用力到加速度，Nova补全逻辑，丝滑~"""
        self.acceleration += force

    def update_trail(self):
        """更新捕食者轨迹，Nova的细节优化"""
        self.trail.append(self.position.copy())
        if len(self.trail) > Config.TRAIL_LENGTH:
            self.trail.pop(0)

    def update_growth(self):
        if self.age < 3600:  # ~1 min
            self.growth_stage = 'juvenile'
            self.size = Config.PREDATOR_SIZE * 0.7
            self.max_speed = Config.PREDATOR_SPEED * 1.2
        elif self.age < 10800:  # ~3 min
            self.growth_stage = 'adult'
            self.size = Config.PREDATOR_SIZE
            self.max_speed = Config.PREDATOR_SPEED
        else:
            self.growth_stage = 'senior'
            self.size = Config.PREDATOR_SIZE * 1.2
            self.max_speed = Config.PREDATOR_SPEED * 0.8

    def attempt_mating(self, current_time, swarm):
        for other in swarm.predators:
            if (other != self and other.growth_stage == 'adult' and other.is_alive and
                    self.position.distance_to(other.position) < 100):
                offspring_x = (self.position.x + other.position.x) / 2
                offspring_y = (self.position.y + other.position.y) / 2
                swarm.predators.append(Predator(offspring_x, offspring_y))
                break

    def check_feed(self, fishes, mid_fishes, current_time, swarm):
        if self.hunger >= Config.PREDATOR_MAX_HUNGER * 0.8:
            return  # 饱了不吃
        for fish in fishes[:]:
            if self.position.distance_to(fish.position) < self.size + fish.size:
                fish.is_alive = False
                self.feed_on_fish(current_time, energy=50)  # Small fish energy
                return
        for mid_fish in mid_fishes[:]:
            if self.position.distance_to(mid_fish.position) < self.size + mid_fish.size:
                mid_fish.is_alive = False
                self.feed_on_fish(current_time, energy=80)  # Mid fish higher energy
                return

    def feed_on_fish(self, current_time, energy):
        self.hunger = min(Config.PREDATOR_MAX_HUNGER, self.hunger + Config.PREDATOR_FEED_RESTORE * (energy / 50))
        self.last_feed_time = current_time
        self.feed_frequency.append(current_time)
        if len(self.feed_frequency) > 10:
            self.feed_frequency.pop(0)

    def hunt(self, fishes, mid_fishes):
        """Hunt with a preference for small fish over mid fish."""
        hunger_ratio = self.get_hunger_ratio()
        if hunger_ratio >= 0.8:
            self.wander()
            self.hunt_target = None
            return Vector2(0, 0)
        targets = [(f, f.position, f.max_speed, 'small') for f in fishes if f.is_alive] + \
                  [(m, m.position, m.max_speed, 'mid') for m in mid_fishes if m.is_alive]
        if not targets:
            self.wander()
            return Vector2(0, 0)
        detection_range = Config.PREDATOR_HUNTER_RANGE_MAX * (1.0 - hunger_ratio)
        target_candidates = []
        for target, pos, speed, fish_type in targets:
            distance = self.position.distance_to(pos)
            if distance < detection_range:
                priority = (detection_range - distance) + (2.0 - speed) * 50
                if fish_type == 'mid':
                    priority *= 1.8  # Prefer mid fish
                target_candidates.append((target, priority, distance))
        if target_candidates:
            target_candidates.sort(key=lambda x: x[1], reverse=True)
            best_target, _, distance = target_candidates[0]
            self.hunt_target = best_target
            should_dash = self.should_initiate_dash(distance)
            if should_dash and self.dash_cooldown <= 0:
                self.initiate_dash(best_target)
            else:
                return self.pursue_target(best_target)
        else:
            self.hunt_target = None
            self.wander()
        return Vector2(0, 0)

    def should_initiate_dash(self, target_distance):
        if not (40 < target_distance < 120):
            return False
        hunger_ratio = self.get_hunger_ratio()
        if hunger_ratio >= 0.8:  # 饱了不冲刺
            return False
        # 越饿冲刺概率越高
        hunger_factor = (1.0 - hunger_ratio)  # 0.2到1.0
        recent_kills = len([t for t in self.feed_frequency if pygame.time.get_ticks() - t < 3600])
        kill_penalty = min(recent_kills * 0.3, 0.8)
        dash_probability = 0.01 + hunger_factor * 0.05 - kill_penalty
        return random.random() < dash_probability

    def initiate_dash(self, target):
        self.is_dashing = True
        self.dash_timer = Config.PREDATOR_DASH_DURATION
        target_future_pos = target.position + target.velocity * 10
        dash_direction = target_future_pos - self.position
        self.dash_direction = dash_direction.normalize() if dash_direction.length() > 0 else self.velocity.normalize()
        self.hunger -= Config.PREDATOR_DASH_HUNGER_COST
        recent_kills = len(self.feed_frequency)
        self.dash_cooldown = int(Config.PREDATOR_DASH_COOLDOWN_BASE * (1.0 + min(recent_kills * 0.5, 3.0)))

    def update_dash(self, current_time):
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
            steer = limit_vector(steer, self.max_force)
            return steer
        return Vector2(0, 0)

    def wander(self):
        if random.random() < 0.03:
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = Vector2(math.cos(angle), math.sin(angle)) * self.max_speed * 0.7

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

    def get_hunger_ratio(self):
        return self.hunger / Config.PREDATOR_MAX_HUNGER


class Swarm:
    def __init__(self):
        self.fishes = []
        self.mid_fishes = []
        self.foods = []
        self.predators = []
        self.grid = {}
        self.grid_size = 50
        self.balancer = SmartEcosystemBalancer()
        self.initialize()
        self.stats = {
            'fish_count': 0,
            'mid_fish_count': 0,
            'food_consumed': 0,
            'average_speed': 0,
            'cohesion_level': 0
        }

    def initialize(self):
        self.create_fishes(self.balancer.adjusted_params.get('FISH_COUNT', Config.FISH_COUNT))
        self.create_mid_fishes(self.balancer.adjusted_params.get('MID_FISH_COUNT', Config.MID_FISH_COUNT))
        self.create_foods(self.balancer.adjusted_params.get('FOOD_COUNT', Config.FOOD_COUNT))
        self.create_predators(Config.PREDATOR_COUNT)

    def update(self, water_current=None, day_night_factor=1.0):
        current_time = pygame.time.get_ticks()
        self.balancer.update_balance(self, current_time / 1000.0)
        total_fish_count = len(self.fishes) + len(self.mid_fishes)
        self.update_grid()

        for fish in self.fishes[:]:
            neighbors = self.get_neighbors(fish, self.balancer.adjusted_params.get('FISH_COHESION_RADIUS', Config.FISH_COHESION_RADIUS))
            fish.update(
                neighbors, self.foods, self.predators, current_time, day_night_factor, water_current,
                separation_weight=self.balancer.adjusted_params.get('SEPARATION_WEIGHT', Config.SEPARATION_WEIGHT),
                alignment_weight=self.balancer.adjusted_params.get('ALIGNMENT_WEIGHT', Config.ALIGNMENT_WEIGHT),
                cohesion_weight=self.balancer.adjusted_params.get('COHESION_WEIGHT', Config.COHESION_WEIGHT),
                food_weight=self.balancer.adjusted_params.get('FOOD_WEIGHT', Config.FOOD_WEIGHT),
                escape_weight=self.balancer.adjusted_params.get('ESCAPE_WEIGHT', Config.ESCAPE_WEIGHT)
            )
            if not fish.is_alive:
                self.fishes.remove(fish)
                self.foods.append(Food(fish.position.x, fish.position.y, 'small_fish'))
            elif total_fish_count < 300 and fish.can_reproduce:
                offspring = fish.attempt_reproduction(current_time,
                                                      self.balancer.adjusted_params.get('FISH_NATURAL_BREED_CHANCE',
                                                                                        Config.FISH_NATURAL_BREED_CHANCE))
                if offspring:
                    self.fishes.append(offspring)
        for mid_fish in self.mid_fishes[:]:
            neighbors = self.get_neighbors(mid_fish, self.balancer.adjusted_params.get('MID_FISH_COHESION_RADIUS', Config.MID_FISH_COHESION_RADIUS))
            mid_fish.update(
                neighbors, self.foods, self.predators, current_time, day_night_factor, water_current,
                separation_weight=self.balancer.adjusted_params.get('SEPARATION_WEIGHT', Config.SEPARATION_WEIGHT),
                alignment_weight=self.balancer.adjusted_params.get('ALIGNMENT_WEIGHT', Config.ALIGNMENT_WEIGHT),
                cohesion_weight=self.balancer.adjusted_params.get('COHESION_WEIGHT', Config.COHESION_WEIGHT),
                food_weight=self.balancer.adjusted_params.get('FOOD_WEIGHT', Config.FOOD_WEIGHT),
                escape_weight=self.balancer.adjusted_params.get('MID_FISH_ESCAPE_WEIGHT', Config.MID_FISH_ESCAPE_WEIGHT)
            )
            if not mid_fish.is_alive:
                self.mid_fishes.remove(mid_fish)
                self.foods.append(Food(mid_fish.position.x, mid_fish.position.y, 'small_fish'))
            elif total_fish_count < 300 and mid_fish.can_reproduce:
                offspring = mid_fish.attempt_reproduction(current_time,
                                                          self.balancer.adjusted_params.get('MID_FISH_BREED_CHANCE',
                                                                                            Config.MID_FISH_BREED_CHANCE))
                if offspring:
                    self.mid_fishes.append(offspring)
        for predator in self.predators[:]:
            predator.update(self.fishes, self.mid_fishes, current_time, self)
            if not predator.is_alive:
                self.predators.remove(predator)

        for food in self.foods[:]:
            food.update(water_current)
            if food.consumed:
                self.foods.remove(food)

        self.handle_food_consumption()
        self.respawn_food()
        self.update_stats()

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

    def respawn_food(self):
        target_count = self.balancer.adjusted_params.get('FOOD_COUNT', Config.FOOD_COUNT)
        plankton_count = len([f for f in self.foods if f.food_type == 'plankton'])
        if plankton_count < target_count * 0.6:
            needed = int(target_count * 0.6 - plankton_count)
            for _ in range(needed):
                x = random.uniform(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
                y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
                self.foods.append(Food(x, y, 'plankton'))
        if random.random() < self.balancer.adjusted_params.get('DEAD_FISH_SPAWN_CHANCE', Config.DEAD_FISH_SPAWN_CHANCE):
            center_x = random.uniform(100, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 100)
            center_y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            for _ in range(3):
                x = center_x + random.uniform(-20, 20)
                y = center_y + random.uniform(-10, 10)
                self.foods.append(Food(x, y, 'small_fish'))
        if random.random() < self.balancer.adjusted_params.get('DEAD_WHALE_SPAWN_CHANCE', Config.DEAD_WHALE_SPAWN_CHANCE):
            center_x = random.uniform(100, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 100)
            center_y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            for _ in range(10):
                x = center_x + random.uniform(-50, 50)
                y = center_y + random.uniform(-20, 20)
                self.foods.append(Food(x, y, 'large_corpse'))

    def create_fishes(self, count):
        self.fishes.clear()
        center_x = (Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH) // 2
        center_y = Config.WINDOW_HEIGHT // 2
        for _ in range(int(count)):
            x = center_x + random.uniform(-100, 100)
            y = center_y + random.uniform(-100, 100)
            x = max(50, min(Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50, x))
            y = max(50, min(Config.WINDOW_HEIGHT - 50, y))
            self.fishes.append(Fish(x, y))

    def create_mid_fishes(self, count):
        self.mid_fishes.clear()
        center_x = (Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH) // 2
        center_y = Config.WINDOW_HEIGHT // 2
        for _ in range(int(count)):
            x = center_x + random.uniform(-100, 100)
            y = center_y + random.uniform(-100, 100)
            x = max(50, min(Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50, x))
            y = max(50, min(Config.WINDOW_HEIGHT - 50, y))
            self.mid_fishes.append(MidFish(x, y))

    def create_predators(self, count):
        self.predators.clear()
        for _ in range(int(count)):
            x = random.uniform(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
            y = random.uniform(50, Config.WINDOW_HEIGHT - 50)
            self.predators.append(Predator(x, y))

    def update_grid(self):
        self.grid.clear()
        for fish in self.fishes + self.mid_fishes:
            if fish.is_alive:
                grid_x = int(fish.position.x // self.grid_size)
                grid_y = int(fish.position.y // self.grid_size)
                if (grid_x, grid_y) not in self.grid:
                    self.grid[(grid_x, grid_y)] = []
                self.grid[(grid_x, grid_y)].append(fish)

    def get_neighbors(self, fish, radius):
        grid_x = int(fish.position.x // self.grid_size)
        grid_y = int(fish.position.y // self.grid_size)
        neighbors = []
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        grid_width = int(map_width // self.grid_size)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx = (grid_x + dx) % grid_width
                ny = grid_y + dy
                if (nx, ny) in self.grid:
                    for other in self.grid[(nx, ny)]:
                        if other != fish:
                            dx = other.position.x - fish.position.x
                            if dx > map_width / 2:
                                dx -= map_width
                            elif dx < -map_width / 2:
                                dx += map_width
                            distance = pygame.math.Vector2(dx, other.position.y - fish.position.y).length()
                            if distance < radius:
                                neighbors.append(other)
        return neighbors

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
        target_count = self.balancer.adjusted_params.get('FOOD_COUNT', Config.FOOD_COUNT)
        if len(self.foods) < target_count * 2:
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

    # Nova的彩蛋：瑞瑞专属小提示~
    def __str__(self):
        return f"瑞瑞的鱼群世界，当前鱼群数量：{len(self.fishes)}小鱼 + {len(self.mid_fishes)}中型鱼，食物：{len(self.foods)}，捕食者：{len(self.predators)}，生态健康度：{self.balancer.get_balance_status()['health_score']:.2f}，啧，记得多喂点鱼粮哦~"