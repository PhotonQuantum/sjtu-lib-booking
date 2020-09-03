from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Reservation:
    sn: int
    date: date
