from src.utilities.pmd_cpd_xml_parser import *

def test_parse():
    # arrange
    xml_content = ""
    with open("/app/unit_tests/utilities/pmd_cpd_xml_parser_test_directory/pmd_cpd_python_output.xml") as f:
        xml_content = f.read()
    parser = PmdCdpXmlParser("/app/unit_tests/tools")

    # act 
    parser.parse(xml_content)
    reports = parser.get_reports()

    # assert 
    assert len(reports) == 2
    assert len(reports[0].instances) == 2
    assert len(reports[1].instances) == 2
    assert reports[0].instances[0].filename == "pmd_cpd_wrapper_test_directory/file_a.py"
    assert reports[1].instances[1].filename == "pmd_cpd_wrapper_test_directory/file_b.py"
    return
