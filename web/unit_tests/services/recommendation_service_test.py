from src.reports.recommendation_report import (RecommendationReport,
                                               RecommendationEnum, 
                                               ProblemEnum)
from src.reports.tech_debt_report import (FunctionDebtMetrics,
                                          FileDebtMetrics, 
                                          TechDebtReport, 
                                          RiskEnum)
from src.services.recommendations_service import RecommendationsService
from src.reports.duplication_report import DuplicationReport
from src.utilities.value_range import ValueRange
from src.utilities.pair import Pair

def test_get_no_problem():
    # arrange 
    service = RecommendationsService()

    # act
    result = service.get_no_problem()

    # assert 
    assert result.first == ProblemEnum.NO_PROBLEM.value
    assert result.second == ""

def test_get_global_risk():
    # arrange
    medians_no_problem = FileDebtMetrics(10.0, 11.0, 12.0, 13.0)
    medians_problem = FileDebtMetrics(29.0, 29.0, 29.0, 29.0)
    service = RecommendationsService()

    # act
    result_no_problem = service.get_global_risk(medians_no_problem)
    result_problem = service.get_global_risk(medians_problem)

    # assert 
    assert result_no_problem.first == ProblemEnum.NO_PROBLEM.value
    assert result_problem.first == ProblemEnum.GLOBAL_RISK_PROBLEM.value.replace("@1", str(RiskEnum.HIGH_RISK.name))
    assert result_problem.second == RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value
    
def test_get_global_duplication():
    # arrange
    class LocalReportMock(DuplicationReport):
        called : bool
        file_nb : int

        def __init__(self, file_nb : int):
            super().__init__(1, "")
            self.file_nb = file_nb
            self.called = False

        def get_file_nb(self):
            self.called = True
            return self.file_nb

    reports_no_problem = {"a": LocalReportMock(3)}
    reports_problem = {"b": LocalReportMock(7)}
    service = RecommendationsService()
    problem = ProblemEnum.GLOBAL_DUPLICATION_PROBLEM.value
    problem = problem.replace("@1", str(1))
    problem = problem.replace("@2", str(5))

    # act
    result_no_problem = service.get_global_duplication(reports_no_problem)
    result_problem = service.get_global_duplication(reports_problem)

    # assert
    assert reports_no_problem["a"].called == True
    assert result_no_problem.first == ProblemEnum.NO_PROBLEM.value
    assert result_no_problem.second == ""
    assert reports_problem["b"].called == True
    assert result_problem.first == problem
    assert result_problem.second == RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION.value

def test_get_file_avg_risk():
    # arrange
    service = RecommendationsService()
    problem = ProblemEnum.FILE_AVG_RISK_PROBLEM.value
    problem = problem.replace("@1", "file2.py")
    problem = problem.replace("@2", RiskEnum.HIGH_RISK.name)

    # act
    result_no_problem = service.get_file_avg_risk("file1.py", RiskEnum.LOW_RISK)
    result_problem = service.get_file_avg_risk("file2.py", RiskEnum.HIGH_RISK)

    # assert
    assert result_no_problem.first == ProblemEnum.NO_PROBLEM.value
    assert result_problem.first == problem
    assert result_problem.second == RecommendationEnum.FILE_RISK_RECOMMENDATION.value

def test_get_file_func_risk():
    # arrange
    service = RecommendationsService()
    problem = ProblemEnum.FILE_FUNC_RISK_PROBLEM.value
    problem = problem.replace("@1", "file1.py")
    problem = problem.replace("@2", "def func2():")
    problem = problem.replace("@3", RiskEnum.HIGH_RISK.name)

    # act
    result_no_problem = service.get_file_func_risk("file0.py", "def func1():", 9)
    result_problem = service.get_file_func_risk("file1.py", "def func2():", 23)

    # assert
    assert result_no_problem.first == ProblemEnum.NO_PROBLEM.value
    assert result_problem.first == problem
    assert result_problem.second == RecommendationEnum.FILE_RISK_RECOMMENDATION.value

def test_get_file_func_nb():
    # arrange
    service = RecommendationsService()
    problem = ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value
    problem = problem.replace("@1", "file1.py")
    problem = problem.replace("@2", "49")

    # act
    result_no_problem = service.get_file_func_nb("file0.py", 10)
    result_problem = service.get_file_func_nb("file1.py", 49)

    # assert
    assert result_no_problem.first == ProblemEnum.NO_PROBLEM.value
    assert result_problem.first == problem
    assert result_problem.second == RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value

def test_get_bug_to_func__no_todofixme():
    # arrange
    service = RecommendationsService()

    # act
    result = service.get_bug_to_func("file0.py", 10, 0)

    # assert
    assert result.first == ProblemEnum.NO_PROBLEM.value

