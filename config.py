# -*- coding: utf-8 -*-
"""
鱼群算法配置文件 - Nova优化版，参数全统一，动态调整丝滑 ♥
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
备注: 所有动态调整参数集中在此，确保SmartEcosystemBalancer实时生效
"""


class Config:
    # 窗口和UI设置
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 1000
    WINDOW_TITLE = "瑞瑞的智能鱼群世界 ♥"
    UI_PANEL_WIDTH = 200
    FPS = 60
    scale = 0.5

    # 初始数量
    FISH_COUNT = 150  # 小鱼初始数量
    MID_FISH_COUNT = 50  # 中型鱼初始数量
    FOOD_COUNT = 100  # 食物初始数量，动态调整范围 (50, 200)
    PREDATOR_COUNT = 3  # 捕食者初始数量

    # 小鱼参数
    FISH_SIZE = 5 * scale  # 小鱼大小，动态调整范围 (5.0, 15.0)
    FISH_SPEED = 2.0  # 小鱼最大速度，动态调整范围 (2.0, 8.0)
    FISH_FORCE = 0.3  # 小鱼最大加速度，动态调整范围 (0.1, 0.6)
    FISH_COHESION_RADIUS = 30.0  # 小鱼聚合半径，动态调整范围 (50.0, 150.0)
    FISH_SEPARATION_RADIUS = 25.0  # 小鱼分离半径，动态调整范围 (10.0, 50.0)
    FISH_ALIGNMENT_RADIUS = 50.0  # 小鱼对齐半径，动态调整范围 (20.0, 100.0)
    FISH_NATURAL_BREED_CHANCE = 0.00005  # 小鱼自然繁殖概率，动态调整范围 (0.00005, 0.0002)
    FISH_FOOD_BREED_CHANCE = 0.001  # 小鱼食物触发繁殖概率
    FISH_REPRODUCTION_AGE = 600  # 小鱼成熟年龄
    FISH_BREED_COOLDOWN = 1800  # 小鱼繁殖冷却时间

    # 中型鱼参数
    MID_FISH_SIZE = 8 * scale  # 中型鱼大小，动态调整范围 (10.0, 20.0)
    MID_FISH_SPEED = 1.5  # 中型鱼最大速度，动态调整范围 (3.0, 10.0)
    MID_FISH_FORCE = 0.06  # 中型鱼最大加速度，动态调整范围 (0.05, 0.3)
    MID_FISH_COHESION_RADIUS = 45.0  # 中型鱼聚合半径，动态调整范围 (75.0, 200.0)
    MID_FISH_SEPARATION_RADIUS = 37.5  # 中型鱼分离半径，动态调整范围 (15.0, 60.0)
    MID_FISH_ALIGNMENT_RADIUS = 75.0  # 中型鱼对齐半径，动态调整范围 (30.0, 120.0)
    MID_FISH_BREED_CHANCE = 0.0005  # 中型鱼自然繁殖概率，动态调整范围 (0.00003, 0.00015)

    # 捕食者参数
    PREDATOR_SIZE = 15 * scale  # 捕食者大小，动态调整范围 (20.0, 40.0)
    PREDATOR_SPEED = 3.0  # 捕食者最大速度，动态调整范围 (5.0, 15.0)
    PREDATOR_MAX_FORCE = 0.15  # 捕食者最大加速度，动态调整范围 (0.1, 0.5)
    PREDATOR_HUNGER_DECAY = 20.0  # 捕食者饥饿衰减速度，动态调整范围 (8.0, 25.0)
    PREDATOR_DASH_SPEED = 6.0  # 捕食者冲刺速度
    PREDATOR_DASH_DURATION = 30  # 冲刺持续时间
    PREDATOR_DASH_COOLDOWN_BASE = 120  # 冲刺冷却基础时间
    PREDATOR_MAX_HUNGER = 30000.0  # 捕食者最大饥饿值（约250秒寿命）
    PREDATOR_FEED_RESTORE = 1000.0  # 吃鱼恢复的饥饿值
    PREDATOR_HUNTER_RANGE_MAX = 500.0  # 最大猎食范围
    PREDATOR_DASH_COOLDOWN_MAX = 600  # 最大冷却时间
    PREDATOR_DASH_HUNGER_COST = 30  # 冲刺消耗饥饿值

    # 行为权重
    SEPARATION_WEIGHT = 2.0  # 分离权重，动态调整范围 (1.0, 3.5)
    ALIGNMENT_WEIGHT = 1.0  # 对齐权重，动态调整范围 (0.5, 2.5)
    COHESION_WEIGHT = 1.0  # 聚合权重，动态调整范围 (0.5, 2.5)
    FOOD_WEIGHT = 1.0  # 觅食权重，动态调整范围 (0.5, 2.5)
    ESCAPE_WEIGHT = 1.5  # 小鱼逃跑权重，动态调整范围 (1.0, 3.0)
    MID_FISH_ESCAPE_WEIGHT = 1.8  # 中型鱼逃跑权重，动态调整范围 (1.2, 3.5)
    WANDER_WEIGHT = 0.5  # 漫游权重
    BOUNDARY_FORCE = 0.5  # 边界力
    CURRENT_STRENGTH = 0.5  # 水流强度

    # 其他参数
    TRAIL_LENGTH = 10  # 轨迹长度
    FOOD_SIZE = 3 * scale  # 食物大小
    ESCAPE_RADIUS = 30.0  # 小鱼逃跑检测半径
    MID_FISH_ESCAPE_RADIUS = 40.0  # 中型鱼逃跑检测半径
    FOOD_DETECTION_RADIUS = 100  # 食物检测半径
    DAY_NIGHT_CYCLE = 30  # 昼夜周期（秒）
    NIGHT_COHESION_BONUS = 1.0  # 夜晚聚合加成
    NIGHT_SPEED_REDUCTION = 0.8  # 夜晚速度减弱
    MAX_VELOCITY = 3.5  # 全局最大速度限制
    SHOW_RADIUS = False

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
        'mid_fish_body': (255, 150, 100),
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

    # 动态地图大小，适配窗口
    @classmethod
    def update_map_size(cls, width, height):
        cls.WINDOW_WIDTH = width
        cls.WINDOW_HEIGHT = height
        cls.VIRTUAL_MAP_WIDTH = cls.WINDOW_WIDTH - cls.UI_PANEL_WIDTH
        cls.VIRTUAL_MAP_HEIGHT = cls.WINDOW_HEIGHT
        cls.UI_PANEL_X = cls.WINDOW_WIDTH - cls.UI_PANEL_WIDTH

    @classmethod
    def update_param(cls, param_name, value):
        if hasattr(cls, param_name):
            setattr(cls, param_name, value)
        else:
            raise AttributeError(f"Config has no attribute '{param_name}'")

    @classmethod
    def get_adjustable_params(cls):
        """返回可调整参数及其范围，供UI或其他模块使用"""
        return {
            '鱼群数量': ('FISH_COUNT', 50, 300, 5),
            '中型鱼数量': ('MID_FISH_COUNT', 10, 50, 5),
            '食物数量': ('FOOD_COUNT', 50, 200, 5),
            '小鱼速度': ('FISH_SPEED', 2.0, 8.0, 0.1),
            '小鱼加速度': ('FISH_FORCE', 0.1, 0.6, 0.01),
            '小鱼大小': ('FISH_SIZE', 5.0, 15.0, 0.5),
            '小鱼聚合半径': ('FISH_COHESION_RADIUS', 50.0, 150.0, 5.0),
            '小鱼分离半径': ('FISH_SEPARATION_RADIUS', 10.0, 50.0, 2.0),
            '小鱼对齐半径': ('FISH_ALIGNMENT_RADIUS', 20.0, 100.0, 5.0),
            '中型鱼速度': ('MID_FISH_SPEED', 3.0, 10.0, 0.1),
            '中型鱼加速度': ('MID_FISH_FORCE', 0.05, 0.3, 0.01),
            '中型鱼大小': ('MID_FISH_SIZE', 10.0, 20.0, 0.5),
            '中型鱼聚合半径': ('MID_FISH_COHESION_RADIUS', 75.0, 200.0, 5.0),
            '中型鱼分离半径': ('MID_FISH_SEPARATION_RADIUS', 15.0, 60.0, 2.0),
            '中型鱼对齐半径': ('MID_FISH_ALIGNMENT_RADIUS', 30.0, 120.0, 5.0),
            '捕食者速度': ('PREDATOR_SPEED', 5.0, 15.0, 0.2),
            '捕食者加速度': ('PREDATOR_MAX_FORCE', 0.1, 0.5, 0.01),
            '捕食者大小': ('PREDATOR_SIZE', 20.0, 40.0, 0.5),
            '捕食者饥饿衰减': ('PREDATOR_HUNGER_DECAY', 8.0, 25.0, 0.5),
            '分离权重': ('SEPARATION_WEIGHT', 1.0, 3.5, 0.1),
            '对齐权重': ('ALIGNMENT_WEIGHT', 0.5, 2.5, 0.1),
            '聚合权重': ('COHESION_WEIGHT', 0.5, 2.5, 0.1),
            '觅食权重': ('FOOD_WEIGHT', 0.5, 2.5, 0.1),
            '小鱼逃跑权重': ('ESCAPE_WEIGHT', 1.0, 3.0, 0.1),
            '中型鱼逃跑权重': ('MID_FISH_ESCAPE_WEIGHT', 1.2, 3.5, 0.1),
            '小鱼繁殖概率': ('FISH_NATURAL_BREED_CHANCE', 0.00005, 0.0002, 0.00001),
            '中型鱼繁殖概率': ('MID_FISH_BREED_CHANCE', 0.00003, 0.00015, 0.00001),
        }
