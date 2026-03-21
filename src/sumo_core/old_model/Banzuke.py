from dataclasses import dataclass
from typing import Union, Literal, Optional, Dict, List, Tuple
from .Kimarite import Kimarite
from .BasicEnums import Side, Division, MSD, Ann
from .BasicPrimitives import RikId, Day, Riks

class Level:
    def __new__(cls, value: Union[MSD, Division]):
        if not isinstance(value, (MSD, Division)):
            raise TypeError("Level must be an MSD or Division")
        
        # Ensure Makuuchi division is not used directly
        if isinstance(value, Division) and value == Division.MAKUUCHI:
            raise ValueError("Use MSD values for Makuuchi levels instead of Division.MAKUUCHI")
        
        result = value
        result.as_string = lambda: result.name.capitalize()

        # Add as_abbreviation method
        def get_abbreviation():
            abbrev_map = {
                MSD.YOKOZUNA: 'Y',
                MSD.OZEKI: 'O',
                MSD.SEKIWAKE: 'S',
                MSD.KOMUSUBI: 'K',
                MSD.MAEGASHIRA: 'M',
                Division.JURYO: 'J',
                Division.MAKUSHITA: 'Ms',
                Division.SANDANME: 'Sd',
                Division.JONIDAN: 'Jd',
                Division.JONOKUCHI: 'Jk'
            }
            return abbrev_map[result]
        
        result.as_abbreviation = get_abbreviation
        return result

class Annotation:
    def __new__(cls, value: Union[Ann, Literal["TD", "OB", ""]]):
        if isinstance(value, Ann):
            return value
        
        if value == "TD":
            return Ann.TD
        elif value == "OB":
            return Ann.OB
        elif value == "":
            return Ann.EMPTY

class Shikona(str):
    def __new__(cls, value):
        if not isinstance(value, str):
            raise TypeError(f"Shikona must be created from str, got {type(value)}")
        return super(Shikona, cls).__new__(cls, value)

@dataclass
class Chii:
    level: Level
    number: int
    side: Side
    ann: Annotation

    # TBD: I think post_init is necessary for extensions of immutable types
    # because they have to be created by new() not _init_. That isn't the case
    # here. When I have finished working through all the code I will make a
    # decision about this.

    def __post_init__(self):
        """Validate that Chii components are of correct types and values"""
            
        # Validate number is a positive integer
        if not isinstance(self.number, int):
            raise TypeError(f"number must be int, got {type(self.number)}")
        if self.number <= 0:
            raise ValueError(f"number must be positive, got {self.number}")
            
        # Validate side is a Side enum
        if not isinstance(self.side, Side):
            raise TypeError(f"side must be Side enum, got {type(self.side)}")

        # Validate ann is an Ann enum
        if not isinstance(self.ann, Ann):
            raise TypeError(f"ann must be Ann enum, got {type(self.side)}")

        # Validate ann is an Ann enum
        if not isinstance(self.ann, Ann):
            raise TypeError(f"ann must be Ann enum, got {type(self.ann)}")
            
        #! Val: E2.2.2
        if self.side == Side.NONE and self.ann == Ann.EMPTY:
            raise ValueError("At least one of side or annotation must not be empty")

class RikShikona(dict):
    """
    Maps rikishi IDs to their shikona.
    
    A function from RikId to Shikona, implemented as a dictionary (E?.?.?)
    """
    
    def __new__(cls, mapping=None):
        """
        Create a new RikShikona mapping.
        
        Args:
            mapping: Optional dictionary mapping RikId to Shikona
        """
        instance = super().__new__(cls)
        
        if mapping is not None:
            for rid, shik in mapping.items():
                if not isinstance(rid, RikId):
                    raise TypeError(f"Keys must be RikId objects, got {type(rid)}")
                if not isinstance(shik, Shikona):
                    raise TypeError(f"Values must be Shikona objects, got {type(shik)}")
                instance[rid] = shik
        
        return instance
    
    def __call__(self, rid: RikId) -> Optional[Shikona]:
        """Implement function-like behavior"""
        return self.get(rid)

class RikChii(dict):
    """
    Maps rikishi IDs to their chii.
    
    A function from RikId to Chii, implemented as a dictionary (E2.3.2)
    """
    
    def __new__(cls, mapping=None):
        """
        Create a new RikChii mapping.
        
        Args:
            mapping: Optional dictionary mapping RikId to Chii
        """
        instance = super().__new__(cls)
        
        if mapping is not None:
            for rid, chii in mapping.items():
                if not isinstance(rid, RikId):
                    raise TypeError(f"Keys must be RikId objects, got {type(rid)}")
                if not isinstance(chii, Chii):
                    raise TypeError(f"Values must be Chii objects, got {type(chii)}")
                instance[rid] = chii
        
        return instance
    
    def __call__(self, rid: RikId) -> Optional[Chii]:
        """Implement function-like behavior"""
        return self.get(rid)

class Banzuke:
    """
    Represents a valid sumo tournament banzuke without validation logic.
    """
    
    def __init__(self, riks: Riks, rikchii: RikChii, rikshik: RikShikona):
        """
        Initialize a Banzuke (E2.4.1) with pre-validated data 
        
        Args:
            riks: A Riks object containing rikishi IDs
            rikchii: A RikChii mapping from rikishi IDs to their ranks
        """
        self.riks = riks
        self.rikchii = rikchii
        self.rikshik = rikshik
    
    def get_shik(self, rid: RikId) -> Optional[Shikona]:
        """Get the shik for a specific rikishi."""
        return self.rikshik(rid)
    
    def get_chii(self, rid: RikId) -> Optional[Chii]:
        """Get the chii for a specific rikishi."""
        return self.rikchii(rid)
    
    def __contains__(self, rid: RikId) -> bool:
        """Check if a rikishi ID is in the banzuke"""
        return rid in self.riks
    
    def __len__(self) -> int:
        """Get the number of rikishi in the banzuke"""
        return len(self.riks)

