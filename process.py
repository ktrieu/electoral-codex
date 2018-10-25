import common_defs
import sqlite3
import processor

#barring some kind of royal rumble, this should be more than enough
MAX_CANDIDATES = 12

def save_to_db(candidates, ridings, poll_divs, year):
    conn = sqlite3.connect(year + '.db')
    c = conn.cursor()
    #create the necessary tables
    c.execute(r'DROP TABLE IF EXISTS candidates')
    c.execute(r'CREATE TABLE candidates (cand_id INTEGER, riding_id INTEGER, name TEXT, party TEXT)')
    c.execute(r'DROP TABLE IF EXISTS ridings')
    c.execute(r'CREATE TABLE ridings (riding_id INTEGER, name TEXT)')
    c.execute(r'DROP TABLE IF EXISTS poll_divisions')
    c.execute(r'CREATE TABLE poll_divisions (div_id TEXT, riding_id INTEGER, name TEXT)')
    #add result columns to ridings and poll divisions
    for i in range(MAX_CANDIDATES):
        c.execute(f'ALTER TABLE poll_divisions ADD COLUMN cand{i}_id INTEGER')
        c.execute(f'ALTER TABLE poll_divisions ADD COLUMN cand{i}_result INTEGER')
        c.execute(f'ALTER TABLE ridings ADD COLUMN cand{i}_id INTEGER') 
        c.execute(f'ALTER TABLE ridings ADD COLUMN cand{i}_result INTEGER') 
    conn.commit()
    #load data
    #build a list of candidates separately because they're in a double nested dict
    cand_list = list()
    for riding_cands in candidates.values():
        cand_list.extend(riding_cands.values())
    c.executemany('INSERT INTO candidates VALUES (?, ?, ?, ?)', map(candidate_to_tuple, cand_list))
    c.executemany('INSERT INTO ridings VALUES ' + generate_value_placeholder(2 + (MAX_CANDIDATES * 2)), 
                    map(riding_to_tuple, ridings.values()))
    c.executemany('INSERT INTO poll_divisions VALUES ' + generate_value_placeholder(3 + (MAX_CANDIDATES * 2)), 
                    map(polling_div_to_tuple, poll_divs))
    conn.commit()
    conn.close()
    print(f'{year} data saved.')

def generate_value_placeholder(n):
    return '(' + ', '.join(['?'] * n) + ')'

def candidate_to_tuple(candidate):
    return (candidate.cand_id, candidate.riding_id, candidate.name, candidate.party.name)

def gen_result_columns(results):
    result_list = list()
    for cand_id, result in results.items():
        result_list.append(cand_id)
        result_list.append(round(result))
    #pad out the list to fill up the rest of the columns
    if len(result_list) < MAX_CANDIDATES * 2:
        result_list.extend([None] * (MAX_CANDIDATES * 2 - len(result_list)))
    return result_list

def riding_to_tuple(riding):
    return (riding.riding_id, riding.name, *gen_result_columns(riding.results))

def polling_div_to_tuple(polling_div):
    return (polling_div.div_id, polling_div.riding_id, polling_div.name, *gen_result_columns(polling_div.results))

import raw_data.data_2004.adapter_2004
import raw_data.data_2006.adapter_2006
import raw_data.data_2008.adapter_2008

years = ['2004', '2006', '2008']
csv_adapters = {
    '2004' : raw_data.data_2004.adapter_2004.Adapter2004,
    '2006' : raw_data.data_2006.adapter_2006.Adapter2006,
    '2008' : raw_data.data_2008.adapter_2008.Adapter2008
}

for year in years:
    processor_obj = processor.Processor(year, csv_adapters[year])
    cand_dict, riding_dict, poll_divs = processor_obj.process_data()
    save_to_db(cand_dict, riding_dict, poll_divs, year)
