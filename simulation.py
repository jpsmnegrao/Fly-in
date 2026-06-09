"""mambo jambo.
"""


from data import MapData, Drone, Zone
from pathfinder import NavGraph


class Simulation:
    """mambo"""

    def __init__(self, map_data: MapData, nav_graph: NavGraph) -> None:
        """jambo"""
        self.map_data = map_data
        self.nav_graph = nav_graph
        self.turn: int = 0
        self.paused: bool = False
        self.start_zone: Zone = next(
            zone for zone in map_data.zones if zone.hub_type == "start")
        self.end_zone: Zone = next(
            zone for zone in map_data.zones if zone.hub_type == "end")
        self.drone_count: int = map_data.nb_drones
        self.drones: list[Drone] = [
            Drone(
                id=f"D{i + 1}",
                current_zone=self.start_zone.name,
                finished=False,
                in_transit=False,
                destination_zone=None,
                remaining_turns=0
            )
            for i in range(self.drone_count)
        ]

    def step(self) -> None:
        """mambo"""
        self.turn += 1
        for drone in self.drones:
            if drone.finished:
                continue
            next_zone = self.nav_graph.next_move[drone.current_zone]
            zone = self.nav_graph.zones_by_names[next_zone]
            connection = next(
                c for c in self.nav_graph.adjacency[drone.current_zone]
                if c.zone_b == next_zone
            )
            if zone.zone_type == "blocked":
                continue
            elif zone.drone_count >= zone.max_drones:
                continue
            elif connection.drone_count >= connection.max_capacity:
                continue
            else:
                old_zone_name = drone.current_zone
                old_zone = self.nav_graph.zones_by_names[old_zone_name]
                new_zone = self.nav_graph.zones_by_names[next_zone]
                old_zone.drone_count -= 1
                new_zone.drone_count += 1
                drone.current_zone = next_zone
