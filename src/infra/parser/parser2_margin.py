# parser2_margin.py
from pdb import set_trace
import os
import re
from typing import List, Tuple, Dict

# --- Core Model Dependencies ---
# These would be imported from their proper locations in the project.
from .parser2_IntDate import IntDate as Date
from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.BasicEnums import Symbol
from ...sumo_core.Chii import Chii

# --- Constants and Patterns from the trusted legacy parser ---
YUSHO_DIR = 'files/output/current standings'
DIV_PAT = re.compile(r'.*?>(\w+) Yusho Arasoi:</u></b></font>(.*)', re.DOTALL)
WIN_PAT = re.compile(r'</p>..?<p><font size=.2.><b>(\d+) wins?[^<]*</b></font><font size=.1.><br />(.*)', re.DOTALL)
RIK_PAT = re.compile(r'((\S*) <a title=.*?Rikishi.aspx\?r=(\d+).>(\S+) (\S+)</a>(<br />|</font>))(.*)', re.DOTALL)


def _parse_raw_marginalia(date: Date) -> Tuple[Dict, Dict, str]:
    """
    Parses the raw HTML file from the margin.
    This is a direct, trusted copy of the logic from the old code,
    now using a Date object for context.
    """
    b_rids = {}
    duplicates = {}
    year, month = date.year, date.month
    
    fn = os.path.join(YUSHO_DIR, f'{year} {month:02d}.html')
    
    with open(fn, 'r', encoding='utf-8') as f:
        text = f.read()

    # This is the full HTML content that will be returned for the body parser.
    full_html_text = text

    div_match = DIV_PAT.fullmatch(text)
    chiis = {}
    while div_match:
        div, text_rem = div_match.groups()
        win_match = WIN_PAT.fullmatch(text_rem)
        while win_match:
            wins, text_rem = win_match.groups()
            rik_match = RIK_PAT.fullmatch(text_rem)
            while rik_match:
                _, sym, rid_str, chii, shik, end, text_rem = rik_match.groups()
                
                # Handle specific historical data corrections
                # Fixing them here means we don't have to change the FSM logic
                # but in order to fix the issues we need contextual info from
                # the table which is not available here. This means we need to
                # defer the checkingand fixing to the FSM (and changing its
                # logic anyway).
                if year == 1965 and month == 11 and chii.startswith('Jk0'):
                    chii = chii.replace('Jk0', 'Jk1')
                #if year == 1959 and month == 5 and rid_str == '4182':
                #    # Duplicate Ms15e
                #    chii = 'Ms15eHD'
                #if year == 1962 and month == 5:
                #    if rid_str == '11053':
                #        # Duplicate Sd5e
                #        chii = 'Sd5eHD'
                #    if rid_str == '5643':
                #        # Duplicate Sd55e
                #        chii = 'Sd55eHD'
                #    if rid_str == '5632':
                #        # Duplicate Sd32e
                #        chii = 'Sd32eHD'
                #    if rid_str == '10955':
                #        # Duplicate Sd70e
                #        chii = 'Sd70eHD'
                #    if rid_str == '11402':
                #        # Duplicate Jk3w
                #        chii = 'Jk3wHD'
                #if year == 1973 and month == 1 and rid_str == '5087':
                #    # Duplicate Jk7e
                #    chii = 'Jk7eHD'
                
                rid_obj = RikId(int(rid_str))
                b_rids[rid_obj] = {
                    'chii': chii, 
                    'shik': shik,
                    'symbols': [Symbol.from_unicode(s) for s in sym if s]
                }                    
                if chii in chiis:
                    chiis[ chii ].append( [ rid_obj, shik ] )
                else:
                    chiis[ chii ] = [ [ rid_obj, shik ] ]
                rik_match = RIK_PAT.fullmatch(text_rem)
                if end == '</font>': break
            win_match = WIN_PAT.fullmatch(text_rem)
        div_match = DIV_PAT.fullmatch(text_rem)
    
    for chii in chiis:
        if len( chiis[ chii ] ) > 1:
            duplicates[ chii ] = chiis[ chii ]
    return b_rids, duplicates, full_html_text


def get_margin_data(date: Date) -> Tuple[List[Tuple[RikId, Chii]], Dict, str]:
    """
    Orchestrates loading and preparing the margin data for the FSM.
    
    1. Parses the raw margin HTML using the trusted `_parse_raw_marginalia`.
    2. Converts chii strings to Chii objects.
    3. Filters out non-ranked rikishi (e.g., Mz, Sj).
    4. Sorts the list by rank according to Chii's internal logic.
    
    Returns:
        A tuple containing:
        - A sorted list of (RikId, Chii) tuples (the "expected" data).
        - A dictionary of duplicate chii entries for context.
        - The raw HTML text for the body parser to use.
    """
    marginalia, dups, raw_html_text = _parse_raw_marginalia(date)

    if not marginalia:
        return [], {}, ""

    margin_data_as_foo = []
    for rid, data in marginalia.items():
        chii_str = data['chii']
        if isinstance(chii_str, str) and chii_str not in ('Mz', 'Sj'):
            # Convert the raw chii string into our powerful Chii object
            foo_obj = Chii.from_str(chii_str)
            margin_data_as_foo.append((rid, foo_obj))

    # Sort the list using the rich comparison implemented in Chii.__lt__
    #if date == Date( 1973, 1 ):
        #set_trace()
    margin_data_as_foo.sort(key=lambda item: item[1])
    
    return margin_data_as_foo, dups, raw_html_text
