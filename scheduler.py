"""Computes per-turn drone movement proposals and resolves conflicts against
zone capacity.
"""


from data import MapData, Zone, Drone, Move
from pathfinder import NavGraph


class Scheduler:
    """Computes per-turn drone movement proposals and resolves conflicts.

    Given the current state of all drones and the map's navigation graph, the
    Scheduler determines each drone's next move, filters out moves that would
    violate zone capacity, and commits the approved moves by updating drone
    and zone state.
    """

    def __init__(
        self, map_data: MapData, nav_graph: NavGraph, drones: list[Drone]
    ) -> None:
        """Initialize the scheduler with map state and drone references.

        Args:
            map_data: Parsed map configuration (zones and connections).
            nav_graph: Navigation graph used to compute paths between zones.
            drones: List of drones being managed by this scheduler.
        """
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
        """Compute and cache a path for each drone that hasn't finished.

        Populates self.paths with a mapping of drone id to the list of zone
        names from the drone's current zone to the end zone, as returned by
        the navigation graph. Finished drones are skipped.
        """
        for drone in self.drones:
            if drone.finished:
                continue
            start = drone.current_zone
            path = self.nav_graph.get_path(start)
            self.paths[drone.id] = path

    def run_turn(self) -> list[Move]:
        """Propose, filter, and commit one turn of drone movement."""
        self.get_paths()
        moves: list[Move] = self.propose_moves()
        valid: list[Move] = self.filter_valid_moves(moves)
        self.commit_moves(valid)
        return valid

    def propose_moves(self) -> list[Move]:
        """Propose the next move for all unfinished drones."""
        proposed_moves: list[Move] = []
        for drone in self.drones:
            if drone.finished:
                continue
            if drone.in_transit:
                proposed_moves.append(Move(
                    drone_id=drone.id,
                    target=drone.destination_zone,
                    target_zone=drone.destination_zone,
                    target_connection=None,
                    in_transit=True
                ))
            else:
                path = self.paths.get(drone.id, [])
                if len(path) >= 2:
                    proposed_moves.append(Move(
                        drone_id=drone.id,
                        target=path[1],
                        target_zone=path[1],
                        target_connection=None,
                        in_transit=False
                    ))
        return proposed_moves

    def filter_valid_moves(self, proposed_moves: list[Move]) -> list[Move]:
        """Filter proposed moves against zone capacity."""
        valid: list[Move] = []
        approved_count: dict[str, int] = {}
        for move in proposed_moves:
            zone: Zone = self.zones_by_name[move.target]
            if (
                    zone.drone_count + approved_count.get(move.target, 0)
                    < zone.max_drones):
                approved_count[move.target] = approved_count.get(
                    move.target, 0) + 1
                valid.append(move)
        return valid

    def commit_moves(self, moves: list[Move]) -> None:
        """Updates drone and zone state based on approved moves."""
        for move in moves:
            drone = self.drones_by_id[move.drone_id]
            origin = self.zones_by_name[drone.current_zone]
            destination = self.zones_by_name[move.target]
            if not move.in_transit:
                if destination.zone_type == "restricted":
                    drone.in_transit = True
                    drone.destination_zone = move.target
                    drone.remaining_turns = 1
                    origin.drone_count -= 1
                else:
                    drone.current_zone = move.target
                    origin.drone_count -= 1
                    destination.drone_count += 1
                    if drone.current_zone == self.end_zone:
                        drone.finished = True
