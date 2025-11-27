from src.tools.duplication_report_reader_interface import DupliacationReportReaderInterface

def test_parse():
    # arrange
    reader = DupliacationReportReaderInterface()

    # act
    result = reader.read("")

    # assert
    assert result == None