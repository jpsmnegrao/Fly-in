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

    def step(self) -> list[Move]:
        """Propose, resolve, and commit one turn of drone movement.

        For each unfinished drone with a remaining path, builds a proposed
        Move toward its next zone. Proposed moves are then filtered against
        zone capacity (max_drones), approving moves only while the zone has
        remaining room this turn. Approved moves are committed: the drone's
        current_zone is updated, the origin zone's drone_count is decremented,
        and the destination zone's drone_count is incremented.

        Note:
            The in_transit / restricted-zone branch below builds a Move with
            in_transit=True, but nothing yet commits that back onto
            drone.in_transit or drone.destination_zone, so a drone never
            actually enters the transit state via this method. TODO: wire this
            up on commit.

        Returns:
            The list of Move objects that were approved and committed
            this turn.
        """
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
        approved_count: dict[str, int] = {}
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
