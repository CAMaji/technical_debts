from src.utilities.value_range import ValueRange

def test_value_is_within():
    # arrange
    vr = ValueRange[int](0, 100)

    # act
    result0 = vr.is_value_within(40)
    result1 = vr.is_value_within(-1)
    
    # assert 
    assert result0
    assert not result1
