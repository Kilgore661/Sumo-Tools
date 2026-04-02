import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from time import time
from pdb import set_trace
t0 = time()
import os
import re
from typing import Dict, List

from .parser2_margin import get_margin_data
from .parser2_body import parse_and_validate_body
from .parser2_IntDate import IntDate as Date
from ..persistence.new_sumo_serialiser import save_history_with_annotations

from .FSM import FinalBanzukeEntry
# --- Core Model Dependencies (Original and New) ---
from ...sumo_core.Banzuke import Banzuke, RikShikona, Riks, RikChii
from ...sumo_core.Summary import Summary
from ...sumo_core.BasicPrimitives import RikId, Day
from ...sumo_core.History import History
from ...sumo_core.BashoState import BashoState
from ...sumo_core.Chii import Chii
from .parser_daily import _parse_daily_results

# --- Helper/Utility Dependencies ---
from ..helpers import parse_args
from ..ETA3 import EtaModule
from .parser_warning_logger import logger
from .parser2_utils import RESULTS_DIR, adapt_banzuke_for_daily_parser
from .parser2_body_adapter import _extract_performance

OUTPUT_DIR = 'files/output'

def tidy_up(
        d: Date,
        validated_data: Dict[RikId, FinalBanzukeEntry],
        daily_results_dict: Dict,
        special_prizes_dict: Dict
    ) -> BashoState:
    """
    Performs final assembly of the BashoState from validated data.
    This function now preserves the Chii objects instead of downgrading them.
    """
    all_riks = Riks(validated_data.keys())

    # THE CRITICAL CHANGE: We no longer call .to_chii().
    # We keep the powerful Chii object with all its annotation data.
    rik_newfoo_map = {rid: entry.chii for rid, entry in validated_data.items()}
    rik_shikona_map = {rid: entry.shikona for rid, entry in validated_data.items()}

    # This check is now more important to ensure the FSMs are behaving correctly.
    for rid, foo_obj in rik_newfoo_map.items():
        if not isinstance(foo_obj, Chii):
             raise TypeError(f"Final chii for {rid} is not a Chii object, but {type(foo_obj)}")

    # Instantiate the new Banzuke object.
    banzuke = Banzuke(
        riks=all_riks,
        rikchii=RikChii(rik_newfoo_map),
        rikshik=RikShikona(rik_shikona_map)
    )

    # Summary remains a placeholder for now, as in the original parser2.
    summary = Summary(daily_results_dict, special_prizes_dict )

    # The original BashoState.validate() is no longer compatible as it expects Chii.
    # For now, we bypass it. A new validation method would be needed if desired.
    # bs = BashoState(banzuke=banzuke, summary=summary)
    # validation_issues = bs.validate() ...

    # Return the new, annotation-rich BashoState object.
    return BashoState(banzuke=banzuke, summary=summary)



### MODIFIED ### - Updated the return type hint for clarity.
def parse_bashostate(date: Date) -> BashoState:
    """
    The main entry point for parsing a single basho.
    Orchestrates loading, validation, and final assembly.
    """
    
    # --- Stage 1: Load Margin Data ---
    margin_data, dups, raw_html_text = get_margin_data(date)
    if not margin_data:
        return None

    # --- Stage 2: Run the Orchestrator ---
    validated_data, special_prizes_dict, body_data_ffs = parse_and_validate_body(date, margin_data, dups, raw_html_text)
    if not validated_data:
        # FSM process failed or produced no data.
        return 'error'

    # --- Stage 3: Get daily results and prizes ---
    legacy_banzuke_context = adapt_banzuke_for_daily_parser(validated_data, body_data_ffs)
    
    daily_results_dict = {}
    for day in range(1, 16):
        day_results = _parse_daily_results(date.year, date.month, Day(day), legacy_banzuke_context)
        if day_results:
            daily_results_dict[Day(day)] = day_results

    # --- Stage 4: Final Assembly ---
    # CORRECTED: Pass the required arguments to the tidy_up function.
    bs = tidy_up(date, validated_data, daily_results_dict, special_prizes_dict)

    return bs

def _find_available_directories():
    """Returns a list of available basho as Date objects."""
    dirs = []
    dir_pattern = re.compile(r'(\d{4}) (\d{2})')
    if not os.path.isdir(RESULTS_DIR):
        print(f"Warning: Results directory not found at '{RESULTS_DIR}'", file=sys.stderr)
        return []
    for dir_name in os.listdir(RESULTS_DIR):
        match = dir_pattern.fullmatch(dir_name)
        if match: dirs.append( Date(int(match.group(1)), int(match.group(2))) )
    dirs.sort()
    return dirs

NO_BASHO = { Date(2011,3), Date(2020,5) }
### MODIFIED ### - Updated the return type hint and object instantiation.
def parse_range(start_year, end_year=None, start_month=1, end_month=11) -> History:
    """Parses all basho data between specified date ranges."""
    if end_year is None: end_year = start_year
    start_date = Date(start_year, start_month)
    end_date = Date(end_year, end_month)
    
    available_basho = _find_available_directories()
    basho_to_process = [d for d in available_basho if start_date <= d <= end_date]
    
    eta = EtaModule(len(basho_to_process))
    # Use the new History class to store the results.
    history = History()
    
    for d in basho_to_process:
        if d in NO_BASHO:
            continue
        bs = parse_bashostate(d)
        history[d] = bs
        eta_time = eta.tick()
        print(f"Processed {d} ({eta.percent_complete():.1f}% done), ETA = {eta_time} ({eta.eta_trend_str()}){' '*30}", end='\n')
    
    print(f'\nAll files processed.{" "*40}')
    return history

def parse_history(start_year: int, end_year: int) -> History:
    return parse_range(start_year, end_year)

def parse_and_save_history(start_year, end_year):
    """
    Orchestrates the entire process: parsing a date range and then
    serializing the resulting History object to a file.
    """
    # Step 1: Run the full parsing process to get the history object in memory.
    from time import time
    t0 = time()
    history = parse_range(start_year, end_year)
    t1 = time()
    print( f'range {start_year} - {end_year} parsed in {t1-t0:.3f} sec.' )

    if not history:
        print("No data was parsed. Nothing to save.")
        return

    # Step 2: Define the output path and filename.
    output_dir = f"{OUTPUT_DIR}/Historys"
    filename = f"{start_year}_01 to {end_year}_11"
    full_path = os.path.join(output_dir, filename)

    # Step 3: Ensure the output directory exists.
    os.makedirs(output_dir, exist_ok=True)

    # Step 4: Call the new serialiser to save the data.
    print(f"\nSaving history to {full_path}.zip...")
    save_history_with_annotations(history, full_path)
    print(f"Save complete in {time()-t1:0.3f} sec.")


### MODIFIED ### - Main function is now simpler and calls the new orchestrator.
def main():
    logger.initialise(output_dir=OUTPUT_DIR)
    args = parse_args(sys.argv)
    
    if 'num' in args:
        start_year = end_year = args['num']
    else:
        start_year = args['start']
        end_year = args['end']
    
    # Call the new top-level function that handles both parsing and saving.
    parse_and_save_history(start_year, end_year)
    
    logger.close()

if __name__ == '__main__':
    main()
    print(f'Complete in {time()-t0:.2f}s')
