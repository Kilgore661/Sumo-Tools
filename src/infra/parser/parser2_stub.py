# Was parser_body.py.
# In the context of the parser2 code, _get_banzuke is not needed and has been
# deleted but it is quite likely there is other legacy code here.
import re
from pdb import set_trace
from typing import Dict, Set, Tuple, Optional, List, Union, Literal

from ...sumo_core.BasicEnums import Prize, Direction
from ...sumo_core.Banzuke import Shikona
from ...sumo_core.Performance import Performance
from ...sumo_core.BasicPrimitives import RikId
from .parser_warning_logger import logger
from .TableTypes import TableType, BodyTable, BanzukeTables
WEIRD = 'X'

# Patterns for division tables
division_table_pat = re.compile(
    r'<table class="banzuke"[^>]*>.*?'
    r'<caption>\s*(.*?)\s*</caption>.*?'
    r'<tbody>(.*?)</tbody>.*?</table>',
    re.DOTALL
)
row_pat = re.compile(
    r'<tr(?:\s+class="([^"]*)")?\s*>(.*?)</tr>',
    re.DOTALL
)

# Post-2025 fix
# changed
#   (?:nowrap="nowrap")
# to
#   (?:nowrap="nowrap"|style="white-space:nowrap;|style="border-color:Red;")
# 
# The new format of the nowrap is used in the main division and Mz cells. The
# red border is for Mz (and other?) cells.
#
# May not need the old nowrap syntax?
cell_pat = re.compile(
    r'<td(?:\s+class="([^"]*)")?\s*(?:nowrap="nowrap"|style="white-space:nowrap;"|style="border-color:Red;")?\s*(?:colspan="(\d+)")?\s*>(.*?)</td>',
    re.DOTALL
)
rikishi_pat = re.compile(
    r'<a title=\'([^\']*)\' href=\'Rikishi\.aspx\?r=(\d+)\'>([^<]+)</a>',
    re.DOTALL
)
result_pat = re.compile(r'''
    # Match the opening of the link to the rikishi's basho results
    <a\ href='Rikishi_basho\.aspx\?r=\d+&b=\d+'>
    
    # Group 1: Capture the score (e.g., "14-1" or "9-6"). The .*? is to
    # deal with old draw crap (a = abandoned, d = draw?) which can appear
    # after the w-l as w-l-1[ad] or w-l-x-1[ad]
    (\d+-\d+(?:.*?))
    
    # Group 2: Capture any prize code that follows the score
    # This handles cases like "14-1 Y" where Y is inside the link
    (?:\s+([A-Z]+))?
    
    # Close the link tag
    </a>
    
    # Group 3: Capture the direction arrow (or whatever) in font tag
    # This handles cases with arrows after the link like "<font>↑</font>"
    (?:\s*<font[^>]*>(.+)</font>)?
''', re.VERBOSE | re.DOTALL)


def _parse_mae_zumo_section( section_content):
    """
    Parse Mae-zumo section with its specific two-column format.
    Returns a list of rikishi in this section.
    """
    rikishi_list = []
    
    # Find all rows
    rows = row_pat.findall(section_content)
    
    for row_class, row_content in rows:
        # Extract cells
        cells = []
        remaining = row_content
        
        while remaining:
            cell_match = cell_pat.search(remaining)
            if not cell_match:
                break
                
            cell_class, colspan, content = cell_match.groups()
            cells.append((cell_class, colspan, content))
            remaining = remaining[cell_match.end():]
        
        # Mae-zumo rows should have two cells
        if len(cells) == 2:
            rikishi_cell_class, _, rikishi_content = cells[0]
            result_cell_class, _, result_content = cells[1]
            
            # Extract rikishi information
            rikishi_match = rikishi_pat.search(rikishi_content)
            if rikishi_match:
                bio, rik_id, name = rikishi_match.groups()
                set_trace()
                
                # Extract result and check for promotion
                result = _extract_result(result_content)
                promotion = '↑' in result_content
                
                #set_trace()
                rikishi_record = {
                    'id': RikId(int(rik_id)),
                    'name': name,
                    'bio': bio,
                    'status': 'Mae-zumo',
                    'rank': None,
                    'rank_side': None,
                    'promotion': promotion,
                    'result': result
                }
                rikishi_list.append(rikishi_record)
        else:
            set_trace()
            print(f"Unexpected structure in Mae-zumo row: {len(cells)} cells found")
    
    return rikishi_list

