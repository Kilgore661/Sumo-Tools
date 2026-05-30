from sumo_core.History import Date
from sumo_core.BasicPrimitives import Day, Month, Year
from infra.tracker.types import BashoDayRef
from infra.tracker.scraper.scraper import scrape

requested = [
    BashoDayRef(Date(Year(2024), Month(1)), Day(1)),
    BashoDayRef(Date(Year(2024), Month(1)), Day(15)),
    BashoDayRef(Date(Year(2024), Month(3)), Day(1)),
    BashoDayRef(Date(Year(2024), Month(3)), Day(2)),
    BashoDayRef(Date(Year(2024), Month(3)), Day(3)),
    BashoDayRef(Date(Year(2020), Month(5)), Day(1)),
]

print(scrape(requested))
