"""mambo jambo.
"""


from data import Zone, Connection, MapData


class ParserReturn:
    """jambo"""

    def __init__(self, filename: str) -> None:
        """mambo"""
        self.filename = filename

    def zone_parser(self, line: str, hub_type: str) -> Zone:
        """jambo"""
        zone_values = line.split(" ")
        color = "none"
        max_drones = 1
        zone_type = "normal"
        if "[" in line:
            metadata = " ".join(zone_values[4:]).strip("[]")
            for item in metadata.split(" "):
                if "=" in item:
                    key, value = item.split("=")
                    if key == "color":
                        color = value.strip().strip("[]")
                    elif key == "max_drones":
                        max_drones = int(value.strip().strip("[]"))
                    elif key == "zone" and hub_type not in ("start", "end"):
                        zone_type = value.strip()
        return Zone(
            hub_type=hub_type,
            name=zone_values[1],
            x=int(zone_values[2]),
            y=int(zone_values[3]),
            zone_type=zone_type,
            color=color,
            max_drones=max_drones
        )

    def connection_parser(self, line: str) -> Connection:
        """jambo"""
        connection_values = line.split(" ")
        zone_a: str = connection_values[1].split("-")[0]
        zone_b: str = connection_values[1].split("-")[1].strip()
        max_capacity: int = 1
        if "[" in line:
            metadata = " ".join(connection_values[2:]).strip("[]")
            for item in metadata.split(" "):
                if "=" in item:
                    key, value = item.split("=")
                    if key == "max_link_capacity":
                        max_capacity = int(value.strip().strip("[]"))
        return Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_capacity=max_capacity
        )

    def parser(self) -> MapData:
        """jambo"""
        map_config = MapData()
        try:
            with open(self.filename, 'r') as configs:
                for line in configs:
                    if not line.strip() or line.startswith("#"):
                        continue
                    if line.startswith("nb_drones"):
                        key_value = line.split(":")
                        value: str = key_value[1].strip()
                        map_config.nb_drones = int(value)
                    elif line.startswith("start_hub"):
                        map_config.zones.append(self.zone_parser(line,
                                                "start"))
                    elif line.startswith("end_hub"):
                        map_config.zones.append(self.zone_parser(line, "end"))
                    elif line.startswith("hub"):
                        map_config.zones.append(self.zone_parser(line, "hub"))
                    elif line.startswith("connection"):
                        map_config.connections.append(
                            self.connection_parser(line))
        except Exception as error:
            print(error)
        return map_config


if __name__ == "__main__":
    p = ParserReturn("maps/hard/01_maze_nightmare.txt")
    result = p.parser()
    from pprint import pprint
    pprint(result)
