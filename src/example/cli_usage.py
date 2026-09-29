"""CLI usage examples for python -m adhan."""

import subprocess
import sys


def main() -> None:
    print("CLI usage examples")
    print("=" * 60)
    print()

    # Example 1: Basic usage
    print("1. Basic usage:")
    print("   python -m adhan --latitude 35.7750 --longitude -78.6336")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "adhan",
            "--latitude",
            "35.7750",
            "--longitude",
            "-78.6336",
        ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)

    # Example 2: With date and method
    print("2. With date and method:")
    print(
        "   python -m adhan --latitude 35.7750 --longitude -78.6336 --date 2015-07-12 --method NORTH_AMERICA"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "adhan",
            "--latitude",
            "35.7750",
            "--longitude",
            "-78.6336",
            "--date",
            "2015-07-12",
            "--method",
            "NORTH_AMERICA",
        ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)

    # Example 3: Different method
    print("3. Different method (Muslim World League):")
    print(
        "   python -m adhan --latitude 51.5074 --longitude -0.1278 --method MUSLIM_WORLD_LEAGUE"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "adhan",
            "--latitude",
            "51.5074",
            "--longitude",
            "-0.1278",
            "--method",
            "MUSLIM_WORLD_LEAGUE",
        ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)


if __name__ == "__main__":
    main()
