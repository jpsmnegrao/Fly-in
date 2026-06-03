"""Tests for the map file parser.

Tests cover all error cases and valid map parsing for the ParserReturn class.
"""

import pytest
from pathlib import Path
from parser import ParserReturn


INVALID_MAPS_DIR = "maps/invalid"
VALID_MAPS_DIR = "maps"


class TestParserFileErrors:
    """Tests for file-level errors."""

    def test_file_not_found(self) -> None:
        """Test that a missing file raises ValueError."""
        p = ParserReturn("nonexistent.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_permission_error(self, tmp_path: Path) -> None:
        """Test that an unreadable file raises ValueError."""
        f = tmp_path / "locked.txt"
        f.write_text("nb_drones: 2")
        f.chmod(0o000)
        p = ParserReturn(str(f))
        with pytest.raises(ValueError):
            p.parser()


class TestParserMapErrors:
    """Tests for invalid map content."""

    def test_missing_nb_drones(self) -> None:
        """Test that a missing nb_drones line raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/missing_nb_drones.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_no_zones(self) -> None:
        """Test that a map with no zones raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_zones.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_no_connections(self) -> None:
        """Test that a map with no connections raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_connections.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_no_start(self) -> None:
        """Test that a map with no start hub raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_start.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_no_end(self) -> None:
        """Test that a map with no end hub raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/no_end.txt")
        with pytest.raises(ValueError):
            p.parser()


class TestZoneParserErrors:
    """Tests for invalid zone definitions."""

    def test_missing_zone_fields(self) -> None:
        """Test that a zone with missing fields raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/missing_zone_fields.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_hyphen_in_name(self) -> None:
        """Test that a zone name with a hyphen raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/hyphen_in_name.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_invalid_coordinates(self) -> None:
        """Test that non-integer coordinates raise ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_coordinates.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_invalid_max_drones(self) -> None:
        """Test that a non-integer max_drones raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_max_drones.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_invalid_zone_type(self) -> None:
        """Test that an invalid zone type raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_zone_type.txt")
        with pytest.raises(ValueError):
            p.parser()


class TestConnectionParserErrors:
    """Tests for invalid connection definitions."""

    def test_invalid_connection_format(self) -> None:
        """Test that a connection without hyphen raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_connection_format.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_invalid_max_capacity(self) -> None:
        """Test that a non-integer max_link_capacity raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/invalid_max_capacity.txt")
        with pytest.raises(ValueError):
            p.parser()

    def test_negative_max_capacity(self) -> None:
        """Test that a zero or negative max_link_capacity raises ValueError."""
        p = ParserReturn(f"{INVALID_MAPS_DIR}/negative_max_capacity.txt")
        with pytest.raises(ValueError):
            p.parser()


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