def _parse_banzuke_gai_section( section_content):
    """
    Parse Banzuke-gai section with single-column format.
    Returns a list of rikishi in this section.
    """
    rikishi_list = []
    
    # Find all rows
    rows = row_pat.findall(section_content)
    
    for row_class, row_content in rows:
        # Extract cells
        cells = []
        remaining = row_content
        
        while remaining:
            cell_match = cell_pat.search(remaining)
            if not cell_match:
                break
                
            cell_class, colspan, content = cell_match.groups()
            cells.append((cell_class, colspan, content))
            remaining = remaining[cell_match.end():]
        
        # Banzuke-gai has a single column format
        if len(cells) == 1:
            cell_class, _, rikishi_content = cells[0]
            
            rikishi_match = rikishi_pat.search(rikishi_content)
            if rikishi_match:
                bio, rik_id, name = rikishi_match.groups()
                
                # Check if retired (cell class will be "retired" in newer formats)
                is_retired = cell_class == "retired"
                
                #set_trace()
                rikishi_record = {
                    'id': RikId(int(rik_id)),
                    'name': name,
                    'bio': bio,
                    'status': 'Banzuke-gai',
                    'is_retired': is_retired
                }
                rikishi_list.append(rikishi_record)
        else:
            print(f"Unexpected structure in Banzuke-gai row: {len(cells)} cells found")
    
    return rikishi_list

def _parse_shikona_changes_section( section_content):
    """
    Parse Shikona Changes section with three-column format.
    Returns a list of name changes.
    """
    changes_list = []
    
    # Find all rows
    rows = row_pat.findall(section_content)
    
    for row_class, row_content in rows:
        # Extract cells
        cells = []
        remaining = row_content
        
        while remaining:
            cell_match = cell_pat.search(remaining)
            if not cell_match:
                break
                
            cell_class, colspan, content = cell_match.groups()
            cells.append((cell_class, colspan, content))
            remaining = remaining[cell_match.end():]
        
        # Shikona Changes has three columns
        if len(cells) == 3:
            rank = cells[0][2]
            new_shikona_cell = cells[1]
            old_shikona = cells[2][2]
            
            # Extract rikishi information from middle cell
            _, _, new_shikona_content = new_shikona_cell
            rikishi_match = rikishi_pat.search(new_shikona_content)
            
            if rikishi_match:
                bio, rik_id, name = rikishi_match.groups()
                
                #set_trace()
                change_record = {
                    'id': RikId(int(rik_id)),
                    'new_shikona': name,
                    'old_shikona': old_shikona,
                    'rank': rank,
                    'bio': bio
                }
                changes_list.append(change_record)
        else:
            print(f"Unexpected structure in Shikona Changes row: {len(cells)} cells found")
    
    return changes_list

