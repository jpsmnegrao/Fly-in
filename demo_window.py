"""mambo jambo.
"""


import pygame
from data import MapData
from map_renderer import MapRenderer


class DemoWindow():
    """mambo"""

    def __init__(self, map_data: MapData) -> None:
        """jambo"""
        # pygame initialization
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("==== Fly-In ====")
        self.map_data = map_data
        # display and animation timing
        self.screen = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.map_renderer = MapRenderer(map_data, self.screen)
        # states
        self.running = True
        self.running_animation = False
        # animation sprites
        self.walk = pygame.transform.flip(
            pygame.image.load("assets/wwalk.png"), True, False)
        self.walk.set_colorkey((128, 128, 192))
        self.walk_down = pygame.transform.flip(
            pygame.image.load("assets/wwalkd.png"), True, False)
        self.walk_down.set_colorkey((128, 128, 192))
        self.walk_up = pygame.transform.flip(
            pygame.image.load("assets/wwalku.png"), True, False)
        self.walk_up.set_colorkey((128, 128, 192))
        # font and title
        self.font = pygame.font.SysFont(None, 25)
        self.title = self.font.render(" ====  Fly-In  ==== ", True, "gray")
        self.title_pos = self.title.get_rect(center=(400, 25))
        # map area and dimension offsets
        self.map_x = 95
        self.map_y = 60
        self.map_size = 610
        # animation step
        self.frame_height = self.walk.get_height() // 15
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_direction = 1
        self.speed: float = 590 / 5000
        self.x: float = self.map_x + 10
        self.y: float = self.map_y + 305 - self.frame_height // 2

    def run_renderer(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        self.running_animation = True
                    if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                        self.x = 95 + 10
                        self.current_frame = 0
                        self.frame_timer = 0
                        self.running_animation = False
            dt = self.clock.tick(60)
            self.screen.fill("black")
            self.screen.blit(self.title, self.title_pos)
            map_area = pygame.Rect((800 - 610) // 2, 50, 610, 610)
            pygame.draw.rect(self.screen, "gray", map_area)
            self.map_renderer.draw_connections()
            self.map_renderer.draw_zones()
            current_sprite = self.walk
            frame_area = pygame.Rect(
                0, self.current_frame * self.frame_height,
                current_sprite.get_width(), self.frame_height)
            self.screen.blit(current_sprite, (self.x, self.y), frame_area)
            if self.running_animation:
                self.frame_timer += dt
                if self.frame_timer > 100:
                    self.current_frame += self.frame_direction
                    if self.current_frame >= 14 or self.current_frame <= 0:
                        self.frame_direction *= -1
                    self.frame_timer = 0
                self.x += self.speed * dt
                if self.x > 95 + 610 - 110:
                    self.x = 95 + 610 - 110
                    self.running_animation = False
            pygame.display.flip()
        pygame.quit()
