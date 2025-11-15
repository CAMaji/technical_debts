import json

class JsonEncoderInterface: 
    def encode(self):
        return json.dumps({})
    
class CustomJsonEncoder: 
    def dump(obj : object):
        dict_obj = CustomJsonEncoder.to_dict(obj)
        return json.dumps(dict_obj)
    
    def to_dict(obj : object):
        if isinstance(obj, JsonEncoderInterface) == True:
            return obj.encode()
        
        if isinstance(obj, dict):
            for k in obj:
                obj[k] = CustomJsonEncoder.to_dict(obj[k])
            return obj

        if isinstance(obj, list):
            i = 0
            length = len(obj)
            while i < length:
                obj[i] = CustomJsonEncoder.to_dict(obj[i])
                i += 1 
            return obj
    
        exception_message = (
            "Object of type '" + type(obj).__name__ + "' cannot be converted to JSON. "
            "Object must be either a 'dict', a 'list', or inherit 'JsonEncoderInterface'."
        )
        raise Exception(exception_message)
