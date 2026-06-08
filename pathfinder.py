"""mambo jambo"""


from data import MapData, Zone, Connection


def build_zone_lookup(map_data: MapData) -> dict[str, Zone]:
    """jambo"""
    return {zone.name: zone for zone in map_data.zones}


def build_adjacency(map_data) -> dict[str, list[Connection]]:
    """jambo"""
    adjacency: dict[str, list[Connection]] = {}
    for connection in map_data.connections:
        if connection.zone_a not in adjacency:
            adjacency[connection.zone_a] = []
        adjacency[connection.zone_a].append(connection)
    return adjacency


def reverse_dijkstra(map_data):
    """jambo"""
