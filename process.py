import common_defs
import sqlite3
import processor

def save_to_db(candidates, ridings, poll_divs, year):
    conn = sqlite3.connect(year + '.db')
    c = conn.cursor()
    #create the necessary tables
    c.execute(r'DROP TABLE IF EXISTS candidates')
    c.execute(r'CREATE TABLE candidates (cand_id INTEGER, riding_id INTEGER, name TEXT, party TEXT)')
    c.execute(r'DROP TABLE IF EXISTS ridings')
    c.execute(r'CREATE TABLE ridings (riding_id INTEGER, name TEXT, winning_party TEXT, margin REAL)')
    c.execute(r'DROP TABLE IF EXISTS poll_divisions')
    c.execute(r'CREATE TABLE poll_divisions (div_id TEXT, riding_id INTEGER, name TEXT, winning_party TEXT, margin REAL)')
    c.execute(r'DROP TABLE IF EXISTS riding_candidates')
    c.execute(r'CREATE TABLE riding_candidates (cand_id INTEGER, riding_id INTEGER, result INTEGER)')
    c.execute(r'DROP TABLE IF EXISTS poll_candidates')
    c.execute(r'CREATE TABLE poll_candidates (cand_id INTEGER, riding_id INTEGER, div_id TEXT, result INTEGER)')
    #since candidates is a double-nested list we have to unpack it separately
    cand_list = list()
    for riding_cands in candidates.values():
        cand_list.extend(riding_cands.values())
    cand_values = map(candidate_to_tuple, cand_list)
    c.executemany(r'INSERT INTO candidates VALUES (?, ?, ?, ?)', cand_values)
    riding_values = map(lambda x: riding_to_tuple(x, candidates), ridings.values())
    c.executemany(r'INSERT INTO ridings VALUES (?, ?, ?, ?)', riding_values)
    poll_div_values = map(lambda x: polling_div_to_tuple(x, candidates), poll_divs)
    c.executemany(r'INSERT INTO poll_divisions VALUES (?, ?, ?, ?, ?)', poll_div_values)
    riding_candidates = generate_riding_candidates(ridings)
    c.executemany(r'INSERT INTO riding_candidates VALUES (?, ?, ?)', riding_candidates)
    poll_candidates = generate_poll_candidates(poll_divs)
    c.executemany(r'INSERT INTO poll_candidates VALUES (?, ?, ?, ?)', poll_candidates)
    conn.commit()
    conn.close()
    print(f'{year} data saved.')

def calc_margin(results, riding_cands):
    if len(results) == 0:
        return ('UNK', 0)
    sorted_cands = sorted(riding_cands.values(), key=lambda x: results[x.cand_id])
    winning_party = sorted_cands[-1].party
    margin = results[sorted_cands[-1].cand_id] - results[sorted_cands[-2].cand_id]
    return (str(winning_party), margin)

def candidate_to_tuple(candidate):
    return (candidate.cand_id, candidate.riding_id, candidate.name, candidate.party.name)

def riding_to_tuple(riding, cands):
    winner, margin = calc_margin(riding.results, cands[riding.riding_id])
    return (riding.riding_id, riding.name, winner, margin)

def polling_div_to_tuple(polling_div, cands):
    winner, margin = calc_margin(polling_div.results, cands[polling_div.riding_id])
    return (polling_div.div_id, polling_div.riding_id, polling_div.name, winner, margin)

def generate_riding_candidates(ridings):
    riding_candidates = list()
    for riding in ridings.values():
        for cand_id, result in riding.results.items():
            riding_candidates.append((cand_id, riding.riding_id, result))
    return riding_candidates

def generate_poll_candidates(polls):
    poll_candidates = list()
    for poll in polls:
        for cand_id, result in poll.results.items():
            poll_candidates.append((cand_id, poll.riding_id, poll.div_id, result))
    return poll_candidates

import raw_data.data_2004.adapter_2004
import raw_data.data_2006.adapter_2006
import raw_data.data_2008.adapter_2008
import raw_data.data_2011.adapter_2011
import raw_data.data_2015.adapter_2015

years = ['2004', '2006', '2008', '2011', '2015']
csv_adapters = {
    '2004' : raw_data.data_2004.adapter_2004.Adapter2004,
    '2006' : raw_data.data_2006.adapter_2006.Adapter2006,
    '2008' : raw_data.data_2008.adapter_2008.Adapter2008,
    '2011' : raw_data.data_2011.adapter_2011.Adapter2011,
    '2015' : raw_data.data_2015.adapter_2015.Adapter2015
}

for year in years:
    processor_obj = processor.Processor(year, csv_adapters[year])
    cand_dict, riding_dict, poll_divs = processor_obj.process_data()
    save_to_db(cand_dict, riding_dict, poll_divs, year)
