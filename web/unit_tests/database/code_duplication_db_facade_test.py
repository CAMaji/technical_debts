from mocks.mock_app import init_mock_app
from database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from models.code_duplication import CodeDuplicationModel
from models.file_code_duplication import FileCodeDuplicationModel
from models.model import *
from models.model import db

REPO = 0
BRANCH = 1
COMMITS = 2
FILES = 3

def start_up() -> tuple[Repository, Branch, list[Commit], list[File]]:
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
    
    return (repo0, branch0, commit_list, file_list)

def test_insert_one_duplication():
    app = init_mock_app()
    with app.app_context():
        # arrange
        facade = CodeDuplicationDatabaseFacade()
        model = CodeDuplicationModel("hello world")
    
        # act
        try:
            facade.insert_one_duplication(model)
            result = db.session.query(CodeDuplicationModel).filter_by(id=model.id).first()
            db.session.delete(model)
            db.session.commit()
        # assert
        except Exception as e: 
            print(e)
            assert False
        assert result.text == "hello world"
    return

def test_insert_one_association():
    app = init_mock_app()
    with app.app_context():
        # arrange
        predef = start_up()
        facade = CodeDuplicationDatabaseFacade()
        file = predef[FILES][0]
        code_dup = CodeDuplicationModel("hello world")
        association = FileCodeDuplicationModel(code_dup.id, file.id, 10)
        # act
        try:
            db.session.add(code_dup)
            facade.insert_one_association(association)
            result = db.session.query(FileCodeDuplicationModel).filter_by(id=association.id).first()
            db.session.delete(association)
            db.session.commit()
            db.session.delete(code_dup)
            db.session.commit()
            
        # assert
        except Exception as e: 
            print(e)
            assert False
        assert result.code_duplication_id == code_dup.id
    return

def test_insert_many_duplications(): 
    app = init_mock_app()
    with app.app_context():
        # arrange
        facade = CodeDuplicationDatabaseFacade()
        models = [
            CodeDuplicationModel("hello world"),
            CodeDuplicationModel("world hello")
        ]
    
        # act
        try:
            facade.insert_many_duplications(models)
            result1 = db.session.query(CodeDuplicationModel).filter_by(id=models[0].id).first()
            result2 = db.session.query(CodeDuplicationModel).filter_by(id=models[1].id).first()
            db.session.delete(models[0])
            db.session.delete(models[1])
            db.session.commit()
        # assert
        except Exception as e: 
            print(e)
            assert False
        assert result1.text == "hello world"
        assert result2.text == "world hello"
    return
