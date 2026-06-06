"""Tests for the map file parser.

Tests cover all error cases and valid map parsing for the ParserReturn class.
"""

import subprocess
import pytest
from pathlib import Path
from parser import ParserReturn


INVALID_MAPS_DIR = "maps/invalid"
VALID_MAPS_DIR = "maps"
PYTHON = "venv/bin/python"


class TestValidMaps:
    """Tests for valid map parsing."""

    def test_easy_map(self) -> None:
        """Test that the easy map parses without errors."""
        p = ParserReturn(f"{VALID_MAPS_DIR}/easy/01_linear_path.txt")
        p.parser()

    def test_medium_map(self) -> None:
        """Test that the medium map parses without errors."""
        p = ParserReturn(f"{VALID_MAPS_DIR}/medium/02_circular_loop.txt")
        p.parser()

    def test_hard_map(self) -> None:
        """Test that the hard map parses without errors."""
        p = ParserReturn(f"{VALID_MAPS_DIR}/hard/03_ultimate_challenge.txt")
        p.parser()


class TestParserFileErrors:
    """Tests for file-level errors."""

    def test_file_not_found(self) -> None:
        """Test that a missing file raises ValueError and exits gracefully."""
        p = ParserReturn("maps/invalid/nonexistent.txt")
        with pytest.raises(ValueError, match="not found"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", "maps/invalid/nonexistent.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_permission_error(self, tmp_path: Path) -> None:
        """Test if unreadable file raises ValueError and exits gracefully."""
        f = tmp_path / "locked.txt"
        f.write_text("nb_drones: 2")
        f.chmod(0o000)
        p = ParserReturn(str(f))
        with pytest.raises(ValueError):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", str(f)],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr


class TestParserMapErrors:
    """Tests for invalid map content."""

    def test_missing_nb_drones(self) -> None:
        """
        Test if missing nb_drones line raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/missing_nb_drones.txt")
        with pytest.raises(ValueError, match="No number of drones"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/missing_nb_drones.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_no_zones(self) -> None:
        """
        Test that a map with no zones raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_zones.txt")
        with pytest.raises(ValueError, match="No zones"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/no_zones.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_no_connections(self) -> None:
        """
        Test if map with no connections raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_connections.txt")
        with pytest.raises(ValueError, match="No connections"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/no_connections.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_no_start(self) -> None:
        """
        Test if a map with no start hub raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_start.txt")
        with pytest.raises(ValueError, match="No start zone"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/no_start.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_no_end(self) -> None:
        """
        Test that a map with no end hub raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_end.txt")
        with pytest.raises(ValueError, match="No end zone"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/no_end.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr


class TestZoneParserErrors:
    """Tests for invalid zone definitions."""

    def test_missing_zone_fields(self) -> None:
        """
        Test if a zone missing fields raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/missing_zone_fields.txt")
        with pytest.raises(ValueError, match="Missing fields"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/missing_zone_fields.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_hyphen_in_name(self) -> None:
        """
        Test if zone name with hyphen raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/hyphen_in_name.txt")
        with pytest.raises(ValueError, match="contains"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/hyphen_in_name.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_invalid_coordinates(self) -> None:
        """
        Test if non-integer coordinates raise ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_coordinates.txt")
        with pytest.raises(ValueError, match="Invalid cordinates"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/invalid_coordinates.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_invalid_max_drones(self) -> None:
        """
        Test if a non-integer max_drones raises ValueError, exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_max_drones.txt")
        with pytest.raises(ValueError, match="Max drones"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/invalid_max_drones.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_invalid_zone_type(self) -> None:
        """
        Test that an invalid zone type raises ValueError and exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_zone_type.txt")
        with pytest.raises(ValueError, match="Invalid zone type"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py", f"{INVALID_MAPS_DIR}/invalid_zone_type.txt"],
            capture_output=True, text=True)
        assert "Traceback" not in result.stderr

    def test_multiple_starts(self) -> None:
        """Test that multiple start hubs raise ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/multiple_starts.txt")
        with pytest.raises(ValueError, match="Multiple start zones"):
            p.parser()

    def test_multiple_ends(self) -> None:
        """Test that multiple end hubs raise ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/multiple_ends.txt")
        with pytest.raises(ValueError, match="Multiple end zones"):
            p.parser()


class TestConnectionParserErrors:
    """Tests for invalid connection definitions."""

    def test_invalid_connection_format(self) -> None:
        """
        Test if connection without hyphen raises ValueError, exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_connection_format.txt")
        with pytest.raises(ValueError, match="incorrect format"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py",
             f"{INVALID_MAPS_DIR}/invalid_connection_format.txt"],
            capture_output=True, text=True
        )
        assert "Traceback" not in result.stderr

    def test_invalid_max_capacity(self) -> None:
        """
        Test if a non-int max drones cap raises ValueError, exits gracefully.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_max_capacity.txt")
        with pytest.raises(ValueError, match="must be an integer"):
            p.parser()
        result = subprocess.run(
            [PYTHON, "main.py",
             f"{INVALID_MAPS_DIR}/invalid_max_capacity.txt"],
            capture_output=True, text=True
        )
        assert "Traceback" not in result.stderr

    def test_negative_max_capacity(self) -> None:
        """
        Test if zero or less max drones cap raises ValueError, exits gracefull.
        """
        p = ParserReturn(f"{INVALID_MAPS_DIR}/negative_max_capacity.txt")
        with pytest.raises(ValueError, match="positive integer"):
            p.parser()
        result = subprocess.run(
            [PYTHON,
             "main.py",
             f"{INVALID_MAPS_DIR}/negative_max_capacity.txt"],
            capture_output=True, text=True
        )
        assert "Traceback" not in result.stderr