def _parse_shin_deshi_section( section_content):
    """
    Parse Shin-Deshi section with four-column format.
    Returns a list of new rikishi entries.
    """
    new_rikishi_list = []
    
    # Find all rows
    rows = row_pat.findall(section_content)
    
    for row_class, row_content in rows:
        # Extract cells
        cells = []
        remaining = row_content
        
        while remaining:
            cell_match = cell_pat.search(remaining)
            if not cell_match:
                break
                
            cell_class, colspan, content = cell_match.groups()
            cells.append((cell_class, colspan, content))
            remaining = remaining[cell_match.end():]
        
        # Shin-Deshi has four columns
        if len(cells) == 4:
            shikona_cell = cells[0]
            heya = cells[1][2].strip() if cells[1][2] != '-' else None
            shusshin = cells[2][2].strip() if cells[2][2] != '-' else None
            birth_date = cells[3][2].strip() if cells[3][2] else None
            
            # Extract rikishi information from first cell
            _, _, shikona_content = shikona_cell
            rikishi_match = rikishi_pat.search(shikona_content)
            
            if rikishi_match:
                bio, rik_id, name = rikishi_match.groups()
                
                #set_trace()
                new_rikishi_record = {
                    'id': RikId(int(rik_id)),
                    'name': name,
                    'bio': bio,
                    'heya': heya,
                    'shusshin': shusshin,
                    'birth_date': birth_date
                }
                new_rikishi_list.append(new_rikishi_record)
        else:
            print(f"Unexpected structure in Shin-Deshi row: {len(cells)} cells found")
    
    return new_rikishi_list

def _parse_retired_rikishi_section( section_content):
    """
    Parse Retired Rikishi section with six-column format.
    Returns a list of retired rikishi entries.
    """
    retired_rikishi_list = []
    
    # Find all rows
    rows = row_pat.findall(section_content)
    
    for row_class, row_content in rows:
        # Extract cells
        cells = []
        remaining = row_content
        
        while remaining:
            cell_match = cell_pat.search(remaining)
            if not cell_match:
                break
                
            cell_class, colspan, content = cell_match.groups()
            cells.append((cell_class, colspan, content))
            remaining = remaining[cell_match.end():]
        
        # Retired Rikishi has six columns
        if len(cells) == 6:
            final_rank = cells[0][2].strip()
            shikona_cell = cells[1]
            heya = cells[2][2].strip() if cells[2][2] != '-' else None
            shusshin = cells[3][2].strip() if cells[3][2] != '-' else None
            birth_date = cells[4][2].strip() if cells[4][2] else None
            highest_rank = cells[5][2].strip() if cells[5][2] else None
            
            # Extract rikishi information from second cell
            _, _, shikona_content = shikona_cell
            rikishi_match = rikishi_pat.search(shikona_content)
            
            if rikishi_match:
                bio, rik_id, name = rikishi_match.groups()
                
                #set_trace()
                retired_rikishi_record = {
                    'id': RikId(int(rik_id)),
                    'name': name,
                    'bio': bio,
                    'final_rank': final_rank,
                    'heya': heya,
                    'shusshin': shusshin,
                    'birth_date': birth_date,
                    'highest_rank': highest_rank
                }
                retired_rikishi_list.append(retired_rikishi_record)
        else:
            print(f"Unexpected structure in Retired Rikishi row: {len(cells)} cells found")
    
    return retired_rikishi_list

def parse_body(year,month,text):
    """
    Parse the body content containing multiple division tables.
    Returns a structured representation of all tables organized by table type.
    """
    result = {
        TableType.DIVISION: {}
    }
    
    # Find all division tables
    division_tables = division_table_pat.findall(text)
    
    for division_caption, table_content in division_tables:
        # Extract division name (e.g., "Makuuchi Banzuke" -> "Makuuchi")
        division_name = division_caption.replace(" Banzuke", "").strip()
        
        if division_name == "Banzuke-gai":
            rikishi_list = _parse_banzuke_gai_section(table_content)
            table = BodyTable(TableType.BANZUKE_GAI, division_name, rikishi_list)
            result[TableType.BANZUKE_GAI] = table
            
        elif "Banzuke" in division_caption:
            rikishi_list = _parse_division_rows(year, month, table_content)
            table = BodyTable(TableType.DIVISION, division_name, rikishi_list)
            result[TableType.DIVISION][division_name] = table
            
        elif division_name == "Mae-zumo":
            rikishi_list = _parse_mae_zumo_section(table_content)
            table = BodyTable(TableType.MAE_ZUMO, division_name, rikishi_list)
            result[TableType.MAE_ZUMO] = table
            
        elif division_name == "Shikona Changes":
            changes_list = _parse_shikona_changes_section(table_content)
            table = BodyTable(TableType.SHIKONA_CHANGES, division_name, changes_list)
            result[TableType.SHIKONA_CHANGES] = table
            
        elif division_name == "Shin-Deshi":
            new_rikishi_list = _parse_shin_deshi_section(table_content)
            table = BodyTable(TableType.SHIN_DESHI, division_name, new_rikishi_list)
            result[TableType.SHIN_DESHI] = table
            
        elif division_name == "Retired Rikishi":
            retired_rikishi_list = _parse_retired_rikishi_section(table_content)
            table = BodyTable(TableType.RETIRED, division_name, retired_rikishi_list)
            result[TableType.RETIRED] = table
            
        elif division_name == "Shinjo":
            # Formal presentation of new sekitori
            pass
        else:
            # For unrecognized sections, create empty table in DIVISION
            print( year, month, f'{year}/{month:02d}: Unexpected division "{division_name}"' )
            table = BodyTable(TableType.DIVISION, division_name, [])
            result[TableType.DIVISION][division_name] = table
        
    
    return BanzukeTables( result )

