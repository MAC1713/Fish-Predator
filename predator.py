import math
import random

import pygame
from pygame.math import Vector2

from common_def import limit_vector
from food import Food

from config import Config


class Predator:
    """增强版捕食者类 - 动态参数从balancer获取"""

    def __init__(self, x, y):
        self.acceleration = None
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
        self.max_age = Config.PREDATOR_MAX_AGE
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

        if self.growth_stage == 'adult' and self.hunger > Config.PREDATOR_MAX_HUNGER * 0.3:  # 降低到30%
            self.attempt_mating(current_time, swarm)
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
        elif self.age < 20000:  # ~3 min
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
        if self.hunger >= swarm.balancer.adjusted_params.get('PREDATOR_MAX_HUNGER', Config.PREDATOR_MAX_HUNGER) * 0.8:
            return
        for fish in fishes[:]:
            if self.position.distance_to(fish.position) < self.size + fish.size:
                fish.is_alive = False
                self.feed_on_fish(current_time, energy=50, swarm=swarm)
                return
        for mid_fish in mid_fishes[:]:
            if self.position.distance_to(mid_fish.position) < self.size + mid_fish.size:
                mid_fish.is_alive = False
                self.feed_on_fish(current_time, energy=80, swarm=swarm)
                return

    def feed_on_fish(self, current_time, energy, swarm):
        """捕食逻辑，饥饿值上限动态获取"""
        max_hunger = swarm.balancer.adjusted_params.get('PREDATOR_MAX_HUNGER', Config.PREDATOR_MAX_HUNGER)
        self.hunger = min(max_hunger, self.hunger + Config.PREDATOR_FEED_RESTORE * (energy / 50))
        self.last_feed_time = current_time
        self.feed_frequency.append(current_time)
        if len(self.feed_frequency) > 10:
            self.feed_frequency.pop(0)

    def hunt(self, fishes, mid_fishes):
        """Hunt with a preference for small fish over mid fish - 修复优先级算法"""
        hunger_ratio = self.get_hunger_ratio()
        if hunger_ratio >= 0.8:
            self.wander()
            self.hunt_target = None
            return Vector2(0, 0)

        targets = [(f, f.position, f.max_speed, 'fish') for f in fishes if f.is_alive] + \
                  [(m, m.position, m.max_speed, 'mid_fish') for m in mid_fishes if m.is_alive]

        if not targets:
            self.wander()
            return Vector2(0, 0)

        detection_range = Config.PREDATOR_HUNTER_RANGE_MAX * (1.0 - hunger_ratio)
        target_candidates = []

        for target, pos, speed, fish_type in targets:
            distance = self.position.distance_to(pos)
            if distance < detection_range:
                # 修复：使用更合理的优先级计算
                distance_priority = (detection_range - distance) / detection_range * 100  # 0-100分

                # 速度优先级：越慢越容易抓（避免负数问题）
                # 使用倒数关系，最大速度4.0时得分25，最小速度0.5时得分200
                speed_priority = min(200.0, 100.0 / max(0.5, speed))  # 25-200分

                # 鱼类型优先级
                if fish_type == 'fish':
                    type_priority = Config.PREDATOR_HUNT_FISH_WEIGHT  # 小鱼优先级低
                else:  # mid fish
                    type_priority = Config.PREDATOR_HUNT_MID_FISH_WEIGHT  # 中鱼优先级高

                # 综合优先级：距离40%，速度30%，类型30%
                total_priority = (distance_priority * 0.4 +
                                  speed_priority * 0.3 +
                                  type_priority * 0.3)

                target_candidates.append((target, total_priority, distance))

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
