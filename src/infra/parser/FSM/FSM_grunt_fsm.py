# FSM/FSM_grunt_fsm.py
from pdb import set_trace
import re
from .FSM_base_fsm import BaseFSM
from .FSM_data_classes import *
from .FSM_exceptions import *
from sumo_core.Chii import Chii
from ..parser2_IntDate import IntDate as Date

class GruntFSM(BaseFSM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context['last_rank_division'] = None
        self.context['last_rank_number'] = None
        
    GRUNT_PAT = re.compile(r'^(M|J|Ms|Sd|Jd|Jk)(\d+)$')
    ANN_PAT = re.compile(r'^(TD|HD|OB)$')

    def _classify_token(self, banzuke_row: BanzukeRow) -> Token:
        rank_str = banzuke_row.rank_string
        grunt_match = self.GRUNT_PAT.fullmatch(rank_str)
        if grunt_match:
            division, number_str = grunt_match.groups()
            number = int(number_str)
            if number == self.context.get('last_rank_number'): return GA_Token(banzuke_row)
            return GR_Token(banzuke_row, division, number)
        if self.ANN_PAT.fullmatch(rank_str): return AR_Token(banzuke_row, rank_str)
        raise UnclassifiableRowError(f"GruntFSM cannot classify: '{rank_str}'")

    def _get_next_state(self, token: Token) -> int:
        transitions = { 0: {GR_Token: 1}, 1: {GR_Token: 1, AR_Token: 2, GA_Token: 5}, 2: {GR_Token: 1, AR_Token: 3}, 3: {GR_Token: 1, AR_Token: 3}, 5: {GR_Token: 1} }
        return transitions.get(self.state_id, {}).get(type(token), 4)

    def _execute_transition_action(self, old_state: int, next_state: int, token: Token):
        #if token.banzuke_row.east.id == 6908 and token.banzuke_row.west.id == 6907:
        #set_trace()
        if (old_state, next_state) == (1, 5):
            self._action_defer_ga_data(token)
        elif (old_state, next_state) == (5, 1):
            self._action_resolve_ga_and_process_gr(token)
        elif isinstance(token, GR_Token):
            self._action_process_standard_row(token)
        elif isinstance(token, AR_Token):
            self._action_process_annotation_row(token)

    def _end_of_stream_action(self):
        if self.context['deferred_ga_data']:
            print(f"INFO ({self.date}): Resolving deferred GA data at end of stream.")
            self._resolve_deferred_ga_as_hd()
            self.context['deferred_ga_data'] = None

    def _action_process_standard_row(self, token: GR_Token):
        self.context['last_rank_division'], self.context['last_rank_number'] = token.division, token.number
        if token.banzuke_row.east:
            rid, entry = self._reconcile_and_create_entry(token.banzuke_row.east, Chii.from_str(f"{token.division}{token.number}e"))
            self.output[rid] = entry
        if token.banzuke_row.west:
            rid, entry = self._reconcile_and_create_entry(token.banzuke_row.west, Chii.from_str(f"{token.division}{token.number}w"))
            self.output[rid] = entry

    def _action_process_annotation_row(self, token: AR_Token):
        # --- START SPECIAL CASE KLUDGE for 1978/03 Tsukedashi Anomaly ---
        if self.date == Date(1978, 3) and token.annotation == "TD":
            # This anomaly affects two specific rikishi on consecutive rows.
            # We handle them here and exit before the FSM's flawed logic runs.
            rikishi_data = token.banzuke_row.east

            if rikishi_data and rikishi_data.id == 1379: # Nagaoka
                print(f"WARNING ({self.date}): Applying kludge for Nagaoka (1379). Overriding inferred Ms59eTD with Ms60e.")
                corrected_foo = Chii.from_str("Ms60e")
                rid, entry = self._reconcile_and_create_entry(rikishi_data, corrected_foo)
                self.output[rid] = entry
                return # CRUCIAL: Exit before normal logic can run.

            if rikishi_data and rikishi_data.id == 7889: # Makino
                print(f"WARNING ({self.date}): Applying kludge for Makino (1380). Overriding inferred Ms59eTD with Ms60w.")
                corrected_foo = Chii.from_str("Ms60w")
                rid, entry = self._reconcile_and_create_entry(rikishi_data, corrected_foo)
                self.output[rid] = entry
                return # CRUCIAL: Exit before normal logic can run.
        # --- END SPECIAL CASE ---

        div, num = self.context['last_rank_division'], self.context['last_rank_number']
        if token.banzuke_row.east:
            rid, entry = self._reconcile_and_create_entry(token.banzuke_row.east, Chii.from_str(f"{div}{num}e{token.annotation}"))
            self.output[rid] = entry
        if token.banzuke_row.west:
            rid, entry = self._reconcile_and_create_entry(token.banzuke_row.west, Chii.from_str(f"{div}{num}w{token.annotation}"))
            self.output[rid] = entry

    def _action_defer_ga_data(self, token: GA_Token):
        if self.context['deferred_ga_data']: raise BanzukeParsingError("Encountered GA_Token while another was deferred.")
        self.context['deferred_ga_data'] = { "division": self.context['last_rank_division'], "number": self.context['last_rank_number'], "row": token.banzuke_row }

    def _action_resolve_ga_and_process_gr(self, token: GR_Token):
        self._resolve_deferred_ga_as_hd()
        self.context['deferred_ga_data'] = None
        self._action_process_standard_row(token)
