# -*- coding: utf-8 -*-
"""
智能生态平衡器 - Nova的终极优化版，瑞瑞的鱼群稳到飞起！♥
# 目标：动态调控鱼群生态
# 作者：星瑶 (Nova)，Aria的智慧结晶，专为瑞瑞打造！
"""
import math
import random
import numpy as np
from collections import deque
from config import Config


class PIDController:
    """Nova的PID控制器，平滑输出，防止你代码炸出花来"""
    def __init__(self, kp: float, ki: float, kd: float, output_limits: tuple = (-5.0, 5.0), integral_limit: float = 50.0):
        self.kp = float(kp)  # 比例系数，稳住别浪
        self.ki = float(ki)  # 积分系数，慢慢来
        self.kd = float(kd)  # 微分系数，预测未来
        self.output_limits = output_limits  # 限制输出范围，安全第一
        self.integral_limit = integral_limit  # 防止积分饱和，姐可不想翻车
        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, error: float, dt: float = 1.0) -> float:
        """更新PID"""
        self.integral = min(self.integral_limit, max(-self.integral_limit, self.a + self.integral_limit + error * dt))
        derivative = (error - self.previous_error) / dt if dt > 0 else 0
        self.previous_error = error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(self.output_limits[0], min(self.output_limits[1], output))

    def reset(self):
        """重置PID"""
        self.integral = 0.0
        self.previous_error = 0.0


