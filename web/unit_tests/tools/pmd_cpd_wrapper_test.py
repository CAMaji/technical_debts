from src.tools.pmd_cpd_wrapper import PmdCpdWrapper
import re

def test_run_python(): 
    # arrange
    wrapper = PmdCpdWrapper(20, PmdCpdWrapper.Language.PYTHON, PmdCpdWrapper.ReportFormat.XML, "/app/unit_tests/tools/pmd_cpd_wrapper_test_directory")
    expected_output = ""

    with open("/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/pmd_cpd_python_output.xml") as f:
        expected_output = f.read()
    expected_output = re.sub('timestamp=".+"', 'timestamp=""', expected_output) # We remove the timestamps, otherwise the test would always fail
    
    # act
    result = wrapper.run()
    result = re.sub('timestamp=".+"', 'timestamp=""', result) # We remove the timestamps, otherwise the test would always fail

    # assert
    assert result == expected_output
