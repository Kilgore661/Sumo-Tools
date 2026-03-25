# FSM/FSM_base_fsm.py
from pdb import set_trace
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from .FSM_data_classes import *
from .FSM_exceptions import *
from sumo_core.BasicPrimitives import RikId
from sumo_core.BasicEnums import Side, Annotation
from sumo_core.Chii import Chii
from sumo_core.History import Date

class BaseFSM(ABC):
    def __init__(self, date: Date, sorted_margin_data: List[Tuple[RikId, Chii]], dups: Dict):
        self.state_id = 0
        self.output: Dict[RikId, FinalBanzukeEntry] = {}
        self.margin_data_list = sorted_margin_data
        self.margin_data_idx = 0
        self.duplicates = dups
        self.date = date
        self.context = { 'deferred_ga_data': None } # Context is now minimal
        self.rows_processed = 0

    def _resolve_deferred_ga_as_hd(self):
        """
        Processes a deferred GA token stored in the context, assuming
        it's a standalone HD anomaly. This is GruntFSM-specific logic.
        """
        deferred_data = self.context['deferred_ga_data']
        if not deferred_data:
            return

        div = deferred_data['division']
        num = deferred_data['number']
        row = deferred_data['row']
        
        if row.east:
            inferred_foo = Chii.from_str(f"{div}{num}eHD")
            rid, entry = self._reconcile_and_create_entry(row.east, inferred_foo)
            self.output[rid] = entry
        if row.west:
            inferred_foo = Chii.from_str(f"{div}{num}wHD")
            rid, entry = self._reconcile_and_create_entry(row.west, inferred_foo)
            self.output[rid] = entry

    def run(self, banzuke_row_stream: List[BanzukeRow]):
        for banzuke_row in banzuke_row_stream:
            try: token = self._classify_token(banzuke_row)
            except UnclassifiableRowError: break
            
            old_state = self.state_id
            next_state = self._get_next_state(token)
            if next_state == 4: break
            
            self._execute_transition_action(old_state, next_state, token)
            self.state_id = next_state
            self.rows_processed += 1
        
        self._end_of_stream_action()

        if self.margin_data_idx < len(self.margin_data_list):
            remaining = [item[0] for item in self.margin_data_list[self.margin_data_idx:]]
            raise ReconciliationError(f"FSM finished but margin has more rikishi than body. Missing: {remaining}")
        return self.output

    def _get_next_expected(self) -> Tuple[RikId, Chii]:
        if self.margin_data_idx >= len(self.margin_data_list):
            raise ReconciliationError("Body has more rikishi than margin expects.")
        expected_data = self.margin_data_list[self.margin_data_idx]
        self.margin_data_idx += 1
        return expected_data

        
    def _try_sideless_chii_recovery(self, rikishi_data: RikishiData, inferred_foo: Chii) -> Tuple[RikId, FinalBanzukeEntry] | None:
        """
        Recovers from the specific mismatch where the body infers a side but the margin is sideless.
        POLICY: Trusts the margin's sideless representation.
        """
        # We must consume the margin entry to check it.
        expected_rid, expected_foo = self._get_next_expected()

        # Hypothesis: IDs match, and the only difference is a side inferred by the body
        # that is missing from the margin.
        if (expected_rid == rikishi_data.id and
            inferred_foo.level == expected_foo.level and
            inferred_foo.number == expected_foo.number and
            inferred_foo.ann == expected_foo.ann and
            inferred_foo.side != Side.NONE and # Body has a side
            expected_foo.side == Side.NONE):   # Margin does not

            # SUCCESS! This is the specific pattern we are looking for.
            
            # Log the normalization action and the policy decision.
            print(f"INFO ({self.date}): Normalizing sideless chii for {rikishi_data.shikona} (ID: {rikishi_data.id}). "
                  f"Body implies {inferred_foo}, but margin has {expected_foo}. Using MARGIN'S version.")
            
            print(f"WARNING ({self.date}): Rikishi {rikishi_data.id} has a sideless chii: {expected_foo}. "
                  "Downstream code must handle potential duplicates at this rank.")
            
            # Return the entry using the MARGIN'S sideless foo.
            return (expected_rid, FinalBanzukeEntry(chii=expected_foo, shikona=rikishi_data.shikona))

        # If the pattern doesn't match, this recovery fails. Rewind the margin index.
        self.margin_data_idx -= 1
        return None

    def _reconcile_and_create_entry(self, rikishi_data: RikishiData, inferred_foo: Chii) -> Tuple[RikId, FinalBanzukeEntry]:
        """
        Performs reconciliation using the primary sorted list, but consults the
        duplicates pool for known ambiguous ranks.
        """

        # Look for the chii (with and without side) in duplicates.
        key = str(inferred_foo)
        if key not in self.duplicates:
            key = str( Chii(
                           level=inferred_foo.level,
                           number=inferred_foo.number,
                           side=Side.NONE, 
                           ann=inferred_foo.ann
                       ) 
            )

        if key in self.duplicates:
            # This is an ambiguous rank like Ms60e AND NOT Ms60eHD. Use the pool logic.
            
            # Get the pool of eligible rikishi for this rank.
            # Note: The dups dict maps chii_string to a list of [y, m, rid_str, shikona]
            pool_of_rid_strings = [item[0] for item in self.duplicates[key]]
            pool_of_rids = {RikId(int(rid_str)) for rid_str in pool_of_rid_strings}

            if rikishi_data.id in pool_of_rids:
                # SUCCESS! The rikishi from the body is in the margin's pool.
                
                # We need to remove this rikishi from the main margin_data_as_foo list
                # so it isn't processed again. This is the tricky part.
                # We find its index and remove it.
                found_idx = -1
                for i in range(self.margin_data_idx, len(self.margin_data_list)):
                    if self.margin_data_list[i][0] == rikishi_data.id:
                        found_idx = i
                        break
                
                if found_idx != -1:
                    # We found it out of sequence. Remove it from the list.
                    self.margin_data_list.pop(found_idx)
                    # We don't advance the main index.
                    print(f"RECOVERY ({self.date}): Matched {rikishi_data.id} from duplicates pool for rank {key}.")
                    return (rikishi_data.id, FinalBanzukeEntry(chii=inferred_foo, shikona=rikishi_data.shikona))
                else:
                     # This shouldn't happen if data is consistent.
                     raise ReconciliationError(f"Rikishi {rikishi_data.id} was in duplicates pool but not found in main margin list.")

            else:
                # The rikishi is not in the pool for this ambiguous rank. Hard error.
                raise ReconciliationError(f"Rikishi {rikishi_data.id} not in margin's pool for ambiguous rank {key}.")
        else:
            expected_rid, expected_foo = self._get_next_expected()

            # --- Lenient Reconciliation ---
            if (expected_rid == rikishi_data.id and
                expected_foo.level == inferred_foo.level and
                expected_foo.number == inferred_foo.number):
                
                # Core data matches. Now, resolve side/annotation discrepancies.
                if expected_foo.ann == Annotation.YO:
                    final_foo = expected_foo 
                else:
                    final_foo = inferred_foo 
                
                #if inferred_foo != expected_foo:
                #    #set_trace()
                #    set_trace()
                #    print(f"INFO ({self.date}): Normalizing chii for {rikishi_data.shikona} (ID: {rikishi_data.id}). "
                #          f"Body implies: {inferred_foo}, Margin has: {expected_foo}. Using MARGIN'S version.")
                
                # Check for the sideless issue in the FINAL chosen chii to provide a specific warning.
                if final_foo.side == Side.NONE and final_foo.ann != Annotation.EMPTY:
                     print(f"WARNING ({self.date}): Rikishi {rikishi_data.id} has a sideless chii: {final_foo}. "
                           "Downstream code must handle potential duplicates at this rank.")

                return (expected_rid, FinalBanzukeEntry(chii=final_foo, shikona=rikishi_data.shikona))

            # --- Hard Failure ---
            # The core data (ID, level, number) doesn't match. This requires more advanced recovery.
            # For now, let's keep the transposition recovery.
            self.margin_data_idx -= 1
            
            recovered_entry = self._try_transposition_recovery(rikishi_data, inferred_foo)
            if recovered_entry:
                return recovered_entry

            recovered_entry = self._try_sideless_chii_recovery(rikishi_data, inferred_foo)
            if recovered_entry:
                return recovered_entry

            # Re-consume for accurate error message.
            final_expected_rid, final_expected_foo = self._get_next_expected()
            raise ReconciliationError(
                f"Unrecoverable mismatch for {rikishi_data.shikona} ({rikishi_data.id}). "
                f"Body implies {inferred_foo}, but margin expects {final_expected_foo} (for rid {final_expected_rid})."
            )

    # ADD THIS NEW RECOVERY METHOD TO THE CLASS
    def _try_transposition_recovery(self, rikishi_data: RikishiData, inferred_foo: Chii) -> Tuple[RikId, FinalBanzukeEntry] | None:
        """
        Attempts to recover from a simple transposition error in the margin list.
        Returns a valid output symbol on success, or None on failure.
        """
        current_idx = self.margin_data_idx
        next_idx = current_idx + 1
        if next_idx >= len(self.margin_data_list): return None

        next_rid, next_foo = self.margin_data_list[next_idx]
        
        # Hypothesis: The rikishi we want is the *next* one AND its chii matches what we inferred.
        if next_rid == rikishi_data.id and next_foo == inferred_foo:
            mismatched_entry = self.margin_data_list[current_idx]
            print(f"RECOVERY ({self.date}): Correcting transposition. Swapping margin entries for rid {mismatched_entry[0]} and {next_rid}.")

            # Perform the physical swap to correct the stream.
            self.margin_data_list[current_idx], self.margin_data_list[next_idx] = \
                self.margin_data_list[next_idx], self.margin_data_list[current_idx]
            
            # Now, consume the corrected entry from the margin list.
            final_rid, final_foo = self._get_next_expected()
            return (final_rid, FinalBanzukeEntry(chii=final_foo, shikona=rikishi_data.shikona))

        return None


    def _try_annotation_recovery(self, rikishi_data: RikishiData, inferred_foo: Chii) -> Tuple[RikId, FinalBanzukeEntry] | None:
        """
        Attempts to recover from a chii mismatch where the body implies an
        annotation that the margin is missing.
        """
        # We must consume the margin entry to check it.
        expected_rid, expected_foo = self._get_next_expected()

        # Hypothesis: IDs match, but margin is missing an annotation.
        if (expected_rid == rikishi_data.id and
            inferred_foo.level == expected_foo.level and
            inferred_foo.number == expected_foo.number and
            inferred_foo.side == expected_foo.side and
            inferred_foo.ann != Annotation.EMPTY and 
            expected_foo.ann == Annotation.EMPTY):
            
            # SUCCESS! The hypothesis is correct.
            print(f"RECOVERY ({self.date}): Body-inferred annotation '{inferred_foo.ann.name}' "
                  f"applied to margin entry for {rikishi_data.shikona} (ID: {rikishi_data.id}).")
            
            # Return the corrected entry, using the FSM's inferred_foo.
            return (expected_rid, FinalBanzukeEntry(chii=inferred_foo, shikona=rikishi_data.shikona))

        # If we are here, recovery failed. We must rewind the margin index.
        self.margin_data_idx -= 1
        return None

    @abstractmethod
    def _get_next_state(self, token: Token) -> int: pass
    @abstractmethod
    def _classify_token(self, banzuke_row: BanzukeRow) -> Token: pass
    @abstractmethod
    def _execute_transition_action(self, old_state: int, next_state: int, token: Token): pass
    @abstractmethod
    def _end_of_stream_action(self): pass
