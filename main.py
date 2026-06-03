"""mambo jambo."""

from parser import ParserReturn
from demo_window import DemoWindow


def main() -> None:
    """jambo"""
    # map_parser = ParserReturn("maps/easy/01_linear_path.txt")
    # map_parser = ParserReturn("maps/medium/03_priority_puzzle.txt")
    map_parser = ParserReturn("maps/hard/01_maze_nightmare.txt")
    map_data = map_parser.parser()
    window = DemoWindow(map_data)
    window.run_renderer()


if __name__ == "__main__":
    main()
