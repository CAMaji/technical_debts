from services.code_duplication import *
from models.code_duplication import *
from models.file_code_duplication import *
from mocks.database.code_duplication_db_facade_mock import CodeDuplicationDatabaseFacadeMock

def test_insert_one_duplication(): 
    # arrange 
    called = False
    expected = False
    code_dup = CodeDuplicationModel("hello world")

    def hook(cd : CodeDuplicationModel):
        nonlocal called
        nonlocal code_dup
        nonlocal expected
        called = True
        expected = (cd.text == code_dup.text)
        return

    mock = CodeDuplicationDatabaseFacadeMock()
    mock.insert_one_duplication_hook = hook
    service = CodeDuplicationService(mock)

    # act
    service.insert_one_duplication(code_dup)

    # assert
    assert called == True and expected == True

def test_insert_one_association():
    # arrange 
    called = False
    expected = False
    file_code_dup = FileCodeDuplicationModel('cd1', "f1", 10)

    def hook(fcd : FileCodeDuplicationModel):
        nonlocal called
        nonlocal file_code_dup
        nonlocal expected
        called = True
        expected = (
            fcd.file_id == file_code_dup.file_id and 
            fcd.code_duplication_id == file_code_dup.code_duplication_id and
            fcd.line_count == file_code_dup.line_count
        )
        return

    mock = CodeDuplicationDatabaseFacadeMock()
    mock.insert_one_association_hook = hook
    service = CodeDuplicationService(mock)

    # act
    service.insert_one_association(file_code_dup)

    # assert
    assert called == True and expected == True