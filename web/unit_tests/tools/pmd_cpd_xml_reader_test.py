from src.tools.pmd_cpd_xml_reader import *

def test_parse():
    # arrange
    xml_content = ""
    with open("/app/unit_tests/tools/pmd_cpd_test_directory/pmd_cpd_python_output.xml") as f:
        xml_content = f.read()
    parser = PMD_CPD_XmlReader("/app/unit_tests/tools")

    # act 
    reports = parser.parse(xml_content)

    # assert
    
    assert len(reports) == 2
    assert len(reports[0]._files) == 2
    assert len(reports[1]._files) == 2
    assert reports[0]._files[0].filename == "pmd_cpd_test_directory/file_a.py"
    assert reports[1]._files[1].filename == "pmd_cpd_test_directory/file_b.py"
    assert reports[0]._lines == 8
    #print({"fragment":reports[0]._fragment})
    assert reports[0]._fragment == '    numbers = [1, 2, 3]\n    total = 0\n    for n in numbers:\n        total += n\n    return total\n\n\ndef duplicate_three():\n'

