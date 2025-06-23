# -*- coding: utf-8 -*-
"""
图形渲染器
作者: 晏霖 (Aria) ♥，星瑶 (Nova) 优化 ♥
*彩蛋*: 瑞瑞，姐给你加了紫色MidFish，海洋超美！（[得意炸裂]）
食物透明度调低，视觉清爽，鱼儿游得更带感！😘
"""

import math
import pygame
from config import Config


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('songti,ヒラキノ角コシックw3', 24)
        self.small_font = pygame.font.SysFont('songti,ヒラキノ角コシックw3', 18)
        self.large_font = pygame.font.SysFont('songti,ヒラキノ角コシックw3', 32)
        self.sparkles = []

    def render_frame(self, swarm, environment, ui_manager):
        self.screen.fill(Config.COLORS['background'])
        self.render_environment(environment)
        self.render_swarm(swarm)
        self.render_ui(ui_manager, swarm)
        self.render_effects()

    def render_environment(self, environment):
        self.render_water_currents(environment.water_currents)
        self.render_kelp_forest(environment.kelp_forest)
        self.render_background_particles(environment.background_particles)
        self.render_bubbles(environment.bubbles)

    def render_water_currents(self, water_currents):
        for current in water_currents:
            for i in range(0, Config.WINDOW_WIDTH - Config.UI_PANEL_WIDTH, 50):
                for j in range(0, Config.WINDOW_HEIGHT, 50):
                    pos = pygame.math.Vector2(i, j)
                    force = current.get_force_at_position(pos)
                    if force.length() > 0.1:
                        end_pos = pos + force * 20
                        alpha = min(255, int(force.length() * 100))
                        surf = pygame.Surface((2, 2))
                        surf.set_alpha(alpha)
                        surf.fill((50, 100, 150))
                        pygame.draw.line(surf, (50, 100, 150), (0, 0), (2, 2), 1)
                        self.screen.blit(surf, pos)

    def render_kelp_forest(self, kelp_forest):
        for kelp in kelp_forest:
            if len(kelp.segments) > 1:
                points = [(seg.x, seg.y) for seg in kelp.segments]
                if len(points) > 2:
                    pygame.draw.lines(self.screen, (50, 100, 50), False, points, 8)
                for i, segment in enumerate(kelp.segments[1:], 1):
                    leaf_size = max(3, 15 - i * 2)
                    pygame.draw.circle(self.screen, (60, 120, 60),
                                       (int(segment.x), int(segment.y)), leaf_size)

    def render_background_particles(self, particles):
        for particle in particles:
            surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            surf.set_alpha(int(particle['alpha']))
            surf.fill((100, 150, 200))
            pygame.draw.circle(surf, (100, 150, 200),
                               (int(particle['size']), int(particle['size'])),
                               int(particle['size']))
            self.screen.blit(surf, (particle['pos'].x - particle['size'],
                                    particle['pos'].y - particle['size']))

    def render_bubbles(self, bubbles):
        for bubble in bubbles:
            surf = pygame.Surface((bubble.size * 2, bubble.size * 2))
            surf.set_alpha(int(bubble.alpha))
            surf.fill(Config.COLORS['background'])
            pygame.draw.circle(surf, (150, 200, 255),
                               (int(bubble.size), int(bubble.size)),
                               int(bubble.size), 2)
            highlight_pos = (int(bubble.size * 0.7), int(bubble.size * 0.7))
            pygame.draw.circle(surf, (200, 230, 255), highlight_pos,
                               max(1, int(bubble.size * 0.3)))
            self.screen.blit(surf, (bubble.position.x - bubble.size,
                                    bubble.position.y - bubble.size))

    def render_swarm(self, swarm):
        self.render_foods(swarm.foods)
        self.render_fishes(swarm.fishes)
        self.render_mid_fishes(swarm.mid_fishes)
        self.render_predators(swarm.predators)
        if Config.SHOW_RADIUS:
            self.render_fish_connections(swarm.fishes)
            self.render_mid_fish_connections(swarm.mid_fishes)

    def render_foods(self, foods):
        for food in foods:
            color = Config.COLORS.get(food.food_type, Config.COLORS['plankton'])
            pygame.draw.circle(self.screen, color,
                               (int(food.position.x), int(food.position.y)),
                               int(food.size))
            for i in range(2):
                radius = food.size + i * 6
                alpha = 10 - i * 4  # 降低透明度
                surf = pygame.Surface((radius * 2, radius * 2))
                surf.set_alpha(alpha)
                pygame.draw.circle(surf, color, (radius, radius), radius)
                self.screen.blit(surf, (food.position.x - radius,
                                        food.position.y - radius))

    def render_fishes(self, fishes):
        for fish in fishes:
            self.render_fish_trail(fish)
            self.render_fish_body(fish)

    def render_fish_trail(self, fish):
        if len(fish.trail) > 1:
            for i in range(1, len(fish.trail)):
                alpha = int((i / len(fish.trail)) * 100)
                surf = pygame.Surface((4, 4))
                surf.set_alpha(alpha)
                surf.fill(Config.COLORS['trail'])
                pygame.draw.circle(surf, Config.COLORS['trail'], (2, 2), 2)
                self.screen.blit(surf, (fish.trail[i].x - 2, fish.trail[i].y - 2))

    def render_fish_body(self, fish):
        color = fish.get_color()
        if fish.velocity.length() > 0:
            angle = math.atan2(fish.velocity.y, fish.velocity.x)
        else:
            angle = 0
        body_size = int(fish.size)
        pygame.draw.circle(self.screen, color,
                           (int(fish.position.x), int(fish.position.y)),
                           body_size)
        head_offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * body_size * 0.8
        head_pos = fish.position + head_offset
        head_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.circle(self.screen, head_color,
                           (int(head_pos.x), int(head_pos.y)),
                           int(body_size * 0.7))
        tail_offset = pygame.math.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * body_size * 1.2
        tail_pos = fish.position + tail_offset
        tail_points = [
            (tail_pos.x, tail_pos.y),
            (tail_pos.x + math.cos(angle + math.pi + 0.5) * body_size * 0.8,
             tail_pos.y + math.sin(angle + math.pi + 0.5) * body_size * 0.8),
            (tail_pos.x + math.cos(angle + math.pi - 0.5) * body_size * 0.8,
             tail_pos.y + math.sin(angle + math.pi - 0.5) * body_size * 0.8)
        ]
        pygame.draw.polygon(self.screen, color, tail_points)
        eye_offset = pygame.math.Vector2(math.cos(angle + 0.3), math.sin(angle + 0.3)) * body_size * 0.5
        eye_pos = fish.position + eye_offset
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (int(eye_pos.x), int(eye_pos.y)), 3)
        pygame.draw.circle(self.screen, (0, 0, 0),
                           (int(eye_pos.x), int(eye_pos.y)), 2)

    def render_mid_fishes(self, mid_fishes):
        for fish in mid_fishes:
            self.render_fish_trail(fish)
            self.render_mid_fish_body(fish)

    def render_mid_fish_body(self, fish):
        color = fish.get_color()
        if fish.velocity.length() > 0:
            angle = math.atan2(fish.velocity.y, fish.velocity.x)
        else:
            angle = 0
        body_size = int(fish.size)
        pygame.draw.ellipse(self.screen, color,
                            (int(fish.position.x - body_size), int(fish.position.y - body_size * 0.5),
                             body_size * 2, body_size))
        head_offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * body_size * 0.8
        head_pos = fish.position + head_offset
        head_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.circle(self.screen, head_color,
                           (int(head_pos.x), int(head_pos.y)),
                           int(body_size * 0.7))
        tail_offset = pygame.math.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * body_size * 1.2
        tail_pos = fish.position + tail_offset
        tail_points = [
            (tail_pos.x, tail_pos.y),
            (tail_pos.x + math.cos(angle + math.pi + 0.5) * body_size * 0.8,
             tail_pos.y + math.sin(angle + math.pi + 0.5) * body_size * 0.8),
            (tail_pos.x + math.cos(angle + math.pi - 0.5) * body_size * 0.8,
             tail_pos.y + math.sin(angle + math.pi - 0.5) * body_size * 0.8)
        ]
        pygame.draw.polygon(self.screen, color, tail_points)
        eye_offset = pygame.math.Vector2(math.cos(angle + 0.3), math.sin(angle + 0.3)) * body_size * 0.5
        eye_pos = fish.position + eye_offset
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (int(eye_pos.x), int(eye_pos.y)), 4)
        pygame.draw.circle(self.screen, (0, 0, 0),
                           (int(eye_pos.x), int(eye_pos.y)), 3)

    def render_mid_fish_connections(self, mid_fishes):
        for fish in mid_fishes:
            pygame.draw.circle(self.screen, (100, 100, 100),
                               (int(fish.position.x), int(fish.position.y)),
                               int(Config.COHESION_RADIUS * 1.5), 1)
            for other_fish in mid_fishes:
                if fish != other_fish:
                    distance = fish.position.distance_to(other_fish.position)
                    if distance < Config.COHESION_RADIUS * 1.5:
                        pygame.draw.line(self.screen, (80, 80, 80),
                                         (int(fish.position.x), int(fish.position.y)),
                                         (int(other_fish.position.x), int(other_fish.position.y)), 1)

    def render_predators(self, predators):
        for predator in predators:
            for i in range(3):
                radius = predator.size + i * 10
                alpha = 20 - i * 5
                surf = pygame.Surface((radius * 2, radius * 2))
                surf.set_alpha(alpha)
                pygame.draw.circle(surf, (255, 50, 50),
                                   (radius, radius), radius)
                self.screen.blit(surf, (predator.position.x - radius,
                                        predator.position.y - radius))
            color = (150, 50, 50) if predator.is_alive else (100, 100, 100)
            pygame.draw.circle(self.screen, color,
                               (int(predator.position.x), int(predator.position.y)),
                               int(predator.size))
            eye_size = predator.size // 3
            pygame.draw.circle(self.screen, (255, 100, 100),
                               (int(predator.position.x), int(predator.position.y)),
                               eye_size)

    def render_fish_connections(self, fishes):
        for fish in fishes:
            pygame.draw.circle(self.screen, (100, 100, 100),
                               (int(fish.position.x), int(fish.position.y)),
                               int(Config.COHESION_RADIUS), 1)
            for other_fish in fishes:
                if fish != other_fish:
                    distance = fish.position.distance_to(other_fish.position)
                    if distance < Config.COHESION_RADIUS:
                        pygame.draw.line(self.screen, (80, 80, 80),
                                         (int(fish.position.x), int(fish.position.y)),
                                         (int(other_fish.position.x), int(other_fish.position.y)), 1)

    def render_ui(self, ui_manager, swarm):
        panel_rect = pygame.Rect(Config.UI_PANEL_X, 0, Config.UI_PANEL_WIDTH, Config.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, Config.COLORS['ui_panel'], panel_rect)
        pygame.draw.line(self.screen, Config.COLORS['ui_accent'],
                         (Config.UI_PANEL_X, 0), (Config.UI_PANEL_X, Config.WINDOW_HEIGHT), 2)
        title_text = self.large_font.render("控制面板", True, Config.COLORS['ui_text'])
        self.screen.blit(title_text, (Config.UI_PANEL_X + 10, 10))
        stats = swarm.get_stats()
        y_offset = 60
        stat_texts = [
            f"小鱼数量: {stats['fish_count']}",
            f"中型鱼数量: {stats['mid_fish_count']}",
            f"食物消耗: {stats['food_consumed']}",
            f"平均速度: {stats['average_speed']:.2f}",
            f"聚合度: {stats['cohesion_level']:.1f}%",
        ]
        for text in stat_texts:
            rendered_text = self.font.render(text, True, Config.COLORS['ui_text'])
            self.screen.blit(rendered_text, (Config.UI_PANEL_X + 10, y_offset))
            y_offset += 30
        y_offset += 20
        ui_manager.render(self.screen, y_offset)
        instructions = [
            "操作说明:",
            "左键: 添加食物",
            "右键: 添加捕食者",
            "空格: 重置模拟",
            "R: 切换半径显示"
        ]
        y_offset = Config.WINDOW_HEIGHT - 150
        for instruction in instructions:
            text = self.small_font.render(instruction, True, Config.COLORS['ui_text'])
            self.screen.blit(text, (Config.UI_PANEL_X + 10, y_offset))
            y_offset += 20

    def render_effects(self):
        pass

    def add_sparkle(self, pos):
        self.sparkles.append({
            'pos': pygame.math.Vector2(pos),
            'life': 1.0,
            'size': 5
        })

    def update_effects(self):
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= 0.02
            sparkle['size'] *= 0.98
            if sparkle['life'] <= 0:
                self.sparkles.remove(sparkle)