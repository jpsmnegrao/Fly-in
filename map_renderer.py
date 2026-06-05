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
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0
        self.scale_factor: float = 80.0
        self.zone_radius = max(5, int(self.scale_factor * 0.3))
        # map area and dimension offsets
        self.map_x = 95
        self.map_y = 60
        self.map_size = 610
        self.setup_map()

    def setup_map(self) -> None:
        """mambo"""
        self.max_x = max(zone.x for zone in self.map_data.zones)
        self.max_y = max(zone.y for zone in self.map_data.zones)
        self.min_x = min(zone.x for zone in self.map_data.zones)
        self.min_y = min(zone.y for zone in self.map_data.zones)
        self.zone_dict = {zone.name: zone for zone in self.map_data.zones}

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

    def draw_connections(self) -> None:
        """mambo"""
        for connection in self.map_data.connections:
            start = self.zone_position(self.zone_dict[connection.zone_a])
            end = self.zone_position(self.zone_dict[connection.zone_b])
            pygame.draw.line(self.screen, "black", start, end, 3)

    def zone_position(self, zone: Zone) -> tuple[int, int]:
        """jambo"""
        coords_center_x = (self.min_x + self.max_x) / 2
        coords_center_y = (self.min_y + self.max_y) / 2
        screen_center_x = self.map_x + self.map_size / 2
        screen_center_y = self.map_y + self.map_size / 2
        screen_x = (
            screen_center_x + (zone.x - coords_center_x) *
            self.scale_factor)
        screen_y = (
            screen_center_y + (zone.y - coords_center_y) *
            self.scale_factor)
        return (int(screen_x), int(screen_y))
