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

import sqlite3

from aeromux_db.builder import build_database
from aeromux_db.models import (
    Aircraft,
    AircraftType,
    Manufacturer,
    OpenSkyAircraftData,
    Operator,
)


# --- Issue #4: type stays authoritative; manufacturer is derived from it ---

def test_manufacturer_derived_from_type_overrides_stale_source() -> None:
    """Reassigned hex 4D2145: the type stays A321 (Mictronics, correct) and the
    manufacturer is derived from it as Airbus, overriding OpenSky's stale
    'Dassault' from the previous aircraft on that hex."""
    types = [AircraftType("A321", "AIRBUS A-321", "L2J")]
    result = build_database(
        aircraft=[Aircraft("4D2145", aircraft_registration="9H-WZC", aircraft_type_code="A321")],
        types=types,
        operators=[],
        manufacturers=[Manufacturer("AIRBUS", "Airbus"), Manufacturer("DASSAULT", "Dassault")],
        opensky_aircraft=[
            OpenSkyAircraftData(icao24="4D2145", manufacturer_icao="DASSAULT")
        ],
        db_version="2099.4.w52_r11",
    )
    with sqlite3.connect(result.path) as conn:
        row = conn.execute(
            "SELECT aircraft_type_code, aircraft_manufacturer_icao FROM aircrafts "
            "WHERE aircraft_icao_address='4D2145'"
        ).fetchone()
        assert row == ("A321", "AIRBUS")
        view = conn.execute(
            "SELECT type_description, manufacturer_name FROM aircraft_view "
            "WHERE aircraft_icao_address='4D2145'"
        ).fetchone()
        assert view == ("AIRBUS A-321", "Airbus")


def test_manufacturer_not_derived_when_type_maker_unknown() -> None:
    """A type whose maker is not in the manufacturers table keeps the per-aircraft
    manufacturer rather than being blanked."""
    types = [AircraftType("A109", "AGUSTA AW-109 Grand", "H2T")]
    result = build_database(
        aircraft=[Aircraft("ABC900", aircraft_type_code="A109")],
        types=types,
        operators=[],
        manufacturers=[Manufacturer("LEONARDO", "Leonardo")],
        opensky_aircraft=[OpenSkyAircraftData(icao24="ABC900", manufacturer_icao="LEONARDO")],
        db_version="2099.4.w52_r12",
    )
    with sqlite3.connect(result.path) as conn:
        row = conn.execute(
            "SELECT aircraft_manufacturer_icao FROM aircrafts WHERE aircraft_icao_address='ABC900'"
        ).fetchone()
        assert row[0] == "LEONARDO"


# --- Issue #1: operator write-guard + view fall-through ---

def test_unknown_operator_icao_routes_to_fallback() -> None:
    """OpenSky operator_icao absent from operators table -> name kept as fallback,
    no dangling reference, and the view surfaces the fallback name."""
    result = build_database(
        aircraft=[Aircraft("ABC001", aircraft_registration="N1")],
        types=[],
        operators=[],  # 'ZZZ' is not present
        opensky_aircraft=[
            OpenSkyAircraftData(icao24="ABC001", operator_icao="ZZZ", operator="Mystery Air")
        ],
        db_version="2099.4.w52_r13",
    )
    with sqlite3.connect(result.path) as conn:
        op_icao = conn.execute(
            "SELECT aircraft_operator_icao FROM aircrafts WHERE aircraft_icao_address='ABC001'"
        ).fetchone()[0]
        assert op_icao is None
        name = conn.execute(
            "SELECT operator_name FROM aircraft_view WHERE aircraft_icao_address='ABC001'"
        ).fetchone()[0]
        assert name == "Mystery Air"


def test_known_operator_icao_sets_reference() -> None:
    result = build_database(
        aircraft=[Aircraft("ABC002", aircraft_registration="N2")],
        types=[],
        operators=[Operator("ABC", operator_name="ABC Airlines")],
        opensky_aircraft=[
            OpenSkyAircraftData(icao24="ABC002", operator_icao="ABC", operator="ignored")
        ],
        db_version="2099.4.w52_r14",
    )
    with sqlite3.connect(result.path) as conn:
        op_icao = conn.execute(
            "SELECT aircraft_operator_icao FROM aircrafts WHERE aircraft_icao_address='ABC002'"
        ).fetchone()[0]
        assert op_icao == "ABC"
        name = conn.execute(
            "SELECT operator_name FROM aircraft_view WHERE aircraft_icao_address='ABC002'"
        ).fetchone()[0]
        assert name == "ABC Airlines"


# --- Issue #3: OpenSky model/owner stub-row creation ---

def test_opensky_model_owner_creates_details_row() -> None:
    """Aircraft without an ADS-B details row still receives OpenSky model/owner."""
    result = build_database(
        aircraft=[Aircraft("ABC003", aircraft_registration="N3")],
        types=[],
        operators=[],
        aircraft_details=None,  # no ADS-B details
        opensky_aircraft=[
            OpenSkyAircraftData(icao24="ABC003", model="Test Model", owner="Test Owner")
        ],
        db_version="2099.4.w52_r15",
    )
    with sqlite3.connect(result.path) as conn:
        row = conn.execute(
            "SELECT model, owner_operator FROM aircraft_details WHERE aircraft_icao_address='ABC003'"
        ).fetchone()
        assert row == ("Test Model", "Test Owner")
