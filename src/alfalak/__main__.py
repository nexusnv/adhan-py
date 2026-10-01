import argparse
from datetime import datetime, timezone

from alfalak import CalculationMethod, Prayer, PrayerTimes
from alfalak.data import Coordinates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="al-falak",
        description="Print prayer times (ISO-8601, UTC) for a location and date.",
    )
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument(
        "--date",
        default=None,
        help="Calendar date as YYYY-MM-DD (defaults to today, UTC).",
    )
    parser.add_argument(
        "--method",
        default=CalculationMethod.MUSLIM_WORLD_LEAGUE.name,
        choices=sorted(method.name for method in CalculationMethod),
        help="Calculation method (default: MUSLIM_WORLD_LEAGUE).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.date is None:
        date = datetime.now(timezone.utc)
    else:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            build_parser().error(f"invalid --date (expected YYYY-MM-DD): {args.date}")

    prayer_times = PrayerTimes(
        Coordinates(args.latitude, args.longitude),
        date,
        calculation_method=CalculationMethod[args.method],
    )
    for prayer in Prayer:
        if prayer != Prayer.NONE:
            print(
                f"{prayer.name.lower()}={prayer_times.time_for_prayer(prayer).isoformat()}"
            )


if __name__ == "__main__":
    main()
