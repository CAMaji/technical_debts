import json

class JsonEncoderInterface: 
    def encode(self):
        return json.dumps({})
    
class CustomJsonEncoder: 
    def dump(obj : object):
        if isinstance(obj, JsonEncoderInterface) == True:
            return obj.encode()
        
        if isinstance(obj, dict):
            for k in obj:
                obj[k] = CustomJsonEncoder.dump(obj[k])
            return json.dumps(obj)

        if isinstance(obj, list):
            i = 0
            length = len(obj)
            while i < length:
                obj[i] = CustomJsonEncoder.dump(obj[i])
                i += 1
            return json.dumps(obj)
    
        raise Exception("Conversion of object to JSON must be dict, list, or inherit JsonEncoderInterface.")
