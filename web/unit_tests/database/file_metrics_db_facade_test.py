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
            assert len(avg_complexities) == 2
            assert avg_complexities['file0'] == (5+10+15+25) / 4.0
            assert avg_complexities['file1'] == (20+30+40+50) / 4.0

        except Exception as e: 
            print(e)
            assert False
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
            assert len(entities) == 2
            assert entities['file0'] == 2
            assert entities['file1'] == 2

        except Exception as e: 
            print(e)
            assert False
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
            assert len(duplications) == 2
            assert type(duplications['file0']) == tuple
            assert duplications['file0'][0] == 2 and duplications['file0'][1] == 20
            assert duplications['file1'][0] == 2 and duplications['file1'][1] == 20

        except Exception as e: 
            print(e)
            assert False
    return
