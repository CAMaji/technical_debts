from services.file_statistics_service import FileStatisticsService
from unit_tests.database.mocks.file_statistics_db_facade_mock import FileStatisticsDatabaseFacadeMock

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
    facade.get_function_complexities_for_one_file_hook = hook
    service = FileStatisticsService(facade)

    # act 
    result : dict[str, int] = service.get_function_complexities_for_one_file(test_file_id)

    # assert 
    assert called == True
    assert file_id_ok == True
    assert len(result) == 1
    assert result[test_func_name] == 1
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
    facade.get_function_complexities_for_one_file_hook = hook
    service = FileStatisticsService(facade)

    # act 
    result : float = service.get_complexity_average_for_one_file(test_file_id)

    # assert
    assert result == test_average



