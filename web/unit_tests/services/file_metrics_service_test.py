from services.file_metrics_service import FileMetricsService, FileMetrics
from database.file_metrics_db_facade import FileMetricsDatabaseFacade
from models.code_duplication import CodeDuplicationModel
from models.model import File

def test_get_function_complexities_for_one_file():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        hooks_called : list[bool]

        def __init__(self):
            self.hooks_called = [False]

        def get_function_complexities_for_one_file(self, file_id) -> list[tuple[str, int]]:
            self.hooks_called[0] = True
            if file_id != "file0": return []
            else:                  return [("func0", 1)]
            
    facade = LocalFacadeMock()
    service = FileMetricsService(facade)

    # act 
    result : dict[str, int] = service.get_function_complexities_for_one_file("file0")

    # assert 
    assert facade.hooks_called[0] == True
    assert len(result) == 1
    assert result["func0"] == 1
    return

def test_count_identifiable_identities():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        hooks_called : list[bool]

        def __init__(self):
            self.hooks_called = [False]

        def count_identifiable_entities_for_one_file(self, file_id) -> int:
            self.hooks_called[0] = True
            if(file_id != "file0"): return 0
            else:                   return 3

    facade = LocalFacadeMock()
    service = FileMetricsService(facade)

    # act 
    result : int = service.count_identifiable_identities_for_one_file("file0")

    # assert 
    assert facade.hooks_called[0] == True
    assert result == 3
    return

def test_get_complexity_average_for_one_file():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        hooks_called : list[bool]

        def __init__(self):
            self.hooks_called = [False]

        # average can't be calculated if there is no elements, leads to div by zero
        def get_function_complexities_for_one_file(self, file_id) -> list[tuple[str, int]]:
            self.hooks_called[0] = True
            if file_id != "file0": return []
            else:                  return [("func0", 10), ("func1", 20), ("func2", 30)]
        
    facade = LocalFacadeMock()
    service = FileMetricsService(facade)

    # act 
    result : float = service.get_complexity_average_for_one_file("file0")

    # assert
    assert facade.hooks_called[0] == True
    assert result == (10+20+30)/3.0
    return

def test_get_complexity_average_for_one_file__division_by_zero():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        hooks_called : list[bool]

        def __init__(self):
            self.hooks_called = [False]

        # average can't be calculated if there is no elements, leads to div by zero
        def get_function_complexities_for_one_file(self, file_id) -> list[tuple[str, int]]:
            self.hooks_called[0] = True
            return []
        
    facade = LocalFacadeMock()
    service = FileMetricsService(facade)

    # act 
    result : float = service.get_complexity_average_for_one_file("file0")

    # assert 
    assert result == 0 # shows that divison by zero has been prevented.
    return

def test_get_code_duplications_stats_for_one_file():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        hooks_called : list[bool]

        def __init__(self):
            self.hooks_called = [False]

        def get_code_duplications_for_one_file(self, file_id) -> list[tuple[int, CodeDuplicationModel]]:
            self.hooks_called[0] = True
            if file_id != "file0": return []
            else:                  return [(2, CodeDuplicationModel('a')), 
                                           (4, CodeDuplicationModel('b')),
                                           (6, CodeDuplicationModel('c'))]
    
    facade = LocalFacadeMock()
    service = FileMetricsService(facade)
    
    # act 
    result = service.get_code_duplications_for_one_file("file0")
    
    # assert
    assert result != None
    assert facade.hooks_called[0] == True
    assert result[0] == 3
    assert result[1] == 2+4+6
    return

def test_get_metrics_for_one_file():
    # arrange
    class LocalFacadeMock(FileMetricsDatabaseFacade):
        hooks_called : list[bool]

        def __init__(self):
            self.hooks_called = [False, False, False]
            return

        def get_function_complexities_for_one_file(self, file_id) -> list[tuple[str, int]]:
            self.hooks_called[0] = True
            if file_id != "file0":  return []
            else:                   return [("func0", 1), ("func1", 10), ("func2", 4)]
        
        def count_identifiable_entities_for_one_file(self, file_id : str) -> int:
            self.hooks_called[1] = True
            if file_id != "file0": return 0
            else:                  return 10
        
        def get_code_duplications_for_one_file(self, file_id) -> list[tuple[int, CodeDuplicationModel]]:
            self.hooks_called[2] = True
            if file_id != "file0": return []
            else:                  return [(10, CodeDuplicationModel('abababababa')), (17, CodeDuplicationModel('cbcbcbcbcbc'))]
    
    facade = LocalFacadeMock()
    service = FileMetricsService(facade)

    # act
    result : FileMetrics = service.get_metrics_for_one_file("file0", "file0.py")
    
    # assert
    assert facade.hooks_called[0] == True and facade.hooks_called[1] == True and facade.hooks_called[2] == True
    assert result.avg_complexity == (1+10+4) / 3.0
    assert result.identifiable_entities == 10
    assert result.duplication_count == 2
    assert result.lines_duplicated == 27
    return

def test_get_metrics_for_many_files(): 
    # arrange
    class LocalServiceMock(FileMetricsService):
        hooks_called : list[int]

        def __init__(self):
            super().__init__(None)
            self.hooks_called = [0]

        def get_metrics_for_one_file(self, file_id, file_name) -> FileMetrics:
            self.hooks_called[0] += 1
            if file_id == 'file0' and file_name == 'file0.py':
                return FileMetrics('file0', 'file0.py', 10, 20, 30, 40)
            elif file_id == 'file1' and file_name == 'file1.py':
                return FileMetrics('file0', 'file0.py', 20, 40, 60, 80)
            else:
                return FileMetrics('file0', 'file0.py', 0, 0, 0, 0)
            
    service = LocalServiceMock()
    file_list = [
        File(id='file0',name='file0.py',commit_id='...'),
        File(id='file1',name='file1.py',commit_id='...'),
    ]
    
    # act
    result = service.get_metrics_for_many_files(file_list)

    # assert
    assert service.hooks_called[0] == 2
    assert len(result) == 2
    assert result[0].avg_complexity == 10
    assert result[1].identifiable_entities == 40
    return

