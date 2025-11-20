class DuplicationReport: 
    class _DuplicationInstance: 
        filename: str
        from_line : int
        from_column : int
        to_line : int
        to_column : int

        def __init__(self, filename:str, from_line:int, to_line:int, from_column:int, to_column:int):
            self.filename = filename
            self.from_line = from_line
            self.from_column = from_column
            self.to_line = to_line
            self.to_column = to_column

    lines : int
    fragment : str
    instances : list[_DuplicationInstance]
    _i : int
    
    def __init__(self, lines:int, fragment:str):
        self.lines = lines
        self.fragment = fragment
        self.filenames = []
        self.instances = []
        self._i = 0
        return
    
    def add(self, filename:str, from_line:int, to_line:int, from_column:int, to_column:int):
        instance = DuplicationReport._DuplicationInstance(filename, from_line, to_line, from_column, to_column)
        self.instances.append(instance)

    def __iter__(self):
        self._i = 0
        return self
    
    def __next__(self): 
        if self._i >= len(self.instances):
            raise StopIteration
        ret = self.instances[self._i]
        self._i += 1
        return ret
