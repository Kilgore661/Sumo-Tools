import re
from typing import Dict, List, Tuple
from .FSM import FinalBanzukeEntry # For type hinting
from .TableTypes import TableType, BodyTable, BanzukeTables
from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Banzuke import Shikona
from ...sumo_core.BasicPrimitives import Day

FULL_CHII_PAT = re.compile(r'(([MKSOYJ]|Ms|Sd|Jd|Jk)(\d+)(OB|TD|((e|w)(HD|YO|OB)?)))')
RESULTS_DIR='files/output/HTML results'

def adapt_banzuke_for_daily_parser(
    validated_data: Dict[RikId, FinalBanzukeEntry],
    body_data: BanzukeTables
) -> Dict:
    """
    Serves as a critical compatibility layer between the modern, FSM-based
    banzuke parser and the legacy, trusted daily results parser.
    """

    # --- The Core Problem: Why this Adapter is Necessary ---
    #
    # The new parser's main orchestrator (`parser2.py`) produces a clean, validated
    # banzuke structure: a Dict[RikId, FinalBanzukeEntry], where each entry
    # contains a modern `Chii` rank object.
    #
    # However, the legacy daily results parser (`_parse_daily_results` in
    # `parser_daily.py`) expects a different, legacy data structure as its input:
    # a "Rikishi Context Dictionary". This function's sole purpose is to translate
    # the modern structure into this exact legacy format, allowing us to reuse
    # the trusted and stable `_parse_daily_results` function without any
    # modification.
    #
    # --- The "Mixed-Type Anomaly" Explained ---
    #
    # A key, and seemingly incorrect, feature of this function's output is its
    # use of mixed types for the 'chii' key in the returned dictionary:
    #   - For a ranked rikishi, the value is a `Chii` object.
    #  - For an unranked Mae-zumo rikishi, the value is the literal string 'Mz'.
    #
    # This is a logical error because the old parser's "if data['chii'] == 'Mz'"
    # does not make sense if data['chii'] is a Chii. This does not cause a RTE
    # because in Python, "x==y" returns false when the types of x and y are
    # different. So if data['chii'] is a Chii, then the rank is not Mz, and
    # data['chii'] == 'Mz' returns False which is the desired behaviour but only
    # as an accident of Python's interpretation of eq.
    #
    # --- The Alternative Considered and Rejected (The Ordinal Conflict) ---
    #
    # An alternative, "purer" approach was considered: modifying the legacy daily
    # parser to work directly with `Chii` objects. This would involve formally
    # representing Mae-zumo ('Mz') as a new member of the `Division` enum and,
    # consequently, as its own `Chii` object.
    #
    # This path was rejected for a critical, structural reason: it breaks the
    # `Chii.ordinal()` system. The ordinal function relies on a single-digit
    # level index (0-9 for Y through Jk) to create a unique, sortable integer key.
    # Adding 'Mz' as a new Division would give it a level index of 10, a two-digit
    # number that would break the ordinal's scaling logic and cause data corruption.
    # Fixing this would require changing the fundamental scaling constants in
    # `Chii.ordinal()`, a highly invasive change to a core data structure,
    # all to accommodate an unranked rikishi type that is of low value to
    # downstream analysis.
    #
    # --- Conclusion ---
    #
    # Therefore, this adapter, while creating a temporary and architecturally
    # impure data structure, is the superior engineering choice. It prioritizes
    # stability, minimizes risk by isolating changes, and avoids disruptive
    # modifications to core components for a low-impact edge case. The dictionary
    # it produces is ephemeral, used only as a read-only lookup table by the
    # daily parser, and is discarded immediately after use. The temporary `Chii`
    # objects it contains do not persist in the final `BashoStateWithAnnotations`.
    
    legacy_context_dict = {}

    # --- Part 1: Process RANKED rikishi (unchanged) ---
    for rik_id, entry in validated_data.items():
        legacy_context_dict[rik_id] = {
            'chii':    entry.chii,
            'shik':    entry.shikona,
            'code':    entry.chii.ordinal(),
            'results': "",
            'symbols': []
        }

    # --- Part 2: Process UNRANKED Mae-zumo rikishi (NEW LOGIC) ---
    if TableType.MAE_ZUMO in body_data.tables:
        mae_zumo_list = body_data.tables[TableType.MAE_ZUMO].rikishi_list
        
        for mz_rikishi in mae_zumo_list:
            rik_id = mz_rikishi['id']
            # Replicate the legacy format precisely
            legacy_context_dict[rik_id] = {
                'chii': 'Mz',               # The literal string 'Mz'
                'shik': Shikona(mz_rikishi['name']),
                'code': 100000,             # A hardcoded large number for sorting
                'results': mz_rikishi.get('result', ('', None))[0],
                'symbols': []               # Mz rikishi have no symbols from the margin
            }

    return legacy_context_dict
