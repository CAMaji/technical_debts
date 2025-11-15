from utilities.custom_json_encoder import CustomJsonEncoder, CustomJsonEncoderInterface

class DummyClass(CustomJsonEncoderInterface):
    a : int
    b : float
    c : str

    def __init__(self, a : int, b : float, c : str): 
        self.a = a
        self.b = b
        self.c = c
        return
    
    def encode(self):
        return {
            "a": self.a,
            "b": self.b,
            "c": self.c
        }

def test_dump__interface_successful():
    # arrange
    dummy = DummyClass(1, 3.4, "a")
    
    # act
    result = CustomJsonEncoder.dump(dummy)

    # assert
    assert result == '{"a": 1, "b": 3.4, "c": "a"}'

def test_dump__list_successful():
    # arrange
    dummy_list = [
        DummyClass(1, 3.4, "a"),
        DummyClass(2, 9.4, "b")
    ]

    # act
    result = CustomJsonEncoder.dump(dummy_list)

    # assert
    assert result == '[{"a": 1, "b": 3.4, "c": "a"}, {"a": 2, "b": 9.4, "c": "b"}]'

def test_dump__dict_with_str_key_successful():
    # arrange
    dummy_dict = {
        "d1": DummyClass(1, 3.4, "a"),
        "d2": DummyClass(2, 9.4, "b")
    }

    # act
    result = CustomJsonEncoder.dump(dummy_dict)

    # assert
    assert result == '{"d1": {"a": 1, "b": 3.4, "c": "a"}, "d2": {"a": 2, "b": 9.4, "c": "b"}}'

def test_dump__dict_with_int_key_successful():
    # arrange
    dummy_dict = {
        0: DummyClass(1, 3.4, "a"),
        3: DummyClass(2, 9.4, "b")
    }

    # act
    result = CustomJsonEncoder.dump(dummy_dict)

    # assert
    assert result == '{"0": {"a": 1, "b": 3.4, "c": "a"}, "3": {"a": 2, "b": 9.4, "c": "b"}}'

def test_dump__tuple_successful():
    # arrange
    dummy_dict = (
        DummyClass(1, 3.4, "a"),
        "this is a string",
        None,
        2,
        3.4, 
        True
    )

    # act
    result = CustomJsonEncoder.dump(dummy_dict)

    # assert
    assert result == '[{"a": 1, "b": 3.4, "c": "a"}, "this is a string", null, 2, 3.4, true]'

def test_dump__invalid_object_failure(): 
    # arrange
    invalid_value = "hello"

    try:
        # act
        result = CustomJsonEncoder.dump(invalid_value)
    
        # assert
        assert False # Test fails if 'dump' does not raise an exception. 
                     # Should raise an exception if we try to dump an invalid object.

    except Exception as e:        
        assert True # Test succeeds if 'dump' raises an exception. 

def test_dump__invalid_dict_key_failure(): 
    # arrange
    invalid_dict = {
        ('a') : 3,
        ('b') : 5
    }

    try:
        # act
        result = CustomJsonEncoder.dump(invalid_dict)
    
        # assert
        assert False # Test fails if 'dump' does not raise an exception. 
                     # Should raise an exception if we try to dump a dict
                     # with key types other than 'str' or 'int'

    except Exception as e:
        assert True # Test succeeds if 'dump' raises an exception. 
