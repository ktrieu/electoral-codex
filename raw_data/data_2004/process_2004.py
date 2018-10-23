import csv
import common_defs

DATA_PATH = 'raw_data/data_2004/'

def load_candidates():
    candidates = dict()
    cand_id = 0
    with open(DATA_PATH + 'candidates.tsv', 'r') as cand_file:
        cand_reader = csv.reader(cand_file, delimiter='\t')
        #skip header
        next(cand_reader)
        for line in cand_reader:
            cand = common_defs.Candidate()
            cand.riding_id = int(line[0])
            cand.cand_id = cand_id
            cand.party = common_defs.Party.from_string(line[3])
            #join together first, middle and last
            name_list = [line[6].strip(), line[7].strip(), line[5].strip()]
            cand.name = ' '.join(filter(None, name_list))
            candidates[cand.name] = cand
            cand_id += 1
    return candidates

def load_ridings():
    with open(DATA_PATH + 'ridings.csv', 'r') as ridings_file:
        ridings = dict()
        ridings_reader = csv.reader(ridings_file)
        #skip header
        next(ridings_reader)
        for line in ridings_reader:
            riding = common_defs.Riding()
            riding.riding_id = int(line[0])
            name_raw = line[1]
            #deal with ridings that have different names in French and English
            slash_idx = name_raw.find('/')
            if slash_idx == -1:
                riding.name = name_raw.strip()
            else:
                riding.name = name_raw[0:slash_idx]
            ridings[riding.riding_id] = riding
    return ridings
            

def process_data():
    print('Processing data for 2004...')
    print('Loading candidates...')
    cand_dict = load_candidates()
    print('Candidates loaded.')
    print('Loading ridings...')
    ridings_dict = load_ridings()
    print('Ridings loaded.')
