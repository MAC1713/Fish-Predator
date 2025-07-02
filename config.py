# -*- coding: utf-8 -*-
"""
鱼群算法配置文件 - 增强版
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
"""

import pygame


class Config:
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 1000
    WINDOW_TITLE = "瑞瑞的智能鱼群世界 ♥"
    UI_PANEL_WIDTH = 200
    FPS = 60
    scale = 0.5

    FISH_COUNT = 150
    MID_FISH_COUNT = 50
    FOOD_COUNT = 100
    PREDATOR_COUNT = 3
    TRAIL_LENGTH = 10

    FISH_SIZE = 5 * scale
    MID_FISH_SIZE = 8 * scale
    FOOD_SIZE = 3 * scale
    PREDATOR_SIZE = 15 * scale
    FISH_SPEED = 2.0
    MID_FISH_SPEED = 1.5
    PREDATOR_SPEED = 3.0
    PREDATOR_DASH_SPEED = 6.0
    PREDATOR_DASH_DURATION = 30
    PREDATOR_DASH_COOLDOWN_BASE = 120
    PREDATOR_MAX_HUNGER = 30000.0  # 约250秒寿命
    PREDATOR_HUNGER_DECAY = 20.0  # 饥饿值衰减速度
    PREDATOR_FEED_RESTORE = 1000.0  # 吃鱼恢复的饥饿值
    PREDATOR_HUNTER_RANGE_MAX = 500.0  # 最大猎食范围
    PREDATOR_DASH_COOLDOWN_MAX = 600  # 最大冷却时间
    PREDATOR_DASH_HUNGER_COST = 30  # 冲刺消耗饥饿值

    SEPARATION_RADIUS = 25
    ALIGNMENT_RADIUS = 50
    COHESION_RADIUS = 30
    FOOD_DETECTION_RADIUS = 100
    ESCAPE_RADIUS = 30.0
    MID_FISH_ESCAPE_RADIUS = 40.0
    SEPARATION_WEIGHT = 2.0
    ALIGNMENT_WEIGHT = 1.0
    COHESION_WEIGHT = 1.0
    FOOD_WEIGHT = 1.0
    ESCAPE_WEIGHT = 1.5
    MID_FISH_ESCAPE_WEIGHT = 1.8
    WANDER_WEIGHT = 0.5
    BOUNDARY_FORCE = 0.5
    CURRENT_STRENGTH = 0.5

    FISH_NATURAL_BREED_CHANCE = 0.00005
    FISH_FOOD_BREED_CHANCE = 0.001
    FISH_REPRODUCTION_AGE = 600
    FISH_BREED_COOLDOWN = 1800
    DAY_NIGHT_CYCLE = 30
    NIGHT_COHESION_BONUS = 1.0
    NIGHT_SPEED_REDUCTION = 0.8

    SHOW_RADIUS = False

    # 动态地图大小，适配窗口
    @classmethod
    def update_map_size(cls, width, height):
        cls.WINDOW_WIDTH = width
        cls.WINDOW_HEIGHT = height
        cls.VIRTUAL_MAP_WIDTH = cls.WINDOW_WIDTH - cls.UI_PANEL_WIDTH
        cls.VIRTUAL_MAP_HEIGHT = cls.WINDOW_HEIGHT
        cls.UI_PANEL_X = cls.WINDOW_WIDTH - cls.UI_PANEL_WIDTH

    # 地图设置与实际窗口同步
    VIRTUAL_MAP_WIDTH = WINDOW_WIDTH - 300  # 排除UI面板
    VIRTUAL_MAP_HEIGHT = WINDOW_HEIGHT
    CAMERA_X = 0
    CAMERA_Y = 0

    # 鱼群参数
    MAX_VELOCITY = 3.5

    # 颜色主题
    COLORS = {
        'background': (15, 25, 35),
        'fish_body': (100, 200, 255),
        'fish_accent': (255, 150, 200),
        'trail': (50, 150, 255),
        'ui_panel': (40, 50, 60),
        'ui_text': (255, 255, 255),
        'ui_accent': (255, 255, 0),
        'night_overlay': (10, 10, 30, 100),
        'day_light': (255, 255, 200, 50),
        'plankton': (100, 255, 100),
        'small_fish': (150, 200, 100),
        'large_corpse': (200, 150, 100),
        'mid_fish_body': (255, 150, 100),  # 中型鱼颜色
    }

    # 食物系统
    FOOD_ATTRACTION = 100.0
    PLANKTON_SIZE = 3 * scale
    DEAD_FISH_SIZE = 8
    DEAD_WHALE_SIZE = 15
    PLANKTON_COUNT = 10
    DEAD_FISH_SPAWN_CHANCE = 0.01  # 生成概率
    DEAD_WHALE_SPAWN_CHANCE = 0.002

    # 鱼群繁殖
    FISH_MAX_AGE_VARIATION = 180  # 最大年龄差异

    # 水流系统
    CURRENT_CHANGE_RATE = 0.01  # 水流变化速率
    CURRENT_INFLUENCE_RADIUS = 100  # 水流影响半径

    # UI控制面板
    UI_PANEL_X = WINDOW_WIDTH - UI_PANEL_WIDTH

    @classmethod
    def get_adjustable_params(cls):
        return {
            '鱼群数量': ('FISH_COUNT', 50, 300, 5),
            '中型鱼数量': ('MID_FISH_COUNT', 10, 50, 5),
            '游泳速度': ('FISH_SPEED', 0.5, 4.0, 0.1),
            '分离半径': ('SEPARATION_RADIUS', 10.0, 80.0, 5.0),
            '对齐半径': ('ALIGNMENT_RADIUS', 20.0, 120.0, 5.0),
            '聚合半径': ('COHESION_RADIUS', 20.0, 120.0, 5.0),
            '分离权重': ('SEPARATION_WEIGHT', 0.0, 3.0, 0.1),
            '对齐权重': ('ALIGNMENT_WEIGHT', 0.0, 3.0, 0.1),
            '聚合权重': ('COHESION_WEIGHT', 0.0, 3.0, 0.1),
            '觅食权重': ('FOOD_WEIGHT', 0.0, 5.0, 0.1),
            '最大速度': ('MAX_VELOCITY', 1.0, 8.0, 0.2),
            '水流强度': ('CURRENT_STRENGTH', 0.0, 1.0, 0.05),
            '昼夜周期': ('DAY_NIGHT_CYCLE', 10, 60, 5),
        }
