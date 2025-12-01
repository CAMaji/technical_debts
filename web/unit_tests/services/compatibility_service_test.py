from src.reports.function_complexity_report import FunctionComplexityReport
from src.reports.file_complexity_report import FileComplexityReport
from src.reports.entity_report import EntityReport
from src.services.compatibility_service import CompatibilityService

def test_obj_to_func_complexity_dict():
    # arrange
    complixities = [{"file": "abc.py",
                     "function": "hello_world()",
                     "start_line": 1,
                     "cyclomatic_complexity": 8},
                    {"file": "abc.py",
                     "function": "have_a_good_day()",
                     "start_line": 20,
                     "cyclomatic_complexity": 15}]

    service = CompatibilityService()

    # act
    func_reports = service.obj_to_func_complexity_dict(complixities)

    # assert
    assert len(func_reports) == 1
    assert len(func_reports["abc.py"]) == 2
    assert func_reports["abc.py"][0].cyclomatic_complexity == 8
    assert func_reports["abc.py"][1].cyclomatic_complexity == 15
    return

def test_obj_to_file_complexity_dict():
    # mock
    class LocalServiceMock(CompatibilityService):
        called = 0
        params_valid = True
        complexities = [[{"file": "abc.py",
                          "function": "hello_world()",
                          "start_line": 1,
                          "cyclomatic_complexity": 8}],
                        [{"file": "abc.py",
                          "function": "good_morning()",
                          "start_line": 1,
                          "cyclomatic_complexity": 8}]]

        def obj_to_func_complexity_dict(self, func_list):
            LocalServiceMock.called += 1
            LocalServiceMock.params_valid &= len(func_list) == 1
            if(func_list[0] == LocalServiceMock.complexities[0][0]):
                return {"abc.py": [FunctionComplexityReport("abc.py", "hello_world()", 1, 8)]}
            elif(func_list[0] == LocalServiceMock.complexities[1][0]):
                return {"abc.py": [FunctionComplexityReport("abc.py", "good_morning()", 1, 8)]}
            else:
                LocalServiceMock.params_valid = False
                return {}
    # --------------
    # arrange
    service = LocalServiceMock()

    # act
    file_reports : dict[str, FileComplexityReport] = service.obj_to_file_complexity_dict(LocalServiceMock.complexities)

    # assert
    assert LocalServiceMock.called and LocalServiceMock.params_valid
    assert len(file_reports) == 1
    assert file_reports["abc.py"].complexity == 8
    assert len(file_reports["abc.py"].functions) == 2
    return

def test_obj_to_entity_dict():
    # arrange
    entities = [{"file_name": "abc.py", 
                 "entity_name": "todo",
                 "line_position": 10},
                {"file_name": "abc.py", 
                 "entity_name": "todo",
                 "line_position": 20}]
    service = CompatibilityService()

    # act
    result = service.obj_to_entity_dict(entities)

    # assert
    assert len(result) == 1
    assert "abc.py" in result
    assert len(result["abc.py"]) == 2
    return
