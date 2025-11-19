from typing import TypeVar, Generic

T = TypeVar('T')

class ValueRange(Generic[T]): 
    From : T
    To : T

    def __init__(self, From : T, To : T):
        self.From = From
        self.To = To
    
    def is_value_within(self, val : T) -> bool:
        return self.From <= val and val <= self.To

