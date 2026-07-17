"""Entry point for the Fly-In drone routing simulation.

Parses the map file, builds the navigation graph, initializes the simulation
and launches the demo window.
"""

from parser import ParserReturn
from pathfinder import NavGraph
from demo_window import DemoWindow
from simulation import Simulation
import sys


def main() -> None:
    """Parse the map file, build the nav graph, and run the demo.

    Uses the map file specified as the first command-line argument to build the
    navigation graph and initialize the simulation. If the window requests a
    restart, the simulation is recreated from the same map. On any parsing
    error, prints the error message and exits gracefully.
    """
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    while True:
        try:
            map_parser = ParserReturn(sys.argv[1])
            map_data = map_parser.parser()
            nav_graph = NavGraph(map_data)
            simulation = Simulation(map_data, nav_graph)
            window = DemoWindow(map_data, simulation)
            if not window.run():
                break
        except ValueError as error:
            print(error)
            break


if __name__ == "__main__":
    main()
