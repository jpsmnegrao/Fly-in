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
            options = self.nav_graph.get_possible_next_moves(start)
            if not options:
                self.paths[drone.id] = [start]
                continue
            choice = options[0]
            if len(options) > 1:
                index = (int(drone.id[1:]) - 1) % len(options)
                choice = options[index]
            path = [start, choice]
            remaining = self.nav_graph.get_path(choice)
            path.extend(remaining[1:])
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
            if drone.finished or drone.in_transit or drone.arriving:
                continue
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
        """Filter proposed moves against zone capacity.

        Important:
        A zone becomes available when a drone leaves it in the same turn.
        Therefore, we first calculate departures, then validate arrivals.
        """
        occupancy: dict[str, int] = {
            zone.name: zone.drone_count for zone in
            self.zones_by_name.values()}
        connection_usage: dict[str, int] = {
            connection.name: connection.drone_count
            for connection in self.map_data.connections
        }
        valid: list[Move] = []
        for move in proposed_moves:
            drone = self.drones_by_id[move.drone_id]
            origin = drone.current_zone
            destination = self.zones_by_name[move.target]
            connection = next(
                (
                    c for c in self.map_data.connections
                    if c.zone_a == origin and c.zone_b == destination.name
                ), None)
            if connection and destination.zone_type == "restricted":
                if (connection_usage[connection.name] >=
                        connection.max_capacity):
                    continue
                valid.append(move)
                occupancy[origin] -= 1
                connection_usage[connection.name] += 1
                continue
            if occupancy[move.target] < destination.max_drones:
                valid.append(move)
                occupancy[origin] -= 1
                occupancy[move.target] += 1
        return valid

    def commit_moves(self, moves: list[Move]) -> None:
        """Updates drone and zone state based on approved moves."""
        for move in moves:
            drone = self.drones_by_id[move.drone_id]
            origin = self.zones_by_name[drone.current_zone]
            dest = self.zones_by_name[move.target]
            if not move.in_transit:
                if dest.zone_type == "restricted":
                    drone.in_connection = True
                    drone.in_transit = True
                    drone.destination_zone = move.target
                    drone.current_connection = f"{origin.name}-{dest.name}"
                    drone.remaining_turns = 2
                    origin.drone_count -= 1
                    connection = next(
                        c for c in self.map_data.connections
                        if c.zone_a == origin.name and c.zone_b == dest.name)
                    connection.drone_count += 1
                else:
                    drone.current_zone = move.target
                    origin.drone_count -= 1
                    dest.drone_count += 1
                    if drone.current_zone == self.end_zone:
                        drone.finished = True
