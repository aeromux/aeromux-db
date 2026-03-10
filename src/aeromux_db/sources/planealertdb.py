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

import csv
import logging
from pathlib import Path

from aeromux_db.models import PlaneAlertData

logger = logging.getLogger(__name__)

SOURCE_URL = "https://raw.githubusercontent.com/sdr-enthusiasts/plane-alert-db/main/plane-alert-db.csv"
SOURCE_FILENAME = "plane-alert-db.csv"


def _to_str(value: str | None) -> str | None:
    """Return None for empty strings, otherwise the stripped value."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_aircraft(file_path: Path) -> list[PlaneAlertData]:
    """Parse the Plane Alert DB CSV file.

    The CSV has a header row and columns:
    ``$ICAO, $Registration, $Operator, $Type, $ICAO Type, #CMPG, ...``.

    Duplicate ICAO addresses are deduplicated (last occurrence wins).

    Args:
        file_path: Path to the downloaded CSV file.

    Returns:
        List of parsed Plane Alert DB records.
    """
    aircraft: dict[str, PlaneAlertData] = {}

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 6:
                continue
            icao = _to_str(row[0])
            if icao is None:
                continue
            # Registrations containing only '?' characters are placeholders, not real values
            aircraft[icao.upper()] = PlaneAlertData(
                aircraft_icao_address=icao.upper(),
                aircraft_registration=reg if (reg := _to_str(row[1])) is None or reg.strip("?") else None,
                operator=_to_str(row[2]),
                model=_to_str(row[3]),
                aircraft_type_code=_to_str(row[4]),
                military=row[5].strip() == "Mil",
            )

    result = list(aircraft.values())
    logger.debug("Parsed %d aircraft from Plane Alert DB", len(result))
    return result
