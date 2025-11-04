from models import db
from models.model import *

from lizard import analyze_file
import services.function_service as function_service
import services.complexity_service as complexity_service
import services.identifiable_entity_service as identifiable_entity_service


def calculate_cyclomatic_complexity_analysis(file, code):
    cyclomatic_complexity_analysis = []
    analysis = analyze_file.analyze_source_code(file.name, code)
    for func in analysis.function_list:
        # ensure function record exists
        function = function_service.get_function_by_name_and_file(func.name, file.id)
        if not function:
            function = function_service.create_function(func.name, func.start_line, file.id)

        # update or create complexity
        existing_complexity = Complexity.query.filter_by(function_id=function.id).first()

        if existing_complexity:
            existing_complexity.value = func.cyclomatic_complexity
            db.session.commit()
        else:
            complexity_service.create_complexity(func.cyclomatic_complexity, function.id)

        cyclomatic_complexity_analysis.append({
            "file": file.name,
            "function": func.name,
            "start_line": func.start_line,
            "cyclomatic_complexity": func.cyclomatic_complexity
        })

    return cyclomatic_complexity_analysis


def calculate_identifiable_identities_analysis(file, code):
    identifiable_entity_analysis = []

    # get all the identifiable identities to search for
    identities = identifiable_entity_service.get_all_identifiable_identities()
    for identity in identities:
        # search the file for the identity (e.g. <TODO>, <FIXME>)
        found_identities = identifiable_entity_service.search_identifable_identity(code, identity.name)

        # link the found identity to the file it was found in
        for line in found_identities:
            identifiable_entity_service.create_file_entity(identity.id, file.id, line)

            identifiable_entity_analysis.append({
                "file": file.name,
                "start_line": line,
                "entity_name": identity.name,
            })

    return identifiable_entity_analysis
