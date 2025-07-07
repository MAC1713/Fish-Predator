# -*- coding: utf-8 -*-
"""
智能生态平衡系统 - Nova’s Mega Spicy Remix ♥
作者: 晏霖 (Aria) ♥, 优化者: Nova (winking at 瑞瑞)
参数全统一到config.py，动态调整实时生效
"""

import math
import random
import numpy as np
from collections import deque
from config import Config


class PIDController:
    """PID控制器，Nova调高参数，反应更快"""

    def __init__(self, kp, ki, kd, output_limits=(-20, 20)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, error, dt=1.0):
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0
        self.previous_error = error
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return max(self.output_limits[0], min(self.output_limits[1], output))

    def reset(self):
        self.integral = 0.0
        self.previous_error = 0.0


class SmartEcosystemBalancer:
    """Nova的超强生态平衡器，直击核心参数，粗调细调两手抓！"""

    def __init__(self):
        # 目标生态参数
        self.target_populations = {
            'small_fish': 100,
            'mid_fish': 30,
            'predators': 5,
            'food_ratio': 0.8
        }

        # PID控制器，扩大输出范围
        self.pid_controllers = {
            'small_fish': PIDController(kp=1.0, ki=0.2, kd=0.1, output_limits=(-20, 20)),
            'mid_fish': PIDController(kp=0.8, ki=0.15, kd=0.08, output_limits=(-15, 15)),
            'predators': PIDController(kp=1.2, ki=0.3, kd=0.2, output_limits=(-10, 10)),
            'food': PIDController(kp=0.7, ki=0.1, kd=0.05, output_limits=(-15, 15))
        }

        # 历史数据缓存，长期趋势
        self.history_buffer = {
            'small_fish': deque(maxlen=200),
            'mid_fish': deque(maxlen=200),
            'predators': deque(maxlen=200),
            'food': deque(maxlen=200),
            'errors': deque(maxlen=200)
        }

        # 环境状态
        self.environment_state = {
            'stress_level': 0.0,
            'stability_index': 1.0,
            'growth_momentum': 0.0,
            'last_crisis_time': 0
        }

        # 调控核心参数，统一与config.py一致
        self.param_weights = {
            'FISH_SPEED': 0.5,
            'FISH_FORCE': 0.3,
            'FISH_SIZE': 0.2,
            'FISH_COHESION_RADIUS': 0.2,
            'FISH_SEPARATION_RADIUS': 0.2,
            'FISH_ALIGNMENT_RADIUS': 0.2,
            'MID_FISH_SPEED': 0.5,
            'MID_FISH_FORCE': 0.3,
            'MID_FISH_SIZE': 0.2,
            'MID_FISH_COHESION_RADIUS': 0.2,
            'MID_FISH_SEPARATION_RADIUS': 0.2,
            'MID_FISH_ALIGNMENT_RADIUS': 0.2,
            'PREDATOR_SPEED': 0.3,
            'PREDATOR_MAX_FORCE': 0.2,
            'PREDATOR_SIZE': 0.2,
            'PREDATOR_HUNGER_DECAY': 0.35,
            'FISH_NATURAL_BREED_CHANCE': 0.3,
            'MID_FISH_BREED_CHANCE': 0.3,
            'FOOD_COUNT': 0.4,
            'SEPARATION_WEIGHT': 0.25,
            'ALIGNMENT_WEIGHT': 0.25,
            'COHESION_WEIGHT': 0.25,
            'FOOD_WEIGHT': 0.35,
            'ESCAPE_WEIGHT': 0.3,
            'MID_FISH_ESCAPE_WEIGHT': 0.3
        }
        self.param_ranges = {
            'FISH_SPEED': (2.0, 8.0),
            'FISH_FORCE': (0.1, 0.6),
            'FISH_SIZE': (5.0, 15.0),
            'FISH_COHESION_RADIUS': (50.0, 150.0),
            'FISH_SEPARATION_RADIUS': (10.0, 50.0),
            'FISH_ALIGNMENT_RADIUS': (20.0, 100.0),
            'MID_FISH_SPEED': (3.0, 10.0),
            'MID_FISH_FORCE': (0.05, 0.3),
            'MID_FISH_SIZE': (10.0, 20.0),
            'MID_FISH_COHESION_RADIUS': (75.0, 200.0),
            'MID_FISH_SEPARATION_RADIUS': (15.0, 60.0),
            'MID_FISH_ALIGNMENT_RADIUS': (30.0, 120.0),
            'PREDATOR_SPEED': (5.0, 15.0),
            'PREDATOR_MAX_FORCE': (0.1, 0.5),
            'PREDATOR_SIZE': (20.0, 40.0),
            'PREDATOR_HUNGER_DECAY': (8.0, 25.0),
            'FISH_NATURAL_BREED_CHANCE': (0.00005, 0.0002),
            'MID_FISH_BREED_CHANCE': (0.00003, 0.00015),
            'FOOD_COUNT': (50, 200),
            'SEPARATION_WEIGHT': (1.0, 3.5),
            'ALIGNMENT_WEIGHT': (0.5, 2.5),
            'COHESION_WEIGHT': (0.5, 2.5),
            'FOOD_WEIGHT': (0.5, 2.5),
            'ESCAPE_WEIGHT': (1.0, 3.0),
            'MID_FISH_ESCAPE_WEIGHT': (1.2, 3.5)
        }

        # 退火机制，两阶段调控
        self.temperature = 1.5
        self.cooling_rate = 0.98
        self.learning_rate = 0.05  # 提高学习率
        self.mutation_rate = 0.2  # 提高突变率
        self.performance_metrics = deque(maxlen=200)
        self.rough_tuning = True  # 初始粗调阶段

        # 时间参数
        self.last_update_time = 0
        self.update_interval = 1.0  # 加快更新
        self.micro_adjustment_interval = 0.1
        self.enabled = False

        # 动态调整参数
        self.adjusted_params = {key: getattr(Config, key, self.param_ranges[key][0]) for key in self.param_weights}

    def update_balance(self, swarm, current_time):
        """核心平衡函数，直接调控核心参数，粗调+细调"""
        if not self.enabled:
            self.adjusted_params.update(
                {key: getattr(Config, key, self.param_ranges[key][0]) for key in self.param_weights})
            return 0.0
        dt = current_time - self.last_update_time

        current_state = self._collect_ecosystem_data(swarm)
        self._update_history(current_state)
        health_score = self._calculate_ecosystem_health(current_state)

        trends = self._analyze_population_trends()
        predictions = self._predict_future_state(current_state, trends)

        if dt >= self.update_interval:
            self._apply_neural_adjustments(swarm, current_state, trends, predictions, health_score)
            self._update_environment_state(current_state, self._compute_signals(current_state))
            self.last_update_time = current_time
        elif dt >= self.micro_adjustment_interval:
            self._apply_micro_adjustments(swarm, current_state)

        self._adaptive_weight_tuning(health_score)
        self.temperature *= self.cooling_rate
        return health_score

    def _collect_ecosystem_data(self, swarm):
        """收集生态数据，计算偏差"""
        alive_small_fish = [f for f in swarm.fishes if f.is_alive]
        alive_mid_fish = [f for f in swarm.mid_fishes if f.is_alive]
        alive_predators = [p for p in swarm.predators if p.is_alive]
        available_food = [f for f in swarm.foods if not f.consumed]
        total_fish = len(alive_small_fish) + len(alive_mid_fish)
        food_ratio = len(available_food) / max(total_fish, 1)
        errors = {
            'small_fish': (len(alive_small_fish) - self.target_populations['small_fish']) / max(
                self.target_populations['small_fish'], 1),
            'mid_fish': (len(alive_mid_fish) - self.target_populations['mid_fish']) / max(
                self.target_populations['mid_fish'], 1),
            'predators': (len(alive_predators) - self.target_populations['predators']) / max(
                self.target_populations['predators'], 1),
            'food_ratio': (food_ratio - self.target_populations['food_ratio']) / max(
                self.target_populations['food_ratio'], 1)
        }
        return {
            'small_fish': len(alive_small_fish),
            'mid_fish': len(alive_mid_fish),
            'predators': len(alive_predators),
            'food': len(available_food),
            'total_fish': total_fish,
            'errors': errors
        }

    def _update_history(self, current_state):
        """更新历史数据"""
        for key in ['small_fish', 'mid_fish', 'predators', 'food']:
            self.history_buffer[key].append(current_state[key])
        self.history_buffer['errors'].append(current_state['errors'])

    def _calculate_ecosystem_health(self, current_state):
        """计算生态健康度"""
        pop_health = sum(
            min(current_state[key] / self.target_populations[key], 1.0) * (0.7 if key == 'small_fish' else 0.15)
            for key in ['small_fish', 'mid_fish', 'predators']
        ) / 1.0
        food_health = min(current_state['food'] / max(current_state['total_fish'] * 0.9, 1), 1.0)
        return (pop_health * 0.6 + food_health * 0.4)

    def _analyze_population_trends(self):
        """分析种群趋势"""
        trends = {}
        for key in ['small_fish', 'mid_fish', 'predators', 'food']:
            history = list(self.history_buffer[key])
            if len(history) > 3:
                recent = history[-3:]
                trends[key] = (recent[-1] - recent[0]) / 3
            else:
                trends[key] = 0.0
        return trends

    def _predict_future_state(self, current_state, trends):
        """预测未来状态"""
        predictions = {}
        for key in ['small_fish', 'mid_fish', 'predators', 'food']:
            predictions[key] = max(0, current_state[key] + trends[key] * 8)
        return predictions

    def _compute_signals(self, current_state):
        """计算PID控制信号"""
        signals = {}
        for pop_type in ['small_fish', 'mid_fish', 'predators']:
            error = self.target_populations[pop_type] - current_state[pop_type]
            signals[pop_type] = self.pid_controllers[pop_type].update(error)
        total_fish = current_state['total_fish']
        food_ratio = current_state['food'] / max(total_fish, 1)
        food_error = self.target_populations['food_ratio'] - food_ratio
        signals['food'] = self.pid_controllers['food'].update(food_error)
        return signals

    def _apply_neural_adjustments(self, swarm, current_state, trends, predictions, health_score):
        """神经网络风调整，粗调+细调"""
        signals = self._compute_signals(current_state)
        weighted_error = (
                0.5 * abs(current_state['errors']['small_fish']) +
                0.3 * abs(current_state['errors']['mid_fish']) +
                0.1 * abs(current_state['errors']['predators']) +
                0.1 * abs(current_state['errors']['food_ratio'])
        )
        self.rough_tuning = weighted_error > 0.2  # 偏差>20%时粗调

        for param, weight in self.param_weights.items():
            min_val, max_val = self.param_ranges[param]
            current_val = self.adjusted_params[param]
            pid_influence = signals.get(param.split('_')[0], 0) * (0.5 if self.rough_tuning else 0.1)
            mutation = random.uniform(-0.5, 0.5) * (
                        max_val - min_val) * weight if random.random() < self.mutation_rate * self.temperature else 0
            health_feedback = (0.75 - health_score) * self.learning_rate * weight * (
                2.0 if self.rough_tuning else 1.0) if health_score < 0.75 else 0
            new_val = current_val + pid_influence + mutation + health_feedback
            new_val = max(min_val, min(max_val, new_val))
            Config.update_param(param, new_val)
            self.adjusted_params[param] = new_val

    def _apply_micro_adjustments(self, swarm, current_state):
        """微调，粗调时幅度更大"""
        for param, weight in self.param_weights.items():
            if random.random() < 0.15:
                min_val, max_val = self.param_ranges[param]
                current_val = self.adjusted_params[param]
                tweak = random.uniform(-0.2 if self.rough_tuning else -0.05, 0.2 if self.rough_tuning else 0.05) * (
                            max_val - min_val) * weight
                new_val = max(min_val, min(max_val, current_val + tweak))
                Config.update_param(param, new_val)
                self.adjusted_params[param] = new_val

    def _adaptive_weight_tuning(self, health_score):
        """自适应调整权重"""
        self.performance_metrics.append(health_score)
        if len(self.performance_metrics) >= 200:
            avg_health = np.mean(self.performance_metrics)
            if avg_health < 0.7:
                for param in self.param_weights:
                    self.param_weights[param] = min(1.0, self.param_weights[param] + 0.03)
            else:
                for param in self.param_weights:
                    self.param_weights[param] = max(0.1, self.param_weights[param] - 0.02)
            self.performance_metrics.clear()

    def _update_environment_state(self, current_state, signals):
        """更新环境状态，新stress_level算法"""
        errors = current_state['errors']
        weighted_error = (
                0.5 * abs(errors['small_fish']) +
                0.3 * abs(errors['mid_fish']) +
                0.1 * abs(errors['predators']) +
                0.1 * abs(errors['food_ratio'])
        )
        normalized_error = min(weighted_error / 2.0, 1.0)

        error_trend = 0.0
        if len(self.history_buffer['errors']) >= 100:
            recent_errors = [sum(abs(e[k]) for k in e) for e in list(self.history_buffer['errors'])[-50:]]
            older_errors = [sum(abs(e[k]) for k in e) for e in list(self.history_buffer['errors'])[-100:-50]]
            error_trend = np.mean(recent_errors) - np.mean(older_errors)
            error_trend = min(max(error_trend / 0.5, -1.0), 1.0)

        signal_magnitude = sum(abs(s) for s in signals.values())
        normalized_signal_magnitude = min(signal_magnitude / 20.0, 1.0)

        self.environment_state['stress_level'] = max(0.0, min(1.0, (
                0.7 * normalized_error +
                0.2 * abs(error_trend) +
                0.1 * normalized_signal_magnitude
        )))

        self.environment_state['stability_index'] = max(0.0, 1.0 - (
                0.6 * normalized_error +
                0.3 * abs(error_trend) +
                0.1 * normalized_signal_magnitude
        ))

    def get_balance_status(self):
        """获取当前平衡状态"""
        current_health = self.performance_metrics[-1] if self.performance_metrics else 0.0
        return {
            'health_score': current_health,
            'stability_index': self.environment_state['stability_index'],
            'stress_level': self.environment_state['stress_level'],
            'adjusted_params': self.adjusted_params.copy()
        }
