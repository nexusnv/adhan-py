import subprocess
import sys

import pytest
from adhan.__main__ import main


def test_cli_prints_iso_times(capsys):
    main(
        [
            "--latitude",
            "35.7750",
            "--longitude",
            "-78.6336",
            "--date",
            "2015-07-12",
            "--method",
            "NORTH_AMERICA",
        ]
    )

    lines = dict(
        line.split("=", 1) for line in capsys.readouterr().out.strip().splitlines()
    )
    assert set(lines) == {
        "fajr",
        "sunrise",
        "dhuhr",
        "asr",
        "maghrib",
        "isha",
    }
    assert lines["fajr"] == "2015-07-12T08:42:00+00:00"


def test_cli_defaults_to_today(capsys):
    main(["--latitude", "35.7750", "--longitude", "-78.6336"])

    assert "fajr=" in capsys.readouterr().out


def test_cli_rejects_unknown_method():
    with pytest.raises(SystemExit) as excinfo:
        main(["--latitude", "35", "--longitude", "-78", "--method", "BOGUS"])

    assert excinfo.value.code == 2


def test_cli_rejects_bad_date():
    with pytest.raises(SystemExit) as excinfo:
        main(["--latitude", "35", "--longitude", "-78", "--date", "not-a-date"])

    assert excinfo.value.code == 2


def test_cli_rejects_datetime_for_date():
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--latitude",
                "35",
                "--longitude",
                "-78",
                "--date",
                "2015-07-12T00:00:00",
            ]
        )

    assert excinfo.value.code == 2


def test_cli_requires_coordinates():
    with pytest.raises(SystemExit) as excinfo:
        main(["--latitude", "35"])

    assert excinfo.value.code == 2


def test_cli_module_entry_point():
    # smoke test: the installed package runs as python -m adhan
    result = subprocess.run(
        [sys.executable, "-m", "adhan", "--latitude", "35", "--longitude", "-78"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "fajr=" in result.stdout
