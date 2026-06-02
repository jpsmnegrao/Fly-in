"""mambo jambo.
"""


from dataclasses import dataclass


@dataclass
class Zone:
    """jambo"""
    name: str
    x: int
    y: int
    zone_type: str
    color: str
    max_drones: int


@dataclass
class Connection:
    """jambo"""
    zone_a: str
    zone_b: str
    max_capacity: int


@dataclass
class MapData:
    """jambo"""
    nb_drones: int
    zones: list[Zone]
    connections: list[Connection]
