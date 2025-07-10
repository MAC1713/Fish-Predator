# -*- coding: utf-8 -*-
"""
UI管理器
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
"""
import matplotlib
import pygame
from config import Config

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


class Button:
    def __init__(self, x, y, width, height, text, callback, state='off'):
        """初始化按钮控件"""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.alpha = 100
        self.state = state

    def handle_event(self, event):
        """处理按钮的鼠标事件"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            self.alpha = 255 if self.hovered else 100
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and self.pressed:
            self.callback()
            self.pressed = False
            self.state = 'on' if self.state == 'off' else 'off'
            if self.text.startswith("平衡"):
                self.text = "平衡 ON" if self.state == 'on' else "平衡 OFF"

    def render(self, screen, font):
        """渲染按钮，带虚化效果"""
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.state == 'on':
            color = (0, 255, 0)
        else:
            color = Config.COLORS['ui_accent'] if self.hovered else (80, 80, 80)
        surf.fill((*color, self.alpha))
        text_surface = font.render(self.text, True, Config.COLORS['ui_text'])
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        surf.blit(text_surface, text_rect)
        screen.blit(surf, (self.rect.x, self.rect.y))


class UIManager:
    def __init__(self, eco_balancer):
        self.balance_button = None
        self.eco_balancer = eco_balancer
        self.font = pygame.font.SysFont('songti,ヒラキノ角コシックw3', 12)
        self.buttons = []
        self.data_window_open = False
        self.balance_enabled = False
        self.setup_controls()
        self.data_history = {
            'time': [],
            'fish': [],
            'mid_fish': [],
            'food': [],
            'predators': []
        }
        self.last_update_time = 0
        self.update_interval = 1.0
        self.plot_surface = None
        self.last_plot_update = 0
        self.plot_update_interval = 1.0

    def setup_controls(self):
        # 数据按钮
        self.buttons.append(Button(
            Config.WINDOW_WIDTH - 60, 10, 60, 30, "数据", self.toggle_data_window
        ))
        # 智能平衡开关按钮
        self.balance_button = Button(
            Config.WINDOW_WIDTH - 60, 50, 60, 30, "平衡 OFF", self.toggle_balance, state='off'
        )
        self.buttons.append(self.balance_button)

    def toggle_data_window(self):
        """切换数据显示窗口"""
        self.data_window_open = not self.data_window_open

    def toggle_balance(self):
        self.balance_enabled = not self.balance_enabled
        self.eco_balancer.enabled = self.balance_enabled

    def handle_event(self, event):
        """处理UI事件"""
        for button in self.buttons:
            button.handle_event(event)

    def update_data_history(self, swarm, current_time):
        if current_time - self.last_update_time >= self.update_interval:
            self.data_history['time'].append(current_time)
            self.data_history['fish'].append(len([f for f in swarm.fishes if f.is_alive]))
            self.data_history['mid_fish'].append(len([f for f in swarm.mid_fishes if f.is_alive]))
            self.data_history['food'].append(len([f for f in swarm.foods if not f.consumed]))
            self.data_history['predators'].append(len([p for p in swarm.predators if p.is_alive]))
            self.last_update_time = current_time
            if len(self.data_history['time']) > 100:
                for key in self.data_history:
                    self.data_history[key].pop(0)

    def generate_plot_surface(self):
        if not self.data_history['time'] or len(self.data_history['time']) < 2:
            return None
        try:
            plt.clf()  # Nova: 清空旧图，防内存泄漏
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['figure.max_open_warning'] = 0
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

            # 确保有足够的数据点
            if len(self.data_history['time']) > 0:
                ax.plot(self.data_history['time'], self.data_history['fish'], label='Fish', color='#1f77b4',
                        linewidth=2)
                ax.plot(self.data_history['time'], self.data_history['mid_fish'], label='Mid Fish', color='#ff7f0e',
                        linewidth=2)
                ax.plot(self.data_history['time'], self.data_history['food'], label='Food', color='#2ca02c',
                        linewidth=2)
                ax.plot(self.data_history['time'], self.data_history['predators'], label='Predator', color='#d62728',
                        linewidth=2)

            ax.set_xlabel('Time (s)', fontsize=10)
            ax.set_ylabel('Count', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.7)
            fig.tight_layout()

            # 关键修复：强制渲染canvas
            fig.canvas.draw()

            # 获取渲染后的数据
            plot_data = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
            plot_data = plot_data.reshape(fig.canvas.get_width_height()[::-1] + (4,))[:, :, :3]
            plot_surface = pygame.surfarray.make_surface(plot_data.swapaxes(0, 1))

            plt.close(fig)
            return plot_surface
        except Exception as e:
            print(f"Error generating plot: {e}")
            # 返回一个带错误信息的surface
            error_surface = pygame.Surface((500, 400))
            error_surface.fill((50, 50, 50))
            return error_surface

    def render_balance_data(self, screen):
        if not self.balance_enabled:
            return
        balance_status = self.eco_balancer.get_balance_status()
        panel_width = 400
        panel_height = 420
        panel_x = Config.WINDOW_WIDTH - panel_width - 10
        panel_y = 170
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((50, 50, 50, 150))
        y = 10
        texts = [
            f"Overall Score: {balance_status['overall_score']:.2f}",
            f"Small Fish: {balance_status['small_fish_score']:.2f}",
            f"Mid Fish: {balance_status['mid_fish_score']:.2f}",
            f"Predator: {balance_status['predator_score']:.2f}",
            "Adjusted Params:"
        ]
        for key, value in balance_status['adjusted_params'].items():
            texts.append(f"  {key}: {value: .4f}")
        for text in texts:
            text_surface = self.font.render(text, True, Config.COLORS['ui_text'])
            panel.blit(text_surface, (10, y))
            y += 10
        screen.blit(panel, (panel_x, panel_y))

    def render(self, screen, swarm, day_night_factor):
        """渲染UI，包括虚化按钮和弹出窗口"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.update_data_history(swarm, current_time)
        if current_time - self.last_plot_update >= self.plot_update_interval:
            self.plot_surface = self.generate_plot_surface()
            self.last_plot_update = current_time
        for button in self.buttons:
            button.render(screen, self.font)
        if self.data_window_open and self.plot_surface:  # Nova: 确保plot_surface存在
            self.render_data_window(screen, swarm, day_night_factor)
        if self.balance_enabled:
            self.render_balance_data(screen)

    def render_data_window(self, screen, swarm, day_night_factor):
        panel_width = 500
        panel_height = 400
        panel_x = Config.WINDOW_WIDTH - panel_width - 10
        panel_y = Config.WINDOW_HEIGHT - panel_height - 10
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((50, 50, 50, 150))
        if self.plot_surface:
            plot_rect = self.plot_surface.get_rect(topleft=(10, 10))
            panel.blit(self.plot_surface, plot_rect)
        else:
            error_text = self.font.render("No plot data available", True, Config.COLORS['ui_text'])
            panel.blit(error_text, (10, 10))
        screen.blit(panel, (panel_x, panel_y))
