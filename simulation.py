"""Core simulation loop for advancing the drone simulation turn by turn."""


from data import MapData, Drone, Zone
from pathfinder import NavGraph
from scheduler import Scheduler


class Simulation:
    """Manage the simulation state and advance it one turn at a time."""

    def __init__(self, map_data: MapData, nav_graph: NavGraph) -> None:
        """Initialize the simulation and create all drones.

        Args:
            map_data: Parsed map data.
            nav_graph: Precomputed navigation graph.
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

        Increments the turn counter, updates drones traversing restricted
        connections, delegates movement scheduling, prints the resulting moves,
        and returns the drones that arrived at or completed restricted transit.
        """
        self.turn += 1
        completed_transit, arriving = self.handle_transit()
        unfinished_drones: list[Drone] = [d for d in self.drones if not
                                          d.finished]
        if not unfinished_drones:
            return [], []
        valid_moves = self.scheduler.run_turn()
        output: list[str] = []
        printed: set[str] = set()
        for drone in completed_transit:
            output.append(f"{drone.id}-{drone.current_zone}")
            printed.add(drone.id)
        for move in valid_moves:
            drone = self.scheduler.drones_by_id[move.drone_id]
            if drone.id in printed:
                continue
            if drone.in_transit and not drone.arriving:
                output.append(f"{drone.id}-{drone.current_connection}")
            else:
                output.append(f"{drone.id}-{drone.current_zone}")
            printed.add(drone.id)
        for drone in self.drones:
            if drone.id in printed:
                continue
            if drone.finished:
                continue
            if drone.current_zone == self.start_zone.name:
                continue
            if drone.in_transit and not drone.arriving:
                output.append(f"{drone.id}-{drone.current_connection}")
            else:
                output.append(f"{drone.id}-{drone.current_zone}")
            printed.add(drone.id)
        if output:
            print(" ".join(sorted(output, key=lambda s:
                  int(s.split("-")[0][1:]))))
        return completed_transit, arriving

    def handle_transit(self) -> tuple[list[Drone], list[Drone]]:
        """Advance drones traversing restricted connections.

        Decrements the remaining travel time for every drone in transit. When a
        drone reaches the restricted destination zone, its position and
        occupancy counts are updated and it is marked as arriving. On the
        following turn, the transit state is cleared and the drone is marked as
        finished if it has reached the end zone.

        Returns:
            A tuple containing:
                - completed: Drones whose restricted traversal finished this
                turn.
                - arriving: Drones that reached the destination restricted zone
                this turn but have not yet completed the traversal.
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
