class FileStatistics: 
    avg_complexity : float
    identifiable_entities : int
    duplication_count : int
    lines_duplicated : int

    def __init__(self, avg_cmplx : float = 0.0, identif_entities : int = 0, dupl_count : int = 0, lines_dup : int = 0):
        self.avg_complexity = avg_cmplx
        self.identifiable_entities = identif_entities
        self.duplication_count = dupl_count
        self.lines_duplicated = lines_dup

        return