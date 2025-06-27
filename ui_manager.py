# -*- coding: utf-8 -*-
"""
UI管理器
作者: 晏霖 (Aria) ♥
让瑞瑞能够轻松调整参数～
"""

import pygame
from config import Config


class Slider:
    """滑动条控件"""

    def __init__(self, x, y, width, min_val, max_val, initial_val, label, step=0.1):
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
            text = f"{self.label}: {self.val:.2f}"

        rendered_text = font.render(text, True, Config.COLORS['ui_text'])
        screen.blit(rendered_text, (self.rect.x, self.rect.y - 25))


class Button:
    """按钮控件"""

    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.callback()
            self.pressed = False

    def render(self, screen, font):
        """渲染按钮"""
        # 按钮颜色
        if self.pressed:
            color = (150, 150, 150)
        elif self.hovered:
            color = Config.COLORS['ui_accent']
        else:
            color = (80, 80, 80)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, Config.COLORS['ui_text'], self.rect, 2)

        # 按钮文字
        text_surface = font.render(self.text, True, Config.COLORS['ui_text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class UIManager:
    """UI管理器"""

    def __init__(self):
        self.font = pygame.font.SysFont('songti,ヒラキノ角コシックw3', 20)
        self.sliders = {}
        self.buttons = []
        self.ui_panel_x = Config.UI_PANEL_X
        self.setup_controls()

    def setup_controls(self):
        """设置控件"""
        # 创建参数滑动条
        adjustable_params = Config.get_adjustable_params()
        y_offset = 0

        for display_name, (param_name, min_val, max_val, step) in adjustable_params.items():
            current_val = getattr(Config, param_name)

            slider = Slider(
                Config.UI_PANEL_X + 10,
                y_offset,
                Config.UI_PANEL_WIDTH - 40,
                min_val, max_val, current_val,
                display_name, step
            )

            self.sliders[param_name] = slider
            y_offset += 50

        # 创建按钮
        button_y = y_offset + 20

        self.buttons.append(Button(
            Config.UI_PANEL_X + 10, button_y, 120, 30,
            "重置模拟", self.reset_simulation
        ))

        self.buttons.append(Button(
            Config.UI_PANEL_X + 140, button_y, 120, 30,
            "切换显示", self.toggle_radius_display
        ))

    def handle_event(self, event):
        """处理UI事件"""
        # 处理滑动条事件
        for slider in self.sliders.values():
            slider.handle_event(event)

        # 处理按钮事件
        for button in self.buttons:
            button.handle_event(event)

        # 更新配置参数
        self.update_config()

    def update_config(self):
        """更新配置参数"""
        for param_name, slider in self.sliders.items():
            setattr(Config, param_name, slider.val)

    def render(self, screen, y_offset=20):
        """渲染UI"""
        if self.ui_panel_x != Config.UI_PANEL_X:
            self.ui_panel_x = Config.UI_PANEL_X
            self.setup_controls()  # Reinitialize positions
        current_y = y_offset

        # 渲染滑动条
        for param_name, slider in self.sliders.items():
            slider.rect.y = current_y
            slider.render(screen, self.font)
            current_y += 50

        # 渲染按钮
        button_y = current_y + 20
        for i, button in enumerate(self.buttons):
            button.rect.y = button_y
            if i > 0:
                button.rect.x = Config.UI_PANEL_X + 140
            else:
                button.rect.x = Config.UI_PANEL_X + 10
            button.render(screen, self.font)

    def reset_simulation(self):
        """重置模拟的回调"""
        # 这个会在main.py中被处理
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'action': 'reset'}))

    def toggle_radius_display(self):
        """切换半径显示"""
        Config.SHOW_RADIUS = not Config.SHOW_RADIUS