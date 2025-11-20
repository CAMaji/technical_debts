from typing import Generic, TypeVar
from src.utilities.custom_json_encoder import CustomJsonEncoder

Ta = TypeVar('Ta')
Tb = TypeVar('Tb')

class Pair(Generic[Ta, Tb], CustomJsonEncoder):
    first : Ta
    second : Tb

    def __init__(self, first : Ta, second : Tb):
        self.first = first
        self.second = second

    def to_tuple(self) -> tuple[Ta, Tb]: 
        return (self.first, self.second)
    
    def encode(self):
        _tuple = self.to_tuple()
        return CustomJsonEncoder.breakdown(_tuple)