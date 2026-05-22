# fsm/FSM_yokozuna_fsm.py (MODIFIED)

from .FSM_sanyaku_base_fsm import SanyakuBaseFSM # <-- Inherit from the new base
from .FSM_data_classes import Token, AR_Token
from ..parser2_IntDate import IntDate as Date

class YokozunaFSM(SanyakuBaseFSM): # <-- Class name was already good
    """FSM for parsing the unique Yokozuna rank."""
    
    def __init__(self, date: Date, sorted_margin_data: list, dups: dict):
        super().__init__(date, sorted_margin_data, dups)
        # This init is now clear and has a single purpose: set the rank to 'Y'.
        self.context['sanyaku_rank'] = 'Y'
