#from typing import Dict, Union, Literal, Optional, List
from dataclasses import dataclass
from typing import List, Dict
from .Banzuke import Banzuke
from .Summary import Summary
from .BasicEnums import Symbol


@dataclass
class BashoState:
    """
    Represents a complete state of a basho.
    
    According to the model: BashoState ⊆ Banzuke × Summary.
    
    Note: While type validation follows the same pattern as other classes
    (TypeErrors in __post_init__), BashoState's domain validation (ValueErrors)
    is unique. The validate() method is designed to be called externally by
    table_parser.parse_bashostate() rather than during object construction.
    This separation reflects BashoState's role as the final aggregator of
    complex parsed data, where construction and validation are logically
    distinct steps.
    
    Value inconsistencies are reported as warnings rather than errors because the
    historical record is considered the source of truth, even when it contains
    apparent contradictions with our formal model.
    """
    banzuke: Banzuke
    summary: Summary
    
    def __post_init__(self):
        """Validate basho state structure"""
        if not isinstance(self.banzuke, Banzuke):
            raise TypeError(f"banzuke must be a Banzuke instance, got {type(self.banzuke)}")
            
        if not isinstance(self.summary, Summary):
            raise TypeError(f"summary must be a Summary instance, got {type(self.summary)}")

    def validate(self) -> List[Dict]:
        """
        Validates the internal consistency of BashoState according to model constraints.
        
        Specifically checks symbol-outcome-decision consistency per Equation 3.2.11.
        Returns a list of validation issues (empty list if fully valid).
        """
        validation_issues = []
        
        # Check symbol-outcome-decision consistency per Equation 3.2.11
        for day, daily_results in self.summary.items():
            for pair, bout_result in daily_results.results_lookup.items():
                # Check both rikishi in the bout
                for i, rid in enumerate([bout_result.rikishi1, bout_result.rikishi2]):
                    outcome = bout_result.outcome1 if i == 0 else bout_result.outcome2
                    symbol = bout_result.symbol
                    
                    # Skip DASH symbols as they're handled by separate constraint
                    if symbol == Symbol.DASH:
                        continue
                    
                    # Use the existing inconsistent method to check
                    if symbol.inconsistent(outcome):
                        validation_issues.append({
                            "type": "warning",
                            "message": f"Day {day}: Inconsistent outcome ({outcome}) and symbol ({symbol}) for rikishi {rid}",
                            "model_ref": "3.2.11",
                            "day": day,
                            "rikishi": rid
                        })
        
        return validation_issues
