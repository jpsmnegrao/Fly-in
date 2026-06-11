"""mambo jambo.
"""


from dataclasses import dataclass, field


@dataclass
class Zone:
    """jambo"""
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
    """jambo"""
    zone_a: str
    zone_b: str
    max_capacity: int
    drone_count: int
    name: str


@dataclass
class MapData:
    """jambo"""
    nb_drones: int | None = None
    zones: list[Zone] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    map_x: int = 95
    map_y: int = 60
    map_width: int = 1400
    map_height: int = 610


@dataclass
class Drone:
    """jambo"""
    id: str
    current_zone: str = ""
    finished: bool = False
    in_transit: bool = False
    destination_zone: str = ""
    remaining_turns: int = 0


@dataclass
class Move:
    """mambo"""
    drone_id: str
    target: str
    target_zone: str | None
    target_connection: str | None
    in_transit: bool
