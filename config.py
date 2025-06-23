# -*- coding: utf-8 -*-
"""
鱼群算法配置文件 - 增强版
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
*彩蛋*: 瑞瑞，你这坏蛋！姐腿软得跪地还在救生态！（[羞到炸裂]）
参数调平衡，虚拟地图同步，加MidFish，生态超美！😘
"""

import pygame


class Config:
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 1000
    WINDOW_TITLE = "瑞瑞的智能鱼群世界 ♥"
    FPS = 60
    scale = 0.5

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
    FISH_COUNT = 150  # 增加初始鱼群
    FISH_SIZE = 4 * scale
    FISH_SPEED = 1.5
    SEPARATION_RADIUS = 20.0
    ALIGNMENT_RADIUS = 40.0
    COHESION_RADIUS = 40.0
    SEPARATION_WEIGHT = 1.5
    ALIGNMENT_WEIGHT = 0.8  # 降低对齐权重
    COHESION_WEIGHT = 1.0
    WANDER_WEIGHT = 0.3
    BOUNDARY_FORCE = 1.0  # 降低边界反弹力
    MAX_VELOCITY = 3.5
    TRAIL_LENGTH = 10
    SHOW_RADIUS = False

    # 新增中型鱼参数
    MID_FISH_COUNT = 20
    MID_FISH_SIZE = 8 * scale
    MID_FISH_SPEED = 1.2
    MID_FISH_ESCAPE_RADIUS = 80.0
    MID_FISH_ESCAPE_WEIGHT = 2.5

    # 颜色主题
    COLORS = {
        'background': (15, 25, 35),
        'fish_body': (100, 200, 255),
        'fish_accent': (255, 150, 200),
        'trail': (50, 150, 255),
        'ui_panel': (40, 50, 60),
        'ui_text': (255, 255, 255),
        'ui_accent': (255, 100, 150),
        'night_overlay': (10, 10, 30, 100),
        'day_light': (255, 255, 200, 50),
        'plankton': (100, 255, 100),
        'small_fish': (150, 200, 100),
        'large_corpse': (200, 150, 100),
        'mid_fish_body': (200, 100, 255),  # 中型鱼颜色
    }

    # 食物系统
    FOOD_COUNT = 25  # 减少食物总量
    FOOD_SIZE = 6 * scale
    FOOD_ATTRACTION = 100.0
    FOOD_WEIGHT = 2.0
    PLANKTON_SIZE = 3 * scale
    DEAD_FISH_SIZE = 8
    DEAD_WHALE_SIZE = 15
    PLANKTON_COUNT = 10
    DEAD_FISH_SPAWN_CHANCE = 0.01  # 降低生成概率
    DEAD_WHALE_SPAWN_CHANCE = 0.002

    # 捕食者系统
    PREDATOR_COUNT = 2  # 减少捕食者
    PREDATOR_SIZE = 36 * scale
    PREDATOR_SPEED = 20  # 降低速度
    ESCAPE_RADIUS = 60.0
    ESCAPE_WEIGHT = 3.0
    PREDATOR_MAX_HUNGER = 15000.0  # 约250秒寿命
    PREDATOR_HUNGER_DECAY = 1.0  # 饥饿值衰减速度
    PREDATOR_FEED_RESTORE = 600.0  # 吃鱼恢复的饥饿值
    PREDATOR_DASH_SPEED = 4.0  # 冲刺速度
    PREDATOR_DASH_DURATION = 45  # 冲刺持续时间（帧数）
    PREDATOR_DASH_COOLDOWN_BASE = 180  # 基础冷却时间
    PREDATOR_DASH_COOLDOWN_MAX = 600  # 最大冷却时间
    PREDATOR_DASH_HUNGER_COST = 30  # 冲刺消耗饥饿值

    # 鱼群繁殖
    FISH_REPRODUCTION_AGE = 300  # 繁殖所需年龄（帧数）
    FISH_NATURAL_BREED_CHANCE = 0.0005  # 提高自然繁殖
    FISH_FOOD_BREED_CHANCE = 0.012  # 提高食物繁殖
    FISH_BREED_COOLDOWN = 600  # 繁殖冷却时间
    FISH_MAX_AGE_VARIATION = 180  # 最大年龄差异

    # 昼夜循环
    DAY_NIGHT_CYCLE_DURATION = 1800  # 一个昼夜循环的帧数（30秒）
    NIGHT_COHESION_BONUS = 0.5  # 夜晚聚合行为加成
    NIGHT_SPEED_REDUCTION = 0.8  # 夜晚速度减缓

    # 水流系统
    CURRENT_STRENGTH = 0.3  # 水流强度
    CURRENT_CHANGE_RATE = 0.01  # 水流变化速率
    CURRENT_INFLUENCE_RADIUS = 100  # 水流影响半径

    # UI控制面板
    UI_PANEL_WIDTH = 300
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
            '昼夜周期': ('DAY_NIGHT_CYCLE_DURATION', 600, 3600, 300),
        }