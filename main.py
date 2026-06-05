"""mambo jambo."""

from parser import ParserReturn
from demo_window import DemoWindow
import sys


def main() -> None:
    """jambo"""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    try:
        map_parser = ParserReturn(sys.argv[1])
        map_data = map_parser.parser()
        window = DemoWindow(map_data)
        window.run_renderer()
    except ValueError as error:
        print(error)


if __name__ == "__main__":
    main()
