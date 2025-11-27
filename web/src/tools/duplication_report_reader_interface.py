from src.reports.duplication_report import DuplicationReport

class DupliacationReportReaderInterface:
    def read(self, text: str) -> list[DuplicationReport]:
        return None