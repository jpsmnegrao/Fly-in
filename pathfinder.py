"""Builds a navigation graph from map data and computes shortest paths to the
end zone using a reverse Dijkstra search.

The graph is treated as bidirectional, with distances and next-hop moves
computed once from every zone toward the end zone. Movement costs are
determined by the zone_type (normal/priority=1, restricted=2,
blocked=inaccessible). Paths for individual drones are derived from this
shared table.
"""


import heapq
from data import MapData, Zone, Connection


class NavGraph:
    """Precomputes shortest paths from every zone to the end zone.

    Builds an adjacency structure from the map's connections, then runs a
    reverse Dijkstra search rooted at the end zone to compute, for every zone,
    its distance to the end and which neighboring zone to move to next
    (next_move). Individual drone paths are derived from this shared table
    rather than computed per-drone.
    """

    def __init__(self, map_data: MapData) -> None:
        """Initialize empty lookup/adjacency/distance structures.

        Args:
            map_data: Parsed map configuration (zones and connections) to
            build the navigation graph from.
        """
        self.map_data = map_data
        self.zones_by_names: dict[str, Zone] = {}
        self.adjacency: dict[str, list[Connection]] = {}
        self.distances: dict[str, float] = {}
        self.next_move: dict[str, str] = {}

    def build_zone_lookup(self) -> None:
        """Build a name-to-Zone lookup dict from map_data.zones."""
        self.zones_by_names = {zone.name: zone for zone in self.map_data.zones}

    def build_adjacency(self) -> None:
        """Build an adjacency dict registering each connection in both
        directions.

        For each connection, registers it under both zone_a and zone_b,
        ensuring that the graph can be traversed bidirectionally during
        pathfinding.
        """
        for connection in self.map_data.connections:
            if connection.zone_a not in self.adjacency:
                self.adjacency[connection.zone_a] = []
            self.adjacency[connection.zone_a].append(connection)
            if connection.zone_b not in self.adjacency:
                self.adjacency[connection.zone_b] = []
            self.adjacency[connection.zone_b].append(connection)

    def reverse_dijkstra(self) -> None:
        """Compute shortest distance and next-hop move from every zone to the
        end zone, using a reverse Dijkstra search.

        Starts from the zone with hub_type 'end' at distance 0, then explores
        outward via self.adjacency, accumulating movement cost based on the
        zone_type of the zone being entered (normal/priority=1, restricted=2,
        blocked=skipped entirely). Populates self.distances and self.next_move
        for every reachable zone.
        """
        for zone in self.map_data.zones:
            if zone.hub_type == "end":
                goal_name = zone.name
                self.distances[zone.name] = 0
            else:
                self.distances[zone.name] = float('inf')
        queue: list[tuple[float, str]] = []
        heapq.heappush(queue, (0, goal_name))
        visited = set()
        while queue:
            dist, current = heapq.heappop(queue)
            if current in visited:
                continue
            visited.add(current)
            for connection in self.adjacency.get(current, []):
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
                    self.next_move[prev] = current
                    heapq.heappush(queue, (new_dist, prev))

    def get_path(self, start: str) -> list[str]:
        """Build the full path from a starting zone to the end zone.

        Walks self.next_move starting at `start` until a zone with no recorded
        next move is reached (typically the end zone, or a zone unreachable
        from the end).

        Args:
            start: Name of the zone to start the path from.

        Returns:
            The ordered list of zone names from start to the end zone
            (inclusive), or a partial/single-zone list if start cannot reach
            the end zone.
        """
        path = []
        current: str | None = start
        while current is not None:
            path.append(current)
            current = self.next_move.get(current)
        return path

    def get_possible_next_moves(self, zone_name: str) -> list[str]:
        """mambo jambo"""
        possible_moves: list[str] = []
        current_distance = self.distances[zone_name]
        for connection in self.adjacency.get(zone_name, []):
            if connection.zone_a == zone_name:
                neighbour = connection.zone_b
            else:
                neighbour = connection.zone_a
            if neighbour not in self.distances:
                continue
            zone = self.zones_by_names[zone_name]
            if zone.zone_type == "restricted":
                cost = 2
            else:
                cost = 1
            if self.distances[neighbour] + cost == current_distance:
                possible_moves.append(neighbour)
        return possible_moves
