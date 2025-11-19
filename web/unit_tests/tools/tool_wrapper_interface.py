from src.tools.tool_wrapper_interface import ToolWrapperInterface

def test_run__expecting_exception():
    # arrange
    tool = ToolWrapperInterface()

    # act
    try: 
        tool.run(None)

        # assert
        assert False
    except Exception as e:
        assert True