import csv
import os
import common_defs

DATA_PATH = 'raw_data/data_2004/'
POLL_DIV_FOLDER = 'poll_by_poll/'

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
            
    return ridings

def read_candidate_cols(header, candidates):
    candidate_cols = dict()
    for idx, item in enumerate(header):
        if item in candidates:
            candidate_cols[idx] = candidates[item]
    return candidate_cols

def load_riding_from_poll_csv(id, ridings, line):
    riding = common_defs.Riding()
    riding.riding_id = id
    name_raw = line[0]
    #deal with ridings that have different names in French and English
    slash_idx = name_raw.find('/')
    if slash_idx == -1:
        riding.name = name_raw.strip()
    else:
        riding.name = name_raw[0:slash_idx]
    ridings[riding.riding_id] = riding
    ridings[id] = riding


def poll_divs_from_file(ridings, candidates, file_name):
    RIDING_ID_BEGIN = 10
    RIDING_ID_LEN = 5
    MOBILE_POLL_NAME = 'Mobile poll/Bureau itinérant'
    riding_id = int(file_name[RIDING_ID_BEGIN:RIDING_ID_BEGIN + RIDING_ID_LEN])
    merged_dict = dict()
    poll_divs = dict()
    with open(DATA_PATH + POLL_DIV_FOLDER + file_name, 'r') as poll_div_file:
        poll_div_reader = csv.reader(poll_div_file)
        #skip the header
        next(poll_div_reader)
        #load the riding
        load_riding_from_poll_csv(riding_id, ridings, next(poll_div_reader))
        #reset the file
        poll_div_file.seek(0)
        header = next(poll_div_reader)
        cand_cols = read_candidate_cols(header, candidates)
        for line in poll_div_reader:
            poll_div = common_defs.PollDivision()
            poll_div.name = line[2].strip()
            if poll_div.name == MOBILE_POLL_NAME:
                #mobile polls don't show up on the map and get folded into a different division
                #we can skip them
                continue
            if line[1] == '':
                poll_div.div_id = poll_div.name
            else:
                poll_div.div_id = line[1]
            poll_div.riding_id = riding_id
            if 'Merged with No.' in line[3]:
                #this poll has been merged with another one, record that and move on
                merged_id = line[3][line[3].rfind(' ') + 1:]
                if merged_dict.get(merged_id) == None:
                    merged_dict[merged_id] = list()
                merged_dict[merged_id].append(poll_div.div_id)
            elif line[3] == 'Void' or line[3] == 'No poll held':
                #no one voted here
                pass
            else:
                for idx, cand in cand_cols.items():
                    poll_div.results[cand] = int(line[idx])
            poll_divs[poll_div.div_id] = poll_div
    if len(merged_dict) > 0:
        print('Splitting merged poll divisions...')
        for merged, merge_to in merged_dict.items():
            #plus one because the merged poll division gets a share as well
            divisor = len(merge_to) + 1
            merged_div = poll_divs[merged]
            for cand, result in merged_div.results.items():
                merged_div.results[cand] = result / divisor
                for merge_to_id in merge_to:
                    poll_div = poll_divs[merge_to_id]
                    poll_div.results[cand] = result / divisor
        print('Merged poll divisions split.')
    print(f'Poll divisions loaded for riding {ridings[riding_id].name}, id {riding_id}.')
    return poll_divs
            

def load_poll_divs(ridings, candidates):
    poll_divs = list()
    for poll_file_name in os.listdir(DATA_PATH + POLL_DIV_FOLDER):
        divs_from_file = poll_divs_from_file(ridings, candidates, poll_file_name)
        poll_divs.extend(divs_from_file.values())
    return poll_divs
            

def process_data():
    print('Loading data for 2004...')
    print('Loading candidates...')
    cand_dict = load_candidates()
    print('Candidates loaded.')
    ridings_dict = dict()
    #there is no global list of ridings and their ids
    #so we have to load them along with poll divisions
    print('Loading poll divisions and ridings....')
    poll_divs = load_poll_divs(ridings_dict, cand_dict)
    print('Poll divisions and ridings loaded.')
    print('2004 data loaded.')
    return cand_dict, ridings_dict, poll_divs
