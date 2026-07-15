"""Builds a navigation graph from map data and precomputes shortest paths.

An adjacency structure is created from the map connections, then a reverse
Dijkstra search computes the minimum distance and next move from every
reachable zone to the end zone.
"""


import heapq
from data import MapData, Zone, Connection


class NavGraph:
    """Precompute shortest paths from every zone to the end zone.

    Builds an adjacency structure from the map's connections, then runs a
    reverse Dijkstra search rooted at the end zone to compute, for every zone,
    its distance to the end zone and the next zone along the selected shortest
    path. Individual drone paths are derived from this shared table rather than
    computed per-drone.
    """

    def __init__(self, map_data: MapData) -> None:
        """Initialize the navigation graph.

        Args:
            map_data: Parsed map data used to build the navigation graph.
        """
        self.map_data = map_data
        self.zones_by_names: dict[str, Zone] = {}
        self.adjacency: dict[str, list[Connection]] = {}
        self.distances: dict[str, float] = {}
        self.next_move: dict[str, str] = {}

    def build_zone_lookup(self) -> None:
        """Build a lookup table from zone names to Zone objects."""
        self.zones_by_names = {zone.name: zone for zone in self.map_data.zones}

    def build_adjacency(self) -> None:
        """Build an adjacency list for the navigation graph.

        Registers every connection under both connected zones so the graph can
        be traversed in either direction.
        """
        for connection in self.map_data.connections:
            if connection.zone_a not in self.adjacency:
                self.adjacency[connection.zone_a] = []
            self.adjacency[connection.zone_a].append(connection)
            if connection.zone_b not in self.adjacency:
                self.adjacency[connection.zone_b] = []
            self.adjacency[connection.zone_b].append(connection)

    def reverse_dijkstra(self) -> None:
        """Compute the shortest path from every reachable zone to the end zone.

        Runs a reverse Dijkstra search starting from the end zone. The cost of
        entering a normal or priority zone is 1 turn, entering a restricted
        zone costs 2 turns, and blocked zones are ignored. When multiple
        shortest paths have the same total cost, paths through priority zones
        are preferred.

        Populates self.distances with the minimum cost from each zone to the
        end zone and self.next_move with the next zone along the selected
        shortest path.
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
                if connection.zone_a == current:
                    prev = connection.zone_b
                else:
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
                elif new_dist == self.distances[prev]:
                    current_next = self.next_move.get(prev)
                    if (current_next is not None and
                            self.zones_by_names[current].zone_type ==
                            "priority" and
                            self.zones_by_names[current_next].zone_type ==
                            "priority"):
                        self.next_move[prev] = current

    def get_path(self, start: str) -> list[str]:
        """Build the full path from a starting zone to the end zone.

        Walks self.next_move starting at start until a zone with no recorded
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
        """Return neighbouring zones that belong to a shortest path.

        Args:
            zone_name: Name of the current zone.

        Returns:
            A list of neighbouring zones that belong to a shortest path to the
            end zone.
        """
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
