import json, os
from enum import Enum
from typing import Any, Dict, Type, List
from zipfile import ZipFile, ZIP_DEFLATED

from sumo_core.BashoState import BashoState
from sumo_core.Summary import BoutResult, ResultLookup, DailyResults, Summary
from sumo_core.Performance import Performance
from sumo_core.Banzuke import Chii, RikChii, Shikona, RikShikona, Banzuke
from sumo_core.BasicEnums import Division, MSD, Outcome, Side, Symbol, Annotation, Prize, Direction
from sumo_core.Kimarite import Kimarite
from sumo_core.BasicPrimitives import RikId, Day, Pair, Torikumi, Riks
from sumo_core.History import History, Date, Year, Month
from ..parser.TableTypes import TableType, BodyTable, BanzukeTables

from .base_serialiser import BaseSerialiser

class SumoSerialiser(BaseSerialiser):
    """Handles serialisation of Sumo tournament data structures"""

    @classmethod
    def _serialise_chii(cls, chii: Chii) -> Dict:
        """Convert Chii object to dictionary"""
        return {
            "level": cls.enum_to_str(chii.level),
            "level_type": chii.level.__class__.__name__,
            "number": chii.number,
            "side": cls.enum_to_str(chii.side),
            "ann": cls.enum_to_str(chii.ann)
        }

    @classmethod
    def _deserialise_chii(cls, data: Dict) -> Chii:
        """Convert dictionary back to Chii object"""
        level_type = MSD if data["level_type"] == "MSD" else Division
        return Chii(
            level=cls.str_to_enum(data["level"], level_type),
            number=data["number"],
            side=cls.str_to_enum(data["side"], Side),
            ann=cls.str_to_enum(data["ann"], Ann)
        )

    @classmethod
    def _serialise_shik(cls, shik: Shikona) -> str:
        """Convert Shikona object to dictionary"""
        return shik

    @classmethod
    def _deserialise_shik(cls, data: str) -> Shikona:
        """Convert string back to Shikona object"""
        return Shikona(data)

    @classmethod
    def _serialise_rikchii(cls, rikchii: RikChii) -> Dict[str, Dict]:
        """Convert RikChii object to dictionary"""
        return {
            str(rid): cls._serialise_chii(chii)
            for rid, chii in rikchii.items()
            if isinstance(chii, Chii)  # Skip 'Mz' strings
        }

    @classmethod
    def _deserialise_rikchii(cls, data: Dict[str, Dict]) -> RikChii:
        """Convert dictionary back to RikChii object"""
        return RikChii({
            RikId(int(rid)): cls._deserialise_chii(chii_data)
            for rid, chii_data in data.items()
        })

    @classmethod
    def _serialise_rikshik(cls, rikshik: RikShikona) -> Dict[str, Dict]:
        """Convert RikShikona object to dictionary"""
        return {
            str(rid): cls._serialise_shik(shik)
            for rid, shik in rikshik.items()
            if isinstance(shik, Shikona)  # Skip 'Mz' strings
        }

    @classmethod
    def _deserialise_rikshik(cls, data: Dict[str, Dict]) -> RikShikona:
        """Convert dictionary back to RikShikona object"""
        return RikShikona({
            RikId(int(rid)): cls._deserialise_shik(shik_data)
            for rid, shik_data in data.items()
        })

    @classmethod
    def _serialise_bout_result(cls, bout: BoutResult) -> Dict:
        """Convert BoutResult object to dictionary"""
        return {
            "rikishi1": bout.rikishi1,
            "outcome1": cls.enum_to_str(bout.outcome1) if bout.outcome1 else None,
            "rikishi2": bout.rikishi2,
            "outcome2": cls.enum_to_str(bout.outcome2) if bout.outcome2 else None,
            "decision": (bout.decision.value if isinstance(bout.decision, Kimarite) else bout.decision),
            "symbol": None if bout.symbol is None else cls.enum_to_str(bout.symbol)
        }

    @classmethod
    def _deserialise_bout_result(cls, data: Dict) -> BoutResult:
        """Convert dictionary back to BoutResult object"""
        decision_data = data["decision"]
        
        # Convert decision back to enum or special value
        if decision_data in ["fusen", "blank"]:
            decision = decision_data
        else:
            try:
                decision = Kimarite.from_string(decision_data)
            except ValueError:
                # Handle legacy data or unknown kimarite
                print(f"Warning: Unknown kimarite '{decision_data}' in data")
                decision = Kimarite.UNCLASSIFIED
        symbol_str = data.get("symbol", None)
        symbol = cls.str_to_enum(symbol_str, Symbol) if symbol_str else None
        
        return BoutResult(
            rikishi1=RikId(data["rikishi1"]),
            outcome1=cls.str_to_enum(data["outcome1"], Outcome),
            rikishi2=RikId(data["rikishi2"]),
            outcome2=cls.str_to_enum(data["outcome2"], Outcome),
            decision=decision,
            symbol=symbol
        )

    @classmethod
    def _serialise_daily_results(cls, daily: DailyResults) -> Dict:
        return {
            "torikumi": list(daily.torikumi),
            "results_lookup": {
                f"{k[0]},{k[1]}": cls._serialise_bout_result(v)
                for k, v in daily.results_lookup.items()
            }
        }

    @classmethod
    def _serialise_riks(cls, riks: Riks) -> List[int]:
        """Convert Riks object to a list of integers"""
        return [int(rid) for rid in riks]

    @classmethod
    def _deserialise_riks(cls, data: List[int]) -> Riks:
        """Convert list of integers back to Riks object"""
        return Riks({RikId(rid) for rid in data})

    @classmethod
    def _deserialise_daily_results(cls, data: Dict) -> DailyResults:
        results_lookup = ResultLookup({
            Pair(RikId(int(k.split(",")[0])), RikId(int(k.split(",")[1]))): cls._deserialise_bout_result(v)
            for k, v in data["results_lookup"].items()
        })
        
        return DailyResults(
            torikumi=Torikumi([Pair(RikId(x[0]), RikId(x[1])) for x in data["torikumi"]]),
            results_lookup=results_lookup
        )

    @classmethod
    def _serialise_performance(cls, performance: Performance) -> Dict:
        """Convert Performance object to dictionary"""
        return {
            "prizes": [cls.enum_to_str(prise) for prise in performance.prizes] if performance.prizes else [],
            "updown": cls.enum_to_str(performance.updown) if performance.updown else None
        }

    @classmethod
    def _deserialise_performance(cls, data: Dict) -> Performance:
        """Convert dictionary back to Performance object"""
        prizes = frozenset(cls.str_to_enum(prise_str, Prize) for prise_str in data.get("prizes", []))
        updown = cls.str_to_enum(data.get("updown"), Direction) if data.get("updown") else None
        
        return Performance(
            prizes=prizes,
            updown=updown
        )

    @classmethod
    def _serialise_summary(cls, summary: Summary) -> Dict:
        """Convert Summary object to dictionary"""
        return {
            "daily_results": {
                str(day): cls._serialise_daily_results(daily_results)
                for day, daily_results in summary.items()
            },
            "performances": {
                str(rid): cls._serialise_performance(perf)
                for rid, perf in summary.performances.items()
            } if hasattr(summary, 'performances') and summary.performances else {}
        }

    @classmethod
    def _deserialise_summary(cls, data: Dict) -> Summary:
        """Convert dictionary back to Summary object"""
        daily_results = {
            Day(int(day)): cls._deserialise_daily_results(daily_data)
            for day, daily_data in data["daily_results"].items()
        }
        
        performances = {}
        if "performances" in data:
            performances = {
                RikId(int(rid)): cls._deserialise_performance(perf_data)
                for rid, perf_data in data["performances"].items()
            }
        
        return Summary(daily_results, performances)

    @classmethod
    def _serialise_basho_state(cls, state: BashoState) -> Dict:
        """Convert BashoState object to dictionary"""
        return {
            "banzuke": cls._serialise_banzuke(state.banzuke),
            "summary": cls._serialise_summary(state.summary)
        }

    @classmethod
    def deserialise_basho_state(cls, data: Dict) -> BashoState:
        """Convert dictionary back to BashoState object"""
        return BashoState(
            banzuke=cls._deserialise_banzuke(data["banzuke"]),
            summary=cls._deserialise_summary(data["summary"])
        )

    @classmethod
    def _serialise_banzuke(cls, banzuke: Banzuke) -> Dict:
        """Convert Banzuke object to dictionary"""
        return {
            "riks": cls._serialise_riks(banzuke.riks),
            "rikchii": cls._serialise_rikchii(banzuke.rikchii),
            "rikshik": cls._serialise_rikshik(banzuke.rikshik)
        }

    @classmethod
    def _deserialise_banzuke(cls, data: Dict) -> Banzuke:
        """Convert dictionary back to Banzuke object"""
        return Banzuke(
            riks=cls._deserialise_riks(data["riks"]),
            rikchii=cls._deserialise_rikchii(data["rikchii"]),
            rikshik=cls._deserialise_rikshik(data["rikshik"])
        )

    @classmethod
    def _serialise_history(cls, h: History) -> Dict:
        """Convert History object to dictionary"""
        return {
            str(date): cls._serialise_basho_state(bs)
            for date, bs in h.items()
        }

    @classmethod
    def deserialise_history(cls, data: Dict) -> History:
        """Convert dictionary back to History object"""
        result = History()
        for date_str, bs_data in data.items():
            year_str, month_str = date_str[:4], date_str[5:]
            date = Date(Year(int(year_str)), Month(int(month_str)))
            result[date] = cls.deserialise_basho_state(bs_data)
        return result


def save_bashostate(bashostate: BashoState, filename: str) -> None:
    """Save bashostate to a compressed JSON file"""
    serialised = SumoSerialiser._serialise_basho_state(bashostate)
    SumoSerialiser.save_to_zip(serialised, filename)

def load_bashostate(filename: str) -> BashoState:
    """Load bashostate from a compressed ZIP file"""
    data = SumoSerialiser.load_from_zip(filename)
    return SumoSerialiser.deserialise_basho_state(data)

def save_history(h: History, filename: str) -> None:
    """Save history to a compressed JSON file"""
    serialised = SumoSerialiser._serialise_history(h)
    SumoSerialiser.save_to_zip(serialised, filename)

def load_history(filename: str) -> History:
    """Load history from a compressed ZIP file"""
    data = SumoSerialiser.load_from_zip(filename)
    return SumoSerialiser.deserialise_history(data)
