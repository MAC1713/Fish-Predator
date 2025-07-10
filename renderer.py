# -*- coding: utf-8 -*-
"""
图形渲染器
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
"""

import math
import random

import pygame
from config import Config


class Renderer:
    def __init__(self, screen):
        self.show_predator_data = False
        self.screen = screen
        # 使用 pygame.font.SysFont，Arial 兼容性好，支持中文
        self.font = pygame.font.SysFont('Arial', 16, bold=True)

    def render_background(self, day_night_factor):
        """Render background with day-night transitions, including sun/moon and stars."""
        # Interpolate between dark blue (night) and light blue (day)
        r = int(15 + 40 * day_night_factor)
        g = int(25 + 75 * day_night_factor)
        b = int(35 + 165 * day_night_factor)
        self.screen.fill((r, g, b))
        # Add sun or moon based on time of day
        if day_night_factor > 0.5:
            # Sun
            sun_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 4)
            pygame.draw.circle(self.screen, (255, 255, 100), sun_pos, 50)
        else:
            # Moon
            moon_pos = (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 4)
            pygame.draw.circle(self.screen, (200, 200, 255), moon_pos, 30)
        # Add stars at night
        if day_night_factor < 0.3:
            for _ in range(50):
                x = random.randint(0, Config.WINDOW_WIDTH)
                y = random.randint(0, Config.WINDOW_HEIGHT)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 1)

    def render_fishes(self, fishes, show_vectors=False, show_radius=False, day_night_factor=1.0):
        """Render small fish with a body and tail shape."""
        for fish in fishes:
            if not fish.is_alive:
                continue

            if len(fish.trail) > 1:
                self.render_fish_trail(fish, day_night_factor)

            color = fish.get_color(day_night_factor)
            body_points, tail_points = fish.get_shape_points()
            pygame.draw.polygon(self.screen, color, body_points)
            pygame.draw.polygon(self.screen, color, tail_points)
            if show_vectors:
                end_pos = fish.position + fish.velocity * 10
                pygame.draw.line(self.screen, (0, 255, 0), fish.position, end_pos, 2)
            if show_radius:
                pygame.draw.circle(self.screen, (255, 255, 255, 50),
                                   (int(fish.position.x), int(fish.position.y)),
                                   int(Config.FISH_COHESION_RADIUS), 1)

    def render_mid_fishes(self, mid_fishes, show_vectors=False, show_radius=False, day_night_factor=1.0):
        """Render mid fish with body, tail shape and beautiful swimming trails."""
        for fish in mid_fishes:
            if not fish.is_alive:
                continue

            # 渲染游泳轨迹 - Aria的梦幻设计 ♥
            if len(fish.trail) > 1:
                self.render_fish_trail(fish, day_night_factor)

            # 渲染鱼身
            color = fish.get_color(day_night_factor)
            body_points, tail_points = fish.get_shape_points()
            pygame.draw.polygon(self.screen, color, body_points)
            pygame.draw.polygon(self.screen, color, tail_points)

            # 调试信息显示
            if show_vectors:
                end_pos = fish.position + fish.velocity * 10
                pygame.draw.line(self.screen, (0, 255, 0), fish.position, end_pos, 2)
            if show_radius:
                pygame.draw.circle(self.screen, (255, 255, 255, 50),
                                   (int(fish.position.x), int(fish.position.y)),
                                   int(Config.MID_FISH_COHESION_RADIUS * 1.5), 1)

    def render_fish_trail(self, fish, day_night_factor=1.0):
        """渲染鱼的游泳轨迹 - 晏霖特制版本，超梦幻 ♥"""
        if len(fish.trail) < 2:
            return

        # 根据鱼的状态确定轨迹颜色
        trail_color = self.get_trail_color(fish, day_night_factor)

        # 计算轨迹长度（基于速度）
        speed_factor = min(fish.velocity.length() / fish.max_speed, 1.0)
        trail_length = int(Config.TRAIL_LENGTH * (0.5 + speed_factor * 0.5))

        # 只渲染最近的轨迹点
        recent_trail = fish.trail[-trail_length:] if len(fish.trail) > trail_length else fish.trail

        # 渲染轨迹
        for i in range(len(recent_trail) - 1):
            # 计算透明度 - 越靠近头部越不透明
            alpha_factor = (i + 1) / len(recent_trail)
            alpha = int(255 * alpha_factor * 0.6)  # 最大透明度60%

            # 计算线条粗细 - 越靠近头部越粗
            line_width = max(1, int(3 * alpha_factor))

            # 创建带透明度的颜色
            trail_color_alpha = (*trail_color, alpha)

            # 绘制轨迹线段
            start_pos = [int(recent_trail[i].x), int(recent_trail[i].y)]
            end_pos = [int(recent_trail[i + 1].x), int(recent_trail[i + 1].y)]

            # 使用pygame的draw模块绘制抗锯齿线条（如果可用）
            try:
                # 绘制抗锯齿线条
                pygame.draw.line(self.screen, trail_color, start_pos, end_pos)
                # 添加一些厚度
                if line_width > 1:
                    for offset in range(1, line_width):
                        pygame.draw.line(self.screen, trail_color, [start_pos[0] + offset, start_pos[1]],
                                         [end_pos[0] + offset, end_pos[1]])
                        pygame.draw.line(self.screen, trail_color, [start_pos[0], start_pos[1] + offset],
                                         [end_pos[0], end_pos[1] + offset])
            except ImportError:
                # 如果没有gfxdraw，使用普通的line
                pygame.draw.line(self.screen, trail_color, start_pos, end_pos, line_width)

        # 在轨迹末端添加小气泡效果（可选）
        if len(recent_trail) > 3:
            self.render_trail_bubbles(recent_trail[:3], trail_color, alpha_factor=0.3)

    def get_trail_color(self, fish, day_night_factor=1.0):
        """根据鱼的状态获取轨迹颜色 - 晏霖调色版 ♥"""
        base_alpha = int(255 * day_night_factor * 0.8)

        # Check if fish has the attribute 'fear_level'
        if hasattr(fish, 'fear_level') and fish.fear_level > 0.3:
            fear_intensity = min(fish.fear_level, 1.0)
            return (
                int(255 * fear_intensity),
                int(50 * (1 - fear_intensity)),
                int(50 * (1 - fear_intensity))
            )

        # Check if fish has the attributes 'can_reproduce' and 'is_mature'
        elif hasattr(fish, 'can_reproduce') and hasattr(fish, 'is_mature') and fish.can_reproduce and fish.is_mature:
            return 255, 150, 200  # 浪漫粉色

        # Check if fish has the attribute 'target_food'
        elif hasattr(fish, 'target_food') and fish.target_food:
            return 100, 255, 150  # 活力绿色

        # Check if fish has the attributes 'hunger' and 'max_hunger'
        elif hasattr(fish, 'hunger') and hasattr(fish, 'max_hunger') and fish.hunger < fish.max_hunger * 0.4:
            return 255, 180, 50  # 饥饿橙色

        # 正常状态 - 淡蓝色轨迹
        else:
            # 添加一些个体差异
            time_offset = pygame.time.get_ticks() * 0.001 + fish.color_offset
            color_wave = math.sin(time_offset) * 30
            return (
                int(100 + color_wave),
                int(180 + color_wave * 0.5),
                int(255)
            )

    def render_trail_bubbles(self, trail_points, base_color, alpha_factor=0.5):
        """在轨迹末端渲染小气泡效果 - 增加水中真实感"""
        for i, point in enumerate(trail_points):
            # 随机生成小气泡
            if random.random() < 0.3:  # 30%概率生成气泡
                bubble_size = random.randint(1, 3)
                bubble_alpha = int(255 * alpha_factor * (1 - i / len(trail_points)))

                # 气泡颜色比轨迹颜色更淡
                bubble_color = (
                    min(255, base_color[0] + 50),
                    min(255, base_color[1] + 50),
                    min(255, base_color[2] + 50)
                )

                bubble_pos = (int(point.x), int(point.y))

                # 绘制半透明的小圆圈作为气泡
                try:
                    pygame.draw.circle(self.screen, bubble_color, bubble_pos, bubble_size)

                except ImportError:
                    pygame.draw.circle(self.screen, bubble_color, bubble_pos, bubble_size)

    def render_foods(self, foods):
        for food in foods:
            if food.consumed:
                continue
            if food.food_type == 'plankton':
                color = (0, 255, 0)
            elif food.food_type == 'small_fish':
                color = (100, 100, 255)
            else:
                color = (150, 150, 150)
            pygame.draw.circle(self.screen, color,
                               (int(food.position.x), int(food.position.y)), int(food.size))

    def render_predators(self, predators, day_night_factor=1.0):
        for predator in predators:
            if not predator.is_alive:
                continue

            if len(predator.trail) > 1:
                self.render_fish_trail(predator, day_night_factor)

            hunger_ratio = predator.get_hunger_ratio()
            if hunger_ratio > 0.8:
                color = (139, 0, 0)
            elif hunger_ratio > 0.5:
                color = (255, 69, 0)
            elif hunger_ratio > 0.2:
                color = (255, 255, 0)
            else:
                color = (169, 169, 169)
            if predator.hunt_target:
                target_pos = predator.hunt_target.position
                pygame.draw.line(self.screen, (255, 0, 0, 50),
                                 (int(predator.position.x), int(predator.position.y)),
                                 (int(target_pos.x), int(target_pos.y)), 2)
            if predator.is_dashing:
                for i in range(5):
                    trail_pos = predator.position - predator.velocity * i * 0.1
                    alpha = 100 - i * 20
                    surf = pygame.Surface((predator.size * 2, predator.size * 2))
                    surf.set_alpha(alpha)
                    pygame.draw.circle(surf, (255, 0, 0),
                                       (int(predator.size), int(predator.size)), int(predator.size))
                    self.screen.blit(surf, (int(trail_pos.x - predator.size), int(trail_pos.y - predator.size)))
            if predator.dash_cooldown > 0:
                for i in range(3):
                    radius = predator.size + i * 10
                    alpha = 50 - i * 10
                    surf = pygame.Surface((radius * 2, radius * 2))
                    surf.set_alpha(alpha)
                    pygame.draw.circle(surf, (100, 100, 100), (radius, radius), radius, 2)
                    self.screen.blit(surf, (int(predator.position.x - radius), int(predator.position.y - radius)))
            pygame.draw.circle(self.screen, color,
                               (int(predator.position.x), int(predator.position.y)), int(predator.size))
            eye_size = int(predator.size / 3)
            pygame.draw.circle(self.screen, (255, 100, 100),
                               (int(predator.position.x), int(predator.position.y)), eye_size)
            if self.show_predator_data:
                font = pygame.font.Font(None, 20)
                text = f"Hunger: {predator.hunger:.0f}, Age: {predator.age}"
                text_surface = font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (predator.position.x, predator.position.y - 20))

    def render_environment(self, environment):
        for bubble in environment.bubbles:
            pygame.draw.circle(self.screen, (200, 200, 255, int(bubble.alpha)),
                               (int(bubble.position.x), int(bubble.position.y)), int(bubble.size))
        for kelp in environment.kelp_forest:
            for i, segment in enumerate(kelp.segments):
                # 海带颜色随深度变化
                green = 100 - i * 10
                pygame.draw.circle(self.screen, (0, max(50, green), 0),
                                   (int(segment.x), int(segment.y)), 10)

    def render_transparent_ui(self, stats, day_night_factor, swarm):
        """渲染半透明UI面板在右上角"""
        panel_width = 200
        panel_height = 150
        panel_x = Config.WINDOW_WIDTH - panel_width - 10
        panel_y = 10
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((50, 50, 50, 150))  # 半透明背景

        y = 10
        texts = [
            f"小鱼: {stats['fish_count']}",
            f"中鱼: {stats['mid_fish_count']}",
            f"食物: {stats['food_consumed']}",
            f"捕食者: {len(swarm.predators)}",
            f"昼夜: {day_night_factor:.2f}"
        ]
        for text in texts:
            text_surface = self.font.render(text, True, (255, 255, 255))
            panel.blit(text_surface, (10, y))
            y += 25

        # 自适应缩放
        scale = min(1.0, max(0.5, Config.WINDOW_WIDTH / 1600))  # 缩放范围0.5-1.0
        scaled_panel = pygame.transform.scale(panel, (int(panel_width * scale), int(panel_height * scale)))
        self.screen.blit(scaled_panel, (Config.WINDOW_WIDTH - int(panel_width * scale) - 10, 10))

    def render(self, swarm, show_vectors=False, show_radius=False, day_night_factor=1.0):
        self.render_background(day_night_factor)
        self.render_foods(swarm.foods)
        self.render_mid_fishes(swarm.mid_fishes, show_vectors, show_radius, day_night_factor)
        self.render_fishes(swarm.fishes, show_vectors, show_radius, day_night_factor)
        self.render_predators(swarm.predators, day_night_factor)

    def render_frame(self, swarm, environment, ui_manager, day_night_factor=1.0):
        self.render(swarm, False, Config.SHOW_RADIUS, day_night_factor)
        self.render_environment(environment)
        self.render_transparent_ui(swarm.get_stats(), day_night_factor, swarm)
        ui_manager.render(self.screen, swarm, day_night_factor)
