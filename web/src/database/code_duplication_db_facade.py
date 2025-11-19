from src.models.code_fragment import *
from src.models.duplication import *
from src.models.model import File
from src.utilities.smart_list_iterator import SmartListIterator
from src.utilities.facade_utilities import FacadeUtilities
from sqlalchemy.orm import Query
from sqlalchemy.engine import Row

class CodeDuplicationDatabaseFacade: 
    def insert_many_fragments(self, fragments : list[CodeFragment]): 
        for cd in fragments:
            db.session.add(cd)
        db.session.commit()

    def insert_many_duplications(self, duplications : list[Duplication]):
        for dups in duplications:
            db.session.add(dups)
        db.session.commit()

    def get_duplication_by_id(self, id : str) -> CodeFragment:
        return db.session.query(CodeFragment).filter_by(id=id).first()
    
    def get_fragments_for_many_file(self, file_list_iterator : SmartListIterator[File, str]) -> list[tuple[CodeFragment, Duplication]]:
        query : Query = db.session.query(CodeFragment, Duplication)
        query : Query = query.join(Duplication, Duplication.code_fragment_id==CodeFragment.id)
        query : Query = query.filter(Duplication.file_id.in_(file_list_iterator))
        return FacadeUtilities.to_list(query.all(), lambda row: (row[0], row[1]))

    