import json
from enum import Enum

class CustomJsonEncoder: 

    def encode(self): 
        return {}
    
    def _raise_exception(obj : object):
        raise Exception(
            "Type '" + type(obj).__name__ + "' cannot be converted to a JSON dumpable object.\n" +
            "Type must be: list[any], dict[str, any], tuple[any], int, float, bool, None, or\n" +
            "be a class that extends '" + type(CustomJsonEncoder).__name__ + "' and implements\n" +
            "the 'encode' method."
        )

    def _enum_to_raw(_enum: Enum):
        return CustomJsonEncoder._tuple_to_raw((_enum.name, _enum.value))

    def _dict_to_raw(_dict: dict):
        for k in _dict:
            is_string  = isinstance(k, str)
            is_int: int = isinstance(k, int)
            if is_string or is_int:
                _dict[k] = CustomJsonEncoder._object_to_raw(_dict[k])
            else:
                raise Exception("For JSON encoding, only 'str' and 'int' are valid 'dict' key types.\n"
                                "Recieved: " + type(k).__name__)
        return _dict

    def _list_to_raw(_list: list[object]):
        i = 0
        m = len(_list)
        while i < m:
            _list[i] = CustomJsonEncoder._object_to_raw(_list[i])
            i += 1
        return _list
    
    def _tuple_to_raw(_tuple: tuple[object]):
        temp_list = []
        for v in _tuple:
            temp_list.append(CustomJsonEncoder._object_to_raw(v))
        return temp_list
    
    def _set_to_raw(_set: set[object]): 
        temp_list = []
        for v in _set:
            temp_list.append(CustomJsonEncoder._object_to_raw(v))
        return temp_list

    def _object_to_raw(_obj : object): 
        is_encodable = isinstance(_obj, CustomJsonEncoder)
        is_dict  = isinstance(_obj, dict)
        is_list  = isinstance(_obj, list)
        is_tuple  = isinstance(_obj, tuple)
        is_number  = isinstance(_obj, int) or isinstance(_obj, float)
        is_string  = isinstance(_obj, str) 
        is_boolean  = isinstance(_obj, bool)
        is_enum  = isinstance(_obj, Enum)
        is_set  = isinstance(_obj, set)
        
        if is_encodable:
            return _obj.encode()

        if is_dict: 
            return CustomJsonEncoder._dict_to_raw(_obj)
        
        if is_list:
            return CustomJsonEncoder._list_to_raw(_obj)
        
        if is_tuple: 
            return CustomJsonEncoder._tuple_to_raw(_obj)
        
        if is_enum:
            return CustomJsonEncoder._enum_to_raw(_obj)
        
        if is_set: 
            return CustomJsonEncoder._set_to_raw(_obj)

        if is_number or is_string or is_boolean or _obj == None:
            return _obj

        CustomJsonEncoder._raise_exception(_obj)

    def breakdown(obj):
        """
        breaks appart complex python objects into 
        simpler objects that can be dumped as json
        with `json.dumps()`.
        """
        return CustomJsonEncoder._object_to_raw(obj)

    def dump(obj):
        """
        Converts a python object into a JSON string.
        """
        raw = CustomJsonEncoder.breakdown(obj)
        return json.dumps(raw)
