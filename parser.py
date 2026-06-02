"""mambo jambo.
"""


from data import Zone, Connection, MapData


class ParserReturn:
    """jambo"""

    def __init__(self, filename: str) -> None:
        """mambo"""
        self.filename = filename

    def zone_parser(self, line: str, zone_type: str) -> Zone:
        """jambo"""
        zone_values = line.split(" ")
        color = "none"
        max_drones = 1
        if "[" in line:
            metadata = " ".join(zone_values[4:]).strip("[]")
            for item in metadata.split(" "):
                if "=" in item:
                    key, value = item.split("=")
                if key == "color":
                    color = value.strip()
                if key == "max_drones":
                    max_drones = int(value.strip())
                if key == "zone" and zone_type not in ("start", "end"):
                    zone_type = value.strip()
        return Zone(
            name=zone_values[1],
            x=int(zone_values[2]),
            y=int(zone_values[3]),
            zone_type=zone_type,
            color=color,
            max_drones=max_drones
        )

    def connection_parser(self, line: str) -> Connection:
        """jambo"""
        zone_a: str = ""
        zone_b: str = ""
        max_capacity: int = 0
        return Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_capacity=max_capacity
        )

    def parser(self) -> MapData:
        """jambo"""
        try:
            with open(self.filename, 'r') as configs:
                for line in configs:
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("nb_drones"):
                        key_value = line.split(":")
                        value: str = key_value[1].strip()
                        map_config.nb_drones = int(value)
                    if (line.startswith("start_hub")
                            or line.startswith("end_hub")
                            or line.startswith("hub")):
                        self.zone_parser(line)
        except Exception as error:
            print(error)
        return map_config
