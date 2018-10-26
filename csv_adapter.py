class CsvAdapter:

    #column names
    CAND_RIDING_NUM = ''
    CAND_PARTY_NAME = ''
    CAND_FIRST_NAME = ''
    CAND_INITIAL = ''
    CAND_LAST_NAME = ''

    POLL_NAME = ''
    POLL_ID = ''
    POLL_RIDING_NAME = ''

    #encodings
    CAND_ENCODING = 'cp1252'
    POLL_ENCODING = 'cp1252'

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

    @classmethod
    def poll_get_name(cls, line):
        return line[cls.POLL_NAME].strip()

    @classmethod
    def poll_get_riding_name(cls, line):
        return line[cls.POLL_RIDING_NAME].strip()

    @classmethod
    def poll_get_id(cls, line):
        id = line.get(cls.POLL_ID)
        if id is None:
            return cls.poll_get_name(line)
        else:
            return id.strip()
    
    