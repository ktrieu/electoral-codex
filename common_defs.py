import enum

class Party(enum.Enum):
    LIB = enum.auto(),
    NDP = enum.auto(),
    CON = enum.auto(),
    GRN = enum.auto(),
    BQ = enum.auto(),
    PPC = enum.auto()

    @classmethod
    def from_string(cls, str):
        return party_str_table.get(str)

party_str_table = {
    'Liberal' : Party.LIB,
    'N.D.P.' :  Party.NDP,
    'Conservative' : Party.CON,
    'Green Party' : Party.GRN,
    'Bloc Québécois' : Party.BQ,
}

class Candidate:
    
    def __init__(self):
        self.cand_id = 0
        self.name = ''
        self.party = None