from src.models.code_fragment import CodeFragment
from src.models.code_fragment_referent import CodeFragmentReferent
from src.utilities.custom_json_encoder import CustomJsonEncoder

class CodeFragmentRelationships(CustomJsonEncoder): 
    fragment : CodeFragment
    referent : list[CodeFragmentReferent]

    def __init__(self):
        self.fragment = CodeFragment("")
        self.referent = []

    def encode(self):
        return {
            "fragment": self.fragment.encode(),
            "referent": CustomJsonEncoder.breakdown(self.referent)
        }