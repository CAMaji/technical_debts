from src.utilities.json_encoder import JsonEncoder
from src.utilities.pair import Pair
from dataclasses import dataclass
from enum import Enum

class ProblemEnum(Enum):
    NO_PROBLEM = "No problems."
    GLOBAL_RISK_PROBLEM = "50% of files in this commit have an average complexity ranked at or above @1."
    GLOBAL_DUPLICATION_PROBLEM = "@1 code duplication has been detected in over @2 files. Details in 'Duplication' section."
    FILE_AVG_RISK_PROBLEM = "File @1 has an average complexity ranked at or above @2."
    FILE_FUNC_RISK_PROBLEM = "File @1 has complexity of function @2 ranked at or above @3."
    FILE_FUNC_NUMBER_PROBLEM = "File @1 has a total of @2 functions."
    FILE_BUG_TO_FUNCTION_PROBLEM = "File @1 has a ratio of @2 'todo-fixme' comments for @3 functions."

class RecommendationEnum(Enum):
    GLOBAL_RISK_RECOMMENDATION = "Simplify logic and reduce complexity by limiting the number of independent paths in your functions. " \
                                 "Break appart large complex functions into smaller, simpler and testable functions."
    GLOBAL_DUPLICATION_RECOMMENDATION = "Move duplicated code into new coherent and cohesive functions and modules for reusability, " \
                                        "readability, maintainability and testability."
    FILE_RISK_RECOMMENDATION = "Simplify logic and reduce complexity by limiting the number of independent paths. " \
                               "Break appart large and complex logic blocks into smaller, loosely coupled and testable functions."
    FILE_FUNC_NUMBER_RECOMMENDATION = "Decrease the number of functions either by redesigning your architecture or creating a new module. " \
                                      "A large number of functions can be signs of high coupling and low cohesion, and usually decreases " \
                                      "readability and maintainability."
    FILE_BUG_TO_FUNCTION_RECOMMENDATION = "More efforts in bug fixing, refactoring and testing are needed. A high bug-to-function ratio can be " \
                                          "signs of lack of tests, low testability and high logic complexity."

class RecommendationReport(JsonEncoder.Interface):
    class SubReport(JsonEncoder.Interface):
        subject : str = ""
        problems : set[str] = set()
        recommendations : set[str] = set()
        
        def __init__(self, subject : str):
            self.subject = subject
            self.problems = set()
            self.recommendations = set()

        def add(self, problem_recomm : Pair[str, str]):
            if problem_recomm.first == ProblemEnum.NO_PROBLEM.value:
                return

            self.problems.add(problem_recomm.first)
            self.recommendations.add(problem_recomm.second)
            return
        
        def add_list(self, problem_recomm_list : list[Pair[str, str]]):
            for problem_recomm in problem_recomm_list:
                self.add(problem_recomm)
            return
    
    _global : SubReport
    _files : list[SubReport]

    def __init__(self, global_report : SubReport):
        self._global = global_report
        self._files = []
        return

    def add_file(self, file_report : SubReport):
        self._files.append(file_report)
        return