def _parse_division_rows( year, month, table_content):
    """
    Parse all rows within a division table.
    Extracts rikishi information and handles special row formats.
    """
    rikishi_list = []
    
    # Find all rows
    rows = row_pat.findall(table_content)
    
    last_chii = None
    for row_class, row_content in rows:
        # Extract cells
        cells = []
        remaining = row_content
        
        while remaining:
            cell_match = cell_pat.search(remaining)
            if not cell_match:
                break
                
            cell_class, colspan, content = cell_match.groups()
            cells.append((cell_class, colspan, content))
            remaining = remaining[cell_match.end():]
        
        # Process cells based on standard format or special cases
        if len(cells) >= 5:  # Standard row with both east and west
            chii = _process_standard_row(cells, row_class, rikishi_list, last_chii)
        elif len(cells) >= 3:  # Row with only east or west rikishi
            chii = _process_partial_row(cells, row_class, rikishi_list, last_chii)
        else:
            set_trace()
        last_chii = chii
    
    return rikishi_list

def _process_standard_row( cells, row_class, rikishi_list, last_chii):
    """Process a standard row with both east and west rikishi."""
    e_result_class, e_result_colspan, e_result_content = cells[0]
    e_rikishi_class, e_rikishi_colspan, e_rikishi_content = cells[1]
    rank_class, rank_colspan, rank_content = cells[2]
    w_rikishi_class, w_rikishi_colspan, w_rikishi_content = cells[3]
    w_result_class, w_result_colspan, w_result_content = cells[4]
    #if rank_content == last_chii:
        #set_trace()
        #rank_content == WEIRD
    
    # Extract and process data for east rikishi
    e_rikishi_match = rikishi_pat.search(e_rikishi_content)
    if e_rikishi_match:
        e_bio, e_id, e_name = e_rikishi_match.groups()
        x = _extract_result(e_result_content)
        if x is None:
            set_trace()
        e_result, e_special = _extract_result(e_result_content)
        
        #set_trace()
        e_record = {
            'id': RikId(int(e_id)),
            'name': e_name,
            'bio': e_bio,
            'rank': rank_content,
            'rank_side': 'e',
            'row_class': row_class,
            'cell_class': e_rikishi_class,
            'result': e_result,
            'special': e_special
        }
        rikishi_list.append(e_record)
    
    # Extract and process data for west rikishi
    w_rikishi_match = rikishi_pat.search(w_rikishi_content)
    if w_rikishi_match:
        w_bio, w_id, w_name = w_rikishi_match.groups()
        if _extract_result(w_result_content) is None:
            c=1
        w_result, w_special = _extract_result(w_result_content)
        
        #set_trace()
        w_record = {
            'id': RikId(int(w_id)),
            'name': w_name,
            'bio': w_bio,
            'rank': rank_content,
            'rank_side': 'w',
            'row_class': row_class,
            'cell_class': w_rikishi_class,
            'result': w_result,
            'special': w_special
        }
        rikishi_list.append(w_record)
    return rank_content

