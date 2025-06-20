# -*- coding: utf-8 -*-
"""
鱼群算法配置文件 - 增强版
作者: 晏霖 (Aria) ♥
为瑞瑞特制的更真实鱼群系统～
"""

import pygame


class Config:
    """鱼群系统配置类"""

    # 窗口设置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_TITLE = "瑞瑞的智能鱼群世界 ♥"
    FPS = 60

    # 地图扩大设置
    VIRTUAL_MAP_WIDTH = 2400  # 虚拟地图宽度（实际显示区域的2倍）
    VIRTUAL_MAP_HEIGHT = 1600  # 虚拟地图高度
    CAMERA_X = 0  # 摄像机位置
    CAMERA_Y = 0

    # 鱼群基础参数 - 缩小版
    FISH_COUNT = 120  # 增加鱼的数量来补偿地图变大
    FISH_SIZE = 4  # 缩小鱼的大小
    FISH_SPEED = 1.5  # 稍微降低基础速度

    # 鱼群行为参数
    SEPARATION_RADIUS = 20.0
    ALIGNMENT_RADIUS = 40.0
    COHESION_RADIUS = 40.0

    # 行为权重
    SEPARATION_WEIGHT = 1.5
    ALIGNMENT_WEIGHT = 1.0
    COHESION_WEIGHT = 1.0
    WANDER_WEIGHT = 0.3

    # 环境参数
    BOUNDARY_FORCE = 2.0
    MAX_VELOCITY = 3.5

    # 视觉效果
    TRAIL_LENGTH = 10  # 缩短尾迹以提高性能
    SHOW_RADIUS = False

    # 颜色主题
    COLORS = {
        'background': (15, 25, 35),
        'fish_body': (100, 200, 255),
        'fish_accent': (255, 150, 200),
        'trail': (50, 150, 255),
        'ui_panel': (40, 50, 60),
        'ui_text': (255, 255, 255),
        'ui_accent': (255, 100, 150),
        'night_overlay': (10, 10, 30, 100),  # 夜晚遮罩
        'day_light': (255, 255, 200, 50),  # 白天光效
        'plankton': (100, 255, 100),  # 浮游食物
        'small_fish': (150, 200, 100),  # 小鱼尸体
        'large_corpse': (200, 150, 100),  # 大鱼尸体
    }

    # 食物系统 - 多样化
    FOOD_COUNT = 50
    FOOD_SIZE = 6  # 缩小基础食物
    FOOD_ATTRACTION = 100.0
    FOOD_WEIGHT = 2.0

    # 新增：三种食物类型
    PLANKTON_SIZE = 3  # 浮游生物大小
    DEAD_FISH_SIZE = 8  # 死鱼大小
    DEAD_WHALE_SIZE = 15  # 死鲸鱼大小

    PLANKTON_COUNT = 15  # 浮游生物数量
    DEAD_FISH_SPAWN_CHANCE = 0.005  # 死鱼生成概率（每帧）
    DEAD_WHALE_SPAWN_CHANCE = 0.001  # 死鲸鱼生成概率

    # 捕食者系统 - 缩小版
    PREDATOR_COUNT = 3
    PREDATOR_SIZE = 12  # 缩小捕食者
    PREDATOR_SPEED = 1.2
    ESCAPE_RADIUS = 60.0
    ESCAPE_WEIGHT = 3.0

    # 新增：捕食者寿命和冲刺系统
    PREDATOR_MAX_HUNGER = 300.0  # 最大饥饿值（秒数*FPS）
    PREDATOR_HUNGER_DECAY = 1.0  # 饥饿值衰减速度
    PREDATOR_FEED_RESTORE = 120.0  # 吃鱼恢复的饥饿值

    PREDATOR_DASH_SPEED = 4.0  # 冲刺速度
    PREDATOR_DASH_DURATION = 45  # 冲刺持续时间（帧数）
    PREDATOR_DASH_COOLDOWN_BASE = 180  # 基础冷却时间
    PREDATOR_DASH_COOLDOWN_MAX = 600  # 最大冷却时间
    PREDATOR_DASH_HUNGER_COST = 30  # 冲刺消耗饥饿值

    # 鱼群繁殖系统
    FISH_REPRODUCTION_AGE = 300  # 繁殖所需年龄（帧数）
    FISH_NATURAL_BREED_CHANCE = 0.0003  # 自然繁殖概率
    FISH_FOOD_BREED_CHANCE = 0.008  # 进食后繁殖概率
    FISH_BREED_COOLDOWN = 600  # 繁殖冷却时间
    FISH_MAX_AGE_VARIATION = 180  # 最大年龄差异

    # 昼夜循环系统
    DAY_NIGHT_CYCLE_DURATION = 1800  # 一个昼夜循环的帧数（30秒）
    NIGHT_COHESION_BONUS = 0.5  # 夜晚聚合行为加成
    NIGHT_SPEED_REDUCTION = 0.8  # 夜晚速度减缓

    # 水流系统
    CURRENT_STRENGTH = 0.3  # 水流强度
    CURRENT_CHANGE_RATE = 0.01  # 水流变化速率
    CURRENT_INFLUENCE_RADIUS = 100  # 水流影响半径

    # UI控制面板位置
    UI_PANEL_WIDTH = 300
    UI_PANEL_X = WINDOW_WIDTH - UI_PANEL_WIDTH

    @classmethod
    def get_adjustable_params(cls):
        """返回可在UI中调整的参数列表"""
        return {
            '鱼群数量': ('FISH_COUNT', 50, 300, 5),
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