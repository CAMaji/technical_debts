from src.services.code_duplication_service import CodeDuplicationService
from src.models.model import File
from src.models.code_duplication import *
from src.models.file_code_duplication import *
from unit_tests.database.mocks.code_duplication_db_facade_mock import CodeDuplicationDatabaseFacadeMock

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
    mock.hooks.insert_one_duplication = hook
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
    mock.hooks.insert_one_association = hook
    service = CodeDuplicationService(mock)

    # act
    service.insert_one_association(file_code_dup)

    # assert
    assert called == True and expected == True

def test_insert_many_duplications():
    # arrange
    called = False
    expected = False
    code_dup_list = [CodeDuplicationModel("hello"), CodeDuplicationModel("World")]

    def hook(cd_list : list[CodeDuplicationModel]): 
        nonlocal called
        nonlocal expected
        nonlocal code_dup_list

        called = True
        expected = (
            len(cd_list) == len(code_dup_list) and
            cd_list[0].text == code_dup_list[0].text and
            cd_list[1].text == code_dup_list[1].text
        )
        return 

    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.insert_many_duplications = hook
    service = CodeDuplicationService(mock)

    # act
    service.insert_many_duplications(code_dup_list)

    # assert
    assert called == True and expected == True

def test_insert_many_associations():
    # arrange
    called = False
    expected = False
    file_code_dup_list = [
        FileCodeDuplicationModel('a', 'b', 3), 
        FileCodeDuplicationModel('c', 'd', 4)
    ]

    def hook(fcd_list : list[FileCodeDuplicationModel]): 
        nonlocal called
        nonlocal expected
        nonlocal file_code_dup_list

        called = True
        expected = (
            len(fcd_list) == len(file_code_dup_list) and
            fcd_list[0].id == file_code_dup_list[0].id and
            fcd_list[1].id == file_code_dup_list[1].id
        )
        return 

    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.insert_many_associations = hook
    service = CodeDuplicationService(mock)

    # act
    service.insert_many_associations(file_code_dup_list)

    # assert
    assert called == True and expected == True

def test_get_duplication_by_id(): 
    # arrange
    called = False
    expected_result = CodeDuplicationModel('test')
    expected_id = expected_result.id

    def hook(id : str) -> CodeDuplicationModel:
        nonlocal called
        nonlocal expected_result
        nonlocal expected_id

        called = True

        if id == expected_id:
            return expected_result
        
        return None
    
    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_duplication_by_id = hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_duplication_by_id(expected_id)

    # assert
    assert result != None
    assert called == True
    assert result.id == expected_result.id

def test_get_duplications_for_many_objs(): 
    class DummyObj:
        dummy_value : int
        dup_id : str
        id_attribute_name : str = "dup_id"

        def __init__(self, dup_id : str, dummy_value : int):
            self.dup_id = dup_id
            self.dummy_value = dummy_value
            return
    
    # arrange
    called = False
    expected_result = [
        CodeDuplicationModel('hello'), 
        CodeDuplicationModel('world')
    ]
    dummy_list = [
        DummyObj(expected_result[0].id, 14), 
        DummyObj(expected_result[1].id, 34)
    ]

    def hook(obj_list : list[object], id_attrib_name : str) -> list[CodeDuplicationModel]:
        nonlocal called
        nonlocal expected_result
        nonlocal dummy_list

        called = True

        if len(obj_list) != len(dummy_list) or id_attrib_name != DummyObj.id_attribute_name: 
            return None
        
        try: 
            i = 0
            while i < 2:
                id_val = getattr(obj_list[i], id_attrib_name)
                if id_val != expected_result[i].id:
                    return None
                i += 1
            return expected_result
        except:
            print("attribute name '" + id_attrib_name + "' is invalid.")
            return None

    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_duplications_for_many_objects = hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_duplications_for_many_objects(dummy_list, "dup_id")

    # assert
    assert result != None
    assert called == True

def test_get_duplications_for_one_file():
    # arrange
    first_call = False
    second_call = False
    file_id = "1"

    def get_associations_for_one_file_hook(hook_file_id : str) -> list[FileCodeDuplicationModel]:
        nonlocal first_call
        nonlocal file_id

        first_call = True
        if hook_file_id != file_id:
            return []
    
        return [
            FileCodeDuplicationModel('a', file_id, 30),
            FileCodeDuplicationModel('b', file_id, 32)
        ]
    
    def get_duplications_for_many_obj_hook(objs : list[object], id_attrib_name : str) -> list[CodeDuplicationModel]:
        nonlocal second_call
        second_call = True
        result = []
        if getattr(objs[0], id_attrib_name) == 'a':
            temp = CodeDuplicationModel("hello")
            temp.id = 'a'
            result.append(temp)
        if getattr(objs[1], id_attrib_name) == 'b':
            temp = CodeDuplicationModel("world")
            temp.id = 'b'
            result.append(temp)

        return result

    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_associations_for_one_file = get_associations_for_one_file_hook
    mock.hooks.get_duplications_for_many_objects = get_duplications_for_many_obj_hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_duplications_for_one_file(file_id)

    # assert
    assert len(result) > 0
    assert first_call == True and second_call == True
    assert result[0].text == "hello" and result[1].text == "world"

