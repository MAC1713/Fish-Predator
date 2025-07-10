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
        """Render mid fish with a body and tail shape."""
        for fish in mid_fishes:
            if not fish.is_alive:
                continue
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
                                   int(Config.MID_FISH_COHESION_RADIUS * 1.5), 1)

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

    def render_predators(self, predators):
        for predator in predators:
            if not predator.is_alive:
                continue
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
        self.render_mid_fishes(swarm.mid_fishes, show_vectors, show_radius)
        self.render_fishes(swarm.fishes, show_vectors, show_radius)
        self.render_predators(swarm.predators)

    def render_frame(self, swarm, environment, ui_manager, day_night_factor=1.0):
        self.render(swarm, False, Config.SHOW_RADIUS, day_night_factor)
        self.render_environment(environment)
        self.render_transparent_ui(swarm.get_stats(), day_night_factor, swarm)
        ui_manager.render(self.screen, swarm, day_night_factor)
