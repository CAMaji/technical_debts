from unit_tests.mock_app import *
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.models.code_fragment import CodeFragment
from src.models.duplication import Duplication
from src.models.model import *
from src.utilities.smart_list_iterator import SmartListIterator

def test_insert_many_fragments(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        facade = CodeDuplicationDatabaseFacade()
        duplications = [
            CodeFragment("hello world"),
            CodeFragment("world hello")
        ]
    
        # act
        try:
            facade.insert_many_fragments(duplications)

        # assert
        except Exception as e: 
            print(e)
            assert False
    return

def test_insert_many_duplications(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        file1 = predef[FILES][0]
        file2 = predef[FILES][1]
        duplication = predef[CODE_DUPLICATIONS][0]
        associations = [
            Duplication(duplication.id, file1.id, 10),
            Duplication(duplication.id, file2.id, 20)
        ]
    
        # act
        try:
            facade.insert_many_duplications(associations)

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
        duplication = predef[CODE_DUPLICATIONS][0]

        try:
            # act
            result = facade.get_duplication_by_id(duplication.id)
    
            # assert
            assert result != None and result.text == duplication.text
        except Exception as e:
            print(e)
            assert False
    return

def test_get_fragments_for_many_file():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        files = predef[FILES]
        iterator = SmartListIterator[File, str](files, lambda f: f.id)
        
        # act 
        try:
            result = facade.get_fragments_for_many_file(iterator)

        # assert
            assert type(result) == list
            assert len(result) == 4
            assert type(result[0]) == type((CodeFragment, Duplication))
            assert result[0][0].text == 'hello' and result[0][1].file_id == 'file1'
            assert result[1][0].text == 'hello' and result[1][1].file_id == 'file0'
        
        except Exception as e:
            print(e)
            assert False
    return
