"""Core simulation loop for moving drones from the start zone to the end zone,
turn by turn.

Note:
    TODO: this file currently duplicates movement/capacity logic that also
    exists (in a more complete form) in scheduler.py. step() here uses the
    shared next_move table directly rather than per-drone paths, has no
    vacate-frees-capacity-same-turn handling order guarantees beyond drone
    iteration order, and does not generalize zone capacity beyond the same
    max_drones check already covered in scheduler.py. Clarify whether
    Simulation or Scheduler is the intended source of truth for turn
    resolution going forward.
"""


from data import MapData, Drone, Zone
from pathfinder import NavGraph


class Simulation:
    """Owns simulation state (turn count, drones) and advances it by one turn
    at a time via step() and handle_transit().
    """

    def __init__(self, map_data: MapData, nav_graph: NavGraph) -> None:
        """Initialize simulation state and spawn all drones at the start zone.

        Args:
            map_data: Parsed map configuration (zones, connections, and drone
            count).
            nav_graph: Precomputed navigation graph providing next_move and
            adjacency lookups.
        """
        self.map_data = map_data
        self.nav_graph = nav_graph
        self.turn: int = 0
        self.paused: bool = False
        self.start_zone: Zone = next(
            zone for zone in map_data.zones if zone.hub_type == "start")
        self.end_zone: Zone = next(
            zone for zone in map_data.zones if zone.hub_type == "end")
        self.drone_count: int = map_data.nb_drones  # type: ignore[assignment]
        self.drones: list[Drone] = [
            Drone(
                id=f"D{i + 1}",
                current_zone=self.start_zone.name,
                finished=False,
                in_transit=False,
                destination_zone="",
                remaining_turns=0
            )
            for i in range(self.drone_count)
        ]

    def step(self) -> None:
        """Advance the simulation by one turn, moving each drone toward its
        next zone per the shared next_move table if capacity allows.

        Increments self.turn, then for each unfinished drone: looks up its
        next zone and the connection leading to it, skips the move if the
        destination is blocked, at zone capacity, or the connection is at link
        capacity, otherwise commits the move (decrementing the origin zone's
        drone_count, incrementing the destination's, and updating the drone's
        current_zone).

        Note:
            TODO: moves are committed immediately per drone in list order
            rather than planned and resolved together, so a drone may be
            blocked by another drone that was about to vacate the same zone
            later in this same turn (see prior discussion on plan/resolve/
            commit restructuring). Also: `connection.drone_count` is
            referenced for capacity but is never incremented or decremented
            anywhere in this method, so link capacity is not actually enforced
            in practice.
        """
        self.turn += 1
        for drone in self.drones:
            if drone.finished:
                continue
            next_zone: str = self.nav_graph.next_move[drone.current_zone]
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

    def handle_transit(self) -> None:
        """Advance drones currently in transit on a multi-turn (restricted)
        connection, and mark drones finished on arrival at the end zone.

        For each drone with in_transit set, decrements remaining_turns; once
        it reaches 0, moves the drone to its destination_zone, clears
        in_transit, and marks the drone finished if it arrived at the end zone.

        Note:
            TODO: nothing in this file or scheduler.py currently sets
            drone.in_transit to True or assigns drone.destination_zone, so
            this method's main branch is presently unreachable.
        """
        for drone in self.drones:
            if drone.in_transit:
                drone.remaining_turns -= 1
                if drone.remaining_turns > 0:
                    continue
                drone.in_transit = False
                drone.current_zone = drone.destination_zone
                if drone.destination_zone == self.end_zone.name:
                    drone.finished = True
