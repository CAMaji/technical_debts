from unit_tests.mock_app import *
from src.models.model import File
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.utilities.smart_list_iterator import SmartListIterator

def test_get_average_complexities():
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]

        # act
        try:
            avg_complexities = facade.get_average_complexities(files)

        # assert
        except Exception as e: 
            print(e)
            assert False
        
        assert len(avg_complexities) == 2
        assert avg_complexities['file0'] == (5+10+15+25) / 4.0
        assert avg_complexities['file1'] == (20+30+40+50) / 4.0
    return

def test_get_identifiable_entities_count():
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]

        # act
        try:
            entities = facade.get_identifiable_entities_count(files)

        # assert
        except Exception as e: 
            print(e)
            assert False

        assert len(entities) == 2
        assert entities['file0'] == 2
        assert entities['file1'] == 2
    return

def test_get_duplications_metrics():
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]

        # act
        try:
            duplications = facade.get_duplications_metrics(files)

        # assert            
        except Exception as e: 
            print(e)
            assert False

        assert len(duplications) == 2
        assert type(duplications['file0']) == tuple
        assert duplications['file0'][0] == 2 and duplications['file0'][1] == 20
        assert duplications['file1'][0] == 2 and duplications['file1'][1] == 20
    return

def test_get_duplications_metrics():
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]

        # act
        try:
            duplications = facade.get_duplications_metrics(files)

        # assert
        except Exception as e: 
            print(e)
            assert False

        assert len(duplications) == 2
        assert type(duplications['file0']) == tuple
        assert duplications['file0'][0] == 2 and duplications['file0'][1] == 20
        assert duplications['file1'][0] == 2 and duplications['file1'][1] == 20
    return

def test_get_files_per_duplication(): 
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]
        fragments = predef[CODE_FRAGMENTS]

        # act
        try:
            files_duplications = facade.get_files_per_duplication(files)

        # assert
        except Exception as e: 
            print(e)
            assert False

        assert len(files_duplications) == 2
        assert type(files_duplications[fragments[0].id]) == list
        assert type(files_duplications[fragments[1].id]) == list
        assert len(files_duplications[fragments[0].id]) == 2
        assert len(files_duplications[fragments[1].id]) == 2
        
        _list0 = files_duplications[fragments[0].id]
        _tuple0 = _list0[0]
        assert _tuple0[0] == 'file0'
        assert _tuple0[1] == fragments[0].line_count
        return

def test_get_functions_complexity(): 
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]

        # act
        try:
            func_complexities = facade.get_functions_complexity(files)

        # assert
        except Exception as e: 
            print(e)
            assert False

        print(func_complexities)
        assert len(func_complexities) == 2              # 2 files
        assert type(func_complexities['file0']) == list
        assert type(func_complexities['file1']) == list
        assert len(func_complexities['file0']) == 4     # 4 functions per file
        assert len(func_complexities['file1']) == 4
        
        _list0 = func_complexities['file0']
        _tuple0 = _list0[0]
        assert _tuple0[0] == 'def function0():'
        assert _tuple0[1] == 5.0
    return