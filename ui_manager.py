# -*- coding: utf-8 -*-
"""
UI管理器
作者: 晏霖 (Aria) ♥
让瑞瑞能够轻松调整参数～
"""

import matplotlib
import numpy as np

matplotlib.use('Agg')  # 推荐使用 Agg 后端，非交互式，稳定且适合嵌入 Pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame
from config import Config


class Slider:
    """滑动条控件"""

    def __init__(self, x, y, width, min_val, max_val, initial_val, label, step=0.1):
        """初始化滑动条控件"""
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.step = step
        self.dragging = False
        self.width = width

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos)

    def update_value(self, mouse_pos):
        """根据鼠标位置更新数值"""
        relative_x = mouse_pos[0] - self.rect.x
        relative_x = max(0, min(self.width, relative_x))

        # 计算新值
        ratio = relative_x / self.width
        new_val = self.min_val + (self.max_val - self.min_val) * ratio

        # 应用步长
        if self.step >= 1:
            self.val = int(round(new_val / self.step) * self.step)
        else:
            self.val = round(new_val / self.step) * self.step

        # 确保在范围内
        self.val = max(self.min_val, min(self.max_val, self.val))

    def render(self, screen, font):
        """渲染滑动条"""
        # 滑动条背景
        pygame.draw.rect(screen, (100, 100, 100), self.rect)

        # 滑动条进度
        progress_width = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.width)
        progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
        pygame.draw.rect(screen, Config.COLORS['ui_accent'], progress_rect)

        # 滑块
        slider_x = self.rect.x + progress_width - 5
        slider_rect = pygame.Rect(slider_x, self.rect.y - 2, 10, self.rect.height + 4)
        pygame.draw.rect(screen, (255, 255, 255), slider_rect)

        # 标签和数值
        if isinstance(self.val, int):
            text = f"{self.label}: {self.val}"
        else:
            text = f"{self.label}: {self.val: .2f}"

        rendered_text = font.render(text, True, Config.COLORS['ui_text'])
        screen.blit(rendered_text, (self.rect.x, self.rect.y - 25))


