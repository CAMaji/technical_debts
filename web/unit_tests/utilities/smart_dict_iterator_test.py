from src.utilities.smart_dict_iterator import SmartDictIterator

def test_smart_dict_iterator(): 
    # arrange 
    data : dict[str, int] = {"abc": 3, "def": 4, "ghi": 5}
    called = 0
    
    def get_value_for_each_iteration(t : tuple[str, int]) -> int:
        nonlocal called 
        called += 1
        return t[1]

    iter = SmartDictIterator(data, get_value_for_each_iteration)
    bucket = []

    # act
    for s in iter:
        bucket.append(s)

    # assert
    assert called == 3 and len(bucket) == 3
    assert bucket[0] == 3 and bucket[1] == 4 and bucket[2] == 5

