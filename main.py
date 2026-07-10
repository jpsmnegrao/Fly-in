"""Entry point for the Fly-In drone routing simulation.

Parses a map file given on the command line, builds the navigation graph, and
launches the demo window.
"""

from parser import ParserReturn
from pathfinder import NavGraph
from demo_window import DemoWindow
from simulation import Simulation
import sys


def main() -> None:
    """Parse the map file from argv, build the nav graph, and run the demo.

    Expects exactly one command-line argument: the path to a map configuration
    file. On any parsing error (invalid map, missing file, etc.), prints the
    error message and exits gracefully.
    """
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    try:
        map_parser = ParserReturn(sys.argv[1])
        map_data = map_parser.parser()
        nav_graph = NavGraph(map_data)
        nav_graph.build_zone_lookup()
        nav_graph.build_adjacency()
        nav_graph.reverse_dijkstra()
        simulation = Simulation(map_data, nav_graph)
        window = DemoWindow(map_data, simulation)
        window.run()
    except ValueError as error:
        print(error)


if __name__ == "__main__":
    main()
