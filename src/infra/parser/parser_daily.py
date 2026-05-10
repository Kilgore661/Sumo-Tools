import os, re
import sys
from pdb import set_trace
from typing import Dict, Set, Tuple, Optional, List, Union, Literal

from ...sumo_core.BasicEnums import Prize, Direction, Outcome
from ...sumo_core.Banzuke import Shikona
from ...sumo_core.Summary import BoutResult, DailyResults
from ...sumo_core.Kimarite import Kimarite
from ...sumo_core.BasicPrimitives import RikId, Day, Torikumi
from .parser_warning_logger import logger
from .parser2_utils import RESULTS_DIR

def _parse_bout_kimarite( kimarite_str: str) -> Union[Kimarite, Literal["fusen"], Literal["blank"]]:
    """Convert kimarite string from source to proper enum value"""
    if kimarite_str in { "fusen", "blank" }:
        return kimarite_str
        
    try:
        return Kimarite.from_string(kimarite_str)
    except ValueError:
        # Log warning about unrecognized kimarite
        print(f"Warning: Unrecognized kimarite '{kimarite_str}', using default")
        return Kimarite.UNCLASSIFIED  # Fallback value

def _convert_outcome( outcome_str: str) -> Outcome:
    return Outcome[outcome_str]

double_FP = {
    ( 1993, 1,  6, 2354, 2370 ),
    ( 1995, 3,  2, 2512, 2439 ),
    ( 2022, 7, 12, 12384, 12220 ),
    ( 2022, 7, 12, 12488, 11760 ),
    ( 2026, 3, 6, 12815, 6005 )
}

