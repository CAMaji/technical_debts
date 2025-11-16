from models.model import Complexity, Function
from typing import Callable
from database.file_statistics_db_facade import FileStatisticsDatabaseFacade

class FileStatisticsDatabaseFacadeMock(FileStatisticsDatabaseFacade):
    get_function_complexities_for_one_file_hook : Callable[[str], list[tuple[str, int]]]

    def __init__(self):
        self.get_function_complexities_for_one_file_hook = None
        return

    def get_function_complexities_for_one_file(self, file_id : str):
        return self.get_function_complexities_for_one_file_hook(file_id)
    
    