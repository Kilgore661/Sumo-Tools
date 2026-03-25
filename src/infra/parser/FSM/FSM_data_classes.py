# FSM_data_classes.py

from dataclasses import dataclass
from typing import Optional

from sumo_core.BasicPrimitives import RikId, Shikona
from sumo_core.Chii import Chii

# --- Input/Output Data Classes ---
@dataclass(frozen=True)
class RikishiData:
    id: RikId
    shikona: Shikona

@dataclass(frozen=True)
class BanzukeRow:
    east: Optional[RikishiData]
    west: Optional[RikishiData]
    rank_string: str

@dataclass(frozen=True)
class FinalBanzukeEntry:
    chii: Chii
    shikona: Shikona

# --- Token System Classes ---
class Token: pass
@dataclass(frozen=True)
class GR_Token(Token): banzuke_row: BanzukeRow; division: str; number: int
@dataclass(frozen=True)
class SR_Token(Token): banzuke_row: BanzukeRow; rank: str
@dataclass(frozen=True)
class AR_Token(Token): banzuke_row: BanzukeRow; annotation: str
@dataclass(frozen=True)
class GA_Token(Token): banzuke_row: BanzukeRow
