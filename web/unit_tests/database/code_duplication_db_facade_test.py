from mocks.mock_app import init_mock_app
from database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from models.code_duplication import CodeDuplicationModel
from models.file_code_duplication import FileCodeDuplicationModel
from models.model import *

REPO = 0
BRANCH = 1
COMMITS = 2
FILES = 3
DUPLICATIONS = 4
ASSOCIATIONS = 5

def start_up() -> tuple[Repository, Branch, list[Commit], list[File], list[CodeDuplicationModel], list[FileCodeDuplicationModel]]:
    # pre-defined values
    repo0 = Repository(id='repo0', owner='test', name='test')
    branch0 = Branch(id='branch0', name='test',repository_id=repo0.id)
    commit_list = [
        Commit(id='commit0', sha='0', date=datetime.now(), author='test', message='test0', branch_id=branch0.id),
        Commit(id='commit1', sha='1', date=datetime.now(), author='test', message='test1', branch_id=branch0.id)
    ]
    file_list = [
        File(id='file0', name='file0.py', commit_id=commit_list[0].id),
        File(id='file1', name='file1.py', commit_id=commit_list[0].id),
        File(id='file2', name='file2.py', commit_id=commit_list[0].id),
        File(id='file3', name='file0.py', commit_id=commit_list[1].id),
        File(id='file4', name='file1.py', commit_id=commit_list[1].id),
        File(id='file5', name='file2.py', commit_id=commit_list[1].id)
    ]

    duplication_list = [
        CodeDuplicationModel("hello"),
        CodeDuplicationModel("world"),
    ]

    association_list = [
        FileCodeDuplicationModel(duplication_list[0].id, file_list[0].id, 1),
        FileCodeDuplicationModel(duplication_list[0].id, file_list[1].id, 1),
        FileCodeDuplicationModel(duplication_list[1].id, file_list[0].id, 1),
        FileCodeDuplicationModel(duplication_list[1].id, file_list[1].id, 1)
    ]

    db.drop_all()
    db.create_all()
    db.session.add(repo0)
    db.session.commit()
    db.session.add(branch0)
    db.session.commit()
    db.session.add_all(commit_list)
    db.session.commit()
    db.session.add_all(file_list)
    db.session.commit()
    db.session.add_all(duplication_list)
    db.session.commit()
    db.session.add_all(association_list)
    db.session.commit()
    
    return (repo0, branch0, commit_list, file_list, duplication_list, association_list)

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
        associations = predef[ASSOCIATIONS]
        
        # act 
        try:
            result = facade.get_duplications_for_many_objs(associations, "code_duplication_id")

        # assert
            assert len(result) == 2
            assert result[0].text == 'hello' or result[0].text == 'world'
            assert result[1].text == 'world' or result[1].text == 'hello'
        
        except Exception as e:
            print(e)
            assert False
    return

