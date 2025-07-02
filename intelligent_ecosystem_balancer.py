# -*- coding: utf-8 -*-
"""
智能生态平衡系统 - 高级版
作者: 晏霖 (Aria) ♥ 为瑞瑞特制
采用PID控制器 + 非线性响应 + 趋势预测的完美平衡算法～
"""

import math
import random
import numpy as np
from collections import deque
from config import Config


class SmartEcosystemBalancer:
    """高级智能生态平衡器 - 基于PID控制理论"""

    def __init__(self):
        # 目标生态参数 (可以根据环境动态调整)
        self.target_populations = {
            'small_fish': 100,
            'mid_fish': 30,
            'predators': 5,
            'food_ratio': 0.8  # 食物与总鱼类的比例
        }

        # PID控制器参数 (针对不同种群分别调优)
        self.pid_controllers = {
            'small_fish': PIDController(kp=0.8, ki=0.2, kd=0.1, output_limits=(-5, 5)),
            'mid_fish': PIDController(kp=0.6, ki=0.15, kd=0.08, output_limits=(-3, 3)),
            'predators': PIDController(kp=1.2, ki=0.3, kd=0.2, output_limits=(-2, 2)),
            'food': PIDController(kp=0.5, ki=0.1, kd=0.05, output_limits=(-10, 10))
        }

        # 历史数据缓存 (用于趋势分析和预测)
        self.history_buffer = {
            'small_fish': deque(maxlen=50),
            'mid_fish': deque(maxlen=50),
            'predators': deque(maxlen=50),
            'food': deque(maxlen=50),
            'balance_score': deque(maxlen=30)
        }

        # 环境状态监控
        self.environment_state = {
            'stress_level': 0.0,  # 生态压力指数
            'stability_index': 1.0,  # 稳定性指数
            'growth_momentum': 0.0,  # 增长动量
            'last_crisis_time': 0
        }

        # 自适应学习参数
        self.learning_rate = 0.05
        self.adaptation_cycles = 0
        self.performance_metrics = []

        # 非线性响应曲线参数
        self.response_curves = {
            'sigmoid_steepness': 2.0,  # S曲线陡峭度
            'exponential_base': 1.5,  # 指数响应底数
            'dampening_factor': 0.8  # 阻尼系数
        }

        # 时间相关参数
        self.last_update_time = 0
        self.update_interval = 3.0  # 更新间隔(秒)
        self.micro_adjustment_interval = 0.5  # 微调间隔

    def update_balance(self, swarm, current_time):
        """主要的平衡更新函数"""
        dt = current_time - self.last_update_time

        # 收集当前生态数据
        current_state = self._collect_ecosystem_data(swarm)

        # 更新历史记录
        self._update_history(current_state)

        # 计算生态健康度
        health_score = self._calculate_ecosystem_health(current_state)
        self.history_buffer['balance_score'].append(health_score)  # 记录健康度

        # 检测环境变化趋势
        trends = self._analyze_population_trends()

        # 预测未来状态
        predictions = self._predict_future_state(current_state, trends)

        # 执行智能调整
        if dt >= self.update_interval:
            self._apply_smart_adjustments(swarm, current_state, trends, predictions, current_time)
            self.last_update_time = current_time
        elif dt >= self.micro_adjustment_interval:
            self._apply_micro_adjustments(swarm, current_state, current_time)

        # 自适应参数调优
        self._adaptive_parameter_tuning(health_score)

        return health_score

    def _collect_ecosystem_data(self, swarm):
        """收集完整的生态系统数据"""
        alive_small_fish = [f for f in swarm.fishes if f.is_alive]
        alive_mid_fish = [f for f in swarm.mid_fishes if f.is_alive]
        alive_predators = [f for f in swarm.predators if f.is_alive]
        available_food = [f for f in swarm.foods if not f.consumed]

        return {
            'small_fish': len(alive_small_fish),
            'mid_fish': len(alive_mid_fish),
            'predators': len(alive_predators),
            'food': len(available_food),
            'total_fish': len(alive_small_fish) + len(alive_mid_fish),

            # 高级指标
            'fish_density': self._calculate_density(alive_small_fish + alive_mid_fish),
            'predator_efficiency': self._calculate_predator_efficiency(alive_predators),
            'food_distribution': self._calculate_food_distribution(available_food),
            'age_diversity': self._calculate_age_diversity(alive_small_fish + alive_mid_fish),

            # 实时状态
            'avg_fish_speed': self._calculate_avg_speed(alive_small_fish),
            'stress_indicators': self._detect_stress_indicators(swarm)
        }

    def _apply_smart_adjustments(self, swarm, current_state, trends, predictions, current_time):
        """应用智能调整策略"""

        # 1. 计算各种群的控制信号
        control_signals = {}

        for pop_type in ['small_fish', 'mid_fish', 'predators']:
            if pop_type in current_state and pop_type in self.target_populations:
                error = self.target_populations[pop_type] - current_state[pop_type]
                control_signals[pop_type] = self.pid_controllers[pop_type].update(error)

        # 食物系统的特殊处理
        total_fish = current_state['total_fish']
        current_food_ratio = current_state['food'] / max(total_fish, 1)
        food_error = self.target_populations['food_ratio'] - current_food_ratio
        control_signals['food'] = self.pid_controllers['food'].update(food_error)

        # 2. 应用非线性响应曲线
        adjusted_signals = self._apply_nonlinear_response(control_signals, current_state)

        # 3. 考虑趋势和预测进行前瞻性调整
        predictive_signals = self._apply_predictive_adjustments(adjusted_signals, trends, predictions)

        # 4. 执行具体的生态调整
        self._execute_ecosystem_adjustments(swarm, predictive_signals, current_time)

        # 5. 更新环境状态
        self._update_environment_state(current_state, predictive_signals)

    def _apply_nonlinear_response(self, control_signals, current_state):
        """应用非线性响应曲线，使调整更平滑自然"""
        adjusted_signals = {}

        for signal_type, raw_signal in control_signals.items():
            # 使用sigmoid函数平滑响应
            sigmoid_response = self._sigmoid_transform(raw_signal, self.response_curves['sigmoid_steepness'])

            # 根据当前生态压力调整响应强度
            stress_factor = 1.0 + self.environment_state['stress_level'] * 0.5

            # 考虑稳定性指数的阻尼效应
            damping = self.environment_state['stability_index'] * self.response_curves['dampening_factor']

            adjusted_signals[signal_type] = sigmoid_response * stress_factor * damping

        return adjusted_signals

    def _apply_predictive_adjustments(self, signals, trends, predictions):
        """基于趋势和预测进行前瞻性调整"""
        predictive_signals = signals.copy()

        for signal_type, signal in signals.items():
            if signal_type in trends:
                trend = trends[signal_type]

                # 如果趋势和控制信号方向一致，适当增强
                if (signal > 0 and trend > 0) or (signal < 0 and trend < 0):
                    predictive_signals[signal_type] *= 1.2
                # 如果趋势和控制信号相反，适当减弱避免过度调整
                elif (signal > 0 and trend < 0) or (signal < 0 and trend > 0):
                    predictive_signals[signal_type] *= 0.8

        return predictive_signals

    def _execute_ecosystem_adjustments(self, swarm, signals, current_time):
        """执行具体的生态系统调整"""

        # 小鱼种群调整
        if 'small_fish' in signals:
            self._adjust_fish_population(swarm.fishes, signals['small_fish'], 'small', current_time)

        # 中型鱼种群调整
        if 'mid_fish' in signals:
            self._adjust_fish_population(swarm.mid_fishes, signals['mid_fish'], 'mid', current_time)

        # 捕食者调整
        if 'predators' in signals:
            self._adjust_predator_population(swarm, signals['predators'], current_time)

        # 食物系统调整
        if 'food' in signals:
            self._adjust_food_system(swarm, signals['food'])

    def _adjust_fish_population(self, fish_list, control_signal, fish_type, current_time):
        """渐进式调整鱼类种群"""
        alive_fishes = [f for f in fish_list if f.is_alive]

        if control_signal > 0:  # 需要增加鱼的数量
            # 提高繁殖率的渐进调整
            breed_boost = self._calculate_gradual_adjustment(control_signal, max_boost=2.0)

            for fish in alive_fishes:
                if fish.is_alive and fish.is_mature:
                    # 渐进减少繁殖冷却时间
                    cooldown_reduction = Config.FISH_BREED_COOLDOWN * (breed_boost - 1.0) * 0.3
                    fish.last_breed_time = max(0, fish.last_breed_time - cooldown_reduction)

                    # 提高繁殖成功率
                    if hasattr(fish, 'fertility_bonus'):
                        fish.fertility_bonus = min(2.0, fish.fertility_bonus + breed_boost * 0.1)
                    else:
                        fish.fertility_bonus = 1.0 + breed_boost * 0.1

        elif control_signal < 0:  # 需要减少鱼的数量
            # 降低繁殖率和提高自然死亡率
            death_rate_increase = self._calculate_gradual_adjustment(abs(control_signal), max_boost=1.5)

            for fish in alive_fishes:
                if fish.is_alive:
                    # 增加繁殖冷却时间
                    fish.last_breed_time += Config.FISH_BREED_COOLDOWN * death_rate_increase * 0.2

                    # 轻微增加死亡概率（通过环境压力实现）
                    if hasattr(fish, 'survival_penalty'):
                        fish.survival_penalty = min(1.5, fish.survival_penalty + death_rate_increase * 0.05)
                    else:
                        fish.survival_penalty = 1.0 + death_rate_increase * 0.05

    def _adjust_predator_population(self, swarm, control_signal, current_time):
        """智能调整捕食者种群"""
        alive_predators = [p for p in swarm.predators if p.is_alive]

        if control_signal > 0:  # 需要更多捕食者
            # 提高现有捕食者的生存能力
            for predator in alive_predators:
                if predator.is_alive:
                    survival_boost = self._calculate_gradual_adjustment(control_signal, max_boost=1.5)
                    predator.hunger = min(Config.PREDATOR_MAX_HUNGER,
                                          predator.hunger + Config.PREDATOR_HUNGER_DECAY * survival_boost * 0.5)

            # 如果控制信号很强，考虑生成新的捕食者
            if control_signal > 1.5 and len(alive_predators) < self.target_populations['predators']:
                self._spawn_smart_predator(swarm)

        elif control_signal < 0:  # 需要减少捕食者
            # 增加捕食者的饥饿速度
            hunger_penalty = self._calculate_gradual_adjustment(abs(control_signal), max_boost=1.8)

            for predator in alive_predators:
                if predator.is_alive:
                    predator.hunger -= Config.PREDATOR_HUNGER_DECAY * hunger_penalty * 0.3

    def _adjust_food_system(self, swarm, control_signal):
        """智能调整食物系统"""
        if control_signal > 0:  # 需要更多食物
            food_boost = self._calculate_gradual_adjustment(control_signal, max_boost=20)
            self._generate_smart_food(swarm, int(food_boost))

        elif control_signal < 0:  # 需要减少食物
            reduction_rate = self._calculate_gradual_adjustment(abs(control_signal), max_boost=0.8)
            self._reduce_excess_food(swarm, reduction_rate)

    def _calculate_gradual_adjustment(self, signal_strength, max_boost=2.0):
        """计算渐进式调整系数"""
        # 使用平滑的非线性函数，避免突变
        normalized_signal = min(signal_strength / 3.0, 1.0)  # 归一化到[0,1]

        # 应用平滑的增长函数
        if normalized_signal > 0:
            return 1.0 + (max_boost - 1.0) * (1.0 - math.exp(-normalized_signal * 2.0))
        else:
            return 1.0

    def _sigmoid_transform(self, x, steepness=2.0):
        """Sigmoid变换，将输入平滑映射"""
        return (2.0 / (1.0 + math.exp(-steepness * x))) - 1.0

    def _calculate_ecosystem_health(self, current_state):
        """计算生态系统健康度 (0-1)"""
        health_factors = []

        # 种群平衡因子
        for pop_type in ['small_fish', 'mid_fish', 'predators']:
            if pop_type in current_state and pop_type in self.target_populations:
                target = self.target_populations[pop_type]
                current = current_state[pop_type]

                if target > 0:
                    balance_ratio = min(current, target) / target
                    health_factors.append(balance_ratio)

        # 食物系统健康度
        total_fish = current_state['total_fish']
        if total_fish > 0:
            food_health = min(current_state['food'] / (total_fish * 0.8), 1.0)
            health_factors.append(food_health)

        # 多样性指数
        if 'age_diversity' in current_state:
            health_factors.append(current_state['age_diversity'])

        return sum(health_factors) / len(health_factors) if health_factors else 0.0

    # 辅助方法
    def _update_history(self, current_state):
        """更新历史数据"""
        for key in ['small_fish', 'mid_fish', 'predators', 'food']:
            if key in current_state:
                self.history_buffer[key].append(current_state[key])

    def _analyze_population_trends(self):
        """分析种群变化趋势"""
        trends = {}

        for pop_type, history in self.history_buffer.items():
            if len(history) >= 10:
                # 使用线性回归计算趋势
                x = np.arange(len(history))
                y = np.array(history)

                # 计算斜率作为趋势指标
                if len(x) > 1:
                    slope = np.polyfit(x, y, 1)[0]
                    trends[pop_type] = slope

        return trends

    def _predict_future_state(self, current_state, trends):
        """预测未来状态"""
        predictions = {}
        prediction_steps = 10  # 预测10个时间步

        for pop_type, current_value in current_state.items():
            if pop_type in trends:
                trend = trends[pop_type]
                predicted_value = current_value + trend * prediction_steps
                predictions[pop_type] = max(0, predicted_value)  # 确保非负

        return predictions

    # 其他辅助计算方法...
    def _calculate_density(self, fish_list):
        """计算鱼群密度"""
        if not fish_list:
            return 0.0

        total_area = Config.WINDOW_WIDTH * Config.WINDOW_HEIGHT
        return len(fish_list) / total_area * 10000  # 标准化

    def _calculate_predator_efficiency(self, predators):
        """计算捕食者效率"""
        if not predators:
            return 0.0

        total_efficiency = sum(getattr(p, 'hunt_success_rate', 0.5) for p in predators)
        return total_efficiency / len(predators)

    def _calculate_food_distribution(self, food_list):
        """计算食物分布均匀度"""
        if len(food_list) < 2:
            return 1.0

        # 简化的分布均匀度计算
        positions = [(f.position.x, f.position.y) for f in food_list]

        # 计算食物间的平均距离
        total_distance = 0
        count = 0

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dx = positions[i][0] - positions[j][0]
                dy = positions[i][1] - positions[j][1]
                distance = math.sqrt(dx * dx + dy * dy)
                total_distance += distance
                count += 1

        if count > 0:
            avg_distance = total_distance / count
            # 归一化到[0,1]范围
            normalized_distance = min(avg_distance / 200.0, 1.0)
            return normalized_distance

        return 1.0

    def _calculate_age_diversity(self, fish_list):
        """计算年龄多样性"""
        if not fish_list:
            return 0.0

        ages = [getattr(f, 'age', 0) for f in fish_list]

        if len(set(ages)) <= 1:
            return 0.0

        # 计算年龄分布的标准差作为多样性指标
        mean_age = sum(ages) / len(ages)
        variance = sum((age - mean_age) ** 2 for age in ages) / len(ages)
        std_dev = math.sqrt(variance)

        # 归一化到[0,1]
        return min(std_dev / 100.0, 1.0)

    def _calculate_avg_speed(self, fish_list):
        """计算平均游泳速度"""
        if not fish_list:
            return 0.0

        total_speed = sum(
            math.sqrt(f.vx * f.vx + f.vy * f.vy) for f in fish_list if hasattr(f, 'vx') and hasattr(f, 'vy'))
        return total_speed / len(fish_list)

    def _detect_stress_indicators(self, swarm):
        """检测生态系统压力指标"""
        stress_score = 0.0

        # 检测过度聚集
        if hasattr(swarm, 'fishes'):
            fish_positions = [(f.position.x, f.position.y) for f in swarm.fishes if f.is_alive]
            if len(fish_positions) > 10:
                # 简化的聚集度检测
                center_x = sum(pos[0] for pos in fish_positions) / len(fish_positions)
                center_y = sum(pos[1] for pos in fish_positions) / len(fish_positions)

                distances = [math.sqrt((pos[0] - center_x) ** 2 + (pos[1] - center_y) ** 2) for pos in fish_positions]
                avg_distance = sum(distances) / len(distances)

                if avg_distance < 50:  # 过度聚集
                    stress_score += 0.3

        return min(stress_score, 1.0)

    def _apply_micro_adjustments(self, swarm, current_state, current_time):
        """应用微调整"""
        # 实现微小的、高频的调整
        pass

    def _adaptive_parameter_tuning(self, health_score):
        """自适应参数调优"""
        # 根据系统表现调整PID参数
        self.performance_metrics.append(health_score)

        if len(self.performance_metrics) > 20:
            recent_performance = sum(self.performance_metrics[-10:]) / 10
            older_performance = sum(self.performance_metrics[-20:-10]) / 10

            if recent_performance > older_performance:
                # 表现在改善，保持当前参数
                pass
            else:
                # 表现在恶化，微调参数
                for controller in self.pid_controllers.values():
                    controller.kp *= 0.98  # 微调比例系数

    def _update_environment_state(self, current_state, signals):
        """更新环境状态"""
        # 更新压力水平
        signal_magnitude = sum(abs(s) for s in signals.values())
        self.environment_state['stress_level'] = min(signal_magnitude / 10.0, 1.0)

        # 更新稳定性指数
        if self.history_buffer['balance_score']:
            recent_scores = list(self.history_buffer['balance_score'])
            if len(recent_scores) > 1:
                score_variance = np.var(recent_scores)
                self.environment_state['stability_index'] = max(0.1, 1.0 - score_variance)

    def _spawn_smart_predator(self, swarm):
        """智能生成捕食者"""
        from swarm import Predator  # 假设从swarm模块导入

        x = random.randint(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
        y = random.randint(50, Config.WINDOW_HEIGHT - 50)

        new_predator = Predator(x, y)
        new_predator.hunger = Config.PREDATOR_MAX_HUNGER * 0.9  # 给予生存优势
        swarm.predators.append(new_predator)

    def _generate_smart_food(self, swarm, count):
        """智能生成食物"""
        from swarm import Food  # 假设从swarm模块导入

        for _ in range(count):
            x = random.randint(50, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH - 50)
            y = random.randint(50, Config.WINDOW_HEIGHT - 50)
            swarm.foods.append(Food(x, y, 'plankton'))

    def _reduce_excess_food(self, swarm, reduction_rate):
        """减少多余食物"""
        available_food = [f for f in swarm.foods if not f.consumed]
        remove_count = int(len(available_food) * (1.0 - reduction_rate))

        for _ in range(min(remove_count, len(available_food))):
            if available_food:
                food_to_remove = available_food.pop()
                swarm.foods.remove(food_to_remove)

    def get_balance_status(self):
        """获取详细的平衡状态报告"""
        current_health = self.history_buffer['balance_score'][-1] if self.history_buffer['balance_score'] else 0.0

        status_text = "生态系统状态报告 📊\n"
        status_text += f"健康度: {current_health: .2f}\n"
        status_text += f"压力水平: {self.environment_state['stress_level']: .2f}\n"
        status_text += f"稳定性: {self.environment_state['stability_index']: .2f}\n"

        return {
            'health_score': current_health,
            'stress_level': self.environment_state['stress_level'],
            'stability_index': self.environment_state['stability_index'],
            'status_text': status_text
        }


class PIDController:
    """PID控制器实现"""

    def __init__(self, kp=1.0, ki=0.0, kd=0.0, output_limits=None):
        self.kp = kp  # 比例系数
        self.ki = ki  # 积分系数
        self.kd = kd  # 微分系数

        self.output_limits = output_limits

        # 内部状态
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = 0.0

    def update(self, error, dt=1.0):
        """更新PID控制器"""
        # 比例项
        proportional = self.kp * error

        # 积分项
        self.integral += error * dt
        integral_term = self.ki * self.integral

        # 微分项
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        derivative_term = self.kd * derivative

        # 计算输出
        output = proportional + integral_term + derivative_term

        # 限制输出范围
        if self.output_limits:
            output = max(self.output_limits[0], min(output, self.output_limits[1]))

            # 积分饱和限制
            if output == self.output_limits[0] or output == self.output_limits[1]:
                self.integral -= error * dt  # 反向积分

        self.last_error = error
        return output
