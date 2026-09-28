"""Qibla direction for multiple cities."""

from adhan import Qibla


def main() -> None:
    cities = [
        ("Raleigh, US", (35.7750, -78.6336)),
        ("New York, US", (40.7128, -74.0060)),
        ("London, UK", (51.5074, -0.1278)),
        ("Cairo, EG", (30.0444, 31.2357)),
        ("Kuala Lumpur, MY", (3.1390, 101.6869)),
        ("Jakarta, ID", (-6.2088, 106.8456)),
        ("Sydney, AU", (-33.8688, 151.2093)),
        ("Cape Town, ZA", (-33.9249, 18.4241)),
    ]

    print("Qibla direction (degrees clockwise from north)")
    print()
    for name, coords in cities:
        direction = Qibla(coords).direction
        print(f"  {name:<20} {direction:>7.2f}°")


if __name__ == "__main__":
    main()
