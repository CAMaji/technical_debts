import json

class CustomJsonEncoderInterface: 
    def encode(self):
        return {}
    
class CustomJsonEncoder: 

    def _raise_exception(obj : object):
        raise Exception(
            "Type '" + type(obj).__name__ + "' cannot be converted to a JSON dumpable object.\n" +
            "Type must be: list[any], dict[str, any], tuple[any], int, float, bool, None, or\n" +
            "be a class that extends '" + type(CustomJsonEncoderInterface).__name__ + "' and implements\n" +
            "the 'encode' method."
        )

    def _dict_to_raw(_dict: dict):
        for k in _dict:
            is_string : bool = isinstance(k, str)
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

    def _object_to_raw(_obj : object): 
        implements_interface : bool = isinstance(_obj, CustomJsonEncoderInterface)
        is_dict : bool = isinstance(_obj, dict)
        is_list : bool = isinstance(_obj, list)
        is_tuple : bool = isinstance(_obj, tuple)
        is_number : bool = isinstance(_obj, int) or isinstance(_obj, float)
        is_string : bool = isinstance(_obj, str) 
        is_boolean : bool = isinstance(_obj, bool)

        if implements_interface:
            return _obj.encode()
        
        if is_dict: 
            return CustomJsonEncoder._dict_to_raw(_obj)
        
        if is_list:
            return CustomJsonEncoder._list_to_raw(_obj)
        
        if is_tuple: 
            return CustomJsonEncoder._tuple_to_raw(_obj)

        if is_number or is_string or is_boolean or _obj == None:
            return _obj
    
        CustomJsonEncoder._raise_exception()
        return None # should not be reached

    def breakdown(obj : object):
        implements_interface : bool = isinstance(obj, CustomJsonEncoderInterface)
        is_dict : bool = isinstance(obj, dict)
        is_list : bool = isinstance(obj, list)
        is_tuple : bool = isinstance(obj, tuple)

        if implements_interface or is_dict or is_list or is_tuple:
            raw = CustomJsonEncoder._object_to_raw(obj)
            return raw
        

        CustomJsonEncoder._raise_exception()
        return None # should not be reached

    def dump(obj : object):
        raw = CustomJsonEncoder.breakdown(obj)
        return json.dumps(raw)
