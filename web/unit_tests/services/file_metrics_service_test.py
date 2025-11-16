from services.file_metrics_service import FileMetricsService, FileMetrics
from unit_tests.database.mocks.file_metrics_db_facade_mock import FileStatisticsDatabaseFacadeMock
from models.code_duplication import CodeDuplicationModel


def test_get_function_complexities_for_one_file():
    # arrange
    called = False
    file_id_ok = False
    test_file_id = "file0"
    test_func_name = "func0"

    def hook(file_id : str) -> list[tuple[str, int]]:
        nonlocal called
        nonlocal test_file_id
        nonlocal file_id_ok
        nonlocal test_func_name

        called = True
        file_id_ok = (file_id == test_file_id)
        return [(test_func_name, 1)]
    
    facade = FileStatisticsDatabaseFacadeMock()
    facade.hooks.get_function_complexities_for_one_file = hook
    service = FileMetricsService(facade)

    # act 
    result : dict[str, int] = service.get_function_complexities_for_one_file(test_file_id)

    # assert 
    assert called == True
    assert file_id_ok == True
    assert len(result) == 1
    assert result[test_func_name] == 1
    return

def test_count_identifiable_identities():
    # arrange
    called = False
    file_id_ok = False
    test_file_id = "file0"
    test_func_name = "func0"
    expected_result = 3

    def hook(file_id : str) -> int:
        nonlocal called
        nonlocal test_file_id
        nonlocal file_id_ok
        nonlocal test_func_name
        nonlocal expected_result

        called = True
        file_id_ok = (file_id == test_file_id)
        return expected_result
    
    facade = FileStatisticsDatabaseFacadeMock()
    facade.hooks.count_identifiable_entities_for_one_file = hook
    service = FileMetricsService(facade)

    # act 
    result : int = service.count_identifiable_identities_for_one_file(test_file_id)

    # assert 
    assert called == True
    assert file_id_ok == True
    assert result == expected_result
    return

def test_get_complexity_average_for_one_file():
    # arrange
    called = False
    file_id_ok = False
    test_file_id = "file0"
    test_func_name_list = ["func0", "func1", "func2"]
    test_complexity_list = [10, 20, 30]
    test_average = sum(test_complexity_list) / len(test_func_name_list)

    def hook(file_id : str) -> list[tuple[str, int]]:
        nonlocal called
        nonlocal test_file_id
        nonlocal file_id_ok
        nonlocal test_func_name_list
        nonlocal test_complexity_list

        called = True
        file_id_ok = (file_id == test_file_id)
        return [
            (test_func_name_list[0], test_complexity_list[0]),
            (test_func_name_list[1], test_complexity_list[1]),
            (test_func_name_list[2], test_complexity_list[2])
        ]
    
    facade = FileStatisticsDatabaseFacadeMock()
    facade.hooks.get_function_complexities_for_one_file = hook
    service = FileMetricsService(facade)

    # act 
    result : float = service.get_complexity_average_for_one_file(test_file_id)

    # assert
    assert result == test_average

def test_get_complexity_average_for_one_file__division_by_zero():
    # arrange
    called = False
    file_id_ok = False
    test_file_id = "file0"

    def hook(file_id : str) -> list[tuple[str, int]]:
        nonlocal called
        nonlocal file_id_ok
        called = True
        return [] # average can't be calculated if there is no elements, leads to div by zero
        
    facade = FileStatisticsDatabaseFacadeMock()
    facade.hooks.get_function_complexities_for_one_file = hook
    service = FileMetricsService(facade)

    # act 
    result : float = service.get_complexity_average_for_one_file(test_file_id)

    # assert 
    assert result == 0 # shows that divison by zero has been prevented.
    return

def test_get_code_duplications_stats_for_one_file():
    # arrange
    called = False
    file_id_ok = False
    test_file_id = "file0"
    expected_lines_dupped = 2 + 4 + 6
    expected_duplication_count = 3
    test_lines_dupped_count = [2, 4, 6]
    test_code_dup_model = [
        CodeDuplicationModel('a'), 
        CodeDuplicationModel('b'), 
        CodeDuplicationModel('c')
    ]

    def hook(file_id : str) -> list[tuple[int, CodeDuplicationModel]]: 
        nonlocal called
        nonlocal file_id_ok
        nonlocal test_file_id
        nonlocal test_lines_dupped_count
        nonlocal test_code_dup_model

        called = True
        file_id_ok = (file_id == test_file_id)
        return [
            (test_lines_dupped_count[0], test_code_dup_model[0]),
            (test_lines_dupped_count[1], test_code_dup_model[1]),
            (test_lines_dupped_count[2], test_code_dup_model[2]),
        ]
    
    facade = FileStatisticsDatabaseFacadeMock()
    facade.hooks.get_code_duplications_for_one_file = hook
    service = FileMetricsService(facade)
    
    # act 
    result = service.get_code_duplications_metrics_for_one_file(test_file_id)
    
    # assert
    assert result != None
    assert result[1] == expected_lines_dupped
    assert result[0] == expected_duplication_count

def test_get_metrics_for_one_file():
    # arrange
    hook1_called = False
    hook2_called = False
    hook3_called = False
    test_file_id = "file0"
    complexity0 = 1
    complexity1 = 10
    complexity2 = 4
    identifiable_entities_count = 10
    duplication_count = 2
    lines_dupped_0 = 10
    lines_dupped_1 = 37
    
    def get_function_complexities_for_one_file(file_id: str) -> list[tuple[str, int]]: 
        nonlocal hook1_called
        nonlocal test_file_id
        nonlocal complexity0
        nonlocal complexity1
        nonlocal complexity2
        hook1_called = True

        if file_id != test_file_id:
            return []
        return [("func0", complexity0), ("func1", complexity1), ("func2", complexity2)]
    
    def count_identifiable_entities_for_one_file(file_id: str) -> int:
        nonlocal hook2_called
        nonlocal test_file_id
        nonlocal identifiable_entities_count

        hook2_called = True
        if file_id != test_file_id:
            return 0
        return identifiable_entities_count
    
    def get_code_duplications_for_one_file(file_id: str) -> list[tuple[int, CodeDuplicationModel]]:
        nonlocal hook3_called
        nonlocal test_file_id
        nonlocal lines_dupped_0
        nonlocal lines_dupped_1

        hook3_called = True
        if file_id != test_file_id:
            return []
        return [
            (lines_dupped_0, CodeDuplicationModel('abababababa')),
            (lines_dupped_1, CodeDuplicationModel('cbcbcbcbcbc')),
        ]
    
    facade = FileStatisticsDatabaseFacadeMock()
    facade.hooks.get_function_complexities_for_one_file = get_function_complexities_for_one_file
    facade.hooks.count_identifiable_entities_for_one_file = count_identifiable_entities_for_one_file
    facade.hooks.get_code_duplications_for_one_file = get_code_duplications_for_one_file
    service = FileMetricsService(facade)

    # act
    result : FileMetrics = service.get_metrics_for_one_file(test_file_id, "fichier.py")
    
    # assert
    assert result.avg_complexity == (complexity0 + complexity1 + complexity2) / 3
    assert result.identifiable_entities == identifiable_entities_count
    assert result.duplication_count == duplication_count
    assert result.lines_duplicated == lines_dupped_0 + lines_dupped_1
    return

