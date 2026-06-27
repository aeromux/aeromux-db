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

from pathlib import Path

from aeromux_db.sources.opensky import parse_aircraft_enrichment, parse_manufacturers


def _write_csv(path: Path, header: str, rows: list[str]) -> Path:
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


# --- Issue #5: case-fold keys + deterministic (mode) manufacturer name ---

def test_manufacturers_case_fold_and_mode_name(tmp_path: Path) -> None:
    csv_path = _write_csv(
        tmp_path / "opensky.csv",
        "manufacturerIcao,manufacturerName",
        [
            "BOEING,Boeing",
            "Boeing,Boeing",
            "MCDONNELL DOUGLAS,Mcdonnell Douglas",
            "MCDONNELL DOUGLAS,Mcdonnell Douglas",
            "MCDONNELL DOUGLAS,Douglas",
        ],
    )
    result = {m.manufacturer_icao: m.manufacturer_name for m in parse_manufacturers(csv_path)}

    # BOEING / Boeing collapse into a single upper-cased key
    assert "Boeing" not in result
    assert result["BOEING"] == "Boeing"
    # Mode wins over the last-written minority value
    assert result["MCDONNELL DOUGLAS"] == "Mcdonnell Douglas"
    assert len(result) == 2


def test_manufacturers_all_empty_name_is_none(tmp_path: Path) -> None:
    csv_path = _write_csv(
        tmp_path / "opensky.csv",
        "manufacturerIcao,manufacturerName",
        ["FOO,", "FOO,"],
    )
    result = {m.manufacturer_icao: m.manufacturer_name for m in parse_manufacturers(csv_path)}
    assert result == {"FOO": None}


# --- Issue #5: enrichment upper-cases the manufacturer ref to match the table key ---

def test_enrichment_folds_manufacturer_icao(tmp_path: Path) -> None:
    csv_path = _write_csv(
        tmp_path / "opensky.csv",
        "icao24,manufacturerIcao,manufacturerName,model,registration,country,serialNumber,operatorIcao,operator,owner,typecode",
        ["abc123,Boeing,Boeing,737-800,N1,USA,,,,,B738"],
    )
    records = parse_aircraft_enrichment(csv_path)
    assert len(records) == 1
    rec = records[0]
    assert rec.icao24 == "ABC123"
    assert rec.manufacturer_icao == "BOEING"  # case-folded to match manufacturers key
