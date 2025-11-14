from models.code_duplication import *
from models.file_code_duplication import *
from sqlalchemy import or_

class CodeDuplicationDatabaseFacade: 
    def insert_one_duplication(self, code_dup : CodeDuplicationModel):
        db.session.add(code_dup)
        db.session.commit()
    
    def insert_one_association(self, association : FileCodeDuplicationModel):
        db.session.add(association)
        db.session.commit()

    def insert_many_duplications(self, code_dups : list[CodeDuplicationModel]): 
        for cd in code_dups:
            db.session.add(cd)
        db.session.commit()

    def insert_many_associations(self, associations : list[FileCodeDuplicationModel]):
        for ass in associations:
            db.session.add(ass)
        db.session.commit()

    def get_duplication_by_id(self, id : str) -> CodeDuplicationModel:
        return db.session.query(CodeDuplicationModel).filter_by(id=id).first()
    
    def get_associations_for_one_file(self, file_id : str) -> list[FileCodeDuplicationModel]:
        return db.session.query(FileCodeDuplicationModel).filter_by(file_id=file_id).all()
    
    def get_duplications_for_many_objs(self, obj_list : list[object], attrib_name : str) -> list[CodeDuplicationModel]: 
        clauses = or_()

        for obj in obj_list:
            clauses = clauses | (CodeDuplicationModel.id == getattr(obj, attrib_name))
        
        return db.session.query(CodeDuplicationModel).filter(clauses).all()