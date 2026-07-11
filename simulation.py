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

    def step(self) -> tuple[list[Drone], list[Drone]]:
        """Advance the simulation by one turn.

        Increments self.turn, advances any drones currently in transit,
        then delegates move proposal/resolution/commit to the scheduler.
        """
        self.turn += 1
        if self.turn == 1:
            for drone_id, path in self.scheduler.paths.items():
                print(f"DEBUG - Path {drone_id}: {path}")
        completed_transit, arriving = self.handle_transit()
        unfinished_drones: list[Drone] = [d for d in self.drones if not
                                          d.finished]
        if not unfinished_drones:
            return [], []
        valid_moves = self.scheduler.run_turn()
        output: list[str] = []
        for drone in completed_transit:
            output.append(f"{drone.id}-{drone.current_zone}")
        for move in valid_moves:
            drone = self.scheduler.drones_by_id[move.drone_id]
            if drone.in_transit:
                output.append(f"{drone.id}-{drone.current_connection}")
            else:
                output.append(f"{drone.id}-{move.target}")
        if output:
            print(" ".join(output))
        return completed_transit, arriving

    def handle_transit(self) -> tuple[list[Drone], list[Drone]]:
        """Advance drones currently in transit on a multi-turn (restricted)
        connection, and mark drones finished on arrival at the end zone.

        Decrements remaining_turns for each in-transit drone. At
        remaining_turns == 1 (phase 2): drone arrives at restricted zone,
        updates position and counts, sets arriving=True but stays in_transit.
        At remaining_turns == 0 (phase 3): clears all transit state and marks
        drone as completeed.
        """
        completed: list[Drone] = []
        arriving: list[Drone] = []
        for drone in self.drones:
            if drone.in_transit:
                drone.remaining_turns -= 1
                if drone.remaining_turns == 1:
                    origin = self.nav_graph.zones_by_names[drone.current_zone]
                    destination = (
                        self.nav_graph.zones_by_names[drone.destination_zone])
                    connection = next(
                        c for c in self.nav_graph.map_data.connections
                        if c.zone_a == origin.name and
                        c.zone_b == destination.name)
                    connection.drone_count -= 1
                    origin.drone_count -= 1
                    destination.drone_count += 1
                    drone.current_zone = drone.destination_zone
                    drone.destination_zone = ""
                    drone.arriving = True
                    arriving.append(drone)
                elif drone.remaining_turns == 0:
                    drone.in_transit = False
                    drone.arriving = False
                    drone.current_connection = ""
                    if drone.current_zone == self.end_zone.name:
                        drone.finished = True
                    completed.append(drone)
        return completed, arriving
