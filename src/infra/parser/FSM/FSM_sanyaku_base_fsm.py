# FSM/FSM_sanyaku_base_fsm.py
from .FSM_base_fsm import BaseFSM
from .FSM_data_classes import *
from .FSM_exceptions import *
from ....sumo_core.Chii import Chii

class SanyakuBaseFSM(BaseFSM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context['sanyaku_counter'] = 1

    def _classify_token(self, banzuke_row: BanzukeRow) -> Token:
        rank_str = banzuke_row.rank_string
        if rank_str == self.context['sanyaku_rank']:
            return SR_Token(banzuke_row, rank_str)
        if rank_str in ['HD', 'TD', 'OB', 'YO']:
            return AR_Token(banzuke_row, rank_str)
        raise UnclassifiableRowError(f"SanyakuFSM for rank {self.context['sanyaku_rank']} cannot classify: '{rank_str}'")

    def _get_next_state(self, token: Token) -> int:
        transitions = { 0: {SR_Token: 1}, 1: {SR_Token: 1, AR_Token: 2}, 2: {SR_Token: 1, AR_Token: 3}, 3: {SR_Token: 1, AR_Token: 3} }
        if self.context['sanyaku_rank'] == 'Y' and self.state_id == 0 and isinstance(token, AR_Token): return 2
        if self.context['sanyaku_rank'] in ['O', 'S', 'K'] and self.state_id == 0 and isinstance(token, AR_Token): return 4
        return transitions.get(self.state_id, {}).get(type(token), 4)

    def _execute_transition_action(self, old_state: int, next_state: int, token: Token):
        rank_str_base = f"{self.context['sanyaku_rank']}{self.context['sanyaku_counter']}"
        anno = token.annotation if isinstance(token, AR_Token) else ""
        
        if token.banzuke_row.east:
            rid, entry = self._reconcile_and_create_entry(token.banzuke_row.east, Chii.from_str(f"{rank_str_base}e{anno}"))
            self.output[rid] = entry
        if token.banzuke_row.west:
            rid, entry = self._reconcile_and_create_entry(token.banzuke_row.west, Chii.from_str(f"{rank_str_base}w{anno}"))
            self.output[rid] = entry
            
        self.context['sanyaku_counter'] += 1
    
    def _end_of_stream_action(self):
        pass # No deferred data to handle
