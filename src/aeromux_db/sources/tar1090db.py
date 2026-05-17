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

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SOURCE_URL = "https://github.com/wiedehopf/tar1090-db/archive/refs/heads/master.tar.gz"
SOURCE_FILENAME = "tar1090-db.tar.gz"

_VALID_WTC = frozenset({"L", "M", "H", "J"})


def parse_wtc(extract_dir: Path) -> dict[str, str]:
    """Parse per-type Wake Turbulence Categories from tar1090-db.

    The tarball extracts to a directory containing ``icao_aircraft_types.json``
    at the root (under a single repo-named top-level directory created by
    the GitHub archive endpoint).  The JSON is a flat object of shape::

        {"A388": {"desc": "L4J", "wtc": "J"}, ...}

    Only the ``wtc`` field is consumed here — ``desc`` overlaps with
    Mictronics's ``type_icao_class`` and is intentionally ignored so
    Mictronics stays the single authority for that column.

    Args:
        extract_dir: Path to the extracted tarball directory.

    Returns:
        Dict mapping ICAO type designator to validated WTC letter.
        Entries whose ``wtc`` value is not one of ``{L, M, H, J}`` are
        dropped (and counted in the log).
    """
    candidates = sorted(extract_dir.rglob("icao_aircraft_types.json"))
    if not candidates:
        logger.warning("icao_aircraft_types.json not found under %s", extract_dir)
        return {}
    json_path = candidates[0]

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    out: dict[str, str] = {}
    dropped = 0
    for type_code, entry in raw.items():
        if not isinstance(entry, dict):
            dropped += 1
            continue
        wtc = entry.get("wtc")
        if isinstance(wtc, str) and wtc in _VALID_WTC:
            out[type_code] = wtc
        else:
            dropped += 1

    logger.debug(
        "Parsed %d WTC entries from tar1090-db (%d dropped)",
        len(out),
        dropped,
    )
    return out
