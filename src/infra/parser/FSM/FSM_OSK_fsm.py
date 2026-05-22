# fsm/FSM_OSK_fsm.py

from .FSM_sanyaku_base_fsm import SanyakuBaseFSM # <-- Inherit from the new base
from .FSM_data_classes import Token, AR_Token
from ..parser2_IntDate import IntDate as Date

class OSK_FSM(SanyakuBaseFSM): # <-- Renamed class
    """FSM for parsing non-Yokozuna Sanyaku ranks (O, S, K)."""
    
    def __init__(self, rank: str, date: Date, sorted_margin_data: list, dups: dict):
        super().__init__(date, sorted_margin_data, dups)
        # This init is now clear and has a single purpose
        if rank not in ['O', 'S', 'K']:
            raise ValueError(f"Invalid rank '{rank}' for OSK_FSM.")
        self.context['sanyaku_rank'] = rank
