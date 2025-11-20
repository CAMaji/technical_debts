from src.services.code_duplication_service import CodeDuplicationService
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.models.duplication_report import DuplicationReport
from src.models.model import File
from src.models.code_fragment import *
from src.models.duplication import *

def test_insert_v2():
    # arrange
    class LocalFacadeMock(CodeDuplicationDatabaseFacade):
        frag_called = 0
        dupl_called = 0
        order_followed = True
        params_valid = True

        def insert_many_fragments(self, fragments):
            LocalFacadeMock.frag_called += 1
            LocalFacadeMock.params_valid &= (len(fragments) == 2)
            LocalFacadeMock.order_followed &= (LocalFacadeMock.dupl_called == 0)
            return
        
        def insert_many_duplications(self, associations):
            LocalFacadeMock.dupl_called += 1
            LocalFacadeMock.params_valid &= (len(associations) == 4)
            LocalFacadeMock.order_followed &= (LocalFacadeMock.frag_called != 0)
            return
    
    mock = LocalFacadeMock()
    service = CodeDuplicationService(mock)
    fragments = [CodeFragment("hello", 10), CodeFragment("world", 11)]
    duplications = [Duplication(fragments[0].id, 'file0', 10), Duplication(fragments[1].id, 'file0', 11),
                    Duplication(fragments[0].id, 'file1', 10), Duplication(fragments[1].id, 'file1', 11)]

    # act 
    service.insert(fragments, duplications)

    # assert
    assert LocalFacadeMock.frag_called == 1
    assert LocalFacadeMock.dupl_called == 1
    assert LocalFacadeMock.params_valid
    assert LocalFacadeMock.order_followed

def test_get_duplication_by_id(): 
    # arrange
    class LocalFacadeMock(CodeDuplicationDatabaseFacade):
        called = False
        params_valid = False

        def get_duplication_by_id(self, id):
            LocalFacadeMock.called = True
            LocalFacadeMock.params_valid = id == 'test_id'
            inst = CodeFragment('test')
            inst.id = 'test_id'
            return inst
    
    mock = LocalFacadeMock()
    service = CodeDuplicationService(mock)

    # act
    result = service.get_fragment_by_id('test_id')

    # assert
    assert LocalFacadeMock.called and LocalFacadeMock.params_valid
    assert result.id == 'test_id' and result.text == 'test'

def test_get_fragments_for_many_file_v2():
    # arrange 
    class LocalFacadeMock(CodeDuplicationDatabaseFacade):
        called = False
        params_valid = False

        def get_fragments_for_many_file(self, file_list_iterator):
            LocalFacadeMock.called = True
            LocalFacadeMock.params_valid = (
                file_list_iterator.data[0].id == 'file0' and 
                file_list_iterator.data[1].id == 'file1'
            )
            
            cd0 = CodeFragment("hello", 10)
            cd1 = CodeFragment("world", 20)
            cd0.id = 'c0'
            cd1.id = 'c1'

            return [
                (cd0, Duplication(cd0.id, 'file0', 10)),
                (cd0, Duplication(cd0.id, 'file1', 10)),
                (cd1, Duplication(cd1.id, 'file0', 20)),
                (cd1, Duplication(cd1.id, 'file1', 20))
            ]
        
    mock = LocalFacadeMock()
    service = CodeDuplicationService(mock)

    # act
    result = service.get_fragments_for_many_files([
        File(id='file0',name='file0.py',commit_id='...'),
        File(id='file1',name='file1.py',commit_id='...')
    ])

    # assert 
    assert LocalFacadeMock.called and LocalFacadeMock.params_valid
    assert len(result) == 2
    assert len(result['c0'].referent) == 2

def test_insert_elements_from_parsed_xml(): 
    # arrange
    class LocalServiceMock(CodeDuplicationService):
        called = False
        params_valid = False

        def __init__(self):
            super().__init__(None)

        def insert(self, fragments, duplications):
            LocalServiceMock.called = True
            LocalServiceMock.params_valid = (len(fragments) == 2) and (len(duplications) == 4)

    report0 = DuplicationReport(3, "hello world")
    report0.add("file0.py", 0, 3, 0, 10)
    report0.add("file1.py", 10, 13, 0, 10)

    report1 = DuplicationReport(6, "world hello")
    report1.add("file0.py", 0, 5, 0, 15)
    report1.add("file1.py", 10, 15, 0, 15)

    reports = [report0, report1]

    files = [
        File(id='file0', name='file0.py', commit_id='...'),
        File(id='file1', name='file1.py', commit_id='...'),
    ]

    service = LocalServiceMock()

    # act
    service.insert_elements_from_parsed_xml(reports, files)

    # assert
    assert LocalServiceMock.called and LocalServiceMock.params_valid
