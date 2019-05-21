import common_defs
import sqlite3
import csv
import processor
import sys
import os

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

def process_data():
    for year in years:
        processor_obj = processor.Processor(year, csv_adapters[year])
        election = processor_obj.process_data()
        conn = sqlite3.connect(f'{year}.db')
        election.save(conn.cursor())
        conn.commit()
        conn.close()

CAND_DUMP_QUERY = r'SELECT candidates.cand_id, candidates.name, ridings.name FROM candidates JOIN ridings ON ridings.riding_id == candidates.riding_id'

def dump_cands():
    for year in years:
        if os.path.exists(f'{year}.db'):
            conn = sqlite3.connect(f'{year}.db')
            candidates = conn.cursor().execute(CAND_DUMP_QUERY)
            with open(f'cands_{year}.csv', 'w', newline='', encoding='utf-8') as cand_file:
                cand_csv = csv.writer(cand_file)
                cand_csv.writerow(('id', 'name', 'riding_name', 'last_win_margin', 'party_leader', 'pm', 'mpp', 'premier'))
                for cand in candidates:
                    cand_csv.writerow(cand)
            conn.close()
        else:
            print(f'{year}.db does not exist. Run without arguments to generate database files.')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == '--dump_cands':
            dump_cands()
        else:
            print('Invalid arguments.')
    elif len(sys.argv) == 1:
        process_data()
    else:
        print('Invalid arguments.')