def _parse_daily_results( year: int, month: int, day: Day, 
                       banzuke_mz: Dict[int, Dict[str, str]]) -> Optional[DailyResults]:
    ''' Parses daily results page downloaded with SIMPLE=ON i.e. one big flat table '''

    fn = os.path.join(RESULTS_DIR, f'{year} {month:02d}', f'{day:02d}.html')
    
    try:
        with open(fn, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f'Could not find daily results file: {fn}')
        return None

    torikumi = Torikumi()
    results_lookup = {}

    # First match header
    header_pat = re.compile(r'.*?<h1>\s*(.+?) (\d+), Day (\d+)</h1><h2>(\S+) (\d+), (\d+)</h2>(.*)', re.DOTALL)
    header_match = header_pat.fullmatch(text)
    if not header_match:
        return None
    
    text = header_match.group(7)  # Rest of text after header

    # Find the results table
    body_pat = re.compile(r'.*?<table(.*?)</table>(.*)', re.DOTALL)
    body_match = body_pat.fullmatch(text)
    if not body_match:
        return None
    
    rows = body_match.group(1)

    # Parse rows
    row_pat = re.compile(r'.*?<tr>(.*?)</tr>(.*)', re.DOTALL)
    row_match = row_pat.fullmatch(rows)
    
    twelve_format_assumed = True
    while row_match:
        row, rows = row_match.groups()
        
        # Get columns
        col_pat = re.compile(r'\s*<td.*?>(.*?)</td>(.*)', re.DOTALL)
        cols = []
        col_match = col_pat.fullmatch(row)
        while col_match:
            col, row = col_match.groups()
            cols.append(col)
            col_match = col_pat.fullmatch(row)
        
        if len(cols) == 12:
            # Hypothesis: not all files are contemporary and there are "old
            # format" files that don't have a column 1 in which there is, I
            # think, the bout number starting from the first bout on the
            # torikumi. This is not used, but I think to make such rows
            # consistent with "nre format" files. (It used to insert at
            # column 0. This, I think, is wrong, but it doesn't matter
            # because column 0 isn't used either.)
            #
            # Update. In fact there are 12- and not-12-column files and
            # there is no pattern to them; not e.g. "pre-1989". Weird.
            cols.insert(1, '?') 
        else:
            if twelve_format_assumed:
                logger.log_format_warning(year, month, day)
                twelve_format_assumed = False
        
        if len(cols) >= 13:  # Process only valid bout rows
            if cols[ 4 ] == cols[ 10 ] == 'Mz':
                pass
            else:
                # An Mz's record is only of interest if his opponent is not an Mz.
                id_pat = re.compile(r'<a .*?r=(\d+).*?>(.*?)</a>', re.DOTALL)
                id1_match = id_pat.search(cols[5])
                id2_match = id_pat.search(cols[11])
                
                if id1_match and id2_match:
                    rid1 = RikId(int(id1_match.group(1)))
                    rid2 = RikId(int(id2_match.group(1)))
                    
                    kimarite = cols[8] if cols[8] != '&nbsp;' else 'blank'
                    decision = _parse_bout_kimarite(kimarite)
                    
                    # Only create BoutResult if outcomes are valid
                    if cols[7] in Outcome.__members__ and cols[9] in Outcome.__members__:
                        outcome1 = _convert_outcome(cols[7])
                        outcome2 = _convert_outcome(cols[9])

                        ####################################################
                        # The set_trace below was executed when processing
                        # Omori (13003) in his first appearance in 2026/05. He is
                        # not in banzuke_mz. This should be correct as he is Ms60TD. 
                        # There are all sorts of questions here about the
                        # model, never mind the logic. But the pragmatic thing
                        # is that we are just trying to decide what "sym"
                        # should be; and the outcome is the same whether "temp"
                        # is Mz or not. I think we just say sym =
                        # outcome1.to_symbol(), period.
                        #if rid1 not in banzuke_mz:
                        #    set_trace()
                        #temp = banzuke_mz[ rid1 ][ 'chii' ]
                        #if isinstance( temp, str ) and temp == 'Mz':
                        #    # Mz has snuck into the table because he fought a Jk
                        #    # Mz are not in the margin so there are no symbols.
                        #    # Mz are allowed in the "banzuke" - the type is
                        #    # specifically called BanzukeMz to remind us that
                        #    # they are allowed in. Why - I can't remember :(

                        #    #sym = None # Why do this? It leads to calling None.inconsistent()
                        #    sym = outcome1.to_symbol()
                        #else:
                        #    # This code doesn't work because the symbols in the
                        #    # margin are not always consistent with the
                        #    # corresponding days' results.
                        #    #
                        #    #symbols = banzuke_mz[ rid1 ][ 'symbols' ]
                        #    #if day <= len( symbols ):
                        #    #    sym = symbols[ day - 1 ]
                        #    #else:
                        #    #    sym = None
                        #    #
                        #    # Instead, we'll take the Outcome to be the source
                        #    # of truth and make the symbol from rikishi1's Outcome
                        #    sym = outcome1.to_symbol()
                        sym = outcome1.to_symbol()

                        # There is a potential problem with sym = None which is
                        # that later it will be used in an expression
                        # sym.opposite() which should not be defined. I have
                        # hacked it by not checking None for consistency, in
                        # order to get to the next stage in testing i.e if the
                        # implementation's records are the same as the one
                        # produced by this code. See sumo_enum in the
                        # *implementation* folder for more info. (Opposite is
                        # not a notion needed for the original model. Which may
                        # be telling ...)

                        # Why is this not needed now? Both were Mz? IIRC it
                        # was 1974/11 it happened
                        #print( f'Both {rid1} and {rid2} winners in {year}/{month:02d}, day {day}' )

                        # Very special case: both were absent according to the individual records:
                        #     https://sumodb.sumogames.de/Rikishi.aspx?r=2354
                        #     https://sumodb.sumogames.de/Rikishi.aspx?r=2370
                        # And the totals-so-far in the daily results page
                        #     https://sumodb.sumogames.de/Results.aspx?b=199301&d=6&simple=on
                        # are weird.
                        #
                        # They are both Jk (albeit post-1989) who retired
                        # in the basho, so the effect of just ignoring this
                        # non-bout on the Elo ratings should be negligible
                        #
                        # Other cases as per double_FP:
                        #    1995/03/02 Both riks absent according to individual records. First retires.
                        #    1995/07/12 In both instances, both riks did get a FP according to individual records.
                        if ( year, month, day, rid1, rid2 ) in double_FP:
                            row_match = row_pat.fullmatch(rows)
                            continue

                        try:
                            # Make result.
                            bout_result = BoutResult(
                                rikishi1=rid1,
                                outcome1=outcome1,
                                rikishi2=rid2,
                                outcome2=outcome2,
                                decision=decision,
                                symbol=sym
                            )
                            
                            torikumi.add((rid1, rid2))
                            results_lookup[(rid1, rid2)] = bout_result
                        except (ValueError, TypeError) as e:
                            print(f"{year}/{month:02d}, day {day}: error creating bout result for {rid1} vs {rid2}: {e}", file = sys.stdout )
        
        row_match = row_pat.fullmatch(rows)
    
    historical_cutoff = (1989, 1)  # January 1989
    current_date = (year, month)
    
    all_makuuchi = set()
    for rid, data in banzuke_mz.items():
        # For historical basho, only include Makuuchi division
        chii_code = data['code']
        if chii_code < 50000:  # Makuuchi ranks have lower codes
            all_makuuchi.add(rid)
    
    if torikumi:
        try:
            return DailyResults(
                torikumi=torikumi,
                results_lookup=results_lookup
            )
        except (ValueError, TypeError) as e:
            print(f"Error creating daily results for {year}/{month}/{day}: {e}")
            return None
    
    return None
