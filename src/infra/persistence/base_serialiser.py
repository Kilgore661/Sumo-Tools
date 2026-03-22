from enum import Enum
from zipfile import ZipFile, ZIP_DEFLATED
import json, os
from typing import Any, Dict, Type

class BaseSerializer:
    """Base class for serializers with common functionality"""
    
    @staticmethod
    def enum_to_str(obj: Any) -> Any:
        """Convert enum objects to their names"""
        if isinstance(obj, Enum):
            return obj.name
        return obj

    @staticmethod
    def str_to_enum(value: str, enum_class: Type[Enum]) -> Enum:
        """Convert string back to enum value"""
        if value is None:
            return None
        return enum_class[value]
    
    @classmethod
    def save_to_zip(cls, data: Dict, filename: str) -> None:
        """Save data to a compressed JSON file"""
        base_filename = os.path.basename(filename)
        zip_filename = filename + '.zip'
        
        with ZipFile(zip_filename, 'w', compression=ZIP_DEFLATED) as zip_file:
            zip_file.writestr(base_filename + '.json', json.dumps(data, indent=4))
    
    @classmethod
    def load_from_zip(cls, filename: str) -> Dict:
        """Load data from a compressed ZIP file"""
        zip_filename = filename + '.zip'
        with ZipFile(zip_filename, 'r') as zip_file:
            json_filename = zip_file.namelist()[0]
            json_data = zip_file.read(json_filename).decode('utf-8')
            return json.loads(json_data)
