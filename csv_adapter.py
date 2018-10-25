class CsvAdapter:

    #column names
    CAND_RIDING_NUM = ''
    CAND_PARTY_NAME = ''
    CAND_FIRST_NAME = ''
    CAND_INITIAL = ''
    CAND_LAST_NAME = ''

    @classmethod
    def cand_get_riding_num(cls, line):
        return line[cls.CAND_RIDING_NUM]

    @classmethod
    def cand_get_party(cls, line):
        return line[cls.CAND_PARTY_NAME]

    @classmethod 
    def cand_get_name(cls, line):
        name_list = [line[cls.CAND_FIRST_NAME].strip(), 
                     line[cls.CAND_INITIAL].strip(),
                     line[cls.CAND_LAST_NAME].strip()]
        return ' '.join(filter(None, name_list))
    
    