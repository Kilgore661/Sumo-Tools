# parser2_body_adapter.py
from typing import Dict, List, Optional

# --- Assume these are imported from their proper locations ---
# The legacy data structure from parser_body
from .TableTypes import BanzukeTables, TableType
# The new, structured data classes for the FSM
from .FSM import BanzukeRow, RikishiData
# The core data types
from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Banzuke import Shikona
from .parser2_IntDate import IntDate as Date

def _create_rikishi_data(rikishi_dict: Optional[Dict]) -> Optional[RikishiData]:
    """
    Helper function to convert a dictionary from the legacy parser into a
    structured RikishiData object. Returns None if the input is None.
    """
    if not rikishi_dict:
        return None
    
    return RikishiData(
        id=RikId(rikishi_dict['id']),
        shikona=Shikona(rikishi_dict['name'])
    )

def adapt_body_data_for_fsm(date: Date, body_data: BanzukeTables) -> Dict[str, List[BanzukeRow]]:
    """
    Adapts the output of the legacy `parse_body` function to the structured
    input required by the new FSM.

    It takes the BanzukeTables object, which contains flat lists of rikishi 
    dictionaries for each division, and transforms them into lists of 
    `BanzukeRow` objects, where each object represents a logical pair of 
    East and West rikishi.

    Args:
        body_data: The BanzukeTables object returned by `parse_body`.

    Returns:
        A dictionary mapping division names (e.g., "Makuuchi", "Juryo") to 
        a list of `BanzukeRow` objects for that division, ready for 
        consumption by the FSM orchestrator.
    """
    adapted_data: Dict[str, List[BanzukeRow]] = {}

    # Ensure the DIVISION table type exists before proceeding
    if TableType.DIVISION not in body_data.tables:
        return adapted_data

    # Iterate through each division table parsed by the legacy function
    for division_name, division_table in body_data.tables[TableType.DIVISION].items():
        adapted_rows: List[BanzukeRow] = []
        rikishi_list: List[Dict] = division_table.rikishi_list

        # The legacy parser produces a flat list: [East1, West1, East2, West2, ...].
        # Some entries can be `None` if a side is empty.
        # This `zip` operation correctly pairs them into logical rows,
        # formalizing the trusted logic from the old reconciler.
        logical_rows = zip(rikishi_list[0::2], rikishi_list[1::2])

        for east_dict, west_dict in logical_rows:
            # At least one of the pair must exist to form a row.
            if not east_dict and not west_dict:
                continue

            # Convert the raw dictionaries into our structured RikishiData classes.
            east_data = _create_rikishi_data(east_dict)
            west_data = _create_rikishi_data(west_dict)
            
            # The rank string is the same for both sides of a logical row.
            # We take it from whichever rikishi dictionary is not None.
            rank_string = (east_dict or west_dict)['rank']

            # Sanitize known body data anomalies here
            if date.year == 1965 and date.month == 11 and rank_string == 'Jk0':
                 rank_string = 'Jk1'

            # Create the final, structured BanzukeRow object for the FSM.
            adapted_rows.append(
                BanzukeRow(
                    east=east_data,
                    west=west_data,
                    rank_string=rank_string
                )
            )
        
        adapted_data[division_name] = adapted_rows

    return adapted_data

def _extract_performance(body_data):
    """
    Extract merits from the parsed banzuke tables.

    A hack. Merits should be passed back up (see _extract_result) but that
    would mean hunting down every use of Summary() and changing how it
    used.
    
    Args:
        body_data: BanzukeTables object containing the parsed banzuke tables
        
    Returns:
        Dict[RikId, str]: Dictionary mapping rikishi IDs to their special prizes
    """
    special_prizes = {}
    
    # Process each division table
    for division_name, division_table in body_data.tables[TableType.DIVISION].items():
        # Iterate through all rikishi in the division
        for rikishi in division_table.rikishi_list:
            # Skip None entries (empty slots)
            if rikishi is None:
                continue
                
            # Check if rikishi has a special prize
            if 'special' in rikishi and rikishi['special']:
                rid = rikishi['id']
                special_prizes[rid] = rikishi['special']
    
    return special_prizes
