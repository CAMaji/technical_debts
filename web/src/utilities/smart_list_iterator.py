from typing import TypeVar, Generic, Callable

_T = TypeVar('T')
_O = TypeVar('O')

class SmartListIterator(Generic[_T, _O]):
    data : list[_T]
    value_lambda : Callable[[_T], _O]
    position : int

    def __init__(self, data : list[_T], value_lambda : Callable[[_T], _O]):
        self.data = data
        self.value_lambda = value_lambda
        self.position = 0
        
    def __iter__(self): 
        return self
    
    def __next__(self) -> _O:
        if(self.position >= len(self.data)):
            raise StopIteration
        
        val = self.value_lambda(self.data[self.position])
        self.position += 1
        return val