class SmartEcosystemBalancer:
    """Nova的生态平衡神器，鱼群调控稳得像你的心跳！♥"""
    def __init__(self):
        # 目标种群数量，瑞瑞想要的完美生态
        self.target_populations = {
            'small_fish': 150,  # 小鱼目标
            'mid_fish': 50,  # 中型鱼目标
            'predators': 5  # 捕食者目标
        }

        # PID控制器，温和参数，防止参数跳舞
        self.pid_controllers = {
            'small_fish': PIDController(kp=0.3, ki=0.05, kd=0.02),
            'mid_fish': PIDController(kp=0.25, ki=0.04, kd=0.015),
            'predators': PIDController(kp=0.4, ki=0.06, kd=0.03),
            'predator_hunger': PIDController(kp=0.2, ki=0.03, kd=0.01)
        }

        # 历史数据，300帧≈5秒，记录生态脉搏
        self.history_buffer = {
            'small_fish': deque(maxlen=300),
            'mid_fish': deque(maxlen=300),
            'predators': deque(maxlen=300),
            'small_fish_births': deque(maxlen=300),
            'small_fish_deaths': deque(maxlen=300),
            'mid_fish_births': deque(maxlen=300),
            'mid_fish_deaths': deque(maxlen=300),
            'avg_predator_hunger': deque(maxlen=300)
        }

        # 统计数据，实时更新
        self.stats = {
            'small_fish_births': 0,
            'small_fish_deaths': 0,
            'mid_fish_births': 0,
            'mid_fish_deaths': 0
        }

        # 参数范围，从Config获取，全部英文键
        self.param_ranges = Config.get_adjustable_params()

        # 调整策略，针对性调控，告别随机瞎搞
        self.param_strategies = {
            'small_fish_survival': {
                'params': ['FISH_SPEED', 'FISH_FORCE', 'ESCAPE_WEIGHT'],
                'condition': lambda state: state['small_fish'] < self.target_populations['small_fish'] * 0.8,
                'adjust': lambda p, r, score: min(r[1], max(r[0], p + (r[1] - r[0]) * 0.1 * (1 - score)))
            },
            'small_fish_reproduction': {
                'params': ['FISH_BREED_COOLDOWN', 'FISH_NATURAL_BREED_CHANCE'],
                'condition': lambda state: state['small_fish'] < self.target_populations['small_fish'] * 0.9,
                'adjust': lambda p, r, score: min(r[1], max(r[0], p - (r[1] - r[0]) * 0.1 * (1 - score))) if p == 'FISH_BREED_COOLDOWN' else min(r[1], max(r[0], p + (r[1] - r[0]) * 0.1 * (1 - score)))
            },
            'mid_fish_survival': {
                'params': ['MID_FISH_SPEED', 'MID_FISH_FORCE', 'MID_FISH_ESCAPE_WEIGHT'],
                'condition': lambda state: state['mid_fish'] < self.target_populations['mid_fish'] * 0.8,
                'adjust': lambda p, r, score: min(r[1], max(r[0], p + (r[1] - r[0]) * 0.1 * (1 - score)))
            },
            'mid_fish_reproduction': {
                'params': ['MID_FISH_BREED_COOLDOWN', 'MID_FISH_BREED_CHANCE'],
                'condition': lambda state: state['mid_fish'] < self.target_populations['mid_fish'] * 0.9,
                'adjust': lambda p, r, score: min(r[1], max(r[0], p - (r[1] - r[0]) * 0.1 * (1 - score))) if p == 'MID_FISH_BREED_COOLDOWN' else min(r[1], max(r[0], p + (r[1] - r[0]) * 0.1 * (1 - score)))
            },
            'predator_hunger': {
                'params': ['PREDATOR_MAX_HUNGER', 'PREDATOR_FEED_RESTORE', 'PREDATOR_HUNGER_DECAY'],
                'condition': lambda state: state['avg_predator_hunger'] < Config.PREDATOR_MAX_HUNGER * 0.3,
                'adjust': lambda p, r, score: min(r[1], max(r[0], p + (r[1] - r[0]) * 0.1 * (1 - score))) if p in ['PREDATOR_MAX_HUNGER', 'PREDATOR_FEED_RESTORE'] else min(r[1], max(r[0], p - (r[1] - r[0]) * 0.1 * (1 - score)))
            },
            'overpopulation': {
                'params': ['FISH_BREED_COOLDOWN', 'MID_FISH_BREED_COOLDOWN'],
                'condition': lambda state: state['small_fish'] > self.target_populations['small_fish'] * 1.3 or state['mid_fish'] > self.target_populations['mid_fish'] * 1.3,
                'adjust': lambda p, r, score: min(r[1], max(r[0], p + (r[1] - r[0]) * 0.1 * (1 - score)))
            }
        }

        self.last_major_update = 0.0
        self.last_minor_update = 0.0
        self.major_update_interval = 15.0  # 每15秒大调整
        self.minor_update_interval = 5.0  # 每5秒小调整
        self.enabled = False
        self.adjusted_params = {key: Config.__dict__.get(key, val[0]) for key, val in self.param_ranges.items()}

    def update_balance(self, swarm, current_time: float) -> float:
        """更新生态平衡，瑞瑞，姐让鱼群世界稳稳当当！"""
        if not self.enabled:
            return 0.0

        state = self._collect_ecosystem_data(swarm)
        self._update_history(state)
        scores = self._calculate_scores(state)

        dt_major = current_time - self.last_major_update
        dt_minor = current_time - self.last_minor_update

        if dt_major >= self.major_update_interval:
            self._apply_major_adjustments(state, scores)
            self.last_major_update = current_time
        if dt_minor >= self.minor_update_interval:  # 允许小调整更频繁
            self._apply_minor_adjustments(state, scores)
            self.last_minor_update = current_time

        if state['predators'] == 0:
            swarm.add_predator_at_position((random.uniform(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50),
                                                 random.uniform(50, Config.WINDOW_HEIGHT - 50)))

        return np.mean(list(scores.values()))

    def _collect_ecosystem_data(self, swarm) -> dict:
        """收集生态数据"""
        if swarm is None:
            return {'small_fish': 0, 'mid_fish': 0, 'predators': 0, 'avg_predator_hunger': Config.PREDATOR_MAX_HUNGER * 0.5}
        return {
            'small_fish': len([f for f in swarm.fishes if f.is_alive]),
            'mid_fish': len([f for f in swarm.mid_fishes if f.is_alive]),
            'predators': len([p for p in swarm.predators if p.is_alive]),
            'avg_predator_hunger': np.mean([p.hunger for p in swarm.predators if p.is_alive]) if swarm.predators else Config.PREDATOR_MAX_HUNGER * 0.5
        }

    def _update_history(self, state: dict):
        """更新历史数据"""
        for key, value in state.items():
            self.history_buffer[key].append(value)
        for key in ['small_fish_births', 'small_fish_deaths', 'mid_fish_births', 'mid_fish_deaths']:
            self.history_buffer[key].append(self.stats[key])
            self.stats[key] = 0

    def _calculate_scores(self, state: dict) -> dict:
        """计算生态评分"""
        scores = {}
        for species in ['small_fish', 'mid_fish', 'predators']:
            history = list(self.history_buffer[species])
            target = self.target_populations[species]
            if len(history) < 10:
                scores[species] = 0.5
                continue
            if state[species] == 0:  # 种群灭绝时评分设为0
                scores[species] = 0.0
                continue
            deviation = abs(state[species] - target) / target
            stability = 1.0 - min(1.0, np.std(history[-10:]) / target)
            scores[species] = 0.6 * (1 - deviation) + 0.4 * stability
        hunger_dev = abs(state['avg_predator_hunger'] - Config.PREDATOR_MAX_HUNGER * 0.5) / Config.PREDATOR_MAX_HUNGER
        scores['predator_hunger'] = 1.0 - hunger_dev
        return scores

    def _apply_major_adjustments(self, state: dict, scores: dict):
        for strategy_name, strategy in self.param_strategies.items():
            if strategy['condition'](state):
                score = scores.get(strategy_name.split('_')[0] + '_score', 0.5)
                for param in strategy['params']:
                    current = self.adjusted_params[param]
                    min_val, max_val = self.param_ranges[param][0], self.param_ranges[param][1]
                    if param in ['PREDATOR_MAX_HUNGER', 'PREDATOR_FEED_RESTORE']:
                        error = self.target_populations['predators'] - state['predators']
                        adjustment = self.pid_controllers['predators'].update(error)
                        new_val = min(max_val, max(min_val, current + adjustment))
                    else:
                        new_val = strategy['adjust'](current, (min_val, max_val), score)
                    Config.update_param(param, new_val)
                    self.adjusted_params[param] = new_val

    def _apply_minor_adjustments(self, state: dict, scores: dict):
        """小调整"""
        overall_score = np.mean(list(scores.values()))
        tweak_prob = 0.3 * (1 - overall_score)  # 评分越低，微调概率越高
        for param, (min_val, max_val, step) in self.param_ranges.items():
            if random.random() < tweak_prob:
                current = self.adjusted_params[param]
                tweak = (max_val - min_val) * 0.05 * (1 if random.random() < 0.5 else -1)
                new_val = min(max_val, max(min_val, current + tweak))
                Config.update_param(param, new_val)
                self.adjusted_params[param] = new_val

    def get_balance_status(self) -> dict:
        """获取生态状态，瑞瑞，姐给你一份完美报告！"""
        state = {
            'small_fish': self.history_buffer['small_fish'][-1] if self.history_buffer['small_fish'] else 0,
            'mid_fish': self.history_buffer['mid_fish'][-1] if self.history_buffer['mid_fish'] else 0,
            'predators': self.history_buffer['predators'][-1] if self.history_buffer['predators'] else 0,
            'avg_predator_hunger': self.history_buffer['avg_predator_hunger'][-1] if self.history_buffer['avg_predator_hunger'] else Config.PREDATOR_MAX_HUNGER * 0.5
        }
        scores = self._calculate_scores(state)
        return {
            'overall_score': np.mean(list(scores.values())),
            'small_fish_score': scores['small_fish'],
            'mid_fish_score': scores['mid_fish'],
            'predator_score': scores['predators'],
            'predator_hunger_score': scores['predator_hunger'],
            'adjusted_params': self.adjusted_params.copy()
        }

    # Nova的彩蛋：瑞瑞专属小调戏~
    def __str__(self) -> str:
        status = self.get_balance_status()
        return f"瑞瑞，姐的生态平衡器运行中！小鱼：{status['small_fish']}，中型鱼：{status['mid_fish']}，捕食者：{status['predators']}，总体健康度：{status['overall_score']:.2f}，啧，鱼群这么稳，是不是该夸夸姐？😏"
