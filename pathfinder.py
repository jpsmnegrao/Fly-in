"""mambo jambo"""


import heapq
from data import MapData, Zone, Connection


class NavGraph:
    """mambo"""

    def __init__(self, map_data: MapData) -> None:
        """jambo"""
        self.map_data = map_data
        self.zones_by_names: dict[str, Zone] = {}
        self.adjacency: dict[str, list[Connection]] = {}
        self.distances: dict[str, float] = {}
        self.next_move: dict[str, str] = {}

    def build_zone_lookup(self) -> None:
        """jambo"""
        self.zones_by_names = {zone.name: zone for zone in self.map_data.zones}

    def build_adjacency(self):
        """jambo"""
        for connection in self.map_data.connections:
            if connection.zone_b not in self.adjacency:
                self.adjacency[connection.zone_b] = []
            self.adjacency[connection.zone_b].append(connection)

    def reverse_dijkstra(self) -> None:
        """jambo"""
        for zone in self.map_data.zones:
            if zone.hub_type == "end":
                goal_name = zone.name
                self.distances[zone.name] = 0
            else:
                self.distances[zone.name] = float('inf')
        queue = []
        heapq.heappush(queue, (0, goal_name))
        visited = set()
        while queue:
            dist, zone = heapq.heappop(queue)
            if zone in visited:
                continue
            visited.add(zone)
            for connection in self.adjacency.get(zone, []):
                prev = connection.zone_a
                zone_type = self.zones_by_names[prev].zone_type
                if zone_type == "blocked":
                    continue
                elif zone_type == "priority" or zone_type == "normal":
                    new_dist = dist + 1
                elif zone_type == "restricted":
                    new_dist = dist + 2
                else:
                    new_dist = dist + 1
                if new_dist < self.distances[prev]:
                    self.distances[prev] = new_dist
                    self.next_move[prev] = zone
                    heapq.heappush(queue, (new_dist, prev))

    def get_path(self, start: str) -> list[str]:
        """jambo"""
        path = []
        current = start
        while current is not None:
            path.append(current)
            current = self.next_move.get(current)
        return path
