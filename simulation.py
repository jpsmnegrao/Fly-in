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
        self.scheduler = Scheduler(map_data, nav_graph, self.drones)

    def step(self) -> None:
        """Advance the simulation by one turn.

        Increments self.turn, advances any drones currently in transit,
        then delegates move proposal/resolution/commit to the scheduler.
        """
        self.turn += 1
        self.handle_transit()
        active_drones: list[Drone] = [
            d for d in self.drones if not d.finished and not d.in_transit]
        if active_drones:
            self.scheduler.run_turn()

    def handle_transit(self) -> None:
        """Advance drones currently in transit and process arrivals.

        For each drone currently in transit, this method decrements its
        remaining_turns. Once a drone reaches 0 turns, it is moved to its
        destination zone, the transit state is cleared, and the zone's drone
        count is updated. If the destination is the end zone, the drone is
        marked as finished.
        """
        for drone in self.drones:
            if drone.in_transit:
                drone.remaining_turns -= 1
                if drone.remaining_turns > 0:
                    continue
                drone.in_transit = False
                drone.current_zone = drone.destination_zone
                target_zone: Zone = next(
                    z for z in self.map_data.zones if z.name ==
                    drone.current_zone)
                target_zone.drone_count += 1
                if drone.destination_zone == self.end_zone.name:
                    drone.finished = True