class BanzukeWithWarnings:
    """
    Represents a sumo tournament banzuke
    
    A Banzuke consists of a set of rikishi IDs and a mapping from those IDs to their chii.
    """
    
    def __init__(self, riks: Riks, rikchii: RikChii, rikshik: RikShikona):
        """
        Initialize a Banzuke.
        
        Args:
            riks: A Riks object containing rikishi IDs
            rikchii: A RikChii mapping from rikishi IDs to their ranks
            
        Raises:
            ValueError: If any constraints are violated
        """
        # Validate that riks is not empty
        if not riks:
            raise ValueError("Banzuke must contain at least one rikishi")
        
        # Validate that the domain of rikchii matches riks exactly
        if set(rikchii.keys()) != riks:
            raise ValueError("Domain of rikchii must match riks exactly")
        if set(rikshik.keys()) != riks:
            raise ValueError("Domain of rikshik must match riks exactly")
        
        self.riks = riks
        self.rikchii = rikchii
        self.rikshik = rikshik
        
        # Validate chii assignments according to constraints
        self.warnings = self._validate_chii_assignments()
    
    def get_shik(self, rid: RikId) -> Optional[Shikona]:
        """
        Get the shik for a specific rikishi.
        
        Args:
            rid: The rikishi ID
            
        Returns:
            The rikishi's shik or None if not found
        """
        return self.rikshik(rid)

    def get_chii(self, rid: RikId) -> Optional[Chii]:
        """
        Get the chii for a specific rikishi.
        
        Args:
            rid: The rikishi ID
            
        Returns:
            The rikishi's chii or None if not found
        """
        return self.rikchii(rid)
    
    def _group_by_level(self) -> Dict[Level, List[Tuple[RikId, Chii]]]:
        """
        Group rikishi by their level.
        
        Returns:
            A dictionary mapping levels to lists of (rikishi ID, chii) pairs
        """
        result = {}
        for rid, chii in self.rikchii.items():
            level = chii.level
            if level not in result:
                result[level] = []
            result[level].append((rid, chii))
        
        # Sort each level's rikishi by their position, then side, then annotation
        for level, rikishi in result.items():
            result[level] = sorted(
                rikishi, 
                key=lambda x: (x[1].number, self._side_value(x[1].side), self._ann_value(x[1].ann)), 
                reverse=True
            )
        
        return result
    
    @staticmethod
    def _side_value(side: Side) -> int:
        """Convert Side to numeric value for sorting (higher is greater)"""
        if side == Side.EAST:
            return 2
        elif side == Side.WEST:
            return 1
        return 0
    
    @staticmethod
    def _ann_value(ann: Ann) -> int:
        """Convert Ann to numeric value for sorting (higher is greater)"""
        if ann == Ann.TD:
            return 2
        elif ann == Ann.OB:
            return 1
        return 0
    
    def _validate_chii_assignments(self):
        """
        Validate that chii assignments follow the constraints in the model.
        
        Raises:
            ValueError: If any constraints are violated
        """
        # Group rikishi by level
        by_level = self._group_by_level()
        
        warnings = []
        # Validate each level
        for level, rikishi in by_level.items():
            # Check constraint 2.4.2: No gaps in position numbers
            positions = [chii.number for _, chii in rikishi]
            max_pos = max(positions) if positions else 0
            
            for pos in range(1, max_pos):
                if pos not in positions and pos+1 in positions:
                    raise ValueError(f"Gap in position numbers at level {level}: missing position {pos}")
            
            # For non-sanyaku levels, check constraint 2.4.3:
            # For any position < max, there must be both east and west rikishi
            if not isinstance(level, MSD) or level not in [MSD.YOKOZUNA, MSD.OZEKI, MSD.SEKIWAKE, MSD.KOMUSUBI]:
                for pos in range(1, max_pos):
                    east_exists = any(chii.number == pos and chii.side == Side.EAST and chii.ann == Ann.EMPTY 
                                      for _, chii in rikishi)
                    west_exists = any(chii.number == pos and chii.side == Side.WEST and chii.ann == Ann.EMPTY 
                                     for _, chii in rikishi)
                    
                    if not (east_exists and west_exists):
                        warnings.append( { 'num': level, 'pos': pos } )
                        with open( '_files/output/ew anomalies.txt', 'a', encoding = 'UTF8' ) as op:
                            op.write( f"At level {level}, position {pos} must have both east and west rikishi\n")
        return warnings
    
    def __contains__(self, rid: RikId) -> bool:
        """Check if a rikishi ID is in the banzuke"""
        return rid in self.riks
    
    def __len__(self) -> int:
        """Get the number of rikishi in the banzuke"""
        return len(self.riks)

    def to_banzuke(self) -> Banzuke:
        """
        Create a ValidBanzuke instance if this banzuke is valid.
        
        Returns:
            A ValidBanzuke instance if valid, None otherwise
        """
        return Banzuke(self.riks, self.rikchii, self.rikshik)