def test_get_bug_to_func__ratio_smaller_than_limit():
    # arrange
    service = RecommendationsService()

    # act
    result = service.get_bug_to_func("file0.py", 10, 2)

    # assert
    assert result.first == ProblemEnum.NO_PROBLEM.value

def test_get_bug_to_func():
    # arrange
    service = RecommendationsService()
    problem = ProblemEnum.FILE_BUG_TO_FUNCTION_PROBLEM.value
    problem = problem.replace("@1", "file0.py")
    problem = problem.replace("@2", "10")
    problem = problem.replace("@3", "8")

    # act
    result = service.get_bug_to_func("file0.py", 10, 8)

    # assert
    assert result.first == problem
    assert result.second == RecommendationEnum.FILE_BUG_TO_FUNCTION_RECOMMENDATION.value

def test_get_global_subreport_elements():
    # arrange
    class LocalServiceMock(RecommendationsService):
        global_risk_called = False
        global_dupl_called = False

        def get_global_risk(self, median_metrics):
            LocalServiceMock.global_risk_called = True
            return Pair(ProblemEnum.GLOBAL_RISK_PROBLEM.value, RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value)
        
        def get_global_duplication(self, dup_reports):
            LocalServiceMock.global_dupl_called = True
            return Pair(ProblemEnum.GLOBAL_DUPLICATION_PROBLEM.value, RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION.value)
    
    service = LocalServiceMock()
    dummy_tech_dept_report = TechDebtReport(FileDebtMetrics(), FileDebtMetrics(), FileDebtMetrics())
    dummy_duplications_report = {}

    # act 
    result = service.get_global_subreport_elements(dummy_tech_dept_report, dummy_duplications_report)

    # assert 
    assert LocalServiceMock.global_dupl_called
    assert LocalServiceMock.global_risk_called
    assert len(result) == 2
    assert result[0].first == ProblemEnum.GLOBAL_RISK_PROBLEM.value
    assert result[1].first == ProblemEnum.GLOBAL_DUPLICATION_PROBLEM.value
    assert result[0].second == RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value
    assert result[1].second == RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION.value

def test_get_file_subreport_elements():
    # arrange
    class LocalServiceMock(RecommendationsService): 
        file_avg_risk_called = False
        file_func_nb_called = False
        bug_to_func_called = False

        def get_file_avg_risk(self, filename, risk):
            LocalServiceMock.file_avg_risk_called = True
            return Pair(ProblemEnum.FILE_AVG_RISK_PROBLEM.value, RecommendationEnum.FILE_RISK_RECOMMENDATION.value)
        
        def get_file_func_nb(self, filename, func_nb):
            LocalServiceMock.file_func_nb_called = True
            return Pair(ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value, RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value)
        
        def get_bug_to_func(self, filename, func_nb, todofixme_nb):
            LocalServiceMock.bug_to_func_called = True
            return Pair(ProblemEnum.FILE_BUG_TO_FUNCTION_PROBLEM.value, RecommendationEnum.FILE_BUG_TO_FUNCTION_RECOMMENDATION.value)
    
    service = LocalServiceMock()
    dummy_tech_debt_report = TechDebtReport.File("", 1.0, RiskEnum.HIGH_RISK, FileDebtMetrics())
    dummy_func_nb = 1

    # act 
    result = service.get_file_subreport_elements(dummy_tech_debt_report, dummy_func_nb)

    # assert 
    assert LocalServiceMock.file_avg_risk_called
    assert LocalServiceMock.file_func_nb_called 
    assert LocalServiceMock.bug_to_func_called
    assert len(result) == 3
    assert result[0].first == ProblemEnum.FILE_AVG_RISK_PROBLEM.value
    assert result[1].first == ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value
    assert result[2].first == ProblemEnum.FILE_BUG_TO_FUNCTION_PROBLEM.value
    assert result[0].second == RecommendationEnum.FILE_RISK_RECOMMENDATION.value
    assert result[1].second == RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value
    assert result[2].second == RecommendationEnum.FILE_BUG_TO_FUNCTION_RECOMMENDATION.value

def test_get_file_func_subreport_elements():
    # arrange
    class LocalServiceMock(RecommendationsService): 
        file_func_risk_called = 0

        def get_file_func_risk(self, filename, func_name, complexity):
            LocalServiceMock.file_func_risk_called += 1
            return Pair(ProblemEnum.FILE_FUNC_RISK_PROBLEM.value, RecommendationEnum.FILE_RISK_RECOMMENDATION.value)

    service = LocalServiceMock()
    dummy_func_debt_metrics = [FunctionDebtMetrics(), FunctionDebtMetrics()]

    # act
    result = service.get_file_func_subreport_elements(dummy_func_debt_metrics)

    # assert
    assert LocalServiceMock.file_func_risk_called == 2
    assert len(result) == 2
    assert result[0].first == ProblemEnum.FILE_FUNC_RISK_PROBLEM.value
    assert result[0].second == RecommendationEnum.FILE_RISK_RECOMMENDATION.value