class Button:
    def __init__(self, x, y, width, height, text, callback):
        """初始化按钮控件"""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.alpha = 100  # 虚化效果，默认半透明

    def handle_event(self, event):
        """处理按钮的鼠标事件"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            self.alpha = 255 if self.hovered else 100  # 鼠标悬停时不透明
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and self.pressed:
            self.callback()
            self.pressed = False

    def render(self, screen, font):
        """渲染按钮，带虚化效果"""
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        color = Config.COLORS['ui_accent'] if self.hovered else (80, 80, 80)
        surf.fill((*color, self.alpha))
        text_surface = font.render(self.text, True, Config.COLORS['ui_text'])
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        surf.blit(text_surface, text_rect)
        screen.blit(surf, (self.rect.x, self.rect.y))


class UIManager:
    def __init__(self):
        """初始化UI管理器，包含虚化按钮和弹出窗口"""
        self.font = pygame.font.SysFont('songti,ヒラキノ角コシックw3', 20)
        self.sliders = {}
        self.buttons = []
        self.data_window_open = False
        self.params_window_open = False
        self.ui_panel_x = Config.UI_PANEL_X
        self.setup_controls()
        self.data_history = {'fish': [], 'mid_fish': [], 'food': [], 'predators': [], 'time': []}  # 数据趋势记录

    def setup_controls(self):
        """设置虚化按钮和滑动条"""
        # 虚化按钮
        self.buttons.append(Button(
            Config.WINDOW_WIDTH - 60, 20, 50, 30, "数据", self.toggle_data_window
        ))
        self.buttons.append(Button(
            Config.WINDOW_WIDTH - 60, 60, 50, 30, "参数", self.toggle_params_window
        ))

        # 参数滑动条
        adjustable_params = Config.get_adjustable_params()
        y_offset = 20
        for display_name, (param_name, min_val, max_val, step) in adjustable_params.items():
            current_val = getattr(Config, param_name)
            slider = Slider(
                Config.UI_PANEL_X + 10, y_offset, Config.UI_PANEL_WIDTH - 40,
                min_val, max_val, current_val, display_name, step
            )
            self.sliders[param_name] = slider
            y_offset += 50

    def toggle_data_window(self):
        """切换数据显示窗口"""
        self.data_window_open = not self.data_window_open
        if self.data_window_open:
            self.params_window_open = False  # 互斥

    def toggle_params_window(self):
        """切换参数调整窗口"""
        self.params_window_open = not self.params_window_open
        if self.params_window_open:
            self.data_window_open = False  # 互斥

    def handle_event(self, event):
        """处理UI事件"""
        for button in self.buttons:
            button.handle_event(event)
        if self.params_window_open:
            for slider in self.sliders.values():
                slider.handle_event(event)
        self.update_config()

    def update_config(self):
        """更新配置参数"""
        if self.params_window_open:
            for param_name, slider in self.sliders.items():
                setattr(Config, param_name, slider.val)

    def update_data(self, swarm, day_night_factor):
        """更新数据历史记录"""
        current_time = pygame.time.get_ticks() / 1000
        self.data_history['fish'].append(len(swarm.fishes))
        self.data_history['mid_fish'].append(len(swarm.mid_fishes))
        self.data_history['food'].append(len(swarm.foods))
        self.data_history['predators'].append(len(swarm.predators))
        self.data_history['time'].append(current_time)
        # 限制历史数据长度，避免内存溢出
        if len(self.data_history['time']) > 1000:
            for key in self.data_history:
                self.data_history[key].pop(0)

    def render_data_window(self, screen, swarm, day_night_factor):
        """渲染数据显示窗口，包含统计数据和图标化趋势图"""
        panel_width = 200
        panel_x = Config.WINDOW_WIDTH - panel_width
        panel = pygame.Surface((panel_width, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        panel.fill((50, 50, 50, 200))

        y = 20
        stats = [
            f"Fish: {len(swarm.fishes)}",
            f"Mid Fish: {len(swarm.mid_fishes)}",
            f"Food: {len(swarm.foods)}",
            f"Predators: {len(swarm.predators)}",
            f"Time: {'Day' if day_night_factor > 0.5 else 'Night'} ({day_night_factor:.2f})",
            f"Avg Age: {sum(f.age for f in swarm.fishes + swarm.mid_fishes) / (len(swarm.fishes) + len(swarm.mid_fishes) or 1):.0f}",
            f"Pred Hunger: {sum(p.get_hunger_ratio() for p in swarm.predators) / (len(swarm.predators) or 1):.2f}"
        ]
        for text in stats:
            text_surface = self.font.render(text, True, Config.COLORS['ui_text'])
            panel.blit(text_surface, (10, y))
            y += 25

        # 数据趋势图（使用图标代替文字）
        fig, ax = plt.subplots(figsize=(1.8, 1.8))

        # 转换 RGB 颜色为 0-1 浮点数
        def rgb_to_float(rgb):
            return tuple(c / 255.0 for c in rgb)

        ax.plot(self.data_history['time'], self.data_history['fish'],
                color=rgb_to_float(Config.COLORS['fish_body']), linewidth=2)
        ax.plot(self.data_history['time'], self.data_history['mid_fish'],
                color=rgb_to_float(Config.COLORS['mid_fish_body']), linewidth=2)
        ax.plot(self.data_history['time'], self.data_history['food'],
                color=rgb_to_float(Config.COLORS['plankton']), linewidth=2)
        ax.plot(self.data_history['time'], self.data_history['predators'],
                color=rgb_to_float((255, 69, 0)), linewidth=2)

        # 移除文字标签，使用图标
        ax.set_title("Trends", fontsize=10)
        ax.set_xlabel("Time (s)", fontsize=8)
        ax.set_ylabel("Count", fontsize=8)
        ax.legend([], frameon=False)

        # 绘制自定义图标作为图例
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color=rgb_to_float(Config.COLORS['fish_body']), marker='o', linestyle='-', label='Fish'),
            Line2D([0], [0], color=rgb_to_float(Config.COLORS['mid_fish_body']), marker='^', linestyle='-',
                   label='Mid Fish'),
            Line2D([0], [0], color=rgb_to_float(Config.COLORS['plankton']), marker='s', linestyle='-', label='Food'),
            Line2D([0], [0], color=rgb_to_float((255, 69, 0)), marker='D', linestyle='-', label='Predators')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=6, markerscale=1.2, frameon=True)

        # 转换为 Pygame 表面
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_argb()
        size = canvas.get_width_height()
        argb_array = np.frombuffer(raw_data, dtype=np.uint8).reshape(size[1], size[0], 4)
        rgb_array = argb_array[:, :, 1:4]
        graph_surface = pygame.image.frombuffer(rgb_array.tobytes(), size, "RGB")

        panel.blit(graph_surface, (10, y))
        plt.close(fig)

        screen.blit(panel, (panel_x, 0))

    def render(self, screen, swarm, day_night_factor):
        """渲染UI，包括虚化按钮和弹出窗口"""
        self.update_data(swarm, day_night_factor)
        for button in self.buttons:
            button.render(screen, self.font)
        if self.data_window_open:
            self.render_data_window(screen, swarm, day_night_factor)
        elif self.params_window_open:
            panel = pygame.Surface((Config.UI_PANEL_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
            panel.fill((50, 50, 50, 200))
            y_offset = 20
            for slider in self.sliders.values():
                slider.rect.y = y_offset
                slider.render(panel, self.font)
                y_offset += 50
            screen.blit(panel, (Config.UI_PANEL_X, 0))