def test_get_associations_for_one_file(): 
    # arrange
    called = False
    file_id = '1'

    def hook(id : str) -> list[FileCodeDuplicationModel]:
        nonlocal called
        nonlocal file_id

        called = True
        if id != file_id:
            return []
        
        return [
            FileCodeDuplicationModel('a', file_id, 30),
            FileCodeDuplicationModel('b', file_id, 32)
        ]
    
    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_associations_for_one_file = hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_associations_for_one_file(file_id)

    # assert
    assert len(result) > 0
    assert called == True
    assert result[0].code_duplication_id == 'a'
    assert result[1].code_duplication_id == 'b'

def test_get_duplications_for_many_files():
    # arrange
    first_call_count = 0
    second_call_count = 0
    files = [
        File(id='1', name='fichier1', commit_id='c0'),
        File(id='2', name='fichier2', commit_id='c0'),
    ]

    def get_associations_for_one_file_hook(id : str) -> list[FileCodeDuplicationModel]:
        nonlocal first_call_count
        first_call_count += 1
        if id == '1':
            return [
                FileCodeDuplicationModel('a', '1', 30),
                FileCodeDuplicationModel('b', '1', 32)
            ]
        
        if id == '2':
            return [
                FileCodeDuplicationModel('a', '2', 30),
                FileCodeDuplicationModel('b', '2', 32)
            ]
        
        return []
    
    def get_duplications_for_many_obj_hook(objs : list[object], id_attrib_name : str) -> list[CodeDuplicationModel]:
        nonlocal second_call_count
        second_call_count += 1
        result = []
        if getattr(objs[0], id_attrib_name) == 'a':
            temp = CodeDuplicationModel("hello")
            temp.id = 'a'
            result.append(temp)
        if getattr(objs[1], id_attrib_name) == 'b':
            temp = CodeDuplicationModel("world")
            temp.id = 'b'
            result.append(temp)

        return result
    
    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_associations_for_one_file = get_associations_for_one_file_hook
    mock.hooks.get_duplications_for_many_objects = get_duplications_for_many_obj_hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_duplications_for_many_files(files)

    # assert
    assert first_call_count == 2 and second_call_count == 2
    assert len(result['fichier1']) == 2
    assert len(result['fichier2']) == 2

def test_get_stats_for_one_file(): 
    # arrange
    called = False
    file_id = 'a'

    def hook(id : str) -> list[FileCodeDuplicationModel]:
        nonlocal called
        nonlocal file_id

        called = True
        if id != file_id:
            return []
        
        return [
            FileCodeDuplicationModel('a', file_id, 30),
            FileCodeDuplicationModel('b', file_id, 32)
        ]
    
    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_associations_for_one_file = hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_stats_for_one_file(file_id)

    # assert
    assert called == True
    assert result.nb_of_associations == 2 and result.nb_of_duplicated_lines == 62

def test_get_stats_for_many_files():
    # arrange 
    call_count = 0
    files = [
        File(id='1', name='fichier1', commit_id='c0'),
        File(id='2', name='fichier2', commit_id='c0'),
    ]

    def hook(id : str) -> list[FileCodeDuplicationModel]:
        nonlocal call_count
        call_count += 1
        if id == '1':
            return [
                FileCodeDuplicationModel('a', '1', 30),
                FileCodeDuplicationModel('b', '1', 32)
            ]
        
        return []
    
    mock = CodeDuplicationDatabaseFacadeMock()
    mock.hooks.get_associations_for_one_file = hook
    service = CodeDuplicationService(mock)

    # act
    result = service.get_stats_for_many_files(files)

    # assert
    assert call_count == 2
    assert result['fichier1'].nb_of_associations == 2 and result['fichier1'].nb_of_duplicated_lines == 62
    assert result['fichier2'].nb_of_associations == 0 and result['fichier2'].nb_of_duplicated_lines == 0

#
# too complex to properly unit test at the moment
#

#def test_run_duplication_analyser(): 
#    return