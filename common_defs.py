import enum
import collections

class Party(enum.Enum):
    LIB = enum.auto(),
    NDP = enum.auto(),
    CON = enum.auto(),
    GRN = enum.auto(),
    BQ = enum.auto(),
    PPC = enum.auto()
    OTH = enum.auto()

    @classmethod
    def from_string(cls, str):
        party = party_str_table.get(str)
        if party is None:
            return cls.OTH
        else:
             return party

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
        self.riding_id = 0
        self.name = ''
        self.party = None

class Riding:
    def __init__(self):
        self.riding_id = 0
        self.name = ''
        self.results = collections.Counter()

class PollDivision:
    def __init__(self):
        self.div_id = 0
        self.riding_id = 0
        self.name = ''
        self.results = collections.Counter()