"""Shared data structures used throughout the Fly-In simulation.

Defines the dataclasses representing maps, zones, connections, drones and
movement proposals.
"""


from dataclasses import dataclass, field


@dataclass
class Zone:
    """A single zone (room/hub) in the map graph.

    Attributes:
        hub_type: Role of the zone in the map - 'start', 'end', or 'hub'.
        name: Unique identifier for the zone.
        x: X coordinate, used for rendering.
        y: Y coordinate, used for rendering.
        zone_type: Movement category determining how the zone is traversed:
            'normal' costs 1 turn to enter;
            'priority' costs 1 turn and is preferred when multiple shortest
                paths exist;
            'restricted' costs 2 turns to enter;
            'blocked' cannot be entered.
        color: Display color, used for rendering.
        max_drones: Maximum number of drones allowed in this zone at once.
        drone_count: Current number of drones occupying this zone.
    """
    hub_type: str
    name: str
    x: int
    y: int
    zone_type: str
    color: str
    max_drones: int
    drone_count: int


@dataclass
class Connection:
    """A connection between two zones in the map graph.

    Attributes:
        zone_a: Name of the origin zone.
        zone_b: Name of the destination zone.
        max_capacity: Maximum number of drones allowed to traverse this
            connection simultaneously.
        drone_count: Current number of drones traversing this connection.
        name: Display identifier for the connection, formatted as
            '<zone_a>-<zone_b>'.
    """
    zone_a: str
    zone_b: str
    max_capacity: int
    drone_count: int
    name: str


@dataclass
class MapData:
    """Parsed contents of a map configuration file.

    Attributes:
        map_name: Name of the map.
        nb_drones: Total number of drones to simulate.
        zones: All zones defined in the map.
        connections: All connections defined in the map.
        start_zone: Reference to the map's start zone.
        end_zone: Reference to the map's end zone.
        map_x: X offset for rendering the map. (inferred, not subject-sourced)
        map_y: Y offset for rendering the map. (inferred, not subject-sourced)
        map_width: Width of the rendered map area. (inferred, not
            subject-sourced)
        map_height: Height of the rendered map area. (inferred, not
            subject-sourced)
    """
    map_name: str = ""
    nb_drones: int | None = None
    zones: list[Zone] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    start_zone: Zone | None = None
    end_zone: Zone | None = None
    map_x: int = 95
    map_y: int = 60
    map_width: int = 1400
    map_height: int = 610


@dataclass
class Drone:
    """A single drone moving through the map from start to end zone.

    Attributes:
        id: Unique identifier for the drone (e.g. 'D1').
        current_zone: Name of the zone currently occupied by the drone.
        current_connection: Name of the restricted connection currently being
            traversed, or an empty string if the drone is not in transit.
        finished: Whether the drone has reached the end zone.
        in_transit: Whether the drone is traversing a restricted connection.
        arriving: Whether the drone has reached the destination restricted zone
            but has not yet completed the transit.
        destination_zone: Name of the restricted zone the drone is travelling
            toward while in transit.
        remaining_turns: Number of turns remaining before the restricted
            traversal is complete.
    """
    id: str
    current_zone: str = ""
    current_connection: str = ""
    finished: bool = False
    in_transit: bool = False
    arriving: bool = False
    destination_zone: str = ""
    remaining_turns: int = 0


@dataclass
class Move:
    """A proposed movement for a single drone during one simulation turn.

    Attributes:
        drone_id: Identifier of the drone making the move.
        target: Name of the destination zone proposed for this turn.
    """
    drone_id: str
    target: str
