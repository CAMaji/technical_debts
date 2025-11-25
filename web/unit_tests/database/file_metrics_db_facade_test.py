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

def test_get_functions_complexity(): 
    # arrange
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()

        db.session.add(Function(id='func8', name='def function8():', line_position=0, file_id='file0'))
        db.session.commit()
        db.session.add(Complexity(id='cplx8', value='20', function_id='func8'))
        db.session.commit()

        facade = FileMetricsDatabaseFacade()
        files = predef[FILES]

        # act
        try:
            func_complexities = facade.get_functions_complexity(files)

        # assert
        except Exception as e: 
            print(e)
            assert False
            
        assert func_complexities['file0'] == [('def function0():', 5.0), 
                                              ('def function1():', 10.0),
                                              ('def function2():', 15.0),
                                              ('def function3():', 25.0),
                                              ('def function8():', 20.0)]
        assert func_complexities['file1'] == [('def function4():', 20.0), 
                                              ('def function5():', 30.0),
                                              ('def function6():', 40.0),
                                              ('def function7():', 50.0)]
    return