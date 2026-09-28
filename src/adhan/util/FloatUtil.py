import math


def normalize_with_bound(value: float, max: float) -> float:
    return value - (max * (math.floor(value / max)))


def unwind_angle(value: float) -> float:
    return normalize_with_bound(value, 360)


def closest_angle(angle: float) -> float:
    if angle >= -180 and angle <= 180:
        return angle

    return angle - (360 * round(angle / 360))
