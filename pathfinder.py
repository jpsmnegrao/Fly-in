"""mambo jambo"""


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
            if connection.zone_a not in self.adjacency:
                self.adjacency[connection.zone_a] = []
            self.adjacency[connection.zone_a].append(connection)

    def reverse_dijkstra(self) -> None:
        """jambo"""
        for zone in self.map_data.zones:
            if zone.hub_type == "end":
                self.distances[zone.name] = 0
            self.distances[zone.name] = float('inf')
