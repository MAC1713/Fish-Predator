import math
import random

import pygame
from pygame.math import Vector2

from common_def import limit_vector
from food import Food
from config import Config


class Predator:
    """
    增强版捕食者类 - 更智能的狩猎行为和生存机制

    主要功能：
    - 动态狩猎：根据饥饿程度调整行为
    - 智能冲刺：消耗饥饿值进行爆发性攻击
    - 生命周期：幼年->成年->老年的成长过程
    - 繁殖系统：成年期可以繁殖后代
    - 动态平衡：从balancer获取调整后的参数
    """

    def __init__(self, x, y):
        # === 基础属性 ===
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * Config.PREDATOR_SPEED
        self.acceleration = Vector2(0, 0)

        # === 物理属性 ===
        self.size = Config.PREDATOR_SIZE
        self.max_speed = Config.PREDATOR_SPEED
        self.max_force = Config.PREDATOR_MAX_FORCE

        # === 生存属性 ===
        self.hunger = Config.PREDATOR_MAX_HUNGER
        self.is_alive = True
        self.age = 0
        self.max_age = Config.PREDATOR_MAX_AGE
        self.growth_stage = 'juvenile'  # 幼年期

        # === 狩猎系统 ===
        self.hunt_target = None
        self.last_feed_time = 0
        self.feed_frequency = []  # 记录最近的进食时间

        # === 冲刺系统 ===
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_direction = Vector2(0, 0)

        # === 视觉效果 ===
        self.trail = []  # 移动轨迹
        self.color_offset = random.random() * math.pi * 2  # 颜色偏移，用于个体差异

    def update(self, fishes, mid_fishes, current_time, swarm):
        """主更新函数"""
        if not self.is_alive:
            return

        # 更新动态参数
        self._update_dynamic_params(swarm)

        # 生命周期管理
        self._update_life_cycle(swarm)
        if not self.is_alive:
            return

        # 行为更新
        self._update_dash_system(current_time)
        self._check_feeding(fishes, mid_fishes, current_time, swarm)
        self._update_movement(fishes, mid_fishes)
        self._update_reproduction(current_time, swarm)
        self._update_trail()

    def _update_dynamic_params(self, swarm):
        """从平衡器获取动态参数"""
        balancer = swarm.balancer.adjusted_params
        self.max_speed = balancer.get('PREDATOR_SPEED', Config.PREDATOR_SPEED)
        self.max_force = balancer.get('PREDATOR_MAX_FORCE', Config.PREDATOR_MAX_FORCE)
        self.size = balancer.get('PREDATOR_SIZE', Config.PREDATOR_SIZE)

        # 饥饿值衰减
        hunger_decay = balancer.get('PREDATOR_HUNGER_DECAY', Config.PREDATOR_HUNGER_DECAY)
        self.hunger -= hunger_decay

    def _update_life_cycle(self, swarm):
        """生命周期管理：成长、衰老、死亡"""
        self.age += 1

        # 死亡条件检查
        if self.hunger <= 0 or self.age > self.max_age:
            self.is_alive = False
            # 死亡后变成大块食物
            swarm.foods.append(Food(self.position.x, self.position.y, 'large_corpse'))
            return

        # 成长阶段更新
        self._update_growth_stage()

    def _update_growth_stage(self):
        """更新成长阶段和相应属性"""
        if self.age < 3600:  # 幼年期 (~1分钟)
            self.growth_stage = 'juvenile'
            self.size = Config.PREDATOR_SIZE * 0.7
            # 幼年期更加活跃
            self.max_speed = Config.PREDATOR_SPEED * 1.2
        elif self.age < 20000:  # 成年期 (~3分钟)
            self.growth_stage = 'adult'
            self.size = Config.PREDATOR_SIZE
            self.max_speed = Config.PREDATOR_SPEED
        else:  # 老年期
            self.growth_stage = 'senior'
            self.size = Config.PREDATOR_SIZE * 1.2
            # 老年期行动变慢
            self.max_speed = Config.PREDATOR_SPEED * 0.8

    def _update_movement(self, fishes, mid_fishes):
        """根据饥饿程度和冲刺状态更新移动"""
        self.acceleration = Vector2(0, 0)

        if self.is_dashing:
            # 冲刺状态：直线高速移动
            self.velocity = self.dash_direction
        else:
            # 正常状态：根据饥饿程度调整行为
            hunger_ratio = self.get_hunger_ratio()

            if hunger_ratio > 0.7:
                # 不饿时：缓慢巡游，节约能量
                self._cruise_behavior()
            else:
                # 饿了时：积极狩猎
                steer = self._hunt_behavior(fishes, mid_fishes)
                self.apply_force(steer)

            # 边界处理和速度限制
            self._handle_boundaries()
            self.velocity += self.acceleration

            # 根据饥饿程度调整速度
            current_max_speed = self._get_hunger_adjusted_speed()
            self.velocity = limit_vector(self.velocity, current_max_speed)

        self.position += self.velocity

    def _get_hunger_adjusted_speed(self):
        """根据饥饿程度调整最大速度"""
        hunger_ratio = self.get_hunger_ratio()

        if hunger_ratio > 0.8:
            # 很饱：游得很慢，节约能量
            return self.max_speed * 0.3
        elif hunger_ratio > 0.5:
            # 一般饱：正常速度
            return self.max_speed * 0.6
        elif hunger_ratio > 0.2:
            # 有点饿：加快速度
            return self.max_speed * 0.9
        else:
            # 很饿：全速狩猎
            return self.max_speed

    def _cruise_behavior(self):
        """巡游行为：不饿时的缓慢随机移动"""
        if random.random() < 0.01:  # 降低转向频率
            angle = random.uniform(0, 2 * math.pi)
            desired_velocity = Vector2(math.cos(angle), math.sin(angle)) * self.max_speed * 0.3
            steer = desired_velocity - self.velocity
            self.apply_force(steer * 0.1)  # 更温和的转向

    def _hunt_behavior(self, fishes, mid_fishes):
        """狩猎行为：寻找并追击目标"""
        hunger_ratio = self.get_hunger_ratio()

        # 收集所有可能的目标
        targets = self._collect_targets(fishes, mid_fishes)
        if not targets:
            self._wander()
            return Vector2(0, 0)

        # 根据饥饿程度调整探测范围
        detection_range = Config.PREDATOR_HUNTER_RANGE_MAX * (1.0 - hunger_ratio)

        # 寻找最佳目标
        best_target = self._find_best_target(targets, detection_range)

        if best_target:
            target_obj, distance = best_target
            self.hunt_target = target_obj

            # 决定是否冲刺
            if self._should_initiate_dash(distance):
                self._initiate_dash(target_obj)
            else:
                return self._pursue_target(target_obj)
        else:
            self.hunt_target = None
            self._wander()

        return Vector2(0, 0)

    def _collect_targets(self, fishes, mid_fishes):
        """收集所有活着的目标"""
        targets = []

        # 小鱼目标
        for fish in fishes:
            if fish.is_alive:
                targets.append((fish, fish.position, fish.max_speed, 'fish'))

        # 中鱼目标
        for mid_fish in mid_fishes:
            if mid_fish.is_alive:
                targets.append((mid_fish, mid_fish.position, mid_fish.max_speed, 'mid_fish'))

        return targets

    def _find_best_target(self, targets, detection_range):
        """寻找最佳狩猎目标"""
        target_candidates = []

        for target_obj, pos, speed, fish_type in targets:
            distance = self.position.distance_to(pos)

            if distance < detection_range:
                # 计算目标优先级
                priority = self._calculate_target_priority(distance, speed, fish_type, detection_range)
                target_candidates.append((target_obj, priority, distance))

        if target_candidates:
            # 按优先级排序，返回最佳目标
            target_candidates.sort(key=lambda x: x[1], reverse=True)
            best_target_obj, _, distance = target_candidates[0]
            return (best_target_obj, distance)

        return None

    def _calculate_target_priority(self, distance, speed, fish_type, detection_range):
        """计算目标优先级分数"""
        # 距离优先级：越近越好
        distance_priority = (detection_range - distance) / detection_range * 100

        # 速度优先级：越慢越容易抓
        speed_priority = min(200.0, 100.0 / max(0.5, speed))

        # 类型优先级：根据配置决定偏好
        if fish_type == 'fish':
            type_priority = Config.PREDATOR_HUNT_FISH_WEIGHT
        else:  # mid_fish
            type_priority = Config.PREDATOR_HUNT_MID_FISH_WEIGHT

        # 综合优先级计算
        total_priority = (distance_priority * 0.4 +
                          speed_priority * 0.3 +
                          type_priority * 0.3)

        return total_priority

    def _should_initiate_dash(self, target_distance):
        """判断是否应该发起冲刺"""
        # 距离条件：不能太近也不能太远
        if not (40 < target_distance < 120):
            return False

        # 冷却时间检查
        if self.dash_cooldown > 0:
            return False

        # 饥饿程度检查：太饱了不需要冲刺
        hunger_ratio = self.get_hunger_ratio()
        if hunger_ratio >= 0.8:
            return False

        # 基于饥饿程度和最近捕获情况的概率计算
        hunger_factor = 1.0 - hunger_ratio  # 越饿冲刺欲望越强
        recent_kills = len([t for t in self.feed_frequency if pygame.time.get_ticks() - t < 3600])
        kill_penalty = min(recent_kills * 0.3, 0.8)  # 最近捕获太多会降低冲刺欲望

        dash_probability = 0.01 + hunger_factor * 0.05 - kill_penalty
        return random.random() < dash_probability

    def _initiate_dash(self, target):
        """发起冲刺攻击"""
        self.is_dashing = True
        self.dash_timer = Config.PREDATOR_DASH_DURATION

        # 预测目标位置
        target_future_pos = target.position + target.velocity * 10
        dash_direction = target_future_pos - self.position

        if dash_direction.length() > 0:
            self.dash_direction = dash_direction.normalize() * self.max_speed * 2  # 冲刺时速度翻倍
        else:
            self.dash_direction = self.velocity.normalize() * self.max_speed * 2

        # 消耗饥饿值
        self.hunger -= Config.PREDATOR_DASH_HUNGER_COST

        # 设置冷却时间
        recent_kills = len(self.feed_frequency)
        self.dash_cooldown = int(Config.PREDATOR_DASH_COOLDOWN_BASE * (1.0 + min(recent_kills * 0.5, 3.0)))

    def _update_dash_system(self, current_time):
        """更新冲刺系统状态"""
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def _check_feeding(self, fishes, mid_fishes, current_time, swarm):
        """检查并处理进食"""
        # 如果太饱就不进食
        max_hunger = swarm.balancer.adjusted_params.get('PREDATOR_MAX_HUNGER', Config.PREDATOR_MAX_HUNGER)
        if self.hunger >= max_hunger * 0.8:
            return

        # 检查小鱼
        for fish in fishes[:]:
            if self.position.distance_to(fish.position) < self.size + fish.size:
                fish.is_alive = False
                self._feed_on_fish(current_time, energy=50, swarm=swarm)
                return

        # 检查中鱼
        for mid_fish in mid_fishes[:]:
            if self.position.distance_to(mid_fish.position) < self.size + mid_fish.size:
                mid_fish.is_alive = False
                self._feed_on_fish(current_time, energy=80, swarm=swarm)
                return

    def _feed_on_fish(self, current_time, energy, swarm):
        """进食处理"""
        max_hunger = swarm.balancer.adjusted_params.get('PREDATOR_MAX_HUNGER', Config.PREDATOR_MAX_HUNGER)

        # 恢复饥饿值
        hunger_restore = Config.PREDATOR_FEED_RESTORE * (energy / 50)
        self.hunger = min(max_hunger, self.hunger + hunger_restore)

        # 记录进食信息
        self.last_feed_time = current_time
        self.feed_frequency.append(current_time)

        # 保持进食记录在合理范围内
        if len(self.feed_frequency) > 10:
            self.feed_frequency.pop(0)

    def _update_reproduction(self, current_time, swarm):
        """更新繁殖系统"""
        # 只有成年期且饥饿值足够才能繁殖
        if (self.growth_stage != 'adult' or
                self.hunger <= Config.PREDATOR_MAX_HUNGER * 0.6):  # 需要60%以上饥饿值
            return

        # 寻找配偶
        for other in swarm.predators:
            if (other != self and
                    other.growth_stage == 'adult' and
                    other.is_alive and
                    other.hunger > Config.PREDATOR_MAX_HUNGER * 0.6 and
                    self.position.distance_to(other.position) < 100):
                # 繁殖成功
                offspring_x = (self.position.x + other.position.x) / 2
                offspring_y = (self.position.y + other.position.y) / 2
                swarm.predators.append(Predator(offspring_x, offspring_y))

                # 繁殖消耗饥饿值
                self.hunger -= Config.PREDATOR_MAX_HUNGER * 0.2
                other.hunger -= Config.PREDATOR_MAX_HUNGER * 0.2
                break

    def _pursue_target(self, target):
        """追击目标"""
        prediction_time = 15
        predicted_pos = target.position + target.velocity * prediction_time
        desired = predicted_pos - self.position

        if desired.length() > 0:
            desired = desired.normalize() * self.max_speed
            steer = desired - self.velocity
            steer = limit_vector(steer, self.max_force)
            return steer

        return Vector2(0, 0)

    def _wander(self):
        """随机游荡"""
        if random.random() < 0.03:
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = Vector2(math.cos(angle), math.sin(angle)) * self.max_speed * 0.7

    def _handle_boundaries(self):
        """处理边界碰撞"""
        margin = 30
        map_width = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH

        # 水平边界：环绕
        if self.position.x < 0:
            self.position.x += map_width
        elif self.position.x > map_width:
            self.position.x -= map_width

        # 垂直边界：反弹
        if self.position.y < margin:
            self.velocity.y = abs(self.velocity.y)
            self.position.y = margin
        elif self.position.y > Config.WINDOW_HEIGHT - margin:
            self.velocity.y = -abs(self.velocity.y)
            self.position.y = Config.WINDOW_HEIGHT - margin

    def _update_trail(self):
        """更新移动轨迹"""
        self.trail.append(self.position.copy())
        if len(self.trail) > Config.TRAIL_LENGTH:
            self.trail.pop(0)

    def apply_force(self, force):
        """应用力到加速度"""
        self.acceleration += force

    def get_hunger_ratio(self):
        """获取饥饿程度比例(0-1)"""
        return self.hunger / Config.PREDATOR_MAX_HUNGER
