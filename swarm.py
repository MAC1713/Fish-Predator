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
from food import Food
from predator import Predator


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

        # 重置出生和死亡计数
        self.balancer.stats['small_fish_births'] = 0
        self.balancer.stats['small_fish_deaths'] = 0
        self.balancer.stats['mid_fish_births'] = 0
        self.balancer.stats['mid_fish_deaths'] = 0

        for fish in self.fishes[:]:
            neighbors = self.get_neighbors(fish, self.balancer.adjusted_params.get('FISH_COHESION_RADIUS',
                                                                                   Config.FISH_COHESION_RADIUS))
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
                self.balancer.stats['small_fish_deaths'] += 1
                self.balancer.history_buffer['small_fish_deaths'].append(1)
            elif total_fish_count < 300 and fish.can_reproduce:
                offspring = fish.attempt_reproduction(current_time,
                                                      self.balancer.adjusted_params.get('FISH_NATURAL_BREED_CHANCE',
                                                                                        Config.FISH_NATURAL_BREED_CHANCE),
                                                      self)
                if offspring:
                    self.fishes.append(offspring)
                    self.balancer.stats['small_fish_births'] += 1
                    self.balancer.history_buffer['small_fish_births'].append(1)
            else:
                self.balancer.history_buffer['small_fish_births'].append(0)
                self.balancer.history_buffer['small_fish_deaths'].append(0)

        for mid_fish in self.mid_fishes[:]:
            neighbors = self.get_neighbors(mid_fish, self.balancer.adjusted_params.get('MID_FISH_COHESION_RADIUS',
                                                                                       Config.MID_FISH_COHESION_RADIUS))
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
                self.balancer.stats['mid_fish_deaths'] += 1
                self.balancer.history_buffer['mid_fish_deaths'].append(1)
            elif total_fish_count < 300 and mid_fish.can_reproduce:
                offspring = mid_fish.attempt_reproduction(current_time,
                                                          self.balancer.adjusted_params.get('MID_FISH_BREED_CHANCE',
                                                                                            Config.MID_FISH_BREED_CHANCE),
                                                          self)
                if offspring:
                    self.mid_fishes.append(offspring)
                    self.balancer.stats['mid_fish_births'] += 1
                    self.balancer.history_buffer['mid_fish_births'].append(1)
            else:
                self.balancer.history_buffer['mid_fish_births'].append(0)
                self.balancer.history_buffer['mid_fish_deaths'].append(0)

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
        if random.random() < self.balancer.adjusted_params.get('DEAD_WHALE_SPAWN_CHANCE',
                                                               Config.DEAD_WHALE_SPAWN_CHANCE):
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
        """重置模拟，Nova清空历史数据，瑞瑞你这鱼群世界焕然一新~"""
        self.initialize()
        self.stats['food_consumed'] = 0
        self.balancer.history_buffer.clear()  # Nova: 清空历史，防止评分偏差
        for pid in self.balancer.pid_controllers.values():
            pid.reset()  # Nova: 重置PID控制器，消除累积误差

    def get_stats(self):
        return self.stats.copy()

    # Nova的彩蛋：瑞瑞专属小提示~
    def __str__(self):
        return f"瑞瑞的鱼群世界，当前鱼群数量：{len(self.fishes)}小鱼 + {len(self.mid_fishes)}中型鱼，食物：{len(self.foods)}，捕食者：{len(self.predators)}，生态健康度：{self.balancer.get_balance_status()['health_score']:.2f}，啧，记得多喂点鱼粮哦~"
