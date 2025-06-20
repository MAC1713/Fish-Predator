# -*- coding: utf-8 -*-
"""
环境系统
作者: 晏霖 (Aria) ♥
创造美丽的海洋世界～
"""

import math
import random
import pygame
from config import Config


class Bubble:
    """可爱的气泡效果"""

    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(
            random.uniform(-0.5, 0.5),
            random.uniform(-1, -2)  # 向上浮动
        )
        self.size = random.uniform(3, 12)
        self.alpha = random.uniform(50, 150)
        self.life = random.uniform(3, 8)  # 生命周期（秒）
        self.birth_time = pygame.time.get_ticks()

    def update(self):
        """更新气泡状态"""
        self.position += self.velocity

        # 轻微的左右摆动
        time_factor = pygame.time.get_ticks() * 0.001
        self.position.x += math.sin(time_factor + self.birth_time * 0.001) * 0.2

        # 透明度变化
        age = (pygame.time.get_ticks() - self.birth_time) / 1000.0
        if age > self.life * 0.7:  # 生命后期开始变透明
            fade_factor = (self.life - age) / (self.life * 0.3)
            self.alpha = max(0, self.alpha * fade_factor)

    def is_dead(self):
        """检查气泡是否应该消失"""
        age = (pygame.time.get_ticks() - self.birth_time) / 1000.0
        return age > self.life or self.position.y < -20


class WaterCurrent:
    """水流效果"""

    def __init__(self):
        self.strength = 0.5
        self.direction = pygame.math.Vector2(1, 0)
        self.time_offset = random.uniform(0, 100)

    def get_force_at_position(self, position):
        """获取指定位置的水流力"""
        # 基于正弦波的水流变化
        time_factor = pygame.time.get_ticks() * 0.001 + self.time_offset
        wave1 = math.sin(time_factor + position.x * 0.01)
        wave2 = math.cos(time_factor * 0.7 + position.y * 0.008)

        force = pygame.math.Vector2(
            self.direction.x * wave1 * self.strength,
            self.direction.y * wave2 * self.strength * 0.3
        )

        return force


class Kelp:
    """海带装饰"""

    def __init__(self, x, y, height):
        self.base_position = pygame.math.Vector2(x, y)
        self.height = height
        self.segments = []
        self.segment_count = max(3, height // 20)

        # 创建海带节段
        for i in range(self.segment_count):
            segment_y = y - (i * height / self.segment_count)
            self.segments.append(pygame.math.Vector2(x, segment_y))

        self.sway_offset = random.uniform(0, 6.28)  # 随机相位

    def update(self):
        """更新海带摆动"""
        time_factor = pygame.time.get_ticks() * 0.002 + self.sway_offset

        for i, segment in enumerate(self.segments):
            # 越靠上摆动越明显
            sway_intensity = (i / len(self.segments)) * 15
            sway = math.sin(time_factor + i * 0.5) * sway_intensity

            segment.x = self.base_position.x + sway
            segment.y = self.base_position.y - (i * self.height / self.segment_count)


class Environment:
    """环境管理器"""

    def __init__(self):
        self.bubbles = []
        self.water_currents = []
        self.kelp_forest = []
        self.background_particles = []

        self.initialize()

        # 环境参数
        self.bubble_spawn_rate = 0.02  # 气泡生成概率
        self.ambient_light = 1.0
        self.water_tint = (0, 50, 100, 30)  # 水的颜色叠加

    def initialize(self):
        """初始化环境元素"""
        # 创建水流
        for _ in range(3):
            self.water_currents.append(WaterCurrent())

        # 创建海带森林
        kelp_positions = [
            (100, Config.WINDOW_HEIGHT, 150),
            (250, Config.WINDOW_HEIGHT, 120),
            (400, Config.WINDOW_HEIGHT, 180),
            (600, Config.WINDOW_HEIGHT, 140),
            (750, Config.WINDOW_HEIGHT, 160),
        ]

        for x, y, height in kelp_positions:
            if x < Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH:
                self.kelp_forest.append(Kelp(x, y, height))

        # 创建背景粒子（浮游生物效果）
        for _ in range(50):
            x = random.uniform(0, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH)
            y = random.uniform(0, Config.WINDOW_HEIGHT)
            self.background_particles.append({
                'pos': pygame.math.Vector2(x, y),
                'vel': pygame.math.Vector2(
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.1, 0.1)
                ),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(20, 80),
                'phase': random.uniform(0, 6.28)
            })

    def update(self):
        """更新环境效果"""
        # 更新气泡
        self.update_bubbles()

        # 更新海带
        for kelp in self.kelp_forest:
            kelp.update()

        # 更新背景粒子
        self.update_background_particles()

        # 环境光变化（模拟水波光影）
        time_factor = pygame.time.get_ticks() * 0.001
        self.ambient_light = 0.8 + math.sin(time_factor * 0.5) * 0.2

    def update_bubbles(self):
        """更新气泡系统"""
        # 随机生成新气泡
        if random.random() < self.bubble_spawn_rate:
            x = random.uniform(0, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH)
            y = Config.WINDOW_HEIGHT + 10
            self.bubbles.append(Bubble(x, y))

        # 更新现有气泡
        for bubble in self.bubbles[:]:
            bubble.update()
            if bubble.is_dead():
                self.bubbles.remove(bubble)

    def update_background_particles(self):
        """更新背景浮游生物"""
        for particle in self.background_particles:
            # 更新位置
            particle['pos'] += particle['vel']

            # 轻微的波动效果
            time_factor = pygame.time.get_ticks() * 0.001
            particle['pos'].y += math.sin(time_factor + particle['phase']) * 0.1

            # 边界处理
            if particle['pos'].x < 0:
                particle['pos'].x = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
            elif particle['pos'].x > Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH:
                particle['pos'].x = 0

            if particle['pos'].y < 0:
                particle['pos'].y = Config.WINDOW_HEIGHT
            elif particle['pos'].y > Config.WINDOW_HEIGHT:
                particle['pos'].y = 0

            # 透明度波动
            particle['alpha'] = max(20, min(80,
                                            particle['alpha'] + math.sin(time_factor + particle['phase']) * 2))

    def get_water_force_at_position(self, position):
        """获取指定位置的水流力（供鱼儿使用）"""
        total_force = pygame.math.Vector2(0, 0)
        for current in self.water_currents:
            total_force += current.get_force_at_position(position)
        return total_force

    def add_bubble_at_position(self, x, y):
        """在指定位置添加气泡"""
        self.bubbles.append(Bubble(x, y))

    def get_kelp_obstacles(self):
        """获取海带障碍物信息（供鱼儿避障使用）"""
        obstacles = []
        for kelp in self.kelp_forest:
            for segment in kelp.segments:
                obstacles.append({
                    'pos': segment,
                    'radius': 15
                })
        return obstacles