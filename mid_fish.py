# -*- coding: utf-8 -*-
"""
中型鱼类 - Nova优化版，参数全从Config获取，动态调整丝滑 ♥
作者: 星瑶 (Nova) ♥
优化: 晏霖 (Aria) ♥
"""

import math
import random
import pygame
from pygame import Vector2

from common_def import limit_vector
from config import Config


class MidFish:
    def __init__(self, x, y, parent_age=0):
        # ===================基础物理属性===================
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1),
                                            random.uniform(-1, 1)).normalize() * Config.MID_FISH_SPEED
        self.acceleration = pygame.math.Vector2(0, 0)

        # ===================生命周期相关===================
        self.age = 0
        self.max_age = random.randint(7200, 14400)  # 鱼的最大寿命
        self.is_alive = True

        # ===================饥饿系统===================
        self.hunger = 150  # 当前饥饿值
        self.max_hunger = 300  # 最大饥饿值
        self.hunger_decay = 0.1  # 饥饿值衰减速度
        self.energy = 100.0 + random.randint(-20, 20)  # 能量值，用于活动和繁殖

        # ===================繁殖系统===================
        self.can_reproduce = False
        self.is_mature = False  # 是否成熟
        self.last_reproduction = 0  # 上次繁殖时间
        self.last_breed_time = 0  # 上次繁殖时间（备用）
        self.last_feed_time = 0  # 上次进食时间

        # ===================遗传和进化属性===================
        age_factor = min(parent_age * 0.001, 0.3)  # 父母年龄对后代的影响
        base_speed_variation = random.uniform(0.7, 1.3)  # 基础速度变异
        age_bonus = age_factor * 0.5  # 年龄奖励

        # ===================动态属性（受Config影响）===================
        self.max_speed = Config.MID_FISH_SPEED * (base_speed_variation + age_bonus)
        self.max_force = Config.MID_FISH_FORCE + age_factor * 0.02
        self.size = Config.MID_FISH_SIZE

        # ===================行为属性===================
        self.experience = 0  # 经验值，影响逃避能力
        self.panic_resistance = random.uniform(0.5, 1.0)  # 恐慌抗性
        self.fear_level = 0.0  # 当前恐惧程度
        self.preferred_food = 'small_fish' if random.random() < Config.MID_FISH_FOOD_PREFERENCE else 'plankton'

        # ===================视觉效果===================
        self.trail = []  # 游泳轨迹
        self.color_offset = random.random() * math.pi * 2  # 颜色偏移，用于个体差异

    def update(self, neighbors, foods=None, predators=None, current_time=0, day_night_factor=1.0, water_current=None,
               separation_weight=Config.SEPARATION_WEIGHT, alignment_weight=Config.ALIGNMENT_WEIGHT,
               cohesion_weight=Config.COHESION_WEIGHT, food_weight=Config.FOOD_WEIGHT,
               escape_weight=Config.MID_FISH_ESCAPE_WEIGHT):
        """主更新方法，处理鱼的所有行为"""
        if not self.is_alive:
            return

        # 生存检查
        if self.hunger <= 0 or self.age > self.max_age:
            self.is_alive = False
            return

        # 基础更新
        self.age += 1
        self.hunger -= self.hunger_decay
        self.energy = max(0, self.energy - 0.1)  # 能量自然消耗

        # 动态更新参数（从Config获取最新值）
        self.max_speed = Config.MID_FISH_SPEED
        self.max_force = Config.MID_FISH_FORCE
        self.size = Config.MID_FISH_SIZE

        # 成熟度检查
        if self.age > Config.FISH_REPRODUCTION_AGE * 1.5:
            self.is_mature = True
            # 繁殖冷却时间检查
            self.can_reproduce = (current_time - self.last_breed_time) > Config.FISH_BREED_COOLDOWN * 1.5

        # 繁殖冷却重置
        if current_time - self.last_reproduction > Config.FISH_BREED_COOLDOWN * 1.5:
            self.can_reproduce = True

        # 经验值增长（遭遇捕食者时增长更快）
        if predators:
            for p in predators:
                if p.is_alive and self.position.distance_to(p.position) < 120:
                    self.experience += 0.1
                    break
        else:
            self.experience += 0.01

        # 重置加速度
        self.acceleration *= 0

        # 昼夜影响
        cohesion_multiplier = 1.0 + (1.0 - day_night_factor) * Config.NIGHT_COHESION_BONUS
        speed_multiplier = day_night_factor * Config.NIGHT_SPEED_REDUCTION + (1.0 - Config.NIGHT_SPEED_REDUCTION)

        # 群体行为力
        sep = self.separate(neighbors) * separation_weight
        ali = self.align(neighbors) * alignment_weight
        coh = self.cohesion(neighbors) * cohesion_weight * cohesion_multiplier
        wan = self.wander() * Config.WANDER_WEIGHT

        # 应用基础力
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)
        self.apply_force(wan)

        # 水流影响
        if water_current:
            self.apply_force(water_current * Config.CURRENT_STRENGTH)

        # 觅食行为
        if foods:
            food_force = self.seek_food(foods)
            self.apply_force(food_force * food_weight)

        # 逃避捕食者
        if predators:
            escape_force = self.flee_from_predators(predators)
            experience_multiplier = 1.0 + min(self.experience * 0.1, 0.5)
            self.apply_force(escape_force * escape_weight * experience_multiplier)

        # 边界处理
        self.handle_boundaries()

        # 物理更新
        self.velocity += self.acceleration
        max_speed = self.max_speed * speed_multiplier
        self.velocity = limit_vector(self.velocity, max_speed)
        self.position += self.velocity

        # 轨迹更新
        self.update_trail()

        # 恐惧值恢复
        fear_recovery = 0.02 + self.panic_resistance * 0.01
        self.fear_level = max(0.0, self.fear_level - fear_recovery)

    def attempt_reproduction(self, current_time, adjusted_breed_chance, swarm):
        """繁殖尝试方法，Nova调参，冷却时间动态调整"""
        breed_cooldown = swarm.balancer.adjusted_params.get('FISH_BREED_COOLDOWN', Config.FISH_BREED_COOLDOWN) * 1.5

        # 基础繁殖条件检查
        if not self.can_reproduce or not self.is_mature or not self.is_alive:
            return None

        # 冷却时间检查
        if (current_time - self.last_reproduction) < breed_cooldown:
            return None

        # 饥饿值检查 - 必须有足够的饥饿值才能繁殖
        min_hunger_for_reproduction = self.max_hunger * 0.6  # 需要至少60%的饥饿值
        if self.hunger < min_hunger_for_reproduction:
            return None

        # 能量检查 - 繁殖需要消耗能量
        if self.energy < 50:
            return None

        # 繁殖概率检查
        if (random.random() < adjusted_breed_chance or
                (current_time - self.last_feed_time < 300 and random.random() < Config.FISH_FOOD_BREED_CHANCE)):
            # 消耗能量和饥饿值
            self.energy -= 30
            self.hunger -= 20

            self.last_reproduction = current_time
            self.can_reproduce = False
            return self.create_offspring(current_time)

        return None

    def create_offspring(self, current_time):
        """创建后代"""
        self.last_breed_time = current_time

        # 在父母附近随机位置产生后代
        offset_x = random.uniform(-30, 30)
        offset_y = random.uniform(-30, 30)
        offspring_x = self.position.x + offset_x
        offspring_y = self.position.y + offset_y

        return MidFish(offspring_x, offspring_y, self.age)

    def feed(self, current_time):
        """进食方法，恢复能量和饥饿值"""
        self.energy = min(150.0, self.energy + 25.0)
        self.hunger = min(self.max_hunger, self.hunger + 30)
        self.last_feed_time = current_time

    def flee_from_predators(self, predators):
        """逃避捕食者的行为"""
        flee_force = pygame.math.Vector2(0, 0)

        for predator in predators:
            if not predator.is_alive:
                continue

            distance = self.position.distance_to(predator.position)
            detection_range = Config.MID_FISH_ESCAPE_RADIUS + self.experience * 10

            if distance < detection_range:
                # 计算逃避方向
                escape_dir = self.position - predator.position
                if escape_dir.length() > 0:
                    escape_dir = escape_dir.normalize()
                    force_magnitude = (detection_range - distance) / detection_range

                    # 如果捕食者在冲刺，增加恐惧
                    if hasattr(predator, 'is_dashing') and predator.is_dashing:
                        force_magnitude *= 2.0
                        self.fear_level = min(1.0, self.fear_level + 0.2)

                    flee_force += escape_dir * force_magnitude * 2.5

        return limit_vector(flee_force, self.max_force * 3)

    def handle_boundaries(self):
        """边界处理，防止鱼游出屏幕"""
        force = pygame.math.Vector2(0, 0)
        margin = 50.0
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        map_height = Config.WINDOW_HEIGHT

        # 水平边界
        if self.position.x < margin:
            force.x = Config.BOUNDARY_FORCE
        elif self.position.x > map_width - margin:
            force.x = -Config.BOUNDARY_FORCE

        # 垂直边界
        if self.position.y < margin:
            force.y = Config.BOUNDARY_FORCE
            self.position.y = max(margin, self.position.y)
        elif self.position.y > map_height - margin:
            force.y = -Config.BOUNDARY_FORCE
            self.position.y = min(map_height - margin, self.position.y)

        self.apply_force(force)

    def separate(self, neighbors):
        """分离行为 - 避免过度拥挤"""
        desired_separation = Config.MID_FISH_SEPARATION_RADIUS
        steer = pygame.math.Vector2(0, 0)
        count = 0

        for fish in neighbors:
            distance = self.position.distance_to(fish.position)
            if 0 < distance < desired_separation:
                diff = self.position - fish.position
                diff = diff.normalize()
                diff /= distance  # 距离越近，力越大
                steer += diff
                count += 1

        if count > 0:
            steer /= count
            steer = steer.normalize() * self.max_speed
            steer -= self.velocity
            steer = limit_vector(steer, self.max_force)

        return steer

    def align(self, neighbors):
        """对齐行为 - 与邻居保持相同方向"""
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
            return steer  # 修复：之前这里返回空向量

        return pygame.math.Vector2(0, 0)

    def cohesion(self, neighbors):
        """聚集行为 - 向群体中心移动"""
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
        """寻找目标的基础方法"""
        desired = target - self.position
        desired = desired.normalize() * self.max_speed
        steer = desired - self.velocity
        steer = limit_vector(steer, self.max_force)
        return steer

    def wander(self, ):
        """随机游荡行为"""
        wander_angle = random.uniform(-0.3, 0.3)
        desired = pygame.math.Vector2(
            math.cos(wander_angle),
            math.sin(wander_angle)
        ) * self.max_speed * 0.5

        steer = desired - self.velocity
        steer = limit_vector(steer, self.max_force * 0.3)
        return steer

    def seek_food(self, foods):
        """寻找食物的行为"""
        if not foods:
            return Vector2(0, 0)

        # 过滤出可用的食物
        available_foods = [f for f in foods if not f.consumed]
        if not available_foods:
            return Vector2(0, 0)

        # 优先选择偏好的食物类型
        preferred_foods = [f for f in available_foods if f.food_type == self.preferred_food]
        other_foods = [f for f in available_foods if f.food_type != self.preferred_food]

        target_foods = preferred_foods if preferred_foods else other_foods
        if not target_foods:
            return Vector2(0, 0)

        # 寻找最近的食物
        closest_food = min(target_foods, key=lambda f: self.position.distance_to(f.position))

        # 计算寻找力
        desired = closest_food.position - self.position
        if desired.length() > 0:
            desired = desired.normalize() * self.max_speed
            steer = desired - self.velocity
            return limit_vector(steer, self.max_force)

        return Vector2(0, 0)

    def apply_force(self, force):
        """应用力到加速度"""
        self.acceleration += force

    def update_trail(self):
        """更新游泳轨迹"""
        self.trail.append(self.position.copy())
        if len(self.trail) > Config.TRAIL_LENGTH:
            self.trail.pop(0)

    def get_shape_points(self):
        """获取鱼的形状点，用于绘制"""
        if self.velocity.length() == 0:
            direction = Vector2(1, 0)
        else:
            direction = self.velocity.normalize()

        perpendicular = Vector2(-direction.y, direction.x)

        # 鱼身参数
        body_length = self.size * 2
        body_width = self.size
        tail_length = self.size * 1.5

        # 计算关键点
        front = self.position + direction * body_length
        left = self.position - perpendicular * body_width
        right = self.position + perpendicular * body_width
        tail_base_left = self.position - perpendicular * (body_width * 0.5)
        tail_base_right = self.position + perpendicular * (body_width * 0.5)
        tail_tip = self.position - direction * tail_length

        # 返回鱼身和鱼尾的点
        body_points = [front, left, right]
        tail_points = [tail_base_left, tail_tip, tail_base_right]

        return body_points, tail_points

    def get_color(self, day_night_factor=1.0):
        """获取鱼的颜色，根据恐惧程度和时间变化"""
        base_color = Config.COLORS['mid_fish_body']

        # 恐惧状态下的颜色变化
        if self.fear_level > 0:
            fear_intensity = self.fear_level * 255
            return (
                min(255, base_color[0] + fear_intensity),
                max(0, base_color[1] - fear_intensity // 2),
                max(0, base_color[2] - fear_intensity // 2)
            )

        # 正常状态下的颜色变化（呼吸效果）
        time_offset = pygame.time.get_ticks() * 0.002 + self.color_offset
        color_variation = math.sin(time_offset) * 30 * day_night_factor

        return (
            max(0, min(255, base_color[0] + color_variation)),
            max(0, min(255, base_color[1] + color_variation // 2)),
            max(0, min(255, base_color[2] + color_variation // 3))
        )
