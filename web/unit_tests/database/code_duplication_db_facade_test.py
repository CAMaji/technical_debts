from unit_tests.mock_app import *
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.models.code_duplication import CodeDuplicationModel
from src.models.file_code_duplication import FileCodeDuplicationModel
from src.models.model import *

def test_insert_duplication():
    app = init_mock_app()
    with app.app_context():
        # arrange
        facade = CodeDuplicationDatabaseFacade()
        model = CodeDuplicationModel("hello world")
    
        # act
        try:
            facade.insert_one_duplication(model)

        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_insert_one_association():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        file = predef[FILES][0]
        duplication = predef[DUPLICATIONS][0]
        association = FileCodeDuplicationModel(duplication.id, file.id, 10)

        # act
        try:
            facade.insert_one_association(association)
            
        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_insert_many_duplications(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        facade = CodeDuplicationDatabaseFacade()
        duplications = [
            CodeDuplicationModel("hello world"),
            CodeDuplicationModel("world hello")
        ]
    
        # act
        try:
            facade.insert_many_duplications(duplications)

        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_insert_many_associations(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        file1 = predef[FILES][0]
        file2 = predef[FILES][1]
        duplication = predef[DUPLICATIONS][0]
        associations = [
            FileCodeDuplicationModel(duplication.id, file1.id, 10),
            FileCodeDuplicationModel(duplication.id, file2.id, 20)
        ]
    
        # act
        try:
            facade.insert_many_associations(associations)

        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_get_duplication_by_id():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        duplication = predef[DUPLICATIONS][0]

        try:
            # act
            result = facade.get_duplication_by_id(duplication.id)
    
            # assert
            assert result != None and result.text == duplication.text
        except Exception as e:
            print(e)
            assert False
    return

def test_get_associations_for_one_file():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        file = predef[FILES][0]
        
        # act 
        try:
            result = facade.get_associations_for_one_file(file.id)

        # assert
            assert len(result) == 2
        
        except Exception as e:
            print(e)
            assert False
    return

def test_get_duplications_for_many_objs():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        associations = predef[FILE_DUPLICATION]
        
        # act 
        try:
            result = facade.get_duplications_for_many_objects(associations, "code_duplication_id")

        # assert
            assert len(result) == 2
            assert result[0].text == 'hello' or result[0].text == 'world'
            assert result[1].text == 'world' or result[1].text == 'hello'
        
        except Exception as e:
            print(e)
            assert False
    return

