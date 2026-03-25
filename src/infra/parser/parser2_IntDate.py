from sumo_core.History import Date, Year, Month

class IntDate(Date):
    def __init__(self, year: int, month: int):
        super().__init__(Year(year), Month(month))

    def __le__(self, other):
        # Python will use the __lt__ and __eq__ methods inherited from Date.
        return self < other or self == other

    


