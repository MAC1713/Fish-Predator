# -*- coding: utf-8 -*-
"""
图形渲染器
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
"""

import math
import pygame
from config import Config


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        # 使用 pygame.font.SysFont，Arial 兼容性好，支持中文
        self.font = pygame.font.SysFont('Arial', 16, bold=True)

    def render_background(self, day_night_factor):
        brightness = int(255 * day_night_factor)
        self.screen.fill((0, 50, brightness))
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = int(50 * day_night_factor)
        pygame.draw.circle(overlay, (255, 255, 200, alpha),
                           (Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 4), 300)
        self.screen.blit(overlay, (0, 0))

    def render_fishes(self, fishes, show_vectors=False, show_radius=False):
        for fish in fishes:
            if not fish.is_alive:
                continue
            fear_color = int(fish.fear_level * 255)
            color = fish.get_color()
            pygame.draw.circle(self.screen, color, (int(fish.position.x), int(fish.position.y)), int(fish.size))
            if show_vectors:
                end_pos = fish.position + fish.velocity * 10
                pygame.draw.line(self.screen, (0, 255, 0), fish.position, end_pos, 2)
            if show_radius:
                pygame.draw.circle(self.screen, (255, 255, 255, 50),
                                   (int(fish.position.x), int(fish.position.y)),
                                   int(Config.COHESION_RADIUS), 1)

    def render_mid_fishes(self, mid_fishes, show_vectors=False, show_radius=False):
        for fish in mid_fishes:
            if not fish.is_alive:
                continue
            fear_color = int(fish.fear_level * 255)
            color = fish.get_color()
            pygame.draw.circle(self.screen, color, (int(fish.position.x), int(fish.position.y)), int(fish.size))
            if show_vectors:
                end_pos = fish.position + fish.velocity * 10
                pygame.draw.line(self.screen, (0, 255, 0), fish.position, end_pos, 2)
            if show_radius:
                pygame.draw.circle(self.screen, (255, 255, 255, 50),
                                   (int(fish.position.x), int(fish.position.y)),
                                   int(Config.COHESION_RADIUS * 1.5), 1)

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

    def render_ui(self, stats, day_night_factor=1.0):
        panel_x = Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (panel_x, 0, Config.UI_PANEL_WIDTH, Config.WINDOW_HEIGHT))
        y = 20
        texts = [
            f"Fish: {stats['fish_count']}",
            f"Mid Fish: {stats['mid_fish_count']}",
            f"Food Consumed: {stats['food_consumed']}",
            f"Avg Speed: {stats['average_speed']:.2f}",
            f"Cohesion: {stats['cohesion_level']:.2f}",
            f"Day/Night: {day_night_factor:.2f}"
        ]
        for text in texts:
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (panel_x + 10, y))
            y += 20

    def render(self, swarm, show_vectors=False, show_radius=False, day_night_factor=1.0):
        self.render_background(day_night_factor)
        self.render_foods(swarm.foods)
        self.render_mid_fishes(swarm.mid_fishes, show_vectors, show_radius)
        self.render_fishes(swarm.fishes, show_vectors, show_radius)
        self.render_predators(swarm.predators)
        self.render_ui(swarm.get_stats(), day_night_factor)

    def render_frame(self, swarm, environment, ui_manager, day_night_factor=1.0):
        self.render(swarm, False, Config.SHOW_RADIUS, day_night_factor)
        self.render_environment(environment)
        ui_manager.render(self.screen, swarm, day_night_factor)
