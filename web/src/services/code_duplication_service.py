from src.models.code_fragment import *
from src.models.duplication import *
from src.models.code_fragment import CodeFragment
from src.models.code_fragment_referent import CodeFragmentReferent
from src.models.code_fragment_relationships import CodeFragmentRelationships
from src.models.duplication_report import DuplicationReport
from src.models.model import File
from src.database.code_duplication_db_facade import *

class CodeDuplicationService: 
    _facade : CodeDuplicationDatabaseFacade

    def __init__(self, facade : CodeDuplicationDatabaseFacade): 
        self._facade = facade

    def insert(self, fragments : list[CodeFragment], duplications : list[Duplication]):
        self._facade.insert_many_fragments(fragments)
        self._facade.insert_many_duplications(duplications)

    def get_fragment_by_id(self, id : str) -> CodeFragment:
        return self._facade.get_duplication_by_id(id)

    def get_fragments_for_many_files(self, files : list[File]) -> dict[str, CodeFragmentRelationships]:
        lookup_table : dict[str, File] = {}
        for f in files: 
            lookup_table[f.id] = f

        iterator = SmartListIterator[File, str](files, lambda f: f.id)
        frag_dupl_list = self._facade.get_fragments_for_many_file(iterator)
        referents_dict : dict[str, CodeFragmentRelationships] = {}

        for frag_dupl in frag_dupl_list:
            cf : CodeFragment = frag_dupl[0]
            dupl : Duplication = frag_dupl[1]
            file = lookup_table[dupl.file_id]

            if cf.id not in referents_dict:
                referents_dict[cf.id] = CodeFragmentRelationships()
                referents_dict[cf.id].fragment = cf
                referents_dict[cf.id].referent = []

            referent = CodeFragmentReferent(file, dupl)
            referents_dict[cf.id].referent.append(referent)
        return referents_dict
      
    def insert_elements_from_parsed_xml(self, reports : list[DuplicationReport], files : list[File]):  
        file_registry : dict[str, File] = {}
        for file in files: 
            file_registry[file.name] = file

        association_list : list[Duplication] = []
        fragments_list : list[CodeFragment] = []

        for r in reports:
            code_dup = CodeFragment(r.fragment)
            fragments_list.append(code_dup)

            for instance in r:
                if instance.filename not in file_registry:
                    msg = "Duplication detection tool has found '"+ instance.filename + "', " \
                          "but file does not appear in provided file list."
                    print(msg)
                    raise Exception(msg)
                file = file_registry[instance.filename]
                lines = ValueRange(instance.from_line, instance.to_line)
                columns = ValueRange(instance.from_column, instance.to_column)
                association = Duplication(code_dup.id, file.id, r.lines, lines, columns) 
                association_list.append(association)

        self.insert(fragments_list, association_list)
        return
