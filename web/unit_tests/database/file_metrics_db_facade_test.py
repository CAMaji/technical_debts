from unit_tests.mock_app import *
from models.model import *
from database.file_metrics_db_facade import FileMetricsDatabaseFacade
from database.file_metrics_db_facade import FileID_str, Complexity_int, FuncName_str, LinesDuppedCount_int

def test_get_function_complexities_for_one_file():
    app = init_mock_app()
    with app.app_context():
        # arrange 
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        file0 = predef[FILES][0]
    
        # act
        try:
            result : list[tuple[FuncName_str, Complexity_int]] = facade.get_function_complexities_for_one_file(file0.id)

            # assert
            assert len(result) == 4
            assert result[2][1] == 15  # in 'complexity_list' (see mock_app.py), 'file0' is linked with 'cplx2' 
        except Exception as e:
            print(e)
            assert False
    return

def test_count_identifiable_entities_for_one_file():
    app = init_mock_app()
    with app.app_context():
        # arrange 
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        file0 = predef[FILES][0]
    
        # act
        try:
            result : int = facade.count_identifiable_entities_for_one_file(file0.id)

            # assert
            assert result == 2 # in 'fie_list' (see mock_app.py), 'file0' is linked with 'fie0' & 'fie1'
        except Exception as e:
            print(e)
            assert False
    return

def test_get_code_duplications_for_one_file():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        file_list = predef[FILES]
        
        # act 
        try:
            result : list[tuple[LinesDuppedCount_int, CodeDuplicationModel]] = facade.get_code_duplications_for_one_file(file_list[0].id)

        # assert
            assert len(result) == 2
            assert result[0][1].text == 'hello' or result[0][1].text == 'world'
            assert result[1][1].text == 'world' or result[1][1].text == 'hello' # check 'mock_app.py' for mock data
        except Exception as e:
            print(e)
            assert False
    return

def test_get_function_complexities_for_many_files():
    app = init_mock_app()
    with app.app_context():
        # arrange 
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        file_list = predef[FILES]

        file_id_list : list[str] = []
        for f in file_list:
            file_id_list.append(f.id)
    
        # act
        try:
            result : list[tuple[FileID_str, FuncName_str, Complexity_int]] = facade.get_function_complexities_for_many_files(file_id_list)

            # assert
            assert len(result) == 8
            assert result[0][0] == 'file0' # check 'mock_app.py' for mock data                                           
        except Exception as e:
            print(e)
            assert False
    return

def test_count_identifiable_entities_for_many_files():
    app = init_mock_app()
    with app.app_context():
        # arrange 
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        file_list = predef[FILES]

        file_id_list : list[str] = []
        for f in file_list:
            file_id_list.append(f.id)
    
        # act
        try:
            result : list[tuple[str, int]] = facade.count_identifiable_entities_for_many_files(file_id_list)

            # assert
            assert len(result) == 4
        except Exception as e:
            print(e)
            assert False
    return

def test_get_code_duplications_for_many_files():
    app = init_mock_app()
    with app.app_context():
        # arrange 
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        file_list = predef[FILES]

        file_id_list : list[str] = []
        for f in file_list:
            file_id_list.append(f.id)
    
        # act
        try:
            result : list[tuple[FileID_str, LinesDuppedCount_int, CodeDuplicationModel]] = facade.get_code_duplications_for_many_files(file_id_list)

            # assert
            assert len(result) == 4
            assert result[0][2].text == 'hello' # check 'mock_app.py' for mock data                                           
        except Exception as e:
            print(e)
            assert False
    return