from src.tools.tool_interface import ToolInterface

def test_run__expecting_exception():
    # arrange
    tool = ToolInterface()

    # act
    result = tool.run()

    # assert
    assert result == []