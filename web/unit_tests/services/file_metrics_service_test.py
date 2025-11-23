from src.services.file_metrics_service import FileMetricsService
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.models.model import File
from src.interface.tech_debt_report import TechDebtMetrics

def test_get_tech_debt_metrics():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        complexity_called = 0
        entity_called = 0
        duplication_called = 0

        def get_average_complexities(self, files):
            LocalFacadeMock.complexity_called += 1
            return {
                'file0': 10.0,
                'file1': 30.0
            }
            
        def get_identifiable_entities_count(self, files):
            LocalFacadeMock.entity_called += 1
            return {
                'file0': 2.0,
                'file1': 3.0
            }

        def get_duplications_metrics(self, files):
            LocalFacadeMock.duplication_called += 1
            return {
                'file0': (3, 10),
                'file1': (5, 20)
            }
            
    mock = LocalFacadeMock()
    service = FileMetricsService(mock)
    files = [File(id='file0', name='file0.py', commit_id='...'),
             File(id='file1', name='file1.py', commit_id='...')]

    # act
    metrics = service.get_tech_debt_metrics(files)

    # assert
    assert len(metrics) == 2
    assert 'file0.py' in metrics and 'file1.py' in metrics
    assert type(metrics['file0.py']) == TechDebtMetrics
    assert metrics['file0.py'].duplications == 3