def test_get_report():
    # arrange 
    class LocalServiceMock(RecommendationsService): 
        global_subreport_called = False
        file_subreport_called = 0
        file_func_subreport_called = 0
        params_valid = True

        def get_global_subreport_elements(self, tech_debt, duplications):
            LocalServiceMock.global_subreport_called = True
            LocalServiceMock.params_valid &= (tech_debt._metrics[0].filename == "file0.py" and 
                                              tech_debt._metrics[1].filename == "file1.py")
            LocalServiceMock.params_valid &= duplications == {}

            if LocalServiceMock.params_valid == False:
                print(tech_debt)
                print(duplications)
                raise Exception()

            return [
                Pair(ProblemEnum.GLOBAL_RISK_PROBLEM.value, RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value),
                Pair(ProblemEnum.NO_PROBLEM.value, "")
            ]

        def get_file_subreport_elements(self, file_debt, func_nb):
            LocalServiceMock.file_subreport_called += 1
            LocalServiceMock.params_valid &= ((file_debt.filename == "file0.py" and file_debt.priority == 1.0) or
                                              (file_debt.filename == "file1.py" and file_debt.priority == 1.0))
            LocalServiceMock.params_valid &= func_nb == 1 

            if LocalServiceMock.params_valid == False:
                print(file_debt)
                print(func_nb)
                raise Exception()

            return [
                Pair(ProblemEnum.FILE_AVG_RISK_PROBLEM.value, RecommendationEnum.FILE_RISK_RECOMMENDATION.value),
                Pair(ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value, RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value),
                Pair(ProblemEnum.FILE_BUG_TO_FUNCTION_PROBLEM.value, RecommendationEnum.FILE_BUG_TO_FUNCTION_RECOMMENDATION.value)
            ]
        
        def get_file_func_subreport_elements(self, func_metrics_list):
            LocalServiceMock.file_func_subreport_called += 1
            LocalServiceMock.params_valid &= len(func_metrics_list) == 1
            LocalServiceMock.params_valid &= (func_metrics_list[0].funcname == "func1" or
                                              func_metrics_list[0].funcname == "func2")
            
            if LocalServiceMock.params_valid == False:
                print(func_metrics_list)
                raise Exception()

            return [
                Pair(ProblemEnum.FILE_FUNC_RISK_PROBLEM.value, RecommendationEnum.FILE_RISK_RECOMMENDATION.value)
            ]
        
    service = LocalServiceMock()
    dummy_tech_debt_element_0 = TechDebtReport.File("file0.py", 1.0, RiskEnum.HIGH_RISK, FileDebtMetrics())
    dummy_tech_debt_element_1 = TechDebtReport.File("file1.py", 1.0, RiskEnum.HIGH_RISK, FileDebtMetrics())
    dummy_tech_debt_report = TechDebtReport(FileDebtMetrics(), FileDebtMetrics(), FileDebtMetrics())
    dummy_tech_debt_report.add_file(dummy_tech_debt_element_0)
    dummy_tech_debt_report.add_file(dummy_tech_debt_element_1)
    dummy_file_func_metrics = {"file0.py": [FunctionDebtMetrics("file0.py", "func1", 0.0)],
                               "file1.py": [FunctionDebtMetrics("file1.py", "func2", 0.0)]}

    # act
    result = service.get_report(dummy_tech_debt_report, {}, dummy_file_func_metrics)

    # assert 
    assert (LocalServiceMock.file_subreport_called == 2 and 
            LocalServiceMock.file_func_subreport_called == 2 and 
            LocalServiceMock.global_subreport_called)
    
    assert LocalServiceMock.params_valid
    
    assert len(result._files) == 2
    assert len(result._global.problems) == 1
    assert len(result._global.recommendations) == 1
    assert len(result._files[0].problems) == 4
    assert len(result._files[0].recommendations) == 3 
        # recommendations have 3 elements instead of 4 
        # because when adding the problem-recommendation pair, 
        # an elemment is inserted only if it is not already present
        # inside the set. 
        #
        # FILE_AVG_RISK_PROBLEM and FILE_FUNC_RISK_PROBLEM share
        # the same recommendation text, therefore the recommendation
        # text FILE_RISK_RECOMMENDATION will only be added once.

    return