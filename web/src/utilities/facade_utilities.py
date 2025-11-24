from sqlalchemy.engine import Row
from typing import Callable, TypeVar


T = TypeVar('T')
TKey = TypeVar('TKey')

class FacadeUtilities: 
    def to_list(orm_result : list[Row], value_function : Callable[[Row], T]) -> list[T]: 
        _list = []
        for row in orm_result:
            _list.append(value_function(row))
        return _list
    
    def to_dict(orm_result : list[Row], value_function : Callable[[Row], tuple[TKey, T]]) -> dict[TKey, T]:
        _dict = {}
        for row in orm_result:
            _tuple = value_function(row)
            _dict[_tuple[0]] = _tuple[1]
        return _dict
    
    def to_list_dict(orm_result : list[Row], value_function : Callable[[Row], tuple[TKey, T]]) -> dict[TKey, list[T]]:
        _dict : dict[TKey, list[T]] = {}
        for row in orm_result:
            _tuple = value_function(row)
            if _tuple[0] not in _dict:
                _dict[_tuple[0]] = []
            _dict[_tuple[0]].append(_tuple[1])
        return _dict
    
        