def _process_partial_row( cells, row_class, rikishi_list, last_chii):
    """Process a row with only east or west rikishi."""
    # Determine if east or west is present based on emptycell
    is_east_empty = False
    
    # Check if any cell is emptycell with colspan
    for cell_class, colspan, _ in cells:
        if cell_class == 'emptycell' and colspan:
            # If first cell is emptycell, east is empty
            if cells[0][0] == 'emptycell':
                is_east_empty = True
            break
    
    if is_east_empty:
        # Find rank cell
        rank_idx = 0
        for i, (cell_class, _, _) in enumerate(cells):
            if cell_class == 'short_rank':
                rank_idx = i
                break
        
        if rank_idx > 0 and rank_idx + 1 < len(cells):
            rank_class, rank_colspan, rank_content = cells[rank_idx]
            #if rank_content == last_chii:
                #set_trace()
                #rank_content = WEIRD
            w_rikishi_class, w_rikishi_colspan, w_rikishi_content = cells[rank_idx + 1]
            
            # Get result if available
            w_result = None
            if rank_idx + 2 < len(cells):
                w_result, w_special = _extract_result(cells[rank_idx + 2][2])
            
            w_rikishi_match = rikishi_pat.search(w_rikishi_content)
            if w_rikishi_match:
                w_bio, w_id, w_name = w_rikishi_match.groups()
                
                #set_trace()
                w_record = {
                    'id': RikId(int(w_id)),
                    'name': w_name,
                    'bio': w_bio,
                    'rank': rank_content,
                    'rank_side': 'w',
                    'row_class': row_class,
                    'cell_class': w_rikishi_class,
                    'result': w_result,
                    'special': w_special
                }
                rikishi_list.append(None)
                rikishi_list.append(w_record)
    else:
        # East rikishi present, west empty
        if len(cells) >= 3:
            e_result_class, e_result_colspan, e_result_content = cells[0]
            e_rikishi_class, e_rikishi_colspan, e_rikishi_content = cells[1]
            rank_class, rank_colspan, rank_content = cells[2]
            #if len( rank_content ) == 1:
                #rank_content += '1'
            #if rank_content == last_chii:
                #set_trace()
                #rank_content = WEIRD
            
            e_rikishi_match = rikishi_pat.search(e_rikishi_content)
            if e_rikishi_match:
                e_bio, e_id, e_name = e_rikishi_match.groups()
                e_result, e_special = _extract_result(e_result_content)
                
                #set_trace()
                e_record = {
                    'id': RikId(int(e_id)),
                    'name': e_name,
                    'bio': e_bio,
                    'rank': rank_content,
                    'rank_side': 'e',
                    'row_class': row_class,
                    'cell_class': e_rikishi_class,
                    'result': e_result,
                    'special': e_special
                }
                rikishi_list.append(e_record)
                rikishi_list.append(None)
    return rank_content

def _extract_result( result_content):
    """Extract structured result information from result cell content."""
    result_match = result_pat.search(result_content)
    if result_match:
        result_text = result_match.group(1).strip()  # Score like "14-1"
        prize_code = result_match.group(2)          # Prize code (if any)
        direction_symbol = result_match.group(3)    # Direction symbol (if any)
        
        # Create empty frozenset for prizes by default
        prizes = frozenset()
        direct = None
        
        # If prize code exists, convert to Prize enum
        if prize_code:
            prizes = frozenset([Prize.abbr_to_prize()[p] for p in prize_code])
        
        # If direction symbol exists, convert to Direction enum
        if direction_symbol:
            # For direction symbols like ↑ or ↓
            if direction_symbol in Direction.abbr_to_direction():
                direct = Direction.abbr_to_direction()[direction_symbol]
        
        # Return Performance object if we have either prizes or a direction
        if prizes or direct is not None:
            return result_text, Performance(prizes, direct)
        else:
            return result_text, None

