from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import RikId


@dataclass(frozen=True)
class Ratings:
    basho_start: dict
    day_end: dict

    def the_rating(self, r: RikId, d, da):
        return self.day_end[d][da][r]
