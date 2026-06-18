"""mambo jambo.
"""


from data import MapData, Zone, Drone, Move
from pathfinder import NavGraph


class Scheduler:
    """mambo"""

    def __init__(
        self, map_data: MapData, nav_graph: NavGraph, drones: list[Drone]
    ) -> None:
        """mambo"""
        self.map_data = map_data
        self.nav_graph = nav_graph
        self.drones = drones
        self.paths: dict[str, list[str]] = {}
        self.zones_by_name: dict[str, Zone] = (
            {zone.name: zone for zone in map_data.zones})
        self.end_zone = next(
            zone.name for zone in map_data.zones if zone.hub_type == "end"
        )
        self.drones_by_id: dict[str, Drone] = (
            {drone.id: drone for drone in drones})

    def get_paths(self) -> None:
        """jambo"""
        for drone in self.drones:
            if drone.finished:
                continue
            start = drone.current_zone
            path = self.nav_graph.get_path(start)
            self.paths[drone.id] = path

    def step(
        self, map_data: MapData, nav_graph: NavGraph, drones: list[Drone]
    ) -> list[Move]:
        """jambo"""
        self.get_paths()
        proposed_moves: list[Move] = []
        valid_moves: list[Move] = []
        for drone in self.drones:
            if not drone.finished:
                path = self.paths[drone.id]
                if len(path) >= 2:
                    if drone.in_transit:
                        drone.remaining_turns -= 1
                        if drone.remaining_turns > 0:
                            next_zone = drone.destination_zone
                            move = Move(
                                drone_id=drone.id,
                                target=next_zone,
                                target_zone=next_zone,
                                target_connection=f"{drone.current_zone}-"
                                                  f"{next_zone}",
                                in_transit=True
                            )
                        else:
                            next_zone = path[1]
                            move = Move(
                                 drone_id=drone.id,
                                 target=next_zone,
                                 target_zone=next_zone,
                                 target_connection=None,
                                 in_transit=False
                             )
                    else:
                        next_zone = path[1]
                        move = Move(
                            drone_id=drone.id,
                            target=next_zone,
                            target_zone=next_zone,
                            target_connection=None,
                            in_transit=False
                        )
                    proposed_moves.append(move)
        target_count: dict[str, int] = {}
        approved_count: dict[str, int] = {}
        for move in proposed_moves:
            target_count[move.target] = target_count.get(move.target, 0) + 1
        for move in proposed_moves:
            zone = self.zones_by_name[move.target]
            if zone.drone_count + approved_count.get(move.target, 0) \
                    < zone.max_drones:
                approved_count[move.target] = (
                    approved_count.get(move.target, 0) + 1)
                valid_moves.append(move)
        for move in valid_moves:
            drone = self.drones_by_id[move.drone_id]
            zone = self.zones_by_name[move.target]
            self.zones_by_name[drone.current_zone].drone_count -= 1
            drone.current_zone = move.target
            zone.drone_count += 1
        return valid_moves
