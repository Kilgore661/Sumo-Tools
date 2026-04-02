# parser2_body.py
# parser2_body.py (Modified)

from pdb import set_trace
import sys
from typing import Dict, List, Tuple

from .parser2_stub import parse_body
from .parser2_body_adapter import adapt_body_data_for_fsm
from .FSM import (
    GruntFSM, OSK_FSM, YokozunaFSM, FinalBanzukeEntry
)

from .parser2_IntDate import IntDate as Date
from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.BasicEnums import Division, MSD, Outcome
from ...sumo_core.Performance import Performance
from .parser2_body_adapter import _extract_performance

FSM_CONFIG = {
    # No changes to FSM_CONFIG
    'Y':  {'fsm': YokozunaFSM, 'args': [], 'level': MSD.YOKOZUNA},
    'O':  {'fsm': OSK_FSM,  'args': ['O'], 'level': MSD.OZEKI},
    'S':  {'fsm': OSK_FSM,  'args': ['S'], 'level': MSD.SEKIWAKE},
    'K':  {'fsm': OSK_FSM,  'args': ['K'], 'level': MSD.KOMUSUBI},
    'M':  {'fsm': GruntFSM,    'args': [], 'level': MSD.MAEGASHIRA},
    'J':  {'fsm': GruntFSM,    'args': [], 'level': Division.JURYO},
    'Ms': {'fsm': GruntFSM,    'args': [], 'level': Division.MAKUSHITA},
    'Sd': {'fsm': GruntFSM,    'args': [], 'level': Division.SANDANME},
    'Jd': {'fsm': GruntFSM,    'args': [], 'level': Division.JONIDAN},
    'Jk': {'fsm': GruntFSM,    'args': [], 'level': Division.JONOKUCHI},
}

# The division names from the legacy parser
MAKUUCHI_DIV_NAME = "Makuuchi"
DIVISION_RANK_MAP = {
    "Juryo": "J", "Makushita": "Ms", "Sandanme": "Sd", 
    "Jonidan": "Jd", "Jonokuchi": "Jk"
}
MAKUUCHI_RANKS = ['Y', 'O', 'S', 'K', 'M']

def parse_and_validate_body(
    date: Date, 
    sorted_margin_data: List[tuple[RikId, Chii]], 
    dups: Dict, 
    raw_html_text: str
) -> Tuple[Dict[RikId, FinalBanzukeEntry], Dict[RikId, Performance]]:

    body_data = parse_body(date.year, date.month, raw_html_text)
    special_prizes_dict = _extract_performance(body_data)

    adapted_body_data = adapt_body_data_for_fsm(date, body_data)

    final_banzuke_data = {}
    
    # --- Sequential Makuuchi Processing ---
    makuuchi_body_rows = adapted_body_data.get(MAKUUCHI_DIV_NAME, [])
    body_cursor = 0
    margin_cursor = 0

    for rank_abbr in MAKUUCHI_RANKS:
        config = FSM_CONFIG[rank_abbr]
        fsm_class = config['fsm']
        level_to_match = config['level']

        # Slice the margin data for this specific Makuuchi rank
        start_margin_idx = margin_cursor
        while (margin_cursor < len(sorted_margin_data) and 
               sorted_margin_data[margin_cursor][1].level == level_to_match):
            margin_cursor += 1
        fsm_margin_slice = sorted_margin_data[start_margin_idx:margin_cursor]

        # Get the remaining body rows for the FSM to consume
        fsm_body_stream = makuuchi_body_rows[body_cursor:]

        if not fsm_body_stream and not fsm_margin_slice:
            continue

        try:
            fsm = fsm_class(*config['args'], date=date, sorted_margin_data=fsm_margin_slice, dups=dups)
            fsm.run(fsm_body_stream)
            final_banzuke_data.update(fsm.output)
            # Advance the cursor by the number of rows the FSM consumed
            body_cursor += fsm.rows_processed
        except Exception as e:
            print(f"\nFSM failed for {date} in Makuuchi rank group {rank_abbr}: {e}", file=sys.stderr)
            #set_trace()
            return None

    # --- Standard Processing for Lower Divisions ---
    for division_name, rank_abbr in DIVISION_RANK_MAP.items():
        if division_name not in adapted_body_data:
            continue

        
        config = FSM_CONFIG[rank_abbr]
        fsm_class = config['fsm']
        level_to_match = config['level']

        # Slice margin data for this division
        start_margin_idx = margin_cursor
        while (margin_cursor < len(sorted_margin_data) and 
               sorted_margin_data[margin_cursor][1].level == level_to_match):
            margin_cursor += 1
        fsm_margin_slice = sorted_margin_data[start_margin_idx:margin_cursor]
        #if division_name == "Makushita":
            #set_trace()
            #pass # A no-op line for the debugger to stop on


        fsm_body_stream = adapted_body_data[division_name]

        try:
            fsm = fsm_class(*config['args'], date=date, sorted_margin_data=fsm_margin_slice, dups=dups)
            #if date == Date( 1959, 5 ) and division_name == 'Makushita':
                #set_trace()
            fsm.run(fsm_body_stream)
            final_banzuke_data.update(fsm.output)
        except Exception as e:
            print(f"\nFSM failed for {date} in division {division_name}: {e}", file=sys.stderr)
            #set_trace()
            return None

    return final_banzuke_data, special_prizes_dict, body_data
