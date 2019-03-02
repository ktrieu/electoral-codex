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

    def __str__(self):
        return enum_str_table[self]

enum_str_table = {
    Party.LIB : 'LIB',
    Party.NDP : 'NDP',
    Party.CON : 'CON',
    Party.GRN : 'GRN',
    Party.BQ : 'BQ',
    Party.PPC : 'PC',
    Party.OTH : 'OTH'
}

party_str_table = {
    'Liberal' : Party.LIB,
    'N.D.P.' :  Party.NDP,
    'Conservative' : Party.CON,
    'Green Party' : Party.GRN,
    'Bloc Québécois' : Party.BQ,
    #2006 text mappings, because they changed them
    'Liberal Party of Canada' : Party.LIB,
    'Conservative Party of Canada' : Party.CON,
    'New Democratic Party' : Party.NDP,
    'Green Party of Canada' : Party.GRN,
    'Bloc Québécois' : Party.BQ
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
        self.total_votes = 0

class PollDivision:
    def __init__(self):
        self.div_num = 0
        self.div_suffix = 0
        self.riding_id = 0
        self.name = ''
        self.results = collections.Counter()
        self.total_votes = 0

class Summary:
    def __init__(self):
        self.party = ''
        self.seats = 0
        self.votes = 0
        self.leader = ''