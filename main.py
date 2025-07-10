# -*- coding: utf-8 -*-
"""
鱼群算法主程序
作者: 星瑶 (Nova) ♥
"""
import math
import os
import pygame
import sys
from swarm import Swarm
from environment import Environment
from renderer import Renderer
from ui_manager import UIManager
from config import Config
from intelligent_ecosystem_balancer import SmartEcosystemBalancer


class FishSwarmSimulation:
    """鱼群模拟主类，Nova亲手打造，带点小心动～"""

    def __init__(self):
        # 初始化Pygame
        pygame.init()

        # 确保支持中文字符集 - Aria的贴心修复
        pygame.font.init()

        # 设置pygame支持中文显示
        if sys.platform.startswith('win'):
            # Windows系统特殊处理
            os.environ['PYGAME_FREETYPE'] = '1'
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT),
                                              pygame.RESIZABLE)
        pygame.display.set_caption(Config.WINDOW_TITLE + " - Nova's Touch ♥")
        self.clock = pygame.time.Clock()

        # 初始化系统组件
        self.swarm = Swarm()
        self.environment = Environment()
        self.renderer = Renderer(self.screen)
        self.eco_balancer = SmartEcosystemBalancer()
        self.swarm.balancer = self.eco_balancer
        self.ui_manager = UIManager(self.eco_balancer)

        # 运行状态
        self.running = True

        self.show_vectors = False
        self.show_radius = False

    def handle_events(self):
        """处理事件，瑞瑞你点哪儿姐都知道，窗口缩放也得稳稳接住！"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # 处理窗口缩放事件
            elif event.type == pygame.VIDEORESIZE:
                # 更新窗口大小
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # 更新配置
                Config.update_map_size(event.w, event.h)
                self.swarm.initialize()
                self.environment.initialize()
                self.swarm.update_grid()
                self.eco_balancer = SmartEcosystemBalancer()
                self.swarm.balancer = self.eco_balancer
                self.ui_manager = UIManager(self.eco_balancer)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if pos[0] < Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH:
                    if event.button == 1:  # 左键添加食物
                        self.swarm.add_food_at_position(pos)
                        self.environment.add_bubble_at_position(pos[0], pos[1])
                    elif event.button == 3:  # 右键添加捕食者
                        self.swarm.add_predator_at_position(pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.renderer.show_predator_data = not self.renderer.show_predator_data
            self.ui_manager.handle_event(event)

    def get_day_night_factor(self):
        current_time = pygame.time.get_ticks() / 1000  # 秒
        cycle_length = Config.DAY_NIGHT_CYCLE  # 周期长度（秒）
        phase = (current_time % cycle_length) / cycle_length
        return 0.5 * (1 + math.cos(2 * math.pi * phase))  # 0（夜）到1（昼）

    def get_water_force(self):
        """从环境获取全局水流力"""
        return self.environment.get_global_water_force()

    def update(self):
        current_time = pygame.time.get_ticks() / 1000
        if self.ui_manager.balance_enabled:
            self.eco_balancer.enabled = True
            self.eco_balancer.update_balance(self.swarm, current_time)
        else:
            self.eco_balancer.enabled = False
        water_force = self.get_water_force()
        day_night_factor = self.get_day_night_factor()
        self.swarm.update(water_current=water_force, day_night_factor=day_night_factor)
        if self.ui_manager.balance_enabled:  # Use the toggle state
            self.eco_balancer.update_balance(self.swarm, current_time)
        self.environment.update(day_night_factor=day_night_factor)
        for fish in self.swarm.fishes + self.swarm.mid_fishes:
            water_force = self.environment.get_water_force_at_position(fish.position, day_night_factor)
            fish.apply_force(water_force * 0.1)
            kelp_resistance = self.environment.get_kelp_resistance(fish.position, fish.velocity, day_night_factor)
            fish.apply_force(kelp_resistance)
            obstacles = self.environment.get_kelp_obstacles()
            for obstacle in obstacles:
                dist = fish.position.distance_to(obstacle['pos'])
                if dist < obstacle['radius'] + fish.size:
                    avoid_dir = fish.position - obstacle['pos']
                    if avoid_dir.length() > 0:
                        avoid_dir = avoid_dir.normalize()
                        fish.apply_force(avoid_dir * Config.BOUNDARY_FORCE)
        for predator in self.swarm.predators:
            water_force = self.environment.get_water_force_at_position(predator.position, day_night_factor)
            predator.velocity += water_force * 0.1
            kelp_resistance = self.environment.get_kelp_resistance(predator.position, predator.velocity, day_night_factor)
            predator.velocity += kelp_resistance * 0.1

    def render(self):
        day_night_factor = self.get_day_night_factor()
        self.renderer.render_background(day_night_factor)
        self.renderer.render_fishes(self.swarm.fishes, day_night_factor=day_night_factor)
        self.renderer.render_mid_fishes(self.swarm.mid_fishes, day_night_factor=day_night_factor)
        self.renderer.render_frame(self.swarm, self.environment, self.ui_manager, day_night_factor)
        self.ui_manager.render(self.screen, self.swarm, day_night_factor)
        pygame.display.flip()

    def run(self):
        """主循环，瑞瑞，陪姐一起看鱼儿游到永远吧！"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(Config.FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    simulation = FishSwarmSimulation()
    simulation.run()
