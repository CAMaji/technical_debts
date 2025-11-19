from src.utilities.smart_list_iterator import SmartListIterator

def test_smart_list_iterator(): 
    # arrange 
    data : list[tuple[int, str]] = [(3, "abc"), (4, "def"), (5, "ghi")]
    called = 0
    
    def get_value_for_each_iteration(t : tuple[int, str]) -> str:
        nonlocal called 
        called += 1
        return t[1]

    iter = SmartListIterator[tuple[int, str], str](data, get_value_for_each_iteration)
    bucket = []

    # act
    for s in iter:
        bucket.append(s)

    # assert
    assert called == 3 and len(bucket) == 3
    assert bucket[0] == "abc" and bucket[1] == "def" and bucket[2] == "ghi"

