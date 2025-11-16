from utilities.pmd_cpd_xml_parser import *

def test_parse():
    # arrange
    xml_content = ""
    with open("/app//unit_tests/utilities/pmd_cpd_xml_parser_test_directory/pmd_cpd_python_output.xml") as f:
        xml_content = f.read()
    parser = PmdCdpXmlParser("/app/unit_tests/tools")

    # act 
    parser.parse(xml_content)

    # assert 
    assert len(parser.associations) == 2
    assert len(parser.associations[0].files) == 2
    assert parser.associations[0].files[0] == "pmd_cpd_wrapper_test_directory/file_a.py"
    assert len(parser.associations[1].files) == 2
    assert parser.associations[1].files[1] == "pmd_cpd_wrapper_test_directory/file_b.py"
    return
