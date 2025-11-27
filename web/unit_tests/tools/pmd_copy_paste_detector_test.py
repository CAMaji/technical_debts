from src.tools.pmd_copy_paste_detector import PMD_CopyPasteDetector
import re

def test_run_python(): 
    # arrange
    wrapper = PMD_CopyPasteDetector(20, [PMD_CopyPasteDetector.Language.PYTHON], "/app/unit_tests/tools/pmd_cpd_test_directory")
    expected_output = ""

    with open("/app/unit_tests/tools/pmd_cpd_test_directory/pmd_cpd_python_output.xml") as f:
        expected_output = f.read()
    expected_output = re.sub('timestamp=".+"', 'timestamp=""', expected_output) # We remove the timestamps, otherwise the test would always fail
    
    # act
    result = wrapper.run()
    result[0] = re.sub('timestamp=".+"', 'timestamp=""', result[0]) # We remove the timestamps, otherwise the test would always fail

    # assert
    assert result[0] == expected_output
