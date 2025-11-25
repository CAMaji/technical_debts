from src.tools.reader_interface import ReaderInterface

def test_parse():
    # arrange
    reader = ReaderInterface()

    # act
    result = reader.parse("")

    # assert
    assert result == None