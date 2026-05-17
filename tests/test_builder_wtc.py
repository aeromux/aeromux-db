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
from aeromux_db.models import AircraftType


def test_build_database_enriches_types_with_wtc() -> None:
    types = [
        AircraftType(type_code="A388", type_description="Airbus A380-800", type_icao_class="L4J"),
        AircraftType(type_code="B748", type_description="Boeing 747-8", type_icao_class="L4J"),
        AircraftType(type_code="C172", type_description="Cessna 172", type_icao_class="L1P"),
        AircraftType(type_code="OBSC", type_description="Obscure type", type_icao_class="L1P"),
    ]
    wtc_map = {"A388": "J", "B748": "H", "C172": "L"}  # OBSC absent on purpose

    result = build_database(
        aircraft=[],
        types=types,
        operators=[],
        wtc_map=wtc_map,
        db_version="2099.4.w52_r9",
    )

    with sqlite3.connect(result.path) as conn:
        rows = dict(conn.execute(
            "SELECT type_code, type_wtc FROM types ORDER BY type_code"
        ).fetchall())

    assert rows == {"A388": "J", "B748": "H", "C172": "L", "OBSC": None}


def test_build_database_db_integrity_wtc_values() -> None:
    """Every non-NULL type_wtc must be one of L, M, H, J."""
    types = [AircraftType(type_code="X", type_description="X", type_icao_class="L1P")]
    result = build_database(
        aircraft=[],
        types=types,
        operators=[],
        wtc_map={"X": "J"},
        db_version="2099.4.w52_r8",
    )

    with sqlite3.connect(result.path) as conn:
        bad = conn.execute(
            "SELECT COUNT(*) FROM types "
            "WHERE type_wtc IS NOT NULL AND type_wtc NOT IN ('L','M','H','J')"
        ).fetchone()[0]
    assert bad == 0


def test_build_database_works_without_wtc_map() -> None:
    """When wtc_map is None, all type_wtc values are NULL."""
    types = [AircraftType(type_code="A320", type_description="Airbus A320", type_icao_class="L2J")]
    result = build_database(
        aircraft=[],
        types=types,
        operators=[],
        wtc_map=None,
        db_version="2099.4.w52_r7",
    )

    with sqlite3.connect(result.path) as conn:
        row = conn.execute("SELECT type_wtc FROM types WHERE type_code = 'A320'").fetchone()
    assert row[0] is None
