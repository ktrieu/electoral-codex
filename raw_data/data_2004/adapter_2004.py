import csv_adapter

class Adapter2004(csv_adapter.CsvAdapter):
    CAND_RIDING_NUM = 'Electoral District Number / No. de circonscription'
    CAND_PARTY_NAME = 'Political Affiliation'
    CAND_FIRST_NAME = 'Candidate\'s First Name / Prénom du candidat'
    CAND_INITIAL = 'Candidate\'s Initial / Initiale du candidat'
    CAND_LAST_NAME = 'Candidate\'s Family Name / Nom de famille du candidat'

    POLL_ID = 'Poll Number'
    POLL_NAME = 'Poll Name'
    POLL_RIDING_NAME = 'District'