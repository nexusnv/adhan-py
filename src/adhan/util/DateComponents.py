from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DateComponents:
    year: int
    month: int
    day: int

    @classmethod
    def from_utc(cls, date: datetime | DateComponents) -> DateComponents:
        return cls(date.year, date.month, date.day)
