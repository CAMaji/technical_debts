from src.services.file_metrics_service import FileMetricsService
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.models.model import File
from src.reports.tech_debt_report import FileDebtMetrics

def test_get_file_metrics():
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
    metrics = service.get_file_metrics(files)

    # assert
    assert len(metrics) == 2
    assert 'file0.py' in metrics and 'file1.py' in metrics
    assert type(metrics['file0.py']) == FileDebtMetrics
    assert metrics['file0.py'].duplications == 3


def test_get_file_function_metrics():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        called = False

        def get_functions_complexity(self, files):
            LocalFacadeMock.called = True
            return {
                "file0": [('def f():', 29), ('def g():', 12)],
                "file1": [('def h():', 29), ('def i():', 12)]
            }
    
    mock = LocalFacadeMock()
    service = FileMetricsService(mock)
    files = [File(id='file0', name='file0.py', commit_id='...'),
             File(id='file1', name='file1.py', commit_id='...'),
             File(id='file2', name='file2.py', commit_id='...')]
    
    # act
    metrics = service.get_files_function_metrics(files)
    print(metrics)

    # assert 
    assert len(metrics) == 3
    assert 'file0.py' in metrics
    assert 'file1.py' in metrics 
    assert 'file2.py' in metrics
    assert len(metrics['file0.py']) == 2 
    assert len(metrics['file1.py']) == 2
    assert len(metrics['file2.py']) == 0
    assert metrics['file0.py'][0].funcname == 'def f():'
    assert metrics['file1.py'][0].funcname == 'def h():'