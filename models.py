from dataclasses import dataclass, field
from enum import Enum
from typing import DefaultDict
from sqlite3 import Cursor
from collections import defaultdict

ids: DefaultDict[type, int] = defaultdict(int)
def id_factory(id_type: type):
    new_id = ids[id_type]
    ids[id_type] += 1
    return new_id

class Party(Enum):
    Liberal = 'LIB'
    Conservative = 'CON'
    NDP = 'NDP'
    BQ = 'BQ'
    Green = 'GRN'
    PPC = 'PPC'
    Independent = 'IND'
    Other = 'OTH'

@dataclass
class Candidate:
    name: str
    party: Party
    incumbent: bool
    pk: int = field(default_factory=lambda: id_factory(Candidate))

    @classmethod
    def get_schema(cls):
        return '''
        CREATE TABLE candidate (
            name TEXT NOT NULL,
            party TEXT NOT NULL,
            incumbent INTEGER NOT NULL,
            pk INTEGER NOT NULL PRIMARY KEY
        )
        '''

@dataclass
class Riding:
    number: int
    name: str

    @classmethod
    def get_schema(cls):
        return '''
        CREATE TABLE riding (
            number INTEGER NOT NULL PRIMARY KEY,
            name TEXT NOT NULL
        )
        '''

@dataclass
class RidingResult:
    cand_id: int
    riding_num: int
    votes: int
    pk: int = field(default_factory=lambda: id_factory(RidingResult))

    @classmethod
    def get_schema(cls):
        return '''
        CREATE TABLE riding_result (
            cand_id INTEGER NOT NULL,
            riding_num INTEGER NOT NULL,
            votes INTEGER NOT NULL,
            pk INTEGER NOT NULL PRIMARY KEY,
            FOREIGN KEY(cand_id) REFERENCES candidate(pk),
            FOREIGN KEY(riding_num) REFERENCES riding(number)
        )
        '''

@dataclass
class PollingStation:
    number: int
    subdivision: int
    name: str
    riding_num: int
    pk: int = field(default_factory=lambda: id_factory(PollingStation))

    @classmethod
    def get_schema(cls):
        return '''
        CREATE TABLE polling_station (
            number INTEGER NOT NULL,
            subdivision INTEGER,
            name TEXT NOT NULL,
            riding_num INTEGER NOT NULL,
            pk INTEGER NOT NULL PRIMARY KEY,
            FOREIGN KEY(riding_num) REFERENCES riding(number)
        )
        '''

@dataclass
class PollingStationResult:
    cand_id: int
    station_id: int
    votes: int
    pk: int = field(default_factory=lambda: id_factory(PollingStationResult))

    @classmethod
    def get_schema(cls):
        return '''
        CREATE TABLE polling_station_result (
            cand_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            votes INTEGER,
            pk INTEGER NOT NULL PRIMARY KEY,
            FOREIGN KEY(cand_id) REFERENCES candidate(pk),
            FOREIGN KEY(station_id) REFERENCES polling_station(pk)
        )
        '''

def drop_tables(cursor: Cursor):
    cursor.execute(r'DROP TABLE IF EXISTS candidate')
    cursor.execute(r'DROP TABLE IF EXISTS riding')
    cursor.execute(r'DROP TABLE IF EXISTS riding_result')
    cursor.execute(r'DROP TABLE IF EXISTS polling_station')
    cursor.execute(r'DROP TABLE IF EXISTS polling_station_result')

def create_tables(cursor: Cursor):
    cursor.execute(Candidate.get_schema())
    cursor.execute(Riding.get_schema())
    cursor.execute(RidingResult.get_schema())
    cursor.execute(PollingStation.get_schema())
    cursor.execute(PollingStationResult.get_schema())