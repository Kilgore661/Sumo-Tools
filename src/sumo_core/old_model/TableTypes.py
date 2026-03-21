from enum import Enum, auto
from typing import Dict, Union
from dataclasses import dataclass


class TableType(Enum):
    DIVISION = auto()  # Regular division (Makuuchi, Juryo, etc.)
    MAE_ZUMO = auto()  # Mae-zumo section
    BANZUKE_GAI = auto()  # Banzuke-gai section
    SHIKONA_CHANGES = auto()  # Shikona Changes section
    SHIN_DESHI = auto()  # Shin-Deshi section
    RETIRED = auto()  # Retired Rikishi section


class BodyTable:
    def __init__(self, table_type, name, rikishi_list, additional_data=None):
        """
        Initialize a BodyTables object.
        
        Args:
            table_type (TableType): Type of the table
            name (str): Name of the table (e.g., "Makuuchi", "Juryo", etc.)
            rikishi_list (list): List of rikishi records
            additional_data (dict, optional): Additional table-specific data
        """
        self.table_type = table_type
        self.name = name
        self.rikishi_list = rikishi_list
        self.additional_data = additional_data or {}
    
    def __len__(self):
        """Return the length of the rikishi list."""
        return len(self.rikishi_list)
    
    def get_print_count(self):
        """Get appropriate count description based on table type."""
        if self.table_type == TableType.SHIKONA_CHANGES:
            return f"{len(self)} changes"
        elif self.table_type == TableType.SHIN_DESHI:
            return f"{len(self)} new rikishi"
        elif self.table_type == TableType.RETIRED:
            return f"{len(self)} retired rikishi"
        else:
            return f"{len(self)} rikishi"


@dataclass
class BanzukeTables:
    """Represents the complete set of tables in a banzuke (tournament ranking document)"""
    tables: Dict[TableType, Union[BodyTable, Dict[str, BodyTable]]]


    def __post_init__(self):
        # Validate tables 
        if not isinstance(self.tables, dict):
            raise TypeError(f"tables must be a dict, got {type(self.tables)}")
        
        for key, value in self.tables.items():
            if not isinstance(key, TableType):
                raise TypeError(f"tables keys must be TableType, got {type(key)}")
            
            if key == TableType.DIVISION:
                if not isinstance(value, dict):
                    raise TypeError(f"For TableType.DIVISION, value must be dict, got {type(value)}")
                for div_name, table in value.items():
                    if not isinstance(table, BodyTable):
                        raise TypeError(f"Division values must be BodyTable, got {type(table)}")
            else:
                if not isinstance(value, BodyTable):
                    raise TypeError(f"Table values must be BodyTable, got {type(value)}")

    def get_division_table(self, division_name: str) -> BodyTable:
        """Retrieves a specific division's table"""
        if TableType.DIVISION in self.tables:
            division_tables = self.tables[TableType.DIVISION]
            if isinstance(division_tables, dict) and division_name in division_tables:
                return division_tables[division_name]
        raise KeyError(f"Division {division_name} not found")

    def get_special_table(self, table_type: TableType) -> BodyTable:
        """Retrieves a non-division table by type"""
        if table_type == TableType.DIVISION:
            raise ValueError("Use get_division_table() for division tables")
        if table_type in self.tables:
            table = self.tables[table_type]
            if isinstance(table, BodyTable):
                return table
        raise KeyError(f"Table type {table_type} not found")
