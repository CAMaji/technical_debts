from src.utilities.json_encoder import JsonEncoder
from dataclasses import dataclass

@dataclass
class EntityReport(JsonEncoder.Interface):
    _FIELDS = {"file_name", "entity_name", "line_position"}
    file_name : str = ""
    entity_name : str = ""
    line_position : int = 0

    def _validate_keys(self, func : dict):
        for key in EntityReport._FIELDS:
            assert key in func   # validates that the dict contains expected keys. 
            continue

    def load(self, entity): 
        assert type(entity) == dict
        
        self._validate_keys(entity)
        for key in EntityReport._FIELDS:
            setattr(self, key, entity[key])
            continue
        
        return self