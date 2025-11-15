from utilities.custom_json_encoder import CustomJsonEncoder, JsonEncoderInterface

class DummyClass(JsonEncoderInterface):
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

def test_dump():
    # arrange
    dummy_list = [
        DummyClass(1, 3.4, "a"),
        DummyClass(2, 9.4, "b")
    ]

    # act
    result = CustomJsonEncoder.dump(dummy_list)

    # assert
    assert result == '[{"a": 1, "b": 3.4, "c": "a"}, {"a": 2, "b": 9.4, "c": "b"}]'