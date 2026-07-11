"""Core simulation loop for moving drones from the start zone to the end zone,
turn by turn.
"""


from data import MapData, Drone, Zone
from pathfinder import NavGraph
from scheduler import Scheduler


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
        self.scheduler = Scheduler(map_data, nav_graph, self.drones)

    def step(self) -> list[Drone]:
        """Advance the simulation by one turn.

        Increments self.turn, advances any drones currently in transit,
        then delegates move proposal/resolution/commit to the scheduler.
        """
        self.turn += 1
        if self.turn == 1:
            for drone_id, path in self.scheduler.paths.items():
                print(f"DEBUG - Path {drone_id}: {path}")
        completed_transit = self.handle_transit()
        unfinished_drones: list[Drone] = [d for d in self.drones if not
                                          d.finished]
        if not unfinished_drones:
            return []
        self.scheduler.run_turn()
        return completed_transit

    def handle_transit(self) -> list[Drone]:
        """Advance drones currently in transit on a multi-turn (restricted)
        connection, and mark drones finished on arrival at the end zone.

        Decrements remaining_turns for each in-transit drone; once it hits 0,
        moves the drone to its destination_zone, clears in_transit, and marks
        the drone finished if it arrived at the end zone.
        """
        completed: list[Drone] = []
        for drone in self.drones:
            if drone.in_transit:
                drone.remaining_turns -= 1
                if drone.remaining_turns > 0:
                    continue
                origin = self.nav_graph.zones_by_names[drone.current_zone]
                destination = (
                    self.nav_graph.zones_by_names[drone.destination_zone])
                origin.drone_count -= 1
                destination.drone_count += 1
                drone.current_zone = drone.destination_zone
                drone.destination_zone = ""
                drone.in_transit = False
                if drone.current_zone == self.end_zone.name:
                    drone.finished = True
                completed.append(drone)
        return completed
