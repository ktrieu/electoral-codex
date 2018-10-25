class CsvAdapter:

    @classmethod
    def cand_get_riding_num(cls, line):
        return line['Electoral District Number / No de circonscription']

    @classmethod
    def cand_get_party(cls, line):
        return line['Political Affiliation']

    @classmethod 
    def cand_get_name(cls, line):
        name_list = [line['Candidate\'s First Name / Prénom du candidat'].strip(), 
                     #this space is here on purpose, someone left it in the csv file
                     line[' Candidate\'s Initial(s) / Initiale(s) du candidat'].strip(),
                     line['Candidate\'s Family Name / Nom de famille du candidat'].strip()]
        return ' '.join(filter(None, name_list))