"""Map file parser for the Fly-In drone routing simulation.

Parses map configuration files into structured data objects for use by the
renderer and pathfinding logic.
"""


from data import Zone, Connection, MapData


class ParserReturn:
    """Parses a map configuration file into a MapData object.

    Reads zone and connection definitions from a structured text file and
    returns validated MapData containing zones and connections.

    Attributes:
        filename: Path to the map configuration file.
    """

    def __init__(self, filename: str) -> None:
        """Initialize the parser with a map file path.

        Args:
            filename: Path to the map configuration file to parse.
        """
        self.filename = filename

    def zone_parser(self, line: str, hub_type: str, line_num: int) -> Zone:
        """Parse a single zone line into a Zone object.

        Args:
            line: A raw line from the map file starting with hub:, start_hub:,
                or end_hub:.
            hub_type: The role of the zone: 'start', 'end', or 'hub'.

        Returns:
            A Zone object populated with the parsed data.

        Raises:
            ValueError: If the line is malformed, coordinates are invalid or
                metadata contains invalid values.
        """
        zone_values: list[str] = line.split(" ")
        if len(zone_values) < 4:
            raise ValueError(f"Line {line_num}: Missing fields for zone!")
        name = zone_values[1].strip()
        if not name:
            raise ValueError(f"Line {line_num}: Zone name is empty!")
        if " " in name:
            raise ValueError(
                f"Line {line_num}: Zone name '{name}' cannot contain spaces!")
        if "-" in name:
            raise ValueError(
                f"Line {line_num}: Invalid zone name '{name}' (contains '-')!")
        try:
            x = int(zone_values[2])
            y = int(zone_values[3])
        except ValueError:
            raise ValueError(
                f"Line {line_num}: Invalid coordinates for zone '{name}'!")
        color = "white"
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
                        try:
                            max_drones = int(value.strip().strip("[]"))
                        except ValueError:
                            raise ValueError(
                                f"Line {line_num}: Invalid max_drones for zone"
                                f" '{name}'")
                    elif key == "zone" and hub_type not in ("start", "end"):
                        zone_type = value.strip()
                        if zone_type not in ("normal", "blocked", "restricted",
                                             "priority"):
                            raise ValueError(
                                f"Line {line_num}: Invalid zone type "
                                f"'{zone_type}' in zone '{name}'")
        return Zone(
            hub_type=hub_type,
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            drone_count=0
        )

    def connection_parser(self, line: str, line_num: int) -> Connection:
        """Parse a single connection line into a Connection object.

        Args:
            line: A raw line from the map file starting with connection:.

        Returns:
            A Connection object populated with the parsed data.

        Raises:
            ValueError: If the line is malformed or metadata contains invalid
                values.
        """
        connection_values = line.split(" ")
        if len(connection_values) < 2:
            raise ValueError(
                f"Line {line_num}: Missing fields for connection!")
        try:
            zone_a: str = connection_values[1].split("-")[0]
            zone_b: str = connection_values[1].split("-")[1].strip()
        except IndexError:
            raise ValueError(f"Line {line_num}: Connection has incorrect "
                             "format (<name1>-<name2>)")
        if not zone_a or not zone_b:
            raise ValueError(
                f"Line {line_num}: Invalid connection '{zone_a}-{zone_b}' "
                "(missing zone name)!")
        max_capacity: int = 1
        if "[" in line:
            metadata = " ".join(connection_values[2:]).strip("[]")
            for item in metadata.split(" "):
                if "=" in item:
                    key, value = item.split("=")
                    if key == "max_link_capacity":
                        try:
                            max_capacity = int(value.strip().strip("[]"))
                        except ValueError:
                            raise ValueError(
                                f"Line {line_num}: Invalid max_link_capacity "
                                f"for connection '{zone_a}-{zone_b}'!")
                        if max_capacity < 1:
                            raise ValueError(
                                f"Line {line_num}: Invalid max_link_capacity "
                                f"for connection '{zone_a}-{zone_b}'!")
        return Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_capacity=max_capacity,
            drone_count=0,
            name=f"{zone_a}-{zone_b}"
        )

    def parser(self) -> MapData:
        """Parse the map file and return a complete MapData object.

        Returns:
            A MapData object containing all zones and connections.

        Raises:
            ValueError: If the file is not found, cannot be read, or contains
                invalid or missing required data.
        """
        map_config = MapData()
        try:
            with open(self.filename, 'r') as configs:
                existing_connections = set()
                line_num = 0
                for line in configs:
                    line_num += 1
                    if not line.strip() or line.startswith("#"):
                        continue
                    if line.startswith("nb_drones"):
                        key_value = line.split(":")
                        value: str = key_value[1].strip()
                        map_config.nb_drones = int(value)
                    elif line.startswith("start_hub"):
                        map_config.zones.append(self.zone_parser(line,
                                                "start", line_num))
                    elif line.startswith("end_hub"):
                        map_config.zones.append(self.zone_parser(line,
                                                "end", line_num))
                    elif line.startswith("hub"):
                        map_config.zones.append(self.zone_parser(line, "hub",
                                                line_num))
                    elif line.startswith("connection"):
                        connection = self.connection_parser(line, line_num)
                        a = connection.zone_a
                        b = connection.zone_b
                        key = tuple(sorted((a, b)))
                        if key in existing_connections:
                            raise ValueError(
                                f"Line {line_num}: Duplicate connection "
                                f"{a}-{b}")
                        existing_connections.add(key)
                        map_config.connections.append(connection)
                if map_config.nb_drones is None:
                    raise ValueError("No number of drones was indicated!")
                if map_config.nb_drones <= 0:
                    raise ValueError("Number of drones must be positive!")
                if len(map_config.zones) == 0:
                    raise ValueError("No zones were provided!")
                if len(map_config.connections) == 0:
                    raise ValueError("No connections were provided!")
                starts = [z for z in map_config.zones if z.hub_type == "start"]
                ends = [z for z in map_config.zones if z.hub_type == "end"]
                if len(starts) == 0:
                    raise ValueError("No start zone was provided!")
                if len(starts) > 1:
                    raise ValueError("Multiple start zones were provided!")
                if len(ends) == 0:
                    raise ValueError("No end zone was provided!")
                if len(ends) > 1:
                    raise ValueError("Multiple end zones were provided!")
                zone_names: set[str] = {zone.name for zone in map_config.zones}
                if len(map_config.zones) > len(zone_names):
                    raise ValueError("There are duplicate zone names!")
                for connection in map_config.connections:
                    if connection.zone_a not in zone_names or \
                            connection.zone_b not in zone_names:
                        raise ValueError(
                            f"Invalid connection: {connection.zone_a}-"
                            f"{connection.zone_b}"
                        )
        except FileNotFoundError:
            raise ValueError(f"Map file '{self.filename}' not found!")
        except PermissionError:
            raise ValueError(f"No permission to open '{self.filename}'")
        return map_config
