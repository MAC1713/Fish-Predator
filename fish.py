# -*- coding: utf-8 -*-
"""
智能鱼类 - Aria优化版，更清晰的结构和完善的功能实现 ♥
作者: 晏霖 (Aria) ♥，基于 Nova 优化版本
"""

import math
import random
import pygame
from pygame import Vector2

from common_def import limit_vector
from config import Config


class Fish:
    def __init__(self, x, y):
        # ===================基础物理属性===================
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * Config.FISH_SPEED
        self.acceleration = Vector2(0, 0)

        # ===================鱼类基本属性===================
        self.size = Config.FISH_SIZE
        self.max_speed = Config.FISH_SPEED
        self.max_force = Config.FISH_FORCE
        self.is_alive = True

        # ===================生命周期相关===================
        self.max_age = random.randint(3600, 7200)  # 最大寿命
        self.age = 0  # 当前年龄

        # ===================饥饿系统===================
        self.max_hunger = 100  # 最大饥饿值
        self.hunger = 200  # 当前饥饿值
        self.hunger_decay = 0.1  # 饥饿值衰减速度
        self.last_feed_time = 0  # 最后进食时间
        self.hunger_threshold_reproduction = 60  # 繁殖所需最低饥饿值

        # ===================繁殖系统===================
        self.is_mature = False  # 是否成熟
        self.can_reproduce = False  # 是否可以繁殖
        self.last_reproduction = 0  # 最后繁殖时间

        # ===================智能系统===================
        self.experience = 0  # 经验值，影响逃避效果
        self.fear_level = 0.0  # 恐惧等级，影响行为和颜色
        self.panic_resistance = random.uniform(0.5, 1.0)  # 抗恐慌能力，影响恐惧恢复

        # ===================视觉效果===================
        self.trail = []  # 游泳轨迹
        self.color_offset = random.uniform(0, 360)  # 颜色偏移，让每条鱼颜色略有不同

    def update(self, neighbors, foods=None, predators=None, current_time=0, day_night_factor=1.0, water_current=None,
               separation_weight=Config.SEPARATION_WEIGHT, alignment_weight=Config.ALIGNMENT_WEIGHT,
               cohesion_weight=Config.COHESION_WEIGHT, food_weight=Config.FOOD_WEIGHT,
               escape_weight=Config.ESCAPE_WEIGHT):
        """主更新函数，处理鱼的所有行为和状态更新"""
        if not self.is_alive:
            return

        # ===================生命状态检查===================
        if self._check_death_conditions():
            return

        # ===================状态更新===================
        self._update_life_status(current_time)
        self._update_dynamic_parameters()

        # ===================行为计算===================
        self._reset_acceleration()
        behavior_weights = self._calculate_behavior_weights(day_night_factor, predators)

        # 应用各种行为力（传入权重参数）
        self._apply_flocking_behaviors(neighbors, behavior_weights, separation_weight, alignment_weight,
                                       cohesion_weight)
        self._apply_environmental_forces(water_current)
        self._apply_survival_behaviors(foods, predators, food_weight, escape_weight)

        # ===================物理更新===================
        self._update_physics(day_night_factor)
        self._update_visual_effects()

    def _check_death_conditions(self):
        """检查鱼是否应该死亡"""
        if self.hunger <= 0 or self.age > self.max_age:
            self.is_alive = False
            return True
        return False

    def _update_life_status(self, current_time):
        """更新生命状态（年龄、饥饿、成熟度等）"""
        self.age += 1
        self.hunger -= self.hunger_decay

        # 成熟度和繁殖能力检查
        if self.age > Config.FISH_REPRODUCTION_AGE:
            self.is_mature = True
            # 繁殖需要：成熟 + 冷却时间过期 + 饥饿值充足
            time_ready = (current_time - self.last_reproduction) > Config.FISH_BREED_COOLDOWN
            hunger_ready = self.hunger >= self.hunger_threshold_reproduction
            self.can_reproduce = time_ready and hunger_ready

        # 经验值更新（基于环境危险程度）
        self.experience += 0.01  # 基础经验增长

    def _update_dynamic_parameters(self):
        """从配置动态更新参数"""
        self.max_speed = Config.FISH_SPEED
        self.max_force = Config.FISH_FORCE
        self.size = Config.FISH_SIZE

    def _reset_acceleration(self):
        """重置加速度"""
        self.acceleration *= 0

    def _calculate_behavior_weights(self, day_night_factor, predators=None):
        """计算行为权重，考虑时间、环境和危险等因素"""
        margin = 50
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        map_height = Config.WINDOW_HEIGHT

        # 检查是否靠近边界
        near_border = (self.position.x < margin or self.position.x > map_width - margin or
                       self.position.y < margin or self.position.y > map_height - margin)

        # 检查是否有近距离威胁
        danger_level = 0
        if predators:
            for predator in predators:
                if predator.is_alive:
                    distance = self.position.distance_to(predator.position)
                    if distance < Config.ESCAPE_RADIUS * 1.5:  # 扩大危险感知范围
                        danger_level = max(danger_level,
                                           (Config.ESCAPE_RADIUS * 1.5 - distance) / (Config.ESCAPE_RADIUS * 1.5))

        # 夜晚聚集加成
        cohesion_multiplier = 1.0 + (1.0 - day_night_factor) * Config.NIGHT_COHESION_BONUS * 2

        # 危险状态下的行为调整
        if danger_level > 0:
            # 危险时大幅增强分离力，避免聚集成团
            separation_multiplier = 2.0 + danger_level * 3.0  # 最高可达5倍
            # 适度降低聚集力，避免过度聚集
            cohesion_multiplier *= max(0.3, 1.0 - danger_level * 0.7)
        else:
            separation_multiplier = 2.0 if near_border else 1.0

        return {
            'separation': separation_multiplier,
            'cohesion': (0.5 if near_border else 1.0) * cohesion_multiplier,
            'speed': day_night_factor * 0.8 + 0.2,
            'danger_level': danger_level
        }

    def _apply_flocking_behaviors(self, neighbors, weights, separation_weight, alignment_weight, cohesion_weight):
        """应用群体行为（分离、对齐、聚集、游荡）"""
        sep = self.separate(neighbors) * (separation_weight * weights['separation'])
        ali = self.align(neighbors) * alignment_weight
        coh = self.cohesion(neighbors) * (cohesion_weight * weights['cohesion'])
        wan = self.wander() * Config.WANDER_WEIGHT

        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)
        self.apply_force(wan)

    def _apply_environmental_forces(self, water_current):
        """应用环境力（水流、边界）"""
        if water_current:
            current_force = water_current * Config.CURRENT_STRENGTH
            self.apply_force(current_force)

        self.handle_boundaries()

    def _apply_survival_behaviors(self, foods, predators, food_weight, escape_weight):
        """应用生存行为（觅食、逃避）"""
        # 觅食行为
        if foods:
            food_force = self.seek_food(foods)
            self.apply_force(food_force * food_weight)

        # 逃避行为
        if predators:
            escape_force = self.flee_from_predators(predators)
            # 经验值影响逃避效果
            experience_multiplier = 1.0 + min(self.experience * 0.1, 0.5)
            self.apply_force(escape_force * escape_weight * experience_multiplier)

    def _update_physics(self, day_night_factor):
        """更新物理状态"""
        self.velocity += self.acceleration

        # 根据时间调整最大速度
        max_speed = self.max_speed * (day_night_factor * 0.8 + 0.2)
        self.velocity = limit_vector(self.velocity, max_speed)

        self.position += self.velocity

    def _update_visual_effects(self):
        """更新视觉效果"""
        self.update_trail()

        # 恐惧恢复（考虑抗恐慌能力）
        fear_recovery = 0.02 + self.panic_resistance * 0.01
        self.fear_level = max(0.0, self.fear_level - fear_recovery)

    # ===================群体行为方法===================
    def separate(self, neighbors):
        """分离行为 - 避免过度拥挤，特别是在危险情况下"""
        steer = Vector2(0, 0)
        count = 0

        for fish in neighbors:
            distance = self.position.distance_to(fish.position)
            separation_radius = Config.FISH_SEPARATION_RADIUS

            # 如果鱼儿在恐惧状态，增加分离半径
            if self.fear_level > 0:
                separation_radius *= (1.0 + self.fear_level * 0.5)

            if 0 < distance < separation_radius:
                diff = self.position - fish.position
                if diff.length() > 0:
                    # 距离越近，分离力越强（平方反比）
                    force_multiplier = (separation_radius - distance) / separation_radius
                    force_multiplier = force_multiplier * force_multiplier  # 平方关系，更强的分离力

                    diff = diff.normalize() * force_multiplier
                    steer += diff
                    count += 1

        if count > 0:
            steer /= count
            if steer.length() > 0:
                steer = steer.normalize() * self.max_speed - self.velocity
                # 在危险情况下，分离力可以超过正常最大力
                max_separation_force = self.max_force * (2.0 if self.fear_level > 0 else 1.0)
                steer = limit_vector(steer, max_separation_force)

        return steer

    def align(self, neighbors):
        """对齐行为 - 与邻居保持相同方向"""
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
        """聚集行为 - 向群体中心移动"""
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
        """游荡行为 - 随机移动，增加自然性"""
        if random.random() < 0.05:  # 5%的概率改变方向
            angle = random.uniform(0, 2 * math.pi)
            return Vector2(math.cos(angle), math.sin(angle)) * self.max_force
        return Vector2(0, 0)

    # ===================生存行为方法===================
    def seek_food(self, foods):
        """寻找食物"""
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
        """逃避捕食者"""
        flee_force = Vector2(0, 0)
        count = 0

        for predator in predators:
            if not predator.is_alive:
                continue

            distance = self.position.distance_to(predator.position)
            # 经验值增加探测范围
            detection_range = Config.ESCAPE_RADIUS + self.experience * 5

            if distance < detection_range:
                # 计算逃避方向
                escape_dir = self.position - predator.position
                if escape_dir.length() > 0:
                    escape_dir = escape_dir.normalize()

                    # 力的强度与距离成反比
                    force_magnitude = (detection_range - distance) / detection_range

                    # 如果捕食者在冲刺，增加恐惧和逃避力
                    if hasattr(predator, 'is_dashing') and predator.is_dashing:
                        force_magnitude *= 1.5
                        self.fear_level = min(1.0, self.fear_level + 0.1)
                        self.experience += 0.1  # 危险经历增加经验

                    # 添加随机扰动，避免过于机械化
                    escape_dir += Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
                    if escape_dir.length() > 0:
                        escape_dir = escape_dir.normalize()

                    flee_force += escape_dir * force_magnitude * 1.5
                    count += 1

        if count > 0:
            flee_force /= count

        return limit_vector(flee_force, self.max_force * 2)

    # ===================边界处理===================
    def handle_boundaries(self):
        """处理边界碰撞和边界力"""
        force = Vector2(0, 0)
        margin = 50.0
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        map_height = Config.WINDOW_HEIGHT

        # 水平边界：环绕处理
        if self.position.x < 0:
            self.position.x += map_width
            # 添加轻微随机扰动，避免重叠
            self.velocity += Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
        elif self.position.x > map_width:
            self.position.x -= map_width
            self.velocity += Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))

        # 垂直边界：柔和推力
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
        """应用力到加速度"""
        self.acceleration += force

    # ===================生存功能===================
    def feed(self, current_time):
        """进食，恢复饥饿值"""
        self.last_feed_time = current_time
        self.hunger = min(self.max_hunger, self.hunger + 20)

        # 刚进食后暂时不能繁殖（需要消化时间）
        self.can_reproduce = False

    def attempt_reproduction(self, current_time, adjusted_breed_chance, swarm):
        """尝试繁殖，考虑饥饿值和其他条件"""
        if not self._can_reproduce_now(current_time, swarm):
            return None

        # 检查繁殖条件
        hunger_bonus = 0 if self.hunger < self.hunger_threshold_reproduction else 0.1
        food_bonus = 0

        # 最近进食的鱼更容易繁殖
        if current_time - self.last_feed_time < 300:
            food_bonus = Config.FISH_FOOD_BREED_CHANCE

        total_chance = adjusted_breed_chance + hunger_bonus + food_bonus

        if random.random() < total_chance:
            self.last_reproduction = current_time
            self.can_reproduce = False
            # 繁殖消耗饥饿值
            self.hunger = max(0, self.hunger - 15)
            return self.create_offspring()

        return None

    def _can_reproduce_now(self, current_time, swarm):
        """检查是否满足繁殖的基本条件"""
        if not (self.can_reproduce and self.is_mature and self.is_alive):
            return False

        # 检查动态冷却时间
        breed_cooldown = swarm.balancer.adjusted_params.get('FISH_BREED_COOLDOWN', Config.FISH_BREED_COOLDOWN)
        if (current_time - self.last_reproduction) < breed_cooldown:
            return False

        # 检查饥饿值
        if self.hunger < self.hunger_threshold_reproduction:
            return False

        return True

    def create_offspring(self):
        """创建后代，继承部分特征"""
        offspring = Fish(self.position.x, self.position.y)

        # 后代继承父母的一些特征（带有随机变异）
        offspring.velocity = self.velocity.rotate(random.uniform(-30, 30))
        offspring.panic_resistance = max(0.3, min(1.0, self.panic_resistance + random.uniform(-0.1, 0.1)))
        offspring.max_age = max(3000, min(8000, self.max_age + random.randint(-300, 300)))

        return offspring

    # ===================视觉效果===================
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

        # 鱼的尺寸
        body_length = self.size * 2
        body_width = self.size
        tail_length = self.size * 1.5

        # 身体形状点
        front = self.position + direction * body_length
        left = self.position - perpendicular * body_width
        right = self.position + perpendicular * body_width

        # 尾部形状点
        tail_base_left = self.position - perpendicular * (body_width * 0.5)
        tail_base_right = self.position + perpendicular * (body_width * 0.5)
        tail_tip = self.position - direction * tail_length

        return [front, left, right], [tail_base_left, tail_tip, tail_base_right]

    def get_color(self, day_night_factor=1.0):
        """获取鱼的颜色，考虑恐惧状态和时间"""
        base_color = Config.COLORS['fish_body']

        # 恐惧状态影响颜色
        if self.fear_level > 0:
            fear_intensity = self.fear_level * 255
            return (
                min(255, base_color[0] + fear_intensity),
                max(0, base_color[1] - fear_intensity // 2),
                max(0, base_color[2] - fear_intensity // 2)
            )

        # 正常状态的颜色变化
        time_offset = pygame.time.get_ticks() * 0.002 + self.color_offset
        color_variation = math.sin(time_offset) * 30 * day_night_factor

        return (
            max(0, min(255, base_color[0] + color_variation)),
            max(0, min(255, base_color[1] + color_variation // 2)),
            max(0, min(255, base_color[2] + color_variation // 3))
        )

    # ===================状态查询方法===================
    def get_status_info(self):
        """获取鱼的状态信息，用于调试或UI显示"""
        return {
            'age': self.age,
            'hunger': self.hunger,
            'experience': self.experience,
            'fear_level': self.fear_level,
            'is_mature': self.is_mature,
            'can_reproduce': self.can_reproduce,
            'panic_resistance': self.panic_resistance
        }
