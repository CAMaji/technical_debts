from models.model import Complexity, Function
from models.code_duplication import CodeDuplicationModel
from typing import Callable
from database.file_statistics_db_facade import FileStatisticsDatabaseFacade

class FileStatisticsDatabaseHooks:
    get_function_complexities_for_one_file      : Callable[[str], list[tuple[str, int]]]
    count_identifiable_entities_for_one_file    : Callable[[str], int]
    get_code_duplications_for_one_file          : Callable[[str], list[tuple[int, CodeDuplicationModel]]]
    get_function_complexities_for_many_files      : Callable[[list[str]], list[tuple[str, str, int]]]
    count_identifiable_entities_for_many_files  : Callable[[list[str]], list[tuple[str, int]]]
    get_code_duplications_for_many_files        : Callable[[list[str]], list[tuple[str, int, CodeDuplicationModel]]]

    def __init__(self):
        # I was too lazy to set every hook to None by hand.
        for _var in self.__dict__:
            setattr(self, _var, None)
        return
        

class FileStatisticsDatabaseFacadeMock(FileStatisticsDatabaseFacade):
    hooks : FileStatisticsDatabaseHooks

    def __init__(self):
        self.hooks = FileStatisticsDatabaseHooks()
        return

    def get_function_complexities_for_one_file(self, file_id : str) -> list[tuple[str, int]]:
        return self.hooks.get_function_complexities_for_one_file(file_id)
    
    def count_identifiable_entities_for_one_file(self, file_id) -> int:
        return self.hooks.count_identifiable_entities_for_one_file(file_id)
    
    def get_code_duplications_for_one_file(self, file_id) -> list[tuple[int, CodeDuplicationModel]]:
        return self.hooks.get_code_duplications_for_one_file(file_id)
    
    def get_function_complexities_for_many_files(self, file_id_list) -> list[tuple[str, str, int]]:
        return self.hooks.get_function_complexities_for_many_files(file_id_list)
    
    def count_identifiable_entities_for_many_files(self, file_id_list) -> list[tuple[str, int]]:
        return self.hooks.count_identifiable_entities_for_many_files(file_id_list)
    
    def get_code_duplications_for_many_files(self, file_id_list) -> list[tuple[str, int, CodeDuplicationModel]]:
        return self.hooks.get_code_duplications_for_many_files(file_id_list)
        