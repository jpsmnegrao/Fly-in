"""mambo jambo.
"""


import pygame
from data import MapData, Zone


class MapRenderer():
    """mambo"""

    def __init__(self, map_data: MapData, screen: pygame.Surface) -> None:
        """jambo"""
        self.map_data = map_data
        self.screen = screen
        self.map_x = self.map_data.map_x
        self.map_y = self.map_data.map_y
        self.map_width = self.map_data.map_width
        self.map_height = self.map_data.map_height
        self.min_x = 0
        self.min_y = 0
        self.scale_factor: float = 100.0
        self.zone_radius = max(5, int(self.scale_factor * 0.3))
        self.setup_map()
        self.coords_center_x = (self.min_x + self.max_x) / 2
        self.coords_center_y = (self.min_y + self.max_y) / 2

    def setup_map(self) -> None:
        """mambo"""
        self.max_x = max(zone.x for zone in self.map_data.zones)
        self.max_y = max(zone.y for zone in self.map_data.zones)
        self.min_x = min(zone.x for zone in self.map_data.zones)
        self.min_y = min(zone.y for zone in self.map_data.zones)
        self.zone_dict = {zone.name: zone for zone in self.map_data.zones}
        range_x = self.max_x - self.min_x
        range_y = self.max_y - self.min_y
        usable_x = self.map_width - 80
        usable_y = self.map_height - 80
        if range_x == 0 and range_y == 0:
            self.scale_factor = 100.0
        elif range_x == 0:
            self.scale_factor = float(min(usable_y // range_y, 150))
        elif range_y == 0:
            self.scale_factor = float(min(usable_x // range_x, 150))
        else:
            self.scale_factor = float(
                min(usable_x // range_x, usable_y // range_y, 150)
            )
        self.zone_radius = max(5, int(self.scale_factor * 0.3))

    def draw_zones(self) -> None:
        """jambo"""
        for zone in self.map_data.zones:
            position = self.zone_position(zone)
            x, y = position
            r = self.zone_radius
            if zone.zone_type == "normal":
                pygame.draw.circle(
                    self.screen, zone.color, position, self.zone_radius)
                pygame.draw.circle(
                    self.screen, "black", position, self.zone_radius, 3)
            if zone.zone_type == "blocked":
                pygame.draw.line(
                    self.screen, zone.color, (x-r, y-r), (x+r, y+r), 10)
                pygame.draw.line(
                    self.screen, zone.color, (x+r, y-r), (x-r, y+r), 10)
            if zone.zone_type == "restricted":
                pygame.draw.polygon(self.screen, zone.color, [
                    (x, y-r), (x+r, y), (x, y+r), (x-r, y)]
                )
                pygame.draw.polygon(self.screen, "black", [
                    (x, y-r), (x+r, y), (x, y+r), (x-r, y)], 3
                )
            if zone.zone_type == "priority":
                points = [
                    (x, y-r),
                    (x+r//4, y-r//4),
                    (x+r, y-r//4),
                    (x+r//2, y+r//4),
                    (x+3*r//4, y+r),
                    (x, y+r//2),
                    (x-3*r//4, y+r),
                    (x-r//2, y+r//4),
                    (x-r, y-r//4),
                    (x-r//4, y-r//4),
                ]
                pygame.draw.polygon(self.screen, zone.color, points)
            font_size = max(10, self.zone_radius)
            font = pygame.font.SysFont(None, font_size)
            text = str(zone.drone_count)
            main = font.render(text, True, "white")
            shadow = font.render(text, True, "black")
            text_rect = main.get_rect(center=(x, y))
            self.screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
            self.screen.blit(main, text_rect)

    def draw_connections(self) -> None:
        """mambo"""
        for connection in self.map_data.connections:
            start = self.zone_position(self.zone_dict[connection.zone_a])
            end = self.zone_position(self.zone_dict[connection.zone_b])
            pygame.draw.line(self.screen, "black", start, end, 3)
            rect = self.connection_mid_rect(start, end)
            pygame.draw.rect(self.screen, "white", rect)
            pygame.draw.rect(self.screen, "black", rect, 2)
            font_size = max(10, self.zone_radius // 2)
            font = pygame.font.SysFont(None, font_size)
            text = str(connection.drone_count)
            main = font.render(text, True, "white")
            shadow = font.render(text, True, "black")
            text_rect = main.get_rect(center=rect.center)
            self.screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
            self.screen.blit(main, text_rect)

    def connection_mid_rect(
            self, start: tuple[int, int], end: tuple[int, int]) -> pygame.Rect:
        """jambo"""
        rect = pygame.Rect(
            0, 0, max(1, self.zone_radius), max(1, self.zone_radius // 2)
        )
        rect.center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        return rect

    def zone_position(self, zone: Zone) -> tuple[int, int]:
        """jambo"""
        screen_center_x = self.map_x + self.map_width / 2
        screen_center_y = self.map_y + self.map_height / 2
        screen_x = (
            screen_center_x + (zone.x - self.coords_center_x) *
            self.scale_factor)
        screen_y = (
            screen_center_y + (zone.y - self.coords_center_y) *
            self.scale_factor)
        return (int(screen_x), int(screen_y))
