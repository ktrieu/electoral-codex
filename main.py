import re
import os
import sqlite3
import models

YEARS = ['2006', '2008', '2011', '2015']

def riding_num_from_csv_name(name):
    pattern = r'pollresults_resultatsbureau([0-9]+).csv'
    match = re.match(pattern, name)
    if not match:
        return None
    else:
        return match.group(1)

if __name__ == "__main__":
    for year in YEARS:
        conn = sqlite3.connect(f'{year}.db')
        #explicitly enable foreign key constraints
        conn.execute(r'PRAGMA foreign_keys = 1')
        conn.commit()
        cursor = conn.cursor()
        models.drop_tables(cursor)
        conn.commit()
        models.create_tables(cursor)
        conn.commit()
        csv_files = os.listdir(f'poll_by_poll/{year}')
        
