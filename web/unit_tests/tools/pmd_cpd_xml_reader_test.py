from src.tools.pmd_cpd_xml_reader import *

def test_constructor():
    # arrange
    path1 = "/app/unit_tests/tools"
    path2 = "/app/unit_tests/tools/"

    # act
    parser1 = PMD_CPD_XmlReader(path1)
    parser2 = PMD_CPD_XmlReader(path2)

    # assert
    assert parser1._directory == "/app/unit_tests/tools/"
    assert parser2._directory == "/app/unit_tests/tools/"


def test_parse():
    # arrange
    expected_fragment = '    numbers = [1, 2, 3]\n    total = 0\n    for n in numbers:\n        total += n\n    return total\n\n\ndef duplicate_three():\n'
    repo_path = "/app/unit_tests/tools"
    xml_path = "/app/unit_tests/tools/pmd_cpd_test_directory/pmd_cpd_python_output.xml"
    
    io = open(xml_path)
    xml_content = io.read()
    io.close()
    
    parser = PMD_CPD_XmlReader(repo_path)

    # act 
    reports = parser.read(xml_content)

    # assert
    assert len(reports) == 2

    report0 = reports[0]
    assert report0._lines == 8
    assert report0._fragment == expected_fragment
    assert len(report0._files) == 2
    assert report0._files[0].filename == "pmd_cpd_test_directory/file_a.py"
