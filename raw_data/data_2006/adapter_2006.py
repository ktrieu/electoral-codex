import csv_adapter

class Adapter2006(csv_adapter.CsvAdapter):
    CAND_RIDING_NUM = 'Electoral District Number / No de circonscription'
    CAND_PARTY_NAME = 'Political Affiliation'
    CAND_FIRST_NAME = 'Candidate\'s First Name / Prénom du candidat'
    #this space is here on purpose, someone left it in the csv file
    CAND_INITIAL = ' Candidate\'s Initial(s) / Initiale(s) du candidat'
    CAND_LAST_NAME = 'Candidate\'s Family Name / Nom de famille du candidat'