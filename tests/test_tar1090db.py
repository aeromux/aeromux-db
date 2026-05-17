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

from aeromux_db.sources.tar1090db import parse_wtc


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tar1090db"


def test_parse_wtc_keeps_valid_letters_and_drops_invalid() -> None:
    result = parse_wtc(FIXTURE_DIR)

    assert result == {
        "A388": "J",
        "B748": "H",
        "C172": "L",
        "B738": "M",
    }
    assert "BADX" not in result  # invalid WTC letter
    assert "BADY" not in result  # empty string
    assert "BADZ" not in result  # missing wtc field


def test_parse_wtc_missing_file_returns_empty(tmp_path: Path) -> None:
    assert parse_wtc(tmp_path) == {}
