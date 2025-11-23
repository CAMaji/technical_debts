from typing import TypeVar, Generic, Callable

_Tk = TypeVar('Tk')
_Tv = TypeVar('Tv')
_O = TypeVar('O')

class SmartDictIterator(Generic[_Tk, _Tv, _O]):
    _data : dict[_Tk, _Tv]
    _value_lambda : Callable[[tuple[_Tk, _Tv]], _O]
    _key_list : list
    _key : int

    def __init__(self, data : dict[_Tk, _Tv], value_lambda : Callable[[tuple[_Tk, _Tv]], _O]):
        self._data = data
        self._key_list = list(data.keys())
        self._value_lambda = value_lambda
        self._key = 0
        
    def __iter__(self): 
        self._key = 0
        return self
    
    def __next__(self) -> _O:
        if(self._key >= len(self._data)):
            self._key = 0
            raise StopIteration
        
        key = self._key_list[self._key]
        value = self._data[key]
        result = self._value_lambda((key, value))
        self._key += 1
        return result
