# Aeromux Database Builder
# Copyright (C) 2025-2026 Nandor Toth <dev@nandortoth.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from aeromux_db.builder import _build_type_manufacturer_map, _resolve_registration
from aeromux_db.models import AircraftType


# --- Issue #2: registration majority-tiebreak prefers OpenSky over ADS-B ---

def test_registration_majority_reports_opensky_over_adsbx() -> None:
    """When a value is backed by both ADS-B and OpenSky, OpenSky is the reported
    source (priority 3 > 2), matching the documented default priority."""
    value, source, reason = _resolve_registration(
        mic="9H-OLD", adsbx="9H-NEW", opensky="9H-NEW",
    )
    assert value == "9H-NEW"
    assert source == "opensky"
    assert reason == "majority"


# --- Issue #4: manufacturer derived from the (authoritative) type description ---

def test_type_manufacturer_map_derives_from_description() -> None:
    types = [
        AircraftType("A321", "AIRBUS A-321", "L2J"),
        AircraftType("FA50", "DASSAULT Falcon 50", "L3J"),
        AircraftType("C17", "BOEING C-17 Globemaster 3", "L4J"),
        AircraftType("EC45", "AIRBUS HELICOPTERS EC-145", "H2T"),
        AircraftType("A109", "AGUSTA AW-109 Grand", "H2T"),  # maker not in keys
        AircraftType("NONE", None, None),  # no description
    ]
    keys = ["AIRBUS", "AIRBUS HELICOPTERS", "DASSAULT", "BOEING"]
    mapping = _build_type_manufacturer_map(types, keys)

    assert mapping["A321"] == "AIRBUS"
    assert mapping["FA50"] == "DASSAULT"
    assert mapping["C17"] == "BOEING"
    # Longest whole-word prefix wins
    assert mapping["EC45"] == "AIRBUS HELICOPTERS"
    # Unknown maker and missing description are omitted (keep per-aircraft value)
    assert "A109" not in mapping
    assert "NONE" not in mapping


def test_type_manufacturer_map_requires_word_boundary() -> None:
    """A manufacturer key must match as a whole leading token, not a substring."""
    types = [AircraftType("X", "AIRBUSX SUPER", "L2J")]
    mapping = _build_type_manufacturer_map(types, ["AIRBUS"])
    assert mapping == {}